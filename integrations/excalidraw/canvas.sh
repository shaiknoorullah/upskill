#!/usr/bin/env bash
# Live Excalidraw canvas for the draw skill. Binds to 127.0.0.1 only; state persists in local/canvas/ (gitignored).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
IMAGE="${EXCALIDRAW_CANVAS_IMAGE:-ghcr.io/yctimlin/mcp_excalidraw-canvas:latest}"   # pin by digest after first pull
NAME=upskill-canvas
case "${1:-status}" in
  up)
    mkdir -p "$REPO/local/canvas"
    docker run -d --name "$NAME" --restart unless-stopped \
      -p 127.0.0.1:3000:3000 \
      -e EXCALIDRAW_DATA_DIR=/data -v "$REPO/local/canvas:/data" \
      "$IMAGE" >/dev/null
    echo "canvas: http://127.0.0.1:3000" ;;
  down) docker rm -f "$NAME" >/dev/null && echo "canvas stopped" ;;
  status) docker ps --filter "name=^${NAME}$" --format '{{.Names}} {{.Status}} {{.Ports}}' ;;
  *) echo "usage: canvas.sh up|down|status"; exit 2 ;;
esac
