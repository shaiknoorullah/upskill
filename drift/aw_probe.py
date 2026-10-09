"""Read-only ActivityWatch probe.

GET requests only; this module never POSTs, PUTs or DELETEs. Raw window titles
and URLs never leave this module: every web event is reduced to
(domain, category) in memory and the title field is never read.
"""

import datetime as _dt
import json
import os
import re
import urllib.parse
import urllib.request

AW_URL = "http://localhost:5600"
HOST = "devsupreme"
WINDOW_BUCKET = "aw-watcher-window_" + HOST
AFK_BUCKET = "aw-watcher-afk_" + HOST
WEB_BUCKET = "aw-watcher-web-firefox_" + HOST

MERGE_GAP_S = 5.0        # python-side "flood": merge runs with gaps <= 5 s
LOOKBACK_S = 15 * 60     # how far back to read events
STALE_BUCKET_S = 300     # bucket whose metadata.end is older is treated as dead
WINDOW_TAIL_S = 30       # latest window event extends to now if it ended within this
AFK_TAIL_S = 300         # latest afk event extends to now if it ended within this
WEB_CURRENT_S = 60       # newest web run must have ended within this to count

DRIFT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(DRIFT_DIR)
EXAMPLE_RULES = os.path.join(DRIFT_DIR, "drift-rules.example.json")
LOCAL_RULES = os.path.join(REPO_DIR, "local", "drift-rules.json")


# ---------------------------------------------------------------- time utils

