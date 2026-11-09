#!/usr/bin/env bash
# Exercise install.sh against a temporary HOME. The real checkout is not modified.
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
install="${root}/install.sh"
skills=(setup-design-index create-requirements)
failures=0

fail() {
  echo "FAIL: $*" >&2
  failures=$((failures + 1))
}

assert_eq() {
  local actual=$1 expected=$2 label=$3
  if [[ $actual != "$expected" ]]; then
    fail "${label}: expected [${expected}] got [${actual}]"
  fi
}

run_install() {
  local home=$1
  shift
  status=0
  output=$(HOME="$home" "$install" "$@" 2>&1) || status=$?
}

skill_path() {
  echo "${root}/.agents/skills/$1"
}

expect_link() {
  local link=$1 skill=$2
  if [[ ! -L $link ]]; then
    fail "${link} is not a symlink"
    return
  fi
  assert_eq "$(realpath "$link")" "$(realpath "$(skill_path "$skill")")" "$link"
}

fresh_home() {
  local home
  home=$(mktemp -d)
  mkdir -p "${home}/.agents/skills" "${home}/.claude/skills" "${home}/.grok/skills"
  echo "$home"
}

test_install_links_and_replaces() {
  local home source_setup source_create relative
  home=$(fresh_home)
  source_setup=$(skill_path setup-design-index)
  source_create=$(skill_path create-requirements)
  ln -s /tmp/other-checkout "${home}/.agents/skills/setup-design-index"
  echo local > "${home}/.claude/skills/setup-design-index"
  ln -s "$source_create" "${home}/.agents/skills/create-requirements"
  relative=$(realpath --relative-to="${home}/.claude/skills" "$source_create")
  ln -s "$relative" "${home}/.claude/skills/create-requirements"

  run_install "$home" --user
  assert_eq "$status" 0 "install status"
  assert_eq "$output" "linked ${home}/.agents/skills/setup-design-index -> ${source_setup}
linked ${home}/.claude/skills/setup-design-index -> ${source_setup}
linked ${home}/.agents/skills/create-requirements -> ${source_create}
linked ${home}/.claude/skills/create-requirements -> ${source_create}" "install output"
  expect_link "${home}/.agents/skills/setup-design-index" setup-design-index
  expect_link "${home}/.claude/skills/setup-design-index" setup-design-index
  expect_link "${home}/.agents/skills/create-requirements" create-requirements
  expect_link "${home}/.claude/skills/create-requirements" create-requirements

  run_install "$home" --user
  assert_eq "$status" 0 "second install status"
  expect_link "${home}/.agents/skills/setup-design-index" setup-design-index
  rm -rf "$home"
}

test_refuses_directory() {
  local home dest
  home=$(fresh_home)
  dest="${home}/.agents/skills/setup-design-index"
  mkdir "$dest"
  echo kept > "${dest}/SKILL.md"

  run_install "$home" --user
  assert_eq "$status" 1 "directory status"
  assert_eq "$output" "refusing to replace ${dest} (directory)" "directory output"
  assert_eq "$(cat "${dest}/SKILL.md")" "kept" "directory contents"
  if [[ -e ${dest}/setup-design-index || -L ${dest}/setup-design-index ]]; then
    fail "install nested a link inside ${dest}"
  fi
  if [[ -e ${home}/.claude/skills/setup-design-index || -L ${home}/.claude/skills/setup-design-index ]]; then
    fail "install continued after refusing a directory"
  fi
  rm -rf "$home"
}

test_missing_skill() {
  local fake home
  fake=$(mktemp -d)
  home=$(fresh_home)
  cp "$install" "${fake}/install.sh"

  status=0
  output=$(HOME="$home" "${fake}/install.sh" --user 2>&1) || status=$?
  assert_eq "$status" 1 "missing skill status"
  assert_eq "$output" "missing skill: ${fake}/.agents/skills/setup-design-index" "missing skill output"
  if [[ -e ${home}/.agents/skills/setup-design-index || -L ${home}/.agents/skills/setup-design-index ]]; then
    fail "missing skill still created a link"
  fi
  rm -rf "$fake" "$home"
}

