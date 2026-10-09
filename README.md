# platform-prep

Study headquarters for Claude Code. It carries everything from the claude.ai planning chat: your background, both interview results, the gap map, the three courses, the 31-day calendar, the lab layout and the tutor rules. Claude Code reads CLAUDE.md automatically whenever you start it in this folder.

## First run (Day 0, setup)
1. Unzip into your home folder so you have ~/platform-prep, then make it a private Git repo so your progress is backed up:
   cd ~/platform-prep && git init && git add . && git commit -m "Start"
2. Start Claude Code here: `cd ~/platform-prep && claude`
3. Type `/today 0`. Claude walks you through Day 0: the laptop server, Incus on the PC, the VMs and the tools.

## Every day after that
1. `./scripts/tutor.sh` opens tmux: the left pane is your shell inside lab-ubuntu, the right pane is Claude Code.
2. In the Claude pane: `/today`
3. Work in the left pane. Claude sees it through ./scripts/pane.sh.
4. Finish with `/wrap`, then tick the day on the calendar page.

## Commands
- `/today [day]`: load the day's plan and start the first unfinished block
- `/watch`: Claude looks at your terminal and tells you the one next step
- `/hint`: one hint, the next rung on the ladder
- `/check`: Claude verifies the block is really done, from evidence
- `/break [topic]`: Claude plants a hidden fault in lab-ubuntu for you to find
- `/quiz [topic] [n]`: rapid-fire questions with sure/guess tracking
- `/interview [screen|troubleshooting|deep-dive|design]`: a mock interview round
- `/checkpoint 1|2|3`: milestone exam
- `/wrap`: end of session: log, ledger, misses, next action

## Micro-sessions: `/pause` (5-minute fillers, home or work)
- `/pause` runs one hands-on session: it resumes where you left off, starts with a due re-challenge, then poses a new challenge. You predict, run it yourself and struggle, then get a full debrief of every attempt.
- `./up status` prints a one-liner such as `upskill · 1 due · 1d streak · 2/7 wk · ▶ regex/1`. Also `./up next`, `./up map`, `./up due`.
- Tracks are in `tracks/`: `regex` (28 checked exercises), `lfcs` (safe local micro-challenges), and `interview` (your 68 misses as spaced re-challenges).
- Progress is the append-only `state/events.jsonl`, merged by union, so home and work both push without conflicts. Spaced review uses FSRS (`tutor/fsrs.py`).
- Skills: `pause`, `debrief`, `forge` (drill sets), `draw` (Excalidraw, a live canvas via `integrations/excalidraw/`), `coach` (retro, roadmap).
- At work: `echo work > local/site`. That turns on companion mode: local data and labs only, never org infra, and work-derived data stays in the gitignored `local/`.
- The drift nudger (`drift/`) offers a session when Claude is busy and you've wandered off. Desktop snippets for the dots repo are in `integrations/dots/`.

## Voice
Type `/voice` once, then hold Space and talk. The PC needs a microphone (a headset or webcam mic works). Transcription doesn't count toward your usage limits.

## House rules
- Claude doesn't do your labs. It hints, checks and explains.
- A skill counts only once you've demonstrated it. progress/skills-ledger.md is the honest record, and your resume only claims what's in it.
- /break plants faults with base64-encoded commands so the transcript doesn't spoil them. Don't decode them.
