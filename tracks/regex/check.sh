#!/usr/bin/env bash
# Usage: ./check.sh <exercise-id> '<your full command>'
# Runs your command inside data/ and compares its output with the expected answer (stored as a hash).
#
# Authoring (used by the forge skill; never shows the answer):
#   ./check.sh --seal <exercise-id> '<reference command>' [ordered]
set -u
root="$(cd "$(dirname "$0")" && pwd)"

seal=0
if [ "${1:-}" = "--seal" ]; then seal=1; shift; fi
[ $# -ge 2 ] || { echo "usage: ./check.sh <id> '<command>'   |   ./check.sh --seal <id> '<ref command>' [ordered]"; exit 2; }
n=$1; cmd=$2

if [ "$seal" = 1 ] && [ "${3:-}" = "ordered" ]; then
  grep -qx "$n" "$root/.ordered" 2>/dev/null || echo "$n" >> "$root/.ordered"
fi
ordered() { grep -qx "$n" "$root/.ordered" 2>/dev/null; }   # exercises where output order matters

norm() {
  sed -E 's/[[:space:]]+$//; s/^[[:space:]]+//; s/[[:space:]]+/ /g; s#^\./##' | sed '/^$/d' |
  if ordered; then cat; else LC_ALL=C sort; fi
}

out=$(cd "$root/data" && bash -c "$cmd" 2>&1 | norm)
got_hash=$(printf '%s\n' "$out" | sha256sum | cut -d' ' -f1)
got_lines=$(printf '%s' "$out" | grep -c '' )

if [ "$seal" = 1 ]; then
  grep -v "^$n " "$root/.answers" > "$root/.answers.tmp" 2>/dev/null || true
  echo "$n $got_hash $got_lines" >> "$root/.answers.tmp" && mv "$root/.answers.tmp" "$root/.answers"
  echo "sealed $n ($got_lines line(s))"
  exit 0
fi

line=$(grep -E "^$n " "$root/.answers" || true)
[ -n "$line" ] || { echo "no exercise $n"; exit 2; }
want_hash=$(cut -d' ' -f2 <<<"$line"); want_lines=$(cut -d' ' -f3 <<<"$line")

if [ "$got_hash" = "$want_hash" ]; then
  echo "✅ Exercise $n: correct"
else
  if [ "$got_lines" = "$want_lines" ]; then
    echo "❌ Exercise $n: not quite — right number of lines ($got_lines), but the content differs. Check the output format the exercise asks for."
  else
    echo "❌ Exercise $n: not quite — you produced $got_lines line(s), expected $want_lines."
  fi
  ordered && echo "   (order matters for this one)"
  exit 1
fi
