#!/usr/bin/env bash
# Create a throwaway Spec Kit project from the fixture, with this repository's living
# extension, preset and living-speckit workflow installed from the working tree (--dev).
#
# Usage: tests/living/setup.sh [DEST]   (DEST must not exist; default: a new temp dir)
set -euo pipefail

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

specify extension add --dev "$repo/extensions/living" >/dev/null
specify preset add --dev "$repo/presets/living" >/dev/null
specify workflow add --dev "$repo/workflows/living-speckit" >/dev/null

python3 -m unittest discover -s tests >/dev/null 2>&1 || {
  echo "error: fixture tests fail" >&2
  exit 1
}

git add -A
git -c user.name="Living Fixture" -c user.email="fixture@example.invalid" \
  commit -q -m "Fixture baseline: living specs 001-add-task and 002-list-tasks"

echo "$dest"
