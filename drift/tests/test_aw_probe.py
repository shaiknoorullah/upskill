import json
import unittest
import urllib.parse
from unittest import mock

from helpers import WED_14, RULES, iso

import aw_probe

NOW = WED_14
TITLE = "SECRET-TITLE"
SECRET_PATH = "/secret/path?token=abc"


def ev(start_offset, duration, **data):
    return {"timestamp": iso(NOW + start_offset), "duration": duration, "data": data}


class FakeAW:
    """Serves canned bucket/event JSON keyed by bucket name; records URLs."""

    def __init__(self, window=None, afk=None, web=None, stale=()):
        self.events = {aw_probe.WINDOW_BUCKET: window or [],
                       aw_probe.AFK_BUCKET: afk or [],
                       aw_probe.WEB_BUCKET: web or []}
        self.stale = set(stale)
        self.urls = []

    def __call__(self, url):
        self.urls.append(url)
        path = urllib.parse.urlsplit(url).path
        if path.rstrip("/") == "/api/0/buckets":
            return {b: {"metadata": {"end": iso(NOW - (900 if b in self.stale else 2))}}
                    for b in self.events}
        bucket = urllib.parse.unquote(path.split("/")[4])
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
        start = aw_probe.parse_ts(q.get("start")) if "start" in q else None
        out = [e for e in self.events[bucket]
               if start is None or aw_probe.parse_ts(e["timestamp"]) + e["duration"] >= start]
        return sorted(out, key=lambda e: e["timestamp"], reverse=True)


def probe(fake):
    return aw_probe.AWProbe(fetch=fake, rules=RULES, clock=lambda: NOW).probe()


def afk_all(status="not-afk"):
    return [ev(-7200, 7200 - 30, status=status)]  # heartbeat 30 s stale: extends to now


class ParseAndRulesTests(unittest.TestCase):
    def test_parse_nanosecond_timestamp(self):
        self.assertAlmostEqual(aw_probe.parse_ts("2026-10-09T16:00:05.218284073Z"),
                               aw_probe.parse_ts("2026-10-09T16:00:05.218284Z"), places=5)
        self.assertIsNone(aw_probe.parse_ts("garbage"))

    def test_domain_of_strips_everything_but_host(self):
        self.assertEqual(aw_probe.domain_of("https://www.YouTube.com/watch?v=1"), "youtube.com")
        self.assertIsNone(aw_probe.domain_of("about:blank"))

    def test_categorize(self):
        c = aw_probe.categorize_domain
        self.assertEqual(c("claude.ai", RULES), "work")
        self.assertEqual(c("m.youtube.com", RULES), "drift")
        self.assertEqual(c("notyoutube.com", RULES), "neutral")
        self.assertEqual(c("docs.python.org", RULES), "work")
        self.assertEqual(c("technews.example", RULES), "drift")
        self.assertEqual(c("example.org", RULES), "neutral")
        self.assertEqual(c(None, RULES), "neutral")

    def test_merge_runs_gap(self):
        runs = aw_probe.merge_runs([(0, 10, "a"), (14, 20, "a"), (30, 40, "a"), (40, 41, "b")])
        self.assertEqual(runs, [(0, 20, "a"), (30, 40, "a"), (40, 41, "b")])

    def test_example_rules_file_is_generic_and_valid(self):
        r = aw_probe.load_rules(aw_probe.EXAMPLE_RULES)
        self.assertEqual(r["domains"]["youtube.com"], "drift")
        self.assertEqual(r["apps"]["zen"], "browser")


