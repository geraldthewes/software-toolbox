#!/usr/bin/env bash
# Link this checkout's skills into the directories read by Grok, Codex,
# OpenCode (.agents/skills) and Claude Code (.claude/skills).
# The script asks whether those directories are under the user account or a repository.
# Uninstall removes a link only when its target is this checkout's skill.
# A real directory is refused: ln -sfn would nest a new link inside it.
set -euo pipefail

root=$(cd "$(dirname "$0")" && pwd)
skills=(setup-design-index create-requirements analyze-review-feedback architecture-critique)
scope=
repo_path=
action=
install_roots=()
uninstall_roots=()

usage() {
  echo "usage: install.sh [--user | --repo PATH] [install|uninstall]" >&2
  exit 2
}

same_target() {
  local link=$1 expected=$2
  [[ -L "$link" ]] || return 1
  [[ "$(realpath -m "$link")" == "$(realpath -m "$expected")" ]]
}

prompt_scope() {
  local choice reply default_repo question
  if [[ ! -t 0 ]]; then
    echo "usage: install.sh [--user | --repo PATH] [install|uninstall]" >&2
    echo "run in a terminal to choose user account or repository" >&2
    exit 2
  fi
  if [[ $action == uninstall ]]; then
    question="Remove the skills from a user account or a repository?"
  else
    question="Install the skills for a user account or a repository?"
  fi
  echo "$question" >&2
  echo "  [u] user account (${HOME}/.agents/skills and ${HOME}/.claude/skills)" >&2
  echo "  [r] repository (.agents/skills and .claude/skills)" >&2
  if ! read -r -p "Choice [u/r]: " choice; then
    echo >&2
    exit 2
  fi
  choice=${choice,,}
  case $choice in
    u|user) scope=user ;;
    r|repo|repository) scope=repo ;;
    *)
      echo "choose u or r" >&2
      exit 2
      ;;
  esac
  if [[ $scope == repo ]]; then
    default_repo=$(pwd)
    if ! read -r -p "Repository path [${default_repo}]: " reply; then
      echo >&2
      exit 2
    fi
    repo_path=${reply:-$default_repo}
  fi
}

apply_scope() {
  local resolved
  if [[ $scope == user ]]; then
    install_roots=(
      "${HOME}/.agents/skills"
      "${HOME}/.claude/skills"
    )
    # ~/.grok/skills is no longer written. Uninstall still clears a link there
    # when it points at this checkout, which is where an older install.sh wrote it.
    uninstall_roots=(
      "${HOME}/.agents/skills"
      "${HOME}/.claude/skills"
      "${HOME}/.grok/skills"
    )
    return
  fi
  if [[ -z $repo_path ]]; then
    echo "missing repository path" >&2
    exit 2
  fi
  if [[ ! -d $repo_path ]]; then
    echo "repository not found: ${repo_path}" >&2
    exit 1
  fi
  resolved=$(cd "$repo_path" && pwd)
  if [[ $resolved == "$root" ]]; then
    echo "this checkout already contains the skills in .agents/skills" >&2
    exit 1
  fi
  repo_path=$resolved
  install_roots=(
    "${repo_path}/.agents/skills"
    "${repo_path}/.claude/skills"
  )
  uninstall_roots=("${install_roots[@]}")
}

install_skill() {
  local skill=$1 source dest_root dest
  source="${root}/.agents/skills/${skill}"
  if [[ ! -d "$source" ]]; then
    echo "missing skill: ${source}" >&2
    exit 1
  fi
  for dest_root in "${install_roots[@]}"; do
    dest="${dest_root}/${skill}"
    mkdir -p "$dest_root"
    if [[ -d "$dest" && ! -L "$dest" ]]; then
      echo "refusing to replace ${dest} (directory)" >&2
      exit 1
    fi
    if ! same_target "$dest" "$source"; then
      ln -sfn "$source" "$dest"
    fi
    echo "linked ${dest} -> ${source}"
  done
}

uninstall_skill() {
  local skill=$1 source dest_root dest
  source="${root}/.agents/skills/${skill}"
  for dest_root in "${uninstall_roots[@]}"; do
    dest="${dest_root}/${skill}"
    if [[ ! -e "$dest" && ! -L "$dest" ]]; then
      continue
    fi
    if same_target "$dest" "$source"; then
      rm "$dest"
      echo "Removed ${dest}"
    else
      echo "Left ${dest} in place; it does not point at this checkout"
    fi
  done
}

install_all() {
  local skill
  for skill in "${skills[@]}"; do
    install_skill "$skill"
  done
}

uninstall_all() {
  local skill
  for skill in "${skills[@]}"; do
    uninstall_skill "$skill"
  done
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --user)
      [[ -n $scope ]] && usage
      scope=user
      shift
      ;;
    --repo)
      [[ -n $scope ]] && usage
      [[ $# -ge 2 && $2 != --* ]] || usage
      scope=repo
      repo_path=$2
      shift 2
      ;;
    install|uninstall)
      [[ -n $action ]] && usage
      action=$1
      shift
      ;;
    *)
      usage
      ;;
  esac
done

action=${action:-install}
if [[ -z $scope ]]; then
  prompt_scope
fi
apply_scope

case $action in
  install) install_all ;;
  uninstall) uninstall_all ;;
esac
