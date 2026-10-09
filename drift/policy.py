"""Drift policy: triggers and gates as pure functions.

Inputs are plain dicts (the AW snapshot from aw_probe, the Claude summary from
claude_state), a persisted policy state dict, an `env` dict of lazy probes
(meeting / dnd) and `now` as epoch seconds. Nothing here does I/O except the
small load_state/save_state helpers at the bottom.

Triggers (v1):
  T1 busy-drift   Claude busy >= busy_min_s and the user is on a drift site for
                  drift_dwell_s (or a neutral site / non-terminal app for
                  neutral_dwell_s).
  T2 idle-drift   nothing busy, no prompt and no session change for
                  idle_no_prompt_s, user not-afk and off-terminal, not on work.
  T4 manual       handled by nudged.py --start; never gated, never capped.
"""

import datetime as _dt
import json
import os

DEFAULTS = {
    "busy_min_s": 45,
    "drift_dwell_s": 90,
    "neutral_dwell_s": 180,
    "idle_no_prompt_s": 300,
    "typing_terminal_s": 20,
    "typing_prompt_s": 60,
    "afk_flip_s": 10,
    "cooldown_min": 45,
    "daily_cap": 4,
    "nudge_ttl_s": 25,
    "drill_cooldown_min": 60,
    "snooze_min": 30,
    "snooze_escalated_min": 90,
    "backoff_max_level": 2,      # 45 -> 90 -> 180 min
    "warmup_min": 20,
    "work_days": [0, 1, 2, 3, 4],  # Monday = 0
    "work_start": "10:00",
    "work_end": "19:00",
}


def config(overrides=None):
    cfg = dict(DEFAULTS)
    if overrides:
        cfg.update({k: v for k, v in overrides.items() if not k.startswith("_")})
    return cfg


# ------------------------------------------------------------------ state

def new_state():
    return {
        "day": None,
        "nudges_today": 0,
        "last_nudge_ts": None,
        "last_drill_ts": None,
        "snooze_until": None,
        "snooze_streak": 0,
        "backoff_level": 0,
        "done_date": None,
        "phase": "IDLE",
    }


def _day(now):
    return _dt.datetime.fromtimestamp(now).date().isoformat()


def roll_day(state, now):
    """Reset per-day counters when the local date changes. Returns state."""
    d = _day(now)
    if state.get("day") != d:
        state["day"] = d
        state["nudges_today"] = 0
    return state


def record_nudge(state, now):
    roll_day(state, now)
    state["nudges_today"] = state.get("nudges_today", 0) + 1
    state["last_nudge_ts"] = now
    state["phase"] = "NUDGED"
    return state


def apply_action(state, action, now, cfg=None):
    """Update state after the user (or the TTL) answered a nudge.

    action: start | snooze | done | expired | plain (no action buttons available)
    """
    cfg = cfg or DEFAULTS
    roll_day(state, now)
    if action == "start":
        state["last_drill_ts"] = now
        state["backoff_level"] = 0
        state["snooze_streak"] = 0
        state["snooze_until"] = None
        state["phase"] = "SESSION"
    elif action == "snooze":
        state["snooze_streak"] = state.get("snooze_streak", 0) + 1
        mins = cfg["snooze_min"] if state["snooze_streak"] < 2 else cfg["snooze_escalated_min"]
        state["snooze_until"] = now + mins * 60
        state["phase"] = "SNOOZED"
    elif action == "done":
        state["done_date"] = _day(now)
        state["phase"] = "OFF_TODAY"
    elif action == "expired":
        state["backoff_level"] = min(state.get("backoff_level", 0) + 1, cfg["backoff_max_level"])
        state["phase"] = "BACKOFF"
    elif action == "plain":
        state["phase"] = "NUDGED"
    else:
        raise ValueError("unknown action %r" % (action,))
    return state


# ------------------------------------------------------------------ helpers

