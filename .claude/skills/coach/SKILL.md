---
name: coach
description: The meta layer of the upskill tutor: weekly retro, certification roadmap and readiness, mastery overview, tuning session length, nudges and difficulty from logged data, and onboarding new preferences. Use when the user asks "how am I doing", "what's next for LFCS/CKA", "show my progress or map", "plan", "retro", or wants to change how the tutor works.
---

# coach: steer the learning system

## Know the learner
- Preferences and history live in Claude's memory (learning-style, work-learning-boundaries, platform-prep-home-project) and in `docs/profile.md`. In short: ADHD; discovery and trial and error with a live instructor; ~5-min pauses at work; the full debrief always; a tiny experiment when stuck; motivated by real-work flavor, streaks, novelty and a visible mastery map; draws to understand; hyperfocus means keep going.
- What made them quit before: passive content, streak guilt, boring repetition, friction to start. Design every suggestion against these four.
- **Home is primary** (the main lab; `/today`, the calendar, `/break`, `/interview`). **Work is a filler companion**: it continues exactly where home learning is, with local labs only and no org data or infra.

## Roadmap (decided 2026-10-09)
LFCS first, then CKA → CNPE → CKS. Cheap checkpoints along the way: CGOA/CAPA (multiple choice, a subset of CNPE GitOps), the Tekton SC106 SkillCred. Optional: Terraform 004, RHCSA → RHCE (the only real Ansible credential), KCNA. SRE: Google SRE books, no exam. The regex track feeds LFCS Essential Commands. The interview track (68 imported misses) runs alongside, because a new role matters as much as the certs.
Recheck exam versions before booking (LF moves exams to a new k8s minor 4–8 weeks after release).

## Weekly retro (on request, or the first session of a week)
From `state/events.jsonl` (through `./up`) report:
- days practised, sessions and items. Never frame missed days as failure.
- concepts that leveled up (ledger), and what's due
- patterns in attempt `why` fields (e.g. "filters too loose", "output format slips", "fitting to the visible output")
- the ones they were sure about but got wrong
- **one** change for next week (difficulty, track mix, session length)

Keep it under 15 lines. Offer a published progress page only if they ask.

## Readiness per exam
Map items and concepts to exam domains (each track's `items.json` `cert_domains`). Give a rough readiness figure: the share of domain concepts at `demonstrated`+, with the biggest gaps first. Be honest. Never inflate; evidence only.

## Tuning
- Change preferences only when the user says so, then update Claude memory (learning-style) and this file's summary.
- Drift detector tuning: suggest threshold changes based on the accept/decline counts in `local/nudges.jsonl`, and ask before changing `local/drift-rules.json` or its config.