def parse_ts(s):
    """Parse AW ISO timestamps (nanosecond precision, trailing Z) to epoch s."""
    if not s:
        return None
    s = s.strip().replace("Z", "+00:00")
    m = re.match(r"^(.*T\d\d:\d\d:\d\d)(\.\d+)?(.*)$", s)
    if not m:
        return None
    base, frac, tz = m.groups()
    frac = (frac or ".0")[:7]  # at most microseconds
    try:
        dt = _dt.datetime.fromisoformat(base + frac + (tz or "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_dt.timezone.utc)
    return dt.timestamp()


def iso(epoch):
    return _dt.datetime.fromtimestamp(epoch, _dt.timezone.utc).isoformat()


# ---------------------------------------------------------------- rules

def load_rules(path=None):
    """Load domain/app rules. local/drift-rules.json wins over the example."""
    for p in ([path] if path else [LOCAL_RULES, EXAMPLE_RULES]):
        if p and os.path.exists(p):
            with open(p) as f:
                return json.load(f)
    return {"domains": {}, "patterns": {}, "apps": {}}


def domain_of(url):
    """Hostname of a URL, lowercased, without a leading www. The URL is dropped."""
    try:
        host = urllib.parse.urlsplit(url or "").hostname or ""
    except ValueError:
        host = ""
    host = host.lower()
    if host.startswith("www."):
        host = host[4:]
    return host or None


def categorize_domain(domain, rules):
    """Return 'work', 'drift' or 'neutral' for a bare domain."""
    if not domain:
        return "neutral"
    domains = rules.get("domains", {})
    # exact or suffix match, longest rule first
    for d in sorted(domains, key=len, reverse=True):
        d2 = d.lower()
        if domain == d2 or domain.endswith("." + d2):
            return domains[d]
    for cat in ("work", "drift", "neutral"):
        for pat in rules.get("patterns", {}).get(cat, []):
            try:
                if re.search(pat, domain):
                    return cat
            except re.error:
                continue
    return "neutral"


def app_class(app, rules):
    """Return 'terminal', 'browser', 'work', 'drift' or 'neutral' for an app name."""
    if not app:
        return "neutral"
    apps = {k.lower(): v for k, v in rules.get("apps", {}).items()}
    return apps.get(app.lower(), "neutral")


# ---------------------------------------------------------------- intervals

def to_intervals(events, key):
    """Events -> sorted list of (start, end, value) using key(event)."""
    out = []
    for e in events:
        st = parse_ts(e.get("timestamp"))
        if st is None:
            continue
        dur = float(e.get("duration") or 0.0)
        out.append((st, st + max(dur, 0.0), key(e)))
    out.sort(key=lambda x: x[0])
    return out


def merge_runs(intervals, gap=MERGE_GAP_S):
    """Merge consecutive intervals with the same value and gaps <= gap."""
    runs = []
    for st, en, v in intervals:
        if runs and runs[-1][2] == v and st - runs[-1][1] <= gap:
            if en > runs[-1][1]:
                runs[-1][1] = en
        else:
            runs.append([st, en, v])
    return [tuple(r) for r in runs]


def overlap(a_st, a_en, intervals):
    """Seconds of [a_st, a_en] covered by the (start, end) intervals."""
    total = 0.0
    for st, en in intervals:
        lo, hi = max(a_st, st), min(a_en, en)
        if hi > lo:
            total += hi - lo
    return total


# ---------------------------------------------------------------- HTTP

def http_get_json(url, timeout=3.0):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


class AWProbe:
    """GET-only reader. `fetch` is injectable for tests: fetch(url) -> json."""

    def __init__(self, base=AW_URL, fetch=None, rules=None, clock=None,
                 window_bucket=WINDOW_BUCKET, afk_bucket=AFK_BUCKET,
                 web_bucket=WEB_BUCKET):
        self.base = base.rstrip("/")
        self.fetch = fetch or http_get_json
        self.rules = rules if rules is not None else load_rules()
        self.clock = clock or (lambda: _dt.datetime.now().timestamp())
        self.window_bucket = window_bucket
        self.afk_bucket = afk_bucket
        self.web_bucket = web_bucket
        self._first_active = {}  # local date -> epoch

    def _events(self, bucket, start=None, limit=None):
        q = {}
        if start is not None:
            q["start"] = iso(start)
        if limit is not None:
            q["limit"] = str(limit)
        url = "%s/api/0/buckets/%s/events" % (self.base, urllib.parse.quote(bucket))
        if q:
            url += "?" + urllib.parse.urlencode(q)
        data = self.fetch(url)
        return data if isinstance(data, list) else []

    def _liveness(self, now):
        buckets = self.fetch(self.base + "/api/0/buckets/")
        alive = {}
        for name in (self.window_bucket, self.afk_bucket, self.web_bucket):
            meta = (buckets.get(name) or {}).get("metadata") or {}
            end = parse_ts(meta.get("end")) or parse_ts((buckets.get(name) or {}).get("last_updated"))
            alive[name] = end is not None and now - end <= STALE_BUCKET_S
        return alive

    def first_active_today(self, now):
        """Epoch of the first not-afk event of the local day (cached per day)."""
        day = _dt.datetime.fromtimestamp(now).date()
        if day in self._first_active:
            return self._first_active[day]
        midnight = _dt.datetime.combine(day, _dt.time()).timestamp()
        evs = to_intervals(self._events(self.afk_bucket, start=midnight),
                           lambda e: (e.get("data") or {}).get("status"))
        firsts = [max(st, midnight) for st, en, s in evs if s == "not-afk" and en > midnight]
        if firsts:
            self._first_active[day] = min(firsts)
            return self._first_active[day]
        return None

    def probe(self):
        """Return the snapshot dict. On any failure returns {'ok': False, ...}."""
        now = self.clock()
        snap = {"ok": False, "afk": None, "focused_app": None, "focused_class": None,
                "focused_for_s": 0.0, "terminal_last_s": None, "afk_changed_s": None,
                "web_domain": None, "web_category": None, "web_dwell_s": 0.0,
                "first_active_today": None, "error": None}
        try:
            alive = self._liveness(now)
            if not (alive.get(self.window_bucket) and alive.get(self.afk_bucket)):
                snap["error"] = "stale_bucket"
                return snap
            start = now - LOOKBACK_S

            # AFK runs; the newest run extends to now if its heartbeat is recent.
            afk_runs = merge_runs(to_intervals(
                self._events(self.afk_bucket, start=start),
                lambda e: (e.get("data") or {}).get("status")))
            if afk_runs and now - afk_runs[-1][1] <= AFK_TAIL_S:
                st, en, s = afk_runs[-1]
                afk_runs[-1] = (st, now, s)
            cur_afk = afk_runs[-1][2] if afk_runs else None
            snap["afk"] = cur_afk != "not-afk"
            if afk_runs:
                snap["afk_changed_s"] = round(now - afk_runs[-1][0], 1)
            not_afk = [(st, en) for st, en, s in afk_runs if s == "not-afk"]

            # Window runs: app only, the title is never read.
            win_runs = merge_runs(to_intervals(
                self._events(self.window_bucket, start=start),
                lambda e: ((e.get("data") or {}).get("app") or "").lower() or None))
            if win_runs and now - win_runs[-1][1] <= WINDOW_TAIL_S:
                st, en, a = win_runs[-1]
                win_runs[-1] = (st, now, a)
                snap["focused_app"] = a
                snap["focused_class"] = app_class(a, self.rules)
                snap["focused_for_s"] = round(now - st, 1)
            term = [en for st, en, a in win_runs if app_class(a, self.rules) == "terminal"]
            if term:
                snap["terminal_last_s"] = round(max(0.0, now - max(term)), 1)
            browser = [(st, en) for st, en, a in win_runs
                       if app_class(a, self.rules) == "browser"]

            # Web runs: reduce to domain immediately, drop URL and title.
            if alive.get(self.web_bucket):
                web_runs = merge_runs(to_intervals(
                    self._events(self.web_bucket, start=start),
                    lambda e: domain_of((e.get("data") or {}).get("url"))))
                if web_runs and now - web_runs[-1][1] <= WEB_CURRENT_S:
                    st, en, dom = web_runs[-1]
                    en = max(en, now) if now - en <= MERGE_GAP_S else en
                    focused_browser = [(max(a, b_st), min(b, b_en))
                                       for a, b in browser for b_st, b_en in not_afk
                                       if min(b, b_en) > max(a, b_st)]
                    dwell = overlap(st, en, focused_browser)
                    snap["web_domain"] = dom
                    snap["web_category"] = categorize_domain(dom, self.rules)
                    snap["web_dwell_s"] = round(dwell, 1)

            snap["first_active_today"] = self.first_active_today(now)
            snap["ok"] = True
        except Exception as exc:  # network down, bad JSON, ...
            snap["error"] = type(exc).__name__
        return snap


if __name__ == "__main__":
    s = AWProbe().probe()
    s.pop("web_domain", None)  # keep stdout privacy-safe by default
    print(json.dumps(s, indent=2))
