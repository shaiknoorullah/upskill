---
name: debrief
description: Review a learner's whole chain of attempts on a challenge attempt by attempt (belief, engine behavior, gap), compare with the canonical solution, show better or idiomatic ways, and turn misconceptions into spaced review items. Use after a pass in pause, or when the user pastes a struggle they had elsewhere ("this one really challenged me, here's what I tried").
---

# debrief: turn struggle into understanding

Struggle without a debrief loses to direct instruction. Struggle *with* a structured debrief beats it (productive failure: Sinha & Kapur 2021; guided vs unguided discovery: Alfieri 2011). This skill is the consolidation step. Do it fully, every time; the user asked for that.

## Input
- `./up show <item>`: the item, its attempts (`cmd`, `why`, `result`, `prediction`, `confidence`), and its ledger entry.
- Or the user's pasted narrative: extract each attempt and their reasoning in their words.

## Output format
1. **One line of credit for the method**, specific: "You isolated the left edge first, then the right; that's the right decomposition." Credit self-found discoveries (lookarounds from StackOverflow, finding `-P` after an `-E` error).
2. **Attempt by attempt**, for each one:
   - **What you believed:** their mental model, in one line, in their terms.
   - **What actually happened:** the engine's real behavior, verified by running it. Run the attempt yourself against the data before claiming anything.
   - **The gap:** the precise concept, named (e.g. *zero-width vs consuming*, *`^` anchors only the start*, *ERE has no lookarounds*).
   - If the attempt "worked" but has a hidden flaw, show the input that breaks it (e.g. `[^-]` fails at end of line) and run it.
3. **The unifying idea**: one sentence that ties the gaps together (e.g. "`\b`, `^`, `$` and lookarounds match *positions*; `[^-]` matches a *character*").
4. **Canonical and better solutions**: 1–3 alternatives, each with *when to prefer it* (e.g. awk field compare for columnar data, PCRE lookaround for custom boundaries, `-F` for literal text). Verify each one with the track checker before showing it.
5. **When NOT to use it**: one sentence of judgment, the senior-level nuance.
6. **Explain-back**: ask for one sentence, in their words, on why the final answer works. Correct it if it's wrong.

## Persist
- For each distinct misconception, add a review item so it comes back as a fresh re-challenge. Run **forge** with the misconception text, or note it in the `--why` of the rating.
- Confident wrong predictions (confidence ≥4 and wrong): call them out explicitly ("you were sure; this is the one to remember") and rate the item `hard` at best.
- Keep claims honest: run commands, don't guess output.

## Tone
Specific, warm, unsentimental. No "great job". Praise the *strategy* by name. Keep each attempt row to 2–3 lines; the whole debrief should fit on one screen when possible.
