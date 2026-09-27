#!/usr/bin/env bash
# Opens the study session in tmux: left pane = your shell (inside lab-ubuntu once it exists), right pane = Claude Code.
set -euo pipefail
cd "$(dirname "$0")/.."
SESSION=prep
if tmux has-session -t "$SESSION" 2>/dev/null; then
  exec tmux attach -t "$SESSION"
fi
if incus info laptop:lab-ubuntu >/dev/null 2>&1; then
  LEFT="incus exec laptop:lab-ubuntu -- su -l me"
else
  LEFT="${SHELL:-bash}"
fi
tmux new-session -d -s "$SESSION" -c "$PWD" "$LEFT"
tmux display-message -p -t "$SESSION" '#{pane_id}' > .tutor-pane
tmux split-window -h -t "$SESSION" -c "$PWD" "claude"
tmux select-pane -t "$(cat .tutor-pane)"
exec tmux attach -t "$SESSION"
