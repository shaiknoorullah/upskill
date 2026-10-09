import json
import os
import tempfile
import unittest

from helpers import WED_14, drifting, claude_snap

import nudged
import policy


class FakeProbe:
    def __init__(self, snap):
        self.snap = snap

    def probe(self):
        return dict(self.snap)


class FakeClaude:
    def __init__(self, snap):
        self.snap = snap

    def summary(self):
        return dict(self.snap)


class FakeNotifier:
    def __init__(self, result):
        self.result = result
        self.sent = []

    def send(self, title, body):
        self.sent.append((title, body))
        return self.result


NO_ENV = {"meeting": lambda: False, "dnd": lambda: False}


class DaemonTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.local = os.path.join(self.tmp.name, "local")
        self.status = os.path.join(self.tmp.name, "cache")
        self.repo = os.path.join(self.tmp.name, "repo")
        os.makedirs(self.repo)
        self.started = []

    def tearDown(self):
        self.tmp.cleanup()

    def daemon(self, result="start", aw=None, cl=None, write=True):
        self.notifier = FakeNotifier(result)
        return nudged.Daemon(local_dir=self.local, status_dir=self.status, repo=self.repo,
                             probe=FakeProbe(aw or drifting()),
                             claude=FakeClaude(cl or claude_snap()), env=NO_ENV,
                             notifier=self.notifier, starter=self.started.append,
                             clock=lambda: WED_14, write=write)

    def _log(self):
        with open(os.path.join(self.local, "nudges.jsonl")) as f:
            return [json.loads(line) for line in f]

    def test_deliver_start_opens_window_and_records(self):
        dec = self.daemon("start").tick(deliver=True)
        self.assertEqual((dec["decision"], dec["delivered"]), ("nudge", "start"))
        self.assertEqual(len(self.started), 1)
        self.assertIn("upskill", self.started[0])
        st = policy.load_state(os.path.join(self.local, "drift-state.json"))
        self.assertEqual(st["nudges_today"], 1)
        self.assertEqual(st["last_drill_ts"], WED_14)
        with open(os.path.join(self.status, "status")) as f:
            self.assertTrue(f.read().startswith("upskill"))
        with open(os.path.join(self.status, "status.json")) as f:
            self.assertIn("class", json.load(f))

    def test_snooze_records_and_does_not_start(self):
        self.daemon("snooze").tick(deliver=True)
        self.assertEqual(self.started, [])
        st = policy.load_state(os.path.join(self.local, "drift-state.json"))
        self.assertEqual(st["snooze_until"], WED_14 + 30 * 60)

    def test_expired_backs_off(self):
        self.daemon("expired").tick(deliver=True)
        st = policy.load_state(os.path.join(self.local, "drift-state.json"))
        self.assertEqual(st["backoff_level"], 1)

    def test_second_tick_respects_cooldown(self):
        d = self.daemon("snooze")
        d.tick(deliver=True)
        dec = d.tick(deliver=True)
        self.assertEqual(dec["decision"], "snooze")
        self.assertEqual(len(self.notifier.sent), 1)

    def test_once_without_deliver_never_notifies(self):
        dec = self.daemon().tick(deliver=False)
        self.assertEqual(dec["decision"], "nudge")
        self.assertEqual(self.notifier.sent, [])
        self.assertEqual(self.started, [])

    def test_dry_run_writes_nothing(self):
        d = self.daemon(write=False)
        d.tick(deliver=True)
        d.manual_start()
        self.assertFalse(os.path.exists(self.local))
        self.assertFalse(os.path.exists(self.status))
        self.assertEqual(self.notifier.sent, [])
        self.assertEqual(self.started, [])

    def test_log_holds_category_not_domain(self):
        self.daemon("snooze").tick(deliver=True)
        rows = self._log()
        self.assertEqual(rows[0]["category"], "drift")
        self.assertEqual(rows[0]["trigger"], "T1")
        self.assertNotIn("youtube", json.dumps(rows))
        self.assertEqual(set(rows[0]), {"ts", "trigger", "decision", "gate", "category",
                                        "delivered"})

    def test_log_deduplicates_repeated_decisions(self):
        d = self.daemon()
        d.tick(deliver=False)
        d.tick(deliver=False)
        self.assertEqual(len(self._log()), 1)

    def test_printable_strips_domain_by_default(self):
        dec = self.daemon().tick(deliver=False)
        self.assertNotIn("youtube", json.dumps(nudged._printable(dec)))
        self.assertIn("youtube", json.dumps(nudged._printable(dec, show_domain=True)))

    def test_manual_start_is_uncapped(self):
        d = self.daemon()
        st = policy.new_state()
        st.update(day="2026-10-07", nudges_today=4, done_date="2026-10-07")
        policy.save_state(os.path.join(self.local, "drift-state.json"), st)
        d.manual_start()
        self.assertEqual(len(self.started), 1)
        self.assertEqual(self._log()[-1]["trigger"], "T4")

    def test_local_config_overrides(self):
        os.makedirs(self.local)
        with open(os.path.join(self.local, "drift-config.json"), "w") as f:
            json.dump({"drift_dwell_s": 999, "start_command": "echo {repo}"}, f)
        d = self.daemon()
        self.assertEqual(d.cfg["drift_dwell_s"], 999)
        self.assertIsNone(d.tick(deliver=False)["trigger"])
        self.assertEqual(nudged.build_start_command(d.dcfg, "/r"), "echo /r")


