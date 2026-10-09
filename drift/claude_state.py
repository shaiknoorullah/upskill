"""Read-only view of Claude Code session state across all sessions.

Sources (never written to):
  ~/.claude/sessions/<pid>.json   undocumented registry; parsed defensively
  ~/.claude/history.jsonl         one line per typed prompt (we read only timestamps)
  ~/.claude/projects/*/<sid>.jsonl  top-level transcript mtimes (fallback only)

Prompt text, cwd, names and transcript contents are never read into the output.
"""

import glob
import json
import os
import sys
import time

CLAUDE_DIR = os.path.expanduser("~/.claude")
BUSY_STATUSES = {"busy", "shell"}
IDLE_STATUSES = {"idle"}
BLOCKED_STATUSES = {"waiting"}
KNOWN_STATUSES = BUSY_STATUSES | IDLE_STATUSES | BLOCKED_STATUSES
TRANSCRIPT_ACTIVE_S = 20
HISTORY_TAIL_BYTES = 64 * 1024

_warned = set()


def _warn_once(key, msg):
    if key not in _warned:
        _warned.add(key)
        print("claude_state: " + msg, file=sys.stderr)


def _ms_to_s(v):
    """Registry timestamps are epoch milliseconds; accept seconds too."""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    return v / 1000.0 if v > 1e11 else v


def pid_alive(pid, proc_start=None, proc_root="/proc"):
    """True if /proc/<pid> exists and (when given) its start time matches."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    stat_path = os.path.join(proc_root, str(pid), "stat")
    try:
        with open(stat_path) as f:
            stat = f.read()
    except OSError:
        return False
    if proc_start in (None, ""):
        return True
    # field 22 (starttime) comes after the parenthesised comm, which may hold spaces
    rest = stat[stat.rfind(")") + 2:].split()
    return len(rest) > 19 and rest[19] == str(proc_start)


def last_prompt_ts(history_path):
    """Max 'timestamp' (epoch s) in the tail of history.jsonl, or None."""
    try:
        size = os.path.getsize(history_path)
        with open(history_path, "rb") as f:
            f.seek(max(0, size - HISTORY_TAIL_BYTES))
            tail = f.read().decode("utf-8", "replace")
    except OSError:
        return None
    best = None
    for line in tail.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue  # first line may be cut by the seek
        try:
            ts = _ms_to_s(json.loads(line).get("timestamp"))
        except (ValueError, AttributeError):
            continue
        if ts and (best is None or ts > best):
            best = ts
    return best


def transcript_mtime(projects_dir, session_id):
    """mtime of the top-level transcript for a session (no subagents/**)."""
    if not session_id:
        return None
    best = None
    for p in glob.glob(os.path.join(glob.escape(projects_dir), "*", glob.escape(session_id) + ".jsonl")):
        try:
            m = os.path.getmtime(p)
        except OSError:
            continue
        best = m if best is None or m > best else best
    return best


def read_sessions(sessions_dir, proc_root="/proc"):
    """Parse the registry; return a list of alive session dicts (sanitized)."""
    out = []
    for path in glob.glob(os.path.join(glob.escape(sessions_dir), "*.json")):
        try:
            with open(path) as f:
                d = json.load(f)
        except (OSError, ValueError):
            _warn_once("parse:" + os.path.basename(path), "unparseable session file skipped")
            continue
        if not isinstance(d, dict):
            continue
        pid = d.get("pid")
        if pid is None:
            base = os.path.basename(path)[:-5]
            pid = base if base.isdigit() else None
        if not pid_alive(pid, d.get("procStart"), proc_root):
            continue
        status = d.get("status")
        if status not in KNOWN_STATUSES:
            _warn_once("status:%s" % status, "unknown session status %r; using transcript mtime" % (status,))
        out.append({
            "pid": int(pid),
            "session_id": d.get("sessionId"),
            "kind": d.get("kind"),
            "status": status,
            "status_since": _ms_to_s(d.get("statusUpdatedAt")) or _ms_to_s(d.get("updatedAt")),
            "waiting_for": bool(d.get("waitingFor")),
        })
    return out


class ClaudeState:
    """Summarise all sessions. Keeps per-session busy_since across polls so a
    busy<->shell flip inside one turn does not reset the busy clock."""

    def __init__(self, claude_dir=CLAUDE_DIR, proc_root="/proc", clock=time.time):
        self.claude_dir = claude_dir
        self.proc_root = proc_root
        self.clock = clock
        self._busy_since = {}

    def summary(self):
        now = self.clock()
        sessions = read_sessions(os.path.join(self.claude_dir, "sessions"), self.proc_root)
        projects = os.path.join(self.claude_dir, "projects")
        busy_for = []
        blocked = False
        last_change = None
        seen = set()
        for s in sessions:
            key = s["session_id"] or s["pid"]
            seen.add(key)
            status = s["status"]
            since = s["status_since"]
            if status not in KNOWN_STATUSES:
                m = transcript_mtime(projects, s["session_id"])
                status = "busy" if m and now - m <= TRANSCRIPT_ACTIVE_S else "idle"
                since = since or m
            if status in BUSY_STATUSES:
                start = self._busy_since.setdefault(key, since or now)
                busy_for.append(max(0.0, now - start))
            else:
                self._busy_since.pop(key, None)
                if status in BLOCKED_STATUSES:
                    # best effort (v1): 'waiting' is also shown while subagents run
                    blocked = True
            if since:
                last_change = since if last_change is None else max(last_change, since)
        for k in list(self._busy_since):
            if k not in seen:
                del self._busy_since[k]

        lp = last_prompt_ts(os.path.join(self.claude_dir, "history.jsonl"))
        last_prompt_age = round(now - lp, 1) if lp else None
        any_busy = bool(busy_for)
        # idle_for_s: time since the most recent status change or prompt, when nothing is busy
        ref = max([t for t in (last_change, lp) if t] or [0]) or None
        idle_for = None if any_busy else (round(now - ref, 1) if ref else None)
        return {
            "sessions_alive": len(sessions),
            "any_busy": any_busy,
            "busy_for_s": round(max(busy_for), 1) if busy_for else 0.0,
            "any_blocked_on_user": blocked,
            "last_prompt_age_s": last_prompt_age,
            "idle_for_s": idle_for,
        }


if __name__ == "__main__":
    print(json.dumps(ClaudeState().summary(), indent=2))