test_uninstall_keeps_foreign_paths() {
  local home source_setup source_create other_target kept
  home=$(fresh_home)
  source_setup=$(skill_path setup-design-index)
  source_create=$(skill_path create-requirements)
  ln -s "$source_setup" "${home}/.agents/skills/setup-design-index"
  ln -s "$(realpath --relative-to="${home}/.claude/skills" "$source_setup")" \
    "${home}/.claude/skills/setup-design-index"
  ln -s "$source_setup" "${home}/.grok/skills/setup-design-index"
  other_target=$(mktemp -d)
  ln -s "$other_target" "${home}/.agents/skills/create-requirements"
  mkdir "${home}/.claude/skills/create-requirements"
  echo local > "${home}/.claude/skills/create-requirements/SKILL.md"
  kept="${home}/.agents/skills/other-skill"
  ln -s "$source_setup" "$kept"

  run_install "$home" --user uninstall
  assert_eq "$status" 0 "uninstall status"
  assert_eq "$output" "Removed ${home}/.agents/skills/setup-design-index
Removed ${home}/.claude/skills/setup-design-index
Removed ${home}/.grok/skills/setup-design-index
Left ${home}/.agents/skills/create-requirements in place; it does not point at this checkout
Left ${home}/.claude/skills/create-requirements in place; it does not point at this checkout" "uninstall output"
  if [[ -e ${home}/.agents/skills/setup-design-index || -L ${home}/.agents/skills/setup-design-index ]]; then
    fail "owned absolute link was not removed"
  fi
  if [[ -e ${home}/.claude/skills/setup-design-index || -L ${home}/.claude/skills/setup-design-index ]]; then
    fail "owned relative link was not removed"
  fi
  if [[ -e ${home}/.grok/skills/setup-design-index || -L ${home}/.grok/skills/setup-design-index ]]; then
    fail "old grok link was not removed"
  fi
  assert_eq "$(realpath "${home}/.agents/skills/create-requirements")" "$(realpath "$other_target")" "foreign link"
  assert_eq "$(cat "${home}/.claude/skills/create-requirements/SKILL.md")" "local" "directory skill"
  assert_eq "$(realpath "$kept")" "$(realpath "$source_setup")" "unrelated skill"
  [[ -f ${source_create}/SKILL.md ]] || fail "checkout skill was removed"

  run_install "$home" uninstall --user
  assert_eq "$status" 0 "second uninstall status"
  assert_eq "$output" "Left ${home}/.agents/skills/create-requirements in place; it does not point at this checkout
Left ${home}/.claude/skills/create-requirements in place; it does not point at this checkout" "second uninstall output"
  rm -rf "$home" "$other_target"
}

test_uninstall_dangling_owned_link() {
  local fake home owned foreign skill
  fake=$(mktemp -d)
  home=$(fresh_home)
  cp "$install" "${fake}/install.sh"
  for skill in "${skills[@]}"; do
    mkdir -p "${fake}/.agents/skills/${skill}"
    echo "name: ${skill}" > "${fake}/.agents/skills/${skill}/SKILL.md"
  done
  owned="${home}/.agents/skills/setup-design-index"
  ln -s "${fake}/.agents/skills/setup-design-index" "$owned"
  rm -rf "${fake}/.agents/skills/setup-design-index"
  foreign="${home}/.claude/skills/setup-design-index"
  ln -s "${fake}/missing/setup-design-index" "$foreign"
  ln -s "${fake}/.agents/skills/create-requirements" "${home}/.agents/skills/create-requirements"

  status=0
  output=$(HOME="$home" "${fake}/install.sh" --user uninstall 2>&1) || status=$?
  assert_eq "$status" 0 "dangling uninstall status"
  assert_eq "$output" "Removed ${owned}
Left ${foreign} in place; it does not point at this checkout
Removed ${home}/.agents/skills/create-requirements" "dangling uninstall output"
  if [[ -L $owned ]]; then
    fail "dangling owned link was not removed"
  fi
  [[ -L $foreign ]] || fail "foreign dangling link was removed"
  [[ -f ${fake}/.agents/skills/create-requirements/SKILL.md ]] || fail "fake skill was removed"
  rm -rf "$fake" "$home"
}

