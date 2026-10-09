"""Shared test fixtures. No network, no real ~/.claude, no real AW."""

import datetime as dt
import os
import sys

DRIFT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DRIFT_DIR not in sys.path:
    sys.path.insert(0, DRIFT_DIR)

# Wednesday 2026-10-07 14:00 local time: inside the default work window.
WED_14 = dt.datetime(2026, 10, 7, 14, 0, 0).timestamp()
SAT_14 = dt.datetime(2026, 10, 10, 14, 0, 0).timestamp()
WED_20 = dt.datetime(2026, 10, 7, 20, 0, 0).timestamp()

RULES = {
    "domains": {"claude.ai": "work", "github.com": "work", "youtube.com": "drift"},
    "patterns": {"work": ["^docs\\."], "drift": ["news"]},
    "apps": {"kitty": "terminal", "zen": "browser", "code": "work"},
}


def aw_snap(**kw):
    """A healthy AW snapshot: user in kitty, warmed up, not afk."""
    s = {"ok": True, "afk": False, "focused_app": "kitty", "focused_class": "terminal",
         "focused_for_s": 600.0, "terminal_last_s": 0.0, "afk_changed_s": 3600.0,
         "web_domain": None, "web_category": None, "web_dwell_s": 0.0,
         "first_active_today": WED_14 - 4 * 3600, "error": None}
    s.update(kw)
    return s


def drifting(**kw):
    """User focused on the browser on a drift domain for 2 minutes."""
    base = dict(focused_app="zen", focused_class="browser", focused_for_s=120.0,
                terminal_last_s=125.0, web_domain="youtube.com",
                web_category="drift", web_dwell_s=120.0)
    base.update(kw)
    return aw_snap(**base)


def claude_snap(**kw):
    s = {"sessions_alive": 1, "any_busy": True, "busy_for_s": 120.0,
         "any_blocked_on_user": False, "last_prompt_age_s": 200.0, "idle_for_s": None}
    s.update(kw)
    return s


def idle_claude(**kw):
    base = dict(any_busy=False, busy_for_s=0.0, idle_for_s=600.0, last_prompt_age_s=600.0)
    base.update(kw)
    return claude_snap(**base)


def iso(epoch):
    return dt.datetime.fromtimestamp(epoch, dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%S.%f") + "123Z"  # nanosecond-style suffix like aw-server-rust
