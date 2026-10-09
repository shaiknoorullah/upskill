# drift: the upskill drift detector (v1)

A small stdlib-only Python 3 daemon. It notices when Claude Code is busy
working for you and you have wandered off to a drift site (T1), or when
Claude has been idle for a while and you are off-terminal (T2), and offers a
5-minute learning session through a mako notification. Manual starts (T4)
come from `--start`, the waybar click or the tmux keybind.

## What it reads

- **ActivityWatch** at `http://localhost:5600`, **GET only**: the window,
  AFK and Zen web buckets, last 15 minutes, plus today's AFK events for the
  warm-up gate. Web events count only while the browser is focused and you
  are not AFK; runs with gaps of 5 s or less are merged.
- **Claude Code session state**, read-only: `~/.claude/sessions/*.json`
  (status per live pid, checked against `/proc`), the timestamps in
  `~/.claude/history.jsonl`, and top-level transcript mtimes under
  `~/.claude/projects/*/` as a fallback.
- `pactl list source-outputs short` (mic in use = meeting) and `makoctl mode`
  (do-not-disturb).

## What it never does

- Never POSTs or PUTs to ActivityWatch, never changes AW settings.
- Never writes window titles or URLs anywhere. They are reduced to
  `(domain, category)` in memory; the log stores only the category.
- Never writes to `~/.claude`, never injects into a work session.
- Never nudges outside the work window (weekdays 10:00 to 19:00), during the
  first 20 minutes of the day, while you are typing, in a meeting, in DND,
  while a Claude session is waiting on you, more than once per 45 minutes or
  more than 4 times a day.

## Files

| Path | What |
|---|---|
| `aw_probe.py` | GET-only AW reader |
| `claude_state.py` | session summary: `any_busy`, `busy_for_s`, `any_blocked_on_user`, `last_prompt_age_s` |
| `policy.py` | triggers, gates, thresholds (`DEFAULTS`), state transitions |
| `nudged.py` | loop, CLI, notify-send and tmux adapters, status file |
| `drift-rules.example.json` | generic domain and app rules |

Runtime files (all gitignored):

- `local/drift-rules.json`: your real rules; overrides the example.
- `local/drift-config.json`: optional threshold overrides, e.g.
  `{"drift_dwell_s": 120, "work_start": "09:30"}`, and `start_command`.
- `local/drift-state.json`: caps, cooldowns, snooze, back-off.
- `local/nudges.jsonl`: one line per decision change (time, trigger,
  decision, gate, category).
- `~/.cache/upskill/status` and `status.json`: written only while the daemon
  runs (not in `--dry-run`).

## Running it

```sh
python3 drift/nudged.py --once --dry-run   # evaluate once, print JSON, write nothing
python3 drift/nudged.py --once             # same, but update status/state/log files
python3 drift/nudged.py --once --deliver   # ...and actually send the notification
python3 drift/nudged.py --dry-run          # loop, one decision line per poll, no side effects
python3 drift/nudged.py --status           # one-line status
python3 drift/nudged.py --start --dry-run  # print the command that opens the upskill window
python3 drift/nudged.py                    # the daemon (what the systemd unit runs)
```

`--show-domain` adds the current web domain to the `--once` output (stdout
only). It is off by default.

Tests: `python3 -m unittest discover -s drift/tests -v` (no network, temp dirs).

Desktop wiring (systemd unit, mako rule, waybar, tmux) lives in
`integrations/dots/` and is applied through the dots repo, not from here.
