#!/usr/bin/env bash
# Link this checkout's skills into the user skill directories.
# Refuses to replace a path that is not already a symlink to this checkout.
set -euo pipefail

root=$(cd "$(dirname "$0")" && pwd)
skills=(setup-design-index create-requirements)
dest_roots=(
  "${HOME}/.grok/skills"
  "${HOME}/.agents/skills"
  "${HOME}/.claude/skills"
)

for dest_root in "${dest_roots[@]}"; do
  mkdir -p "$dest_root"
done

for skill in "${skills[@]}"; do
  source="${root}/.agents/skills/${skill}"
  if [[ ! -d "$source" ]]; then
    echo "missing skill: ${source}" >&2
    exit 1
  fi
  expected=$(readlink -f "$source")
  for dest_root in "${dest_roots[@]}"; do
    dest="${dest_root}/${skill}"
    if [[ -L "$dest" ]]; then
      current=$(readlink -f "$dest")
      if [[ "$current" != "$expected" ]]; then
        echo "refusing to replace ${dest} (symlink to ${current}, not this checkout)" >&2
        exit 1
      fi
    elif [[ -e "$dest" ]]; then
      echo "refusing to replace ${dest} (not a symlink to this checkout)" >&2
      exit 1
    fi
    ln -sfn "$source" "$dest"
    echo "linked ${dest} -> ${source}"
  done
done