test_usage() {
  local home
  home=$(fresh_home)
  run_install "$home" install extra
  assert_eq "$status" 2 "extra arg status"
  assert_eq "$output" "usage: install.sh [--user | --repo PATH] [install|uninstall]" "extra arg usage"
  run_install "$home" no-such
  assert_eq "$status" 2 "unknown command status"
  assert_eq "$output" "usage: install.sh [--user | --repo PATH] [install|uninstall]" "unknown command usage"
  rm -rf "$home"
}

prompt_install() {
  local home=$1 answers=$2
  shift 2
  status=0
  output=$(
    HOME="$home" python3 - "$install" "$answers" "$@" <<'PY'
import os
import pty
import select
import signal
import sys

def line_bytes(text):
    if not text.endswith("\n"):
        text += "\n"
    return text.encode()

script = sys.argv[1]
lines = sys.argv[2].splitlines(keepends=True)
args = sys.argv[3:]
pid, fd = pty.fork()
if pid == 0:
    os.execv(script, [script, *args])

chunks = []
stage = "choice"
timed_out = False
while True:
    readable, _, _ = select.select([fd], [], [], 2)
    if not readable:
        timed_out = True
        os.kill(pid, signal.SIGKILL)
        break
    try:
        chunk = os.read(fd, 4096)
    except OSError:
        break
    if not chunk:
        break
    chunks.append(chunk)
    seen = b"".join(chunks)
    if stage == "choice" and b"Choice [u/r]:" in seen and lines:
        os.write(fd, line_bytes(lines.pop(0)))
        stage = "path" if lines else "done"
    elif stage == "path" and b"Repository path" in seen and lines:
        os.write(fd, line_bytes(lines.pop(0)))
        stage = "done"
_, wait_status = os.waitpid(pid, 0)
sys.stdout.buffer.write(b"".join(chunks))
if timed_out:
    raise SystemExit(1)
raise SystemExit(os.waitstatus_to_exitcode(wait_status))
PY
  ) || status=$?
}

test_repo_install_and_uninstall() {
  local home repo source_setup source_create user_link
  home=$(fresh_home)
  repo=$(mktemp -d)
  source_setup=$(skill_path setup-design-index)
  source_create=$(skill_path create-requirements)
  user_link="${home}/.agents/skills/setup-design-index"
  ln -s "$source_setup" "$user_link"

  run_install "$home" --repo "$repo"
  assert_eq "$status" 0 "repo install status"
  assert_eq "$output" "linked ${repo}/.agents/skills/setup-design-index -> ${source_setup}
linked ${repo}/.claude/skills/setup-design-index -> ${source_setup}
linked ${repo}/.agents/skills/create-requirements -> ${source_create}
linked ${repo}/.claude/skills/create-requirements -> ${source_create}" "repo install output"
  expect_link "${repo}/.agents/skills/setup-design-index" setup-design-index
  expect_link "${repo}/.claude/skills/setup-design-index" setup-design-index
  expect_link "${repo}/.agents/skills/create-requirements" create-requirements
  expect_link "${repo}/.claude/skills/create-requirements" create-requirements
  assert_eq "$(realpath "$user_link")" "$(realpath "$source_setup")" "user link during repo install"

  run_install "$home" uninstall --repo "$repo"
  assert_eq "$status" 0 "repo uninstall status"
  assert_eq "$output" "Removed ${repo}/.agents/skills/setup-design-index
Removed ${repo}/.claude/skills/setup-design-index
Removed ${repo}/.agents/skills/create-requirements
Removed ${repo}/.claude/skills/create-requirements" "repo uninstall output"
  if [[ -L ${repo}/.agents/skills/setup-design-index ]]; then
    fail "repo link survived uninstall"
  fi
  assert_eq "$(realpath "$user_link")" "$(realpath "$source_setup")" "user link during repo uninstall"
  rm -rf "$home" "$repo"
}

