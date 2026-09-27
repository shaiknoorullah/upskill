#!/usr/bin/env bash
# Prints the last N lines (default 200) of your left tmux pane so Claude can see your terminal.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .tutor-pane ]; then
  echo "No tutor pane yet. Start the session with ./scripts/tutor.sh"
  exit 1
fi
tmux capture-pane -p -J -t "$(cat .tutor-pane)" -S "-${1:-200}"
