---
name: draw
description: Visual learning with Excalidraw: draw-before-solve mental models, connect-the-dots canvases after a challenge, reviewing the user's own drawing, and a growing per-track mastery map, collaboratively on a live shared canvas when available. Use when the user wants to draw, sketch, map or connect concepts, or when pause offers a connect step.
---

# draw: think with your hands

The user understands deeply when they **casually draw and connect the dots**. They can't listen and write at the same time, so never lecture while they draw. Drawing is *their* act: you set up the dots and review; they make the connections.

## Pick the canvas (in this order)
1. **Live shared canvas** (preferred): if `mcp__excalidraw__*` tools are available (a local `mcp_excalidraw` server; canvas at http://127.0.0.1:3000), both of you edit the same canvas in real time. Read their strokes with `describe_scene` / `query_elements` / `get_canvas_screenshot`. Write with `batch_create_elements` / `update_element`. Persist with `export_scene` to `drawings/<track>/<name>.excalidraw`.
2. **File-based** (fallback): write `drawings/<track>/<name>.excalidraw` (valid Excalidraw JSON). The user opens it in excalidraw.com or Obsidian, edits it, saves, and says "done". Then read the file back.
3. **Render-only** (`mcp__claude_ai_Excalidraw__create_view`): use it only to *show* a finished map. It cannot read the user's edits. Never use it for the collaborative modes.

If the live canvas is missing, say once: "Live canvas isn't running. Using a file instead." Don't troubleshoot installs mid-session.

## Modes
- **Connect-the-dots** (after a challenge, ~1 min): place 4–7 concept boxes **unconnected**, scattered, including one or two near-confusables (e.g. `\b`, `-w`, `^`, `[^-]`, `(?<!…)`, `awk $1==`). Ask: "Wire these: arrows for 'is a kind of / fails when / use instead of'." Then review.
- **Draw-before-solve** (big topics, e.g. how a Service routes to Pods or how a signal reaches PID 1): ask them to sketch their current mental model in 2 minutes, *before* the hands-on challenge. Save it. After the challenge, put it next to reality: "Your arrow X→Y, the experiment showed X→Z."
- **Review my drawing**: grade it like an attempt chain. List what is connected correctly, what's missing (the 1–2 most important gaps only), and what is wrong (each with the experiment that would disprove it). Never redraw their whole diagram. Add at most 2 suggestion elements, in a distinct color and labelled "?".
- **Mastery map**: one living map per track at `drawings/maps/<track>.excalidraw`. Each concept node is colored by ledger level (`./up map`): grey untouched, yellow practised, green demonstrated, blue exam-ready. Add new nodes as concepts are learned, and link them to the user's own connections from connect-the-dots sessions. Update it when the ledger changes. Show it on request, or as a quick win after a level-up.

## Rules
- Keep it casual: hand-drawn style, few words per box, no perfect layout.
- The user's arrows are theirs. Never "fix" them silently. Discuss, and let them redraw.
- Drawings of concepts are fine in the public repo. Never draw org architecture, hostnames or anything from work systems into tracked files (use `local/drawings/` for that).
