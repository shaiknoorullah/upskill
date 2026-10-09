import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))
import fsrs  # noqa: E402


def run(home, *args, now="2026-10-10T10:00:00+05:30"):
    env = {**os.environ, "UPSKILL_HOME": str(home), "UPSKILL_NOW": now}
    return subprocess.run([sys.executable, str(REPO / "tutor" / "tutor.py"), *args],
                          capture_output=True, text=True, env=env)


class FsrsTest(unittest.TestCase):
    T0 = datetime.fromisoformat("2026-10-01T10:00:00+05:30")

    def test_first_review_intervals_grow_with_rating(self):
        days = [fsrs.interval_days(fsrs.review({}, g, self.T0)["s"]) for g in (2, 3, 4)]
        self.assertEqual(days, sorted(days))

    def test_again_comes_back_same_day(self):
        c = fsrs.review({}, "again", self.T0)
        self.assertLess(datetime.fromisoformat(c["due"]) - self.T0, fsrs.timedelta(hours=1))

    def test_success_grows_stability_and_lapse_shrinks_it(self):
        c = fsrs.review({}, "good", self.T0)
        later = datetime.fromisoformat(c["due"])
        good = fsrs.review(c, "good", later)
        bad = fsrs.review(c, "again", later)
        self.assertGreater(good["s"], c["s"])
        self.assertLess(bad["s"], c["s"])
        self.assertEqual(bad["lapses"], 1)

    def test_r_at_stability_is_target(self):
        self.assertAlmostEqual(fsrs.retrievability(10, 10), 0.9, places=6)


class CliTest(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        shutil.copytree(REPO / "tracks" / "regex", self.home / "tracks" / "regex")
        (self.home / "tracks" / "index.json").write_text('{"order": ["regex"]}')

    def tearDown(self):
        shutil.rmtree(self.home)

    def test_fresh_status_points_at_first_item(self):
        out = run(self.home, "status", "--json")
        st = json.loads(out.stdout)
        self.assertEqual((st["due"], st["next"], st["why"]), (0, "regex/1", "new"))

    def test_check_logs_attempt_and_grades_with_checksh(self):
        good = run(self.home, "check", "regex/1", "grep -cE '\" 5[0-9]{2} ' logs/access.log")
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        bad = run(self.home, "check", "regex/1", "grep -c ' 5[0-9][0-9] ' logs/access.log")
        self.assertEqual(bad.returncode, 1)
        events = (self.home / "state" / "events.jsonl").read_text().splitlines()
        self.assertEqual([json.loads(e)["result"] for e in events], ["pass", "fail"])

    def test_rate_schedules_and_due_returns_later(self):
        run(self.home, "rate", "regex/1", "good", now="2026-10-01T10:00:00+05:30")
        self.assertEqual(run(self.home, "due", now="2026-10-01T11:00:00+05:30").stdout, "")
        self.assertIn("regex/1", run(self.home, "due", now="2026-11-30T10:00:00+05:30").stdout)

    def test_checkpoint_resume_wins_over_new(self):
        run(self.home, "checkpoint", "set", "--item", "regex/7", "--step", "attempt")
        st = json.loads(run(self.home, "status", "--json").stdout)
        self.assertEqual((st["next"], st["why"]), ("regex/7", "resume"))
        run(self.home, "checkpoint", "clear")
        self.assertEqual(json.loads(run(self.home, "status", "--json").stdout)["why"], "new")

    def test_drills_need_prereq(self):
        nxt = json.loads(run(self.home, "next").stdout)["item"]["id"]
        self.assertEqual(nxt, "regex/1")
        listing = run(self.home, "list").stdout
        self.assertIn("regex/4a", listing)

    def test_ledger_requires_evidence_for_demonstrated(self):
        self.assertNotEqual(run(self.home, "ledger", "x", "--level", "demonstrated").returncode, 0)
        ok = run(self.home, "ledger", "x", "--level", "demonstrated", "--evidence", "2026-10-10: explained -w vs \\b")
        self.assertEqual(ok.returncode, 0)

    def test_union_merged_duplicate_and_garbage_lines_are_tolerated(self):
        run(self.home, "rate", "regex/1", "good")
        ev = self.home / "state" / "events.jsonl"
        ev.write_text(ev.read_text() + "<<<<<<< broken\n")
        self.assertEqual(run(self.home, "status").returncode, 0)

    def test_streak_counts_consecutive_days(self):
        for d in ("2026-10-08", "2026-10-09", "2026-10-10"):
            run(self.home, "attempt", "regex/1", "--result", "fail", now=f"{d}T09:00:00+05:30")
        st = json.loads(run(self.home, "status", "--json", now="2026-10-10T20:00:00+05:30").stdout)
        self.assertEqual((st["streak"], st["week"]), (3, 3))


if __name__ == "__main__":
    unittest.main()
