"""FSRS-4.5 scheduler, stdlib only.

Ratings: 1=again (failed), 2=hard (passed with hints / many attempts),
3=good (passed cleanly), 4=easy (passed instantly, confident).
State per card: stability S (days until recall drops to 90%), difficulty D (1..10).
"""
import math
from datetime import datetime, timedelta

W = [0.4872, 1.4003, 3.7145, 13.8206, 5.1618, 1.2298, 0.8975, 0.031,
     1.6474, 0.1367, 1.0461, 2.1072, 0.0793, 0.3246, 1.587, 0.2272, 2.8755]
DECAY = -0.5
FACTOR = 19 / 81          # makes R(S, S) == 0.9
TARGET_RETENTION = 0.9
MAX_INTERVAL_DAYS = 365

RATINGS = {"again": 1, "hard": 2, "good": 3, "easy": 4}


def _clamp_d(d):
    return min(max(d, 1.0), 10.0)


def retrievability(elapsed_days, stability):
    return (1 + FACTOR * elapsed_days / stability) ** DECAY


def interval_days(stability, retention=TARGET_RETENTION):
    days = stability / FACTOR * (retention ** (1 / DECAY) - 1)
    return min(max(1, round(days)), MAX_INTERVAL_DAYS)


def _init_difficulty(g):
    return _clamp_d(W[4] - (g - 3) * W[5])


def review(card, rating, now):
    """Return an updated copy of card after a review at datetime `now`.

    card: dict with optional keys s, d, last (ISO), due (ISO), reps, lapses.
    rating: 1..4 or one of RATINGS keys.
    """
    g = RATINGS.get(rating, rating) if isinstance(rating, str) else int(rating)
    if g not in (1, 2, 3, 4):
        raise ValueError(f"bad rating {rating!r}")
    c = dict(card)
    reps = c.get("reps", 0)
    if reps == 0 or "s" not in c:
        s = W[g - 1]
        d = _init_difficulty(g)
    else:
        s, d = float(c["s"]), float(c["d"])
        last = datetime.fromisoformat(c["last"])
        elapsed = max((now - last).total_seconds() / 86400, 0)
        r = retrievability(elapsed, s)
        d_new = d - W[6] * (g - 3)
        d = _clamp_d(W[7] * _init_difficulty(3) + (1 - W[7]) * d_new)
        if g == 1:
            s = W[11] * d ** -W[12] * ((s + 1) ** W[13] - 1) * math.exp(W[14] * (1 - r))
            c["lapses"] = c.get("lapses", 0) + 1
        else:
            hard = W[15] if g == 2 else 1.0
            easy = W[16] if g == 4 else 1.0
            s = s * (1 + math.exp(W[8]) * (11 - d) * s ** -W[9]
                     * (math.exp(W[10] * (1 - r)) - 1) * hard * easy)
    s = max(s, 0.1)
    # a failed card comes back the same day-ish (10 min) so it can be re-challenged with new data
    due = now + (timedelta(minutes=10) if g == 1 else timedelta(days=interval_days(s)))
    c.update(s=round(s, 4), d=round(d, 4), reps=reps + 1,
             last=now.isoformat(timespec="seconds"), due=due.isoformat(timespec="seconds"))
    return c
