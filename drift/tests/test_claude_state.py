import json
import os
import tempfile
import unittest

import helpers  # noqa: F401  (sets sys.path)

import claude_state

NOW = 1_800_000_000.0


class Fixture:
    def __init__(self, root):
        self.claude = os.path.join(root, "claude")
        self.proc = os.path.join(root, "proc")
        os.makedirs(os.path.join(self.claude, "sessions"))
        os.makedirs(os.path.join(self.claude, "projects", "-some-proj"))
        os.makedirs(self.proc)

    def proc_entry(self, pid, starttime="1000", comm="claude (x)"):
        d = os.path.join(self.proc, str(pid))
        os.makedirs(d, exist_ok=True)
        fields = ["S"] + ["0"] * 18 + [starttime] + ["0"] * 10
        with open(os.path.join(d, "stat"), "w") as f:
            f.write("%d (%s) %s\n" % (pid, comm, " ".join(fields)))

    def session(self, pid, status, since_s_ago=0, alive=True, proc_start="1000", **extra):
        d = {"pid": pid, "sessionId": "sid-%d" % pid, "cwd": "/private/path",
             "procStart": proc_start, "status": status,
             "statusUpdatedAt": int((NOW - since_s_ago) * 1000),
             "updatedAt": int((NOW - since_s_ago) * 1000), "name": "secret-name"}
        d.update(extra)
        with open(os.path.join(self.claude, "sessions", "%d.json" % pid), "w") as f:
            json.dump(d, f)
        if alive:
            self.proc_entry(pid, "1000")

    def history(self, *ages):
        with open(os.path.join(self.claude, "history.jsonl"), "w") as f:
            for a in ages:
                f.write(json.dumps({"display": "secret prompt text", "timestamp":
                                    int((NOW - a) * 1000), "sessionId": "x"}) + "\n")

    def state(self, clock=lambda: NOW):
        return claude_state.ClaudeState(self.claude, self.proc, clock)


class ClaudeStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fx = Fixture(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_sessions(self):
        s = self.fx.state().summary()
        self.assertEqual(s["sessions_alive"], 0)
        self.assertFalse(s["any_busy"])
        self.assertIsNone(s["last_prompt_age_s"])

    def test_busy_and_shell_count_as_busy(self):
        self.fx.session(11, "busy", since_s_ago=50)
        self.fx.session(12, "shell", since_s_ago=120)
        self.fx.session(13, "idle", since_s_ago=10)
        s = self.fx.state().summary()
        self.assertTrue(s["any_busy"])
        self.assertAlmostEqual(s["busy_for_s"], 120, delta=0.5)
        self.assertEqual(s["sessions_alive"], 3)
        self.assertIsNone(s["idle_for_s"])

    def test_dead_pid_ignored(self):
        self.fx.session(21, "busy", since_s_ago=100, alive=False)
        self.assertFalse(self.fx.state().summary()["any_busy"])

    def test_pid_reuse_ignored_by_procstart(self):
        self.fx.session(22, "busy", since_s_ago=100, proc_start="999")
        self.assertFalse(self.fx.state().summary()["any_busy"])

    def test_comm_with_spaces_and_parens(self):
        self.fx.proc_entry(23, "1000", comm="weird ) name")
        self.assertTrue(claude_state.pid_alive(23, "1000", self.fx.proc))

    def test_waiting_is_blocked_on_user(self):
        self.fx.session(31, "waiting", since_s_ago=5, waitingFor="permission")
        s = self.fx.state().summary()
        self.assertTrue(s["any_blocked_on_user"])
        self.assertFalse(s["any_busy"])

    def test_idle_for_and_last_prompt(self):
        self.fx.session(41, "idle", since_s_ago=400)
        self.fx.history(900, 450)
        s = self.fx.state().summary()
        self.assertAlmostEqual(s["last_prompt_age_s"], 450, delta=0.5)
        self.assertAlmostEqual(s["idle_for_s"], 400, delta=0.5)

    def test_busy_clock_survives_status_flip(self):
        t = [NOW]
        st = self.fx.state(clock=lambda: t[0])
        self.fx.session(51, "busy", since_s_ago=60)
        self.assertAlmostEqual(st.summary()["busy_for_s"], 60, delta=0.5)
        t[0] = NOW + 20
        self.fx.session(51, "shell", since_s_ago=-15)  # flipped 5 s ago
        self.assertAlmostEqual(st.summary()["busy_for_s"], 80, delta=0.5)
        self.fx.session(51, "idle", since_s_ago=-20)
        self.assertFalse(st.summary()["any_busy"])

    def test_unknown_status_falls_back_to_transcript_mtime(self):
        self.fx.session(61, "thinking-new", since_s_ago=30)
        tp = os.path.join(self.fx.claude, "projects", "-some-proj", "sid-61.jsonl")
        open(tp, "w").close()
        os.utime(tp, (NOW - 5, NOW - 5))
        self.assertTrue(self.fx.state().summary()["any_busy"])
        os.utime(tp, (NOW - 300, NOW - 300))
        self.assertFalse(self.fx.state().summary()["any_busy"])

    def test_malformed_files_skipped(self):
        with open(os.path.join(self.fx.claude, "sessions", "77.json"), "w") as f:
            f.write("{oops")
        with open(os.path.join(self.fx.claude, "sessions", "78.json"), "w") as f:
            f.write("[1,2]")
        with open(os.path.join(self.fx.claude, "history.jsonl"), "w") as f:
            f.write("garbage\n{\"timestamp\": \"x\"}\n")
        s = self.fx.state().summary()
        self.assertEqual(s["sessions_alive"], 0)
        self.assertIsNone(s["last_prompt_age_s"])

    def test_output_has_no_private_fields(self):
        self.fx.session(81, "busy", since_s_ago=50)
        self.fx.history(10)
        blob = json.dumps(self.fx.state().summary())
        for secret in ("secret", "/private/path", "sid-81"):
            self.assertNotIn(secret, blob)


if __name__ == "__main__":
    unittest.main()