test_repo_refuses_this_checkout_and_missing_path() {
  local home missing
  home=$(fresh_home)
  run_install "$home" --repo "$root"
  assert_eq "$status" 1 "checkout repo status"
  assert_eq "$output" "this checkout already contains the skills in .agents/skills" "checkout repo output"

  missing="${home}/missing-repo"
  run_install "$home" --repo "$missing"
  assert_eq "$status" 1 "missing repo status"
  assert_eq "$output" "repository not found: ${missing}" "missing repo output"
  run_install "$home" --user --repo "$home"
  assert_eq "$status" 2 "both scopes status"
  assert_eq "$output" "usage: install.sh [--user | --repo PATH] [install|uninstall]" "both scopes usage"
  rm -rf "$home"
}

test_prompt_chooses_user_or_repo() {
  local home repo source_setup
  home=$(fresh_home)
  repo=$(mktemp -d)
  source_setup=$(skill_path setup-design-index)

  prompt_install "$home" $'u\n'
  assert_eq "$status" 0 "prompt user status"
  expect_link "${home}/.agents/skills/setup-design-index" setup-design-index
  expect_link "${home}/.claude/skills/create-requirements" create-requirements
  if [[ $output != *"Choice [u/r]:"* ]]; then
    fail "prompt user did not ask for a choice"
  fi
  if [[ -e ${home}/.grok/skills/setup-design-index || -L ${home}/.grok/skills/setup-design-index ]]; then
    fail "prompt user wrote ~/.grok/skills"
  fi

  prompt_install "$home" "$(printf 'r\n%s\n' "$repo")" uninstall
  assert_eq "$status" 0 "prompt repo uninstall status"
  if [[ $output != *"Repository path"* ]]; then
    fail "prompt repo did not ask for a path"
  fi

  pushd "$repo" >/dev/null
  prompt_install "$home" $'r\n\n'
  popd >/dev/null
  assert_eq "$status" 0 "prompt default repo status"
  expect_link "${repo}/.agents/skills/setup-design-index" setup-design-index
  expect_link "${repo}/.claude/skills/setup-design-index" setup-design-index
  assert_eq "$(realpath "${home}/.agents/skills/setup-design-index")" "$(realpath "$source_setup")" \
    "user link after repo prompt"

  prompt_install "$home" $'nope\n'
  assert_eq "$status" 2 "bad choice status"
  if [[ $output != *"choose u or r"* ]]; then
    fail "bad choice output [${output}]"
  fi
  rm -rf "$home" "$repo"
}

test_requires_a_choice_without_a_terminal() {
  local home
  home=$(fresh_home)
  status=0
  output=$(HOME="$home" "$install" </dev/null 2>&1) || status=$?
  assert_eq "$status" 2 "no terminal status"
  assert_eq "$output" "usage: install.sh [--user | --repo PATH] [install|uninstall]
run in a terminal to choose user account or repository" "no terminal output"
  rm -rf "$home"
}

test_install_links_and_replaces
test_refuses_directory
test_missing_skill
test_uninstall_keeps_foreign_paths
test_uninstall_dangling_owned_link
test_usage
test_repo_install_and_uninstall
test_repo_refuses_this_checkout_and_missing_path
test_prompt_chooses_user_or_repo
test_requires_a_choice_without_a_terminal

if [[ $failures -ne 0 ]]; then
  echo "${failures} failure(s)" >&2
  exit 1
fi
echo "ok"