class AdapterTests(unittest.TestCase):
    def test_notifier_with_actions(self):
        calls = []

        def runner(argv, timeout):
            calls.append(argv)
            if argv[1] == "--help":
                return 0, "  -A, --action=[NAME=]Text...\n"
            return 0, "snooze\n"
        n = nudged.Notifier(runner=runner, ttl_s=25)
        self.assertEqual(n.send("t", "b"), "snooze")
        argv = calls[-1]
        self.assertEqual(argv[:3], ["notify-send", "-a", "upskill"])
        self.assertIn("--action=start=Start", argv)
        self.assertIn("--action=snooze=Not now", argv)
        self.assertIn("--action=done=Done today", argv)

    def test_notifier_timeout_and_close_are_expired(self):
        n = nudged.Notifier(runner=lambda a, t: (0, "--action") if a[1] == "--help" else (124, ""))
        self.assertEqual(n.send("t", "b"), "expired")
        n = nudged.Notifier(runner=lambda a, t: (0, "--action") if a[1] == "--help" else (0, ""))
        self.assertEqual(n.send("t", "b"), "expired")

    def test_notifier_without_action_support(self):
        calls = []

        def runner(argv, timeout):
            calls.append(argv)
            return 0, "usage: notify-send [OPTION...] <SUMMARY>\n"
        n = nudged.Notifier(runner=runner)
        self.assertEqual(n.send("t", "b"), "plain")
        self.assertFalse(any(a.startswith("--action") for a in calls[-1]))

    def test_notifier_missing_binary(self):
        n = nudged.Notifier(runner=lambda a, t: (127, ""))
        self.assertEqual(n.send("t", "b"), "failed")

    def test_start_command_tmux_fallback(self):
        cmd = nudged.build_start_command(dict(nudged.DAEMON_DEFAULTS), "/home/u/upskill",
                                         which=lambda n: None, environ={"TMUX": "x"})
        self.assertIn("tmux new-window -n upskill -c /home/u/upskill", cmd)
        self.assertIn("KUBECONFIG=/home/u/upskill/local/kube/practice.yaml", cmd)
        self.assertIn("TUTOR=1", cmd)
        self.assertIn("claude /pause", cmd)

    def test_start_command_prefers_tmux_cli(self):
        cmd = nudged.build_start_command(dict(nudged.DAEMON_DEFAULTS), "/r",
                                         which=lambda n: "/bin/" + n,
                                         environ={"TMUX": "/tmp/tmux-1/default,1,0"})
        self.assertIn("tmux-cli launch zsh", cmd)
        self.assertIn("tmux-cli send", cmd)
        self.assertIn("TUTOR=1", cmd)

    def test_start_command_outside_tmux_uses_tmux(self):
        cmd = nudged.build_start_command(dict(nudged.DAEMON_DEFAULTS), "/r",
                                         which=lambda n: "/bin/" + n, environ={})
        self.assertIn("tmux new-window -n upskill", cmd)
        self.assertNotIn("tmux-cli", cmd)

    def test_meeting_and_dnd_probes(self):
        self.assertTrue(nudged.meeting_active(lambda a: (0, "42\t1\t2\tprotocol-native\n")))
        self.assertFalse(nudged.meeting_active(lambda a: (0, "")))
        self.assertFalse(nudged.meeting_active(lambda a: (127, "")))
        self.assertTrue(nudged.dnd_active(lambda a: (0, "default\ndo-not-disturb\n")))
        self.assertFalse(nudged.dnd_active(lambda a: (0, "default\n")))

    def test_tutor_status_missing_or_present(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(nudged.tutor_status(d))
            os.makedirs(os.path.join(d, "tutor"))
            open(os.path.join(d, "tutor", "tutor.py"), "w").close()
            self.assertEqual(nudged.tutor_status(d, runner=lambda a: (0, "upskill 3 due\nx")),
                             "upskill 3 due")
            self.assertIsNone(nudged.tutor_status(d, runner=lambda a: (1, "")))


if __name__ == "__main__":
    unittest.main()