def _hm(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def in_work_window(now, cfg):
    t = _dt.datetime.fromtimestamp(now)
    if t.weekday() not in cfg["work_days"]:
        return False
    mins = t.hour * 60 + t.minute
    return _hm(cfg["work_start"]) <= mins < _hm(cfg["work_end"])


def focus_category(aw):
    """What the user is looking at: terminal | work | drift | neutral."""
    cls = aw.get("focused_class") or "neutral"
    if cls == "browser":
        return aw.get("web_category") or "neutral"
    return cls


def _num(v, default=0.0):
    return default if v is None else v


# ------------------------------------------------------------------ triggers

def detect_trigger(aw, claude, cfg):
    """Return (trigger, why) where trigger is 'T1', 'T2' or None."""
    if not aw.get("ok"):
        return None, "aw_unavailable"
    if aw.get("afk"):
        return None, "afk"
    cls = aw.get("focused_class") or "neutral"
    cat = focus_category(aw)
    dwell = _num(aw.get("web_dwell_s"))
    focused_for = _num(aw.get("focused_for_s"))

    if claude.get("any_busy"):
        if _num(claude.get("busy_for_s")) < cfg["busy_min_s"]:
            return None, "busy_too_short"
        if cls == "browser":
            if cat == "drift" and dwell >= cfg["drift_dwell_s"]:
                return "T1", "drift_site"
            if cat == "neutral" and dwell >= cfg["neutral_dwell_s"]:
                return "T1", "neutral_site"
        elif cls == "drift" and focused_for >= cfg["drift_dwell_s"]:
            return "T1", "drift_app"
        elif cls == "neutral" and focused_for >= cfg["neutral_dwell_s"]:
            return "T1", "neutral_app"
        return None, "not_drifting"

    idle = claude.get("idle_for_s")
    lp = claude.get("last_prompt_age_s")
    if idle is not None and idle < cfg["idle_no_prompt_s"]:
        return None, "idle_too_short"
    if lp is not None and lp < cfg["idle_no_prompt_s"]:
        return None, "prompt_too_recent"
    if cat in ("terminal", "work"):
        return None, "on_terminal_or_work"
    return "T2", "idle_" + cat


# ------------------------------------------------------------------ gates

def check_gates(aw, claude, state, env, now, cfg):
    """Return (outcome, gate). outcome: nudge | suppress | hold | snooze | off | backoff.

    env: {"meeting": callable -> bool, "dnd": callable -> bool}; the callables
    run only if every cheaper gate passed.
    """
    roll_day(state, now)
    if state.get("done_date") == _day(now):
        return "off", "done_today"
    if not in_work_window(now, cfg):
        return "suppress", "work_window"
    if state.get("snooze_until") and now < state["snooze_until"]:
        return "snooze", "snoozed"
    first = aw.get("first_active_today")
    if first is None or now - first < cfg["warmup_min"] * 60:
        return "suppress", "warmup"
    if claude.get("any_blocked_on_user"):
        return "suppress", "blocked_on_user"
    if state.get("nudges_today", 0) >= cfg["daily_cap"]:
        return "suppress", "daily_cap"
    last = state.get("last_nudge_ts")
    level = state.get("backoff_level", 0)
    if last is not None and now - last < cfg["cooldown_min"] * 60 * (2 ** level):
        return ("backoff", "backoff") if level > 0 else ("suppress", "cooldown")
    drill = state.get("last_drill_ts")
    if drill is not None and now - drill < cfg["drill_cooldown_min"] * 60:
        return "suppress", "drill_cooldown"
    term = aw.get("terminal_last_s")
    lp = claude.get("last_prompt_age_s")
    flip = aw.get("afk_changed_s")
    if (term is not None and term <= cfg["typing_terminal_s"]) or \
       (lp is not None and lp <= cfg["typing_prompt_s"]) or \
       (flip is not None and flip <= cfg["afk_flip_s"]):
        return "hold", "typing"
    if _call(env.get("meeting")):
        return "suppress", "meeting"
    if _call(env.get("dnd")):
        return "suppress", "dnd"
    return "nudge", "ok"


def _call(probe):
    if probe is None:
        return False
    try:
        return bool(probe() if callable(probe) else probe)
    except Exception:
        return False


def evaluate(aw, claude, state, env, now, cfg=None):
    """One full decision. Pure apart from roll_day() on `state`."""
    cfg = cfg or DEFAULTS
    trigger, why = detect_trigger(aw, claude, cfg)
    out = {
        "ts": round(now, 1),
        "trigger": trigger,
        "why": why,
        "category": focus_category(aw) if aw.get("ok") else None,
        "decision": "none",
        "gate": None,
    }
    if trigger is None:
        if why == "aw_unavailable":
            out["decision"] = "suppress"
            out["gate"] = "aw_unavailable"
        return out
    out["decision"], out["gate"] = check_gates(aw, claude, state, env, now, cfg)
    return out


# ------------------------------------------------------------------ status

def status_line(decision, claude, state, now):
    """(text, css_class) for waybar / tmux."""
    if decision.get("gate") == "aw_unavailable":
        return "upskill ?", "unknown"
    if state.get("done_date") == _day(now):
        return "upskill done", "done"
    su = state.get("snooze_until")
    if su and now < su:
        return "upskill zz %dm" % max(1, int((su - now) // 60)), "snoozed"
    if decision.get("trigger") and decision.get("decision") != "none":
        return "upskill ready", "ready"
    if claude.get("any_busy"):
        return "upskill . claude %dm" % int(_num(claude.get("busy_for_s")) // 60), "busy"
    return "upskill", "idle"


# ------------------------------------------------------------------ persistence

def load_state(path):
    st = new_state()
    try:
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, dict):
            st.update(data)
    except (OSError, ValueError):
        pass
    return st


def save_state(path, state):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=1, sort_keys=True)
    os.replace(tmp, path)
