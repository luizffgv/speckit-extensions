#!/usr/bin/env bash
# Create a throwaway Spec Kit project from the fixture, with this repository's living
# extension, preset and living-speckit workflow installed from the working tree (--dev).
#
# Usage: tests/living/setup.sh [--legacy] [DEST]   (DEST must not exist; default: a new temp dir)
#
# --legacy: a codebase from before the extension was installed. 001 and 002 are Draft specs that
# were never archived (001 still has plan, tasks, checklists, data model, contracts and
# quickstart; 002 has only its spec), and 003-friendly-empty-list was delivered with the core
# commands, so it changed 002's empty-list message without recording a delta.
set -euo pipefail

legacy=0
if [[ "${1:-}" == "--legacy" ]]; then
  legacy=1
  shift
fi

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(cd "$here/../.." && pwd)"

if [[ $# -ge 1 ]]; then
  dest="$1"
  if [[ -e "$dest" ]]; then
    echo "error: $dest already exists" >&2
    exit 1
  fi
  mkdir -p "$dest"
else
  dest="$(mktemp -d "${TMPDIR:-/tmp}/living-fixture.XXXXXX")"
fi
dest="$(cd "$dest" && pwd)"

command -v specify >/dev/null || { echo "error: specify is not installed" >&2; exit 1; }

cd "$dest"
git init -q -b main
specify init --here --force --non-interactive --integration claude --ignore-agent-tools >/dev/null

# Fixture files go on top, so its constitution replaces the template.
cp -a "$here/fixture/." "$dest/"
printf 'tasks.json\n__pycache__/\n.specify/workflows/driver/\n' >> .gitignore

if [[ $legacy -eq 1 ]]; then
  for spec in specs/001-add-task/spec.md specs/002-list-tasks/spec.md; do
    # Draft status, no archive line: the core template's header.
    sed -i -e 's/^\*\*Status\*\*: Living$/**Status**: Draft/' \
      -e '/^\*\*Archived artifacts\*\*/,/^$/d' "$spec"
  done
  cp -a "$here/legacy/." "$dest/"
  hint='No tasks yet. Add one with: todo.py add <title>'
  sed -i "s/print(\"No tasks.\")/print(\"$hint\")/" todo.py
  sed -i "s/\"No tasks.\\\\n\"/\"$hint\\\\n\"/" tests/test_todo.py
fi

specify extension add --dev "$repo/extensions/living" >/dev/null
specify preset add --dev "$repo/presets/living" >/dev/null
specify workflow add --dev "$repo/workflows/living-speckit" >/dev/null

python3 -m unittest discover -s tests >/dev/null 2>&1 || {
  echo "error: fixture tests fail" >&2
  exit 1
}

git add -A
git -c user.name="Living Fixture" -c user.email="fixture@example.invalid" \
  commit -q -m "Fixture baseline$([[ $legacy -eq 1 ]] && echo " (pre-extension)")"

echo "$dest"