class ProbeTests(unittest.TestCase):
    def test_web_dwell_counts_only_focused_browser_time(self):
        # Zen focused for the last 100 s; before that kitty for 5 min.
        window = [ev(-400, 300, app="kitty", title=TITLE),
                  ev(-100, 60, app="zen", title=TITLE),
                  ev(-40, 38, app="zen", title=TITLE + "2")]
        # youtube open in the browser for 300 s (background web bucket keeps recording)
        web = [ev(-300 + i * 10, 8, url="https://youtube.com" + SECRET_PATH, title=TITLE)
               for i in range(30)]
        s = probe(FakeAW(window=window, afk=afk_all(), web=web))
        self.assertTrue(s["ok"])
        self.assertEqual(s["focused_app"], "zen")
        self.assertEqual(s["focused_class"], "browser")
        self.assertAlmostEqual(s["focused_for_s"], 100, delta=1)
        self.assertEqual((s["web_domain"], s["web_category"]), ("youtube.com", "drift"))
        self.assertAlmostEqual(s["web_dwell_s"], 100, delta=1)  # not 300
        self.assertAlmostEqual(s["terminal_last_s"], 100, delta=1)

    def test_web_gap_over_5s_splits_run(self):
        window = [ev(-600, 598, app="zen")]
        web = [ev(-500, 100, url="https://youtube.com/a"),
               ev(-390, 388, url="https://youtube.com/b")]  # 10 s gap
        s = probe(FakeAW(window=window, afk=afk_all(), web=web))
        self.assertAlmostEqual(s["web_dwell_s"], 390, delta=1)

    def test_web_dwell_excludes_afk_time(self):
        window = [ev(-600, 598, app="zen")]
        afk = [ev(-600, 400, status="not-afk"), ev(-200, 100, status="afk"),
               ev(-100, 99, status="not-afk")]
        web = [ev(-600, 598, url="https://youtube.com/")]
        s = probe(FakeAW(window=window, afk=afk, web=web))
        self.assertFalse(s["afk"])
        self.assertAlmostEqual(s["web_dwell_s"], 500, delta=2)
        self.assertAlmostEqual(s["afk_changed_s"], 100, delta=1)

    def test_background_browser_is_not_dwell(self):
        window = [ev(-600, 598, app="kitty")]
        web = [ev(-600, 598, url="https://youtube.com/")]
        s = probe(FakeAW(window=window, afk=afk_all(), web=web))
        self.assertEqual(s["web_dwell_s"], 0)
        self.assertEqual(s["focused_class"], "terminal")
        self.assertEqual(s["terminal_last_s"], 0)

    def test_afk(self):
        s = probe(FakeAW(window=[ev(-60, 58, app="zen")], afk=afk_all("afk")))
        self.assertTrue(s["afk"])

    def test_first_active_today(self):
        afk = [ev(-5 * 3600, 600, status="afk"), ev(-4 * 3600, 4 * 3600 - 5, status="not-afk")]
        s = probe(FakeAW(window=[ev(-60, 58, app="kitty")], afk=afk))
        self.assertAlmostEqual(s["first_active_today"], NOW - 4 * 3600, delta=1)

    def test_stale_bucket_fails_quiet(self):
        s = probe(FakeAW(window=[ev(-60, 58, app="kitty")], afk=afk_all(),
                         stale=[aw_probe.WINDOW_BUCKET]))
        self.assertFalse(s["ok"])
        self.assertEqual(s["error"], "stale_bucket")

    def test_network_error_fails_quiet(self):
        def down(url):
            raise OSError("connection refused")
        s = aw_probe.AWProbe(fetch=down, rules=RULES, clock=lambda: NOW).probe()
        self.assertFalse(s["ok"])

    def test_snapshot_never_contains_title_or_url(self):
        window = [ev(-60, 58, app="zen", title=TITLE)]
        web = [ev(-60, 58, url="https://youtube.com" + SECRET_PATH, title=TITLE)]
        s = probe(FakeAW(window=window, afk=afk_all(), web=web))
        blob = json.dumps(s)
        self.assertNotIn(TITLE, blob)
        self.assertNotIn("secret", blob)
        self.assertNotIn("https://", blob)

    def test_only_reads_expected_endpoints(self):
        fake = FakeAW(window=[ev(-60, 58, app="kitty")], afk=afk_all())
        probe(fake)
        for u in fake.urls:
            self.assertTrue(u.startswith("http://localhost:5600/api/0/buckets/"), u)
            self.assertNotIn("/query", u)

    def test_http_get_json_uses_get(self):
        seen = []

        class Resp:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self, *a):
                return b"{}"

        def fake_urlopen(req, timeout=None):
            seen.append(req.get_method())
            self.assertIsNone(req.data)
            return Resp()

        with mock.patch.object(aw_probe.urllib.request, "urlopen", fake_urlopen):
            self.assertEqual(aw_probe.http_get_json("http://localhost:5600/api/0/buckets/"), {})
        self.assertEqual(seen, ["GET"])


if __name__ == "__main__":
    unittest.main()
