#!/usr/bin/env bash
# Run the living-speckit workflow unattended on a fixture project, approving every gate.
# Commits all work (except the workflow's run state) right before the implementation
# review gate, as a person would. Prints the run's final status.
#
# Usage: tests/living/run.sh PROJECT "feature description"
#   PROJECT: a project created by tests/living/setup.sh
# Gate answers and the full log go to PROJECT/.specify/workflows/driver/.
set -u
proj="$(cd "$1" && pwd)"; spec="$2"
work="$proj/.specify/workflows/driver"
mkdir -p "$work"; rm -f "$work/in" "$work/log" "$work/driver.log"; mkfifo "$work/in"
sleep 100000 > "$work/in" & holder=$!
( cd "$proj" && script -qfec "specify workflow run living-speckit -i spec=$(printf '%q' "$spec")" "$work/log" \
    < "$work/in" > /dev/null 2>&1 ) &
runner=$!
answered=0
while kill -0 "$runner" 2>/dev/null; do
  n=$(grep -ac 'Choose \[' "$work/log" 2>/dev/null); n=${n:-0}
  if [ "$n" -gt "$answered" ]; then
    sleep 2
    gate=$(sed 's/\x1b\[[0-9;?]*[a-zA-Z]//g' "$work/log" | awk '/Gate ─/{g=""} /│ /{g=g $0 "\n"} END{printf "%s", g}' | sed -n 1p)
    if echo "$gate" | grep -q 'Review the implementation'; then
      ( cd "$proj" && git add -A -- . ':(exclude).specify/workflows/runs' && \
        git -c user.name="Living Fixture" -c user.email=fixture@example.invalid commit -qm "Implement feature" ) \
        >> "$work/driver.log" 2>&1
      echo "committed before gate $n" >> "$work/driver.log"
    fi
    echo "gate $n:$gate" >> "$work/driver.log"
    echo 1 > "$work/in"
    answered=$n
  fi
  sleep 5
done
kill "$holder" 2>/dev/null
sed 's/\x1b\[[0-9;?]*[a-zA-Z]//g' "$work/log" | grep -a 'Status:' | tail -1
