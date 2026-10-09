# Live shared Excalidraw canvas (for the `draw` skill)

[yctimlin/mcp_excalidraw](https://github.com/yctimlin/mcp_excalidraw) (MIT) gives a canvas at http://127.0.0.1:3000 that you and Claude edit together. Your strokes sync back, and Claude reads them with `describe_scene` / `query_elements` / `get_canvas_screenshot`.

**Not activated automatically.** On an org-managed machine, add it to the IT software inventory first (two container images: `ghcr.io/yctimlin/mcp_excalidraw-canvas`, `ghcr.io/yctimlin/mcp_excalidraw`).

## 1. Canvas (localhost only, persistent)
```bash
./integrations/excalidraw/canvas.sh up      # starts the container bound to 127.0.0.1:3000, data in local/canvas/
./integrations/excalidraw/canvas.sh down
```

## 2. MCP server for Claude Code (user scope)
```bash
claude mcp add excalidraw --scope user -- \
  docker run -i --rm --add-host=host.docker.internal:host-gateway \
  -e EXPRESS_SERVER_URL=http://host.docker.internal:3000 \
  -e ENABLE_CANVAS_SYNC=true \
  ghcr.io/yctimlin/mcp_excalidraw:latest
```
Restart Claude Code. The tools then appear as `mcp__excalidraw__*`, and the `draw` skill switches to live mode automatically.

## Pinning
After the first pull, pin both images by digest (`docker inspect --format '{{index .RepoDigests 0}}' <image>`) in `canvas.sh` and in the `claude mcp add` line, so an upstream update can't change what runs.
