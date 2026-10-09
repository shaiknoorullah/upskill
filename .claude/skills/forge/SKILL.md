---
name: forge
description: Generate a reinforcement drill set for one concept (harden, integrate with earlier concepts, when or when-not to use it), with realistic trap-laden data and sealed answers wired into the track checker. Use after a concept is learned or a misconception shows up, or when the user asks for "more exercises like this", "drills", or "harden this".
---

# forge: build the drill ladder for a concept

The user asked for drills that (1) **harden** the concept, (2) **integrate** it with earlier concepts, and (3) teach **where and when** to use it, and when not to. DRILLS-04 (`tracks/regex/DRILLS-04-word-boundaries.md`) is the reference example of tone, structure and trap design. Read it before writing a new set.

## Inputs
- The concept and its misconceptions: `./up show <item>` attempts (`why` fields), or the debrief notes.
- Earlier concepts the user has seen: `./up map`. Integrate only concepts they have actually touched.
- The track's certification domain (e.g. LFCS Essential Commands) for realism.

## The ladder (5–8 drills)
- **A. Harden (2–3):** the same concept with one new edge case each. Design every trap from a *real* misconception. Example: `_` is a word char (4a); `-` breaks `-w` on hostnames (4b); `.` matches anything, so IPs need `-F` (4c).
- **B. Integrate (2–3):** the concept plus 1–2 earlier ones (position anchoring, counting pipelines, `-i`, `-v`).
- **C. When / when not (1–2):** a realistic scenario where the obvious tool silently fails (e.g. `-w -- --force` matches `--force-with-lease`). End with 3–5 **judgment questions** ("pick `-w`, `\b`, `-F`, anchors or awk field compare, and say why"). These are graded by Claude, with no checker.
- Optional **boss**: one scenario that combines 3+ concepts, unlocked when 2+ related concepts are rated `good`.

## Data rules
- Realistic DevOps data: logs, `kubectl` output, configs, scripts, SQL. Every file gets **deliberate traps** that catch the naive answer.
- **Public repo:** synthetic data only in tracked files. No org hostnames, IPs, cluster names or employer names. If you derive data from the user's real work output (allowed only on the work machine), put it under `local/drills/` (gitignored) and keep its items out of the tracked `items.json`. Put them in `local/items.json` instead, if that is supported later.
- Data files go in `tracks/<track>/data/drills/`.

## Sealing answers (never reveal them)
1. Write a reference solution for each checked drill. Verify it yourself by running it.
2. Seal it: `tracks/regex/check.sh --seal <id> '<reference command>' [ordered]`. This stores only a hash and a line count. Never print the reference output or command in chat.
3. **Prove the traps work:** run 1–2 naive commands through `./check.sh <id> '<naive>'`. They must FAIL. If a naive answer passes, redesign the data.
4. Append the items to `tracks/<track>/items.json` (`id`, `concept`, `kind: "drill"`, `title`, `prompt: "<file>#<id>"`, `check: {"type": "regex", "n": "<id>"}`, `prereqs`, `minutes: 5`). Run `./up list --track <track>` to confirm.
5. Write the drill sheet `tracks/<track>/DRILLS-<NN>-<concept>.md`: the rule behind it, then parts A/B/C, the judgment questions, and a cheat sheet the user will have *earned* by finishing. Each drill states its exact output format in its last sentence (format slips were a recurring miss).

## Hand-off
Tell the user in 3 lines: what the set targets (naming their misconception), how many drills, and the first command to run. Then hand back to **pause**.
