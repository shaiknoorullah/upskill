import unittest

from helpers import WED_14, SAT_14, WED_20, aw_snap, drifting, claude_snap, idle_claude

import policy

CFG = policy.config()


def env(meeting=False, dnd=False, calls=None):
    def mk(name, val):
        def f():
            if calls is not None:
                calls.append(name)
            return val
        return f
    return {"meeting": mk("meeting", meeting), "dnd": mk("dnd", dnd)}


def run(aw=None, cl=None, state=None, e=None, now=WED_14, cfg=CFG):
    return policy.evaluate(aw or drifting(), cl or claude_snap(),
                           state if state is not None else policy.new_state(),
                           e if e is not None else env(), now, cfg)


class TriggerTests(unittest.TestCase):
    def test_t1_drift_site(self):
        d = run()
        self.assertEqual((d["trigger"], d["why"], d["decision"]), ("T1", "drift_site", "nudge"))
        self.assertEqual(d["category"], "drift")

    def test_t1_drift_dwell_too_short(self):
        d = run(aw=drifting(web_dwell_s=60))
        self.assertIsNone(d["trigger"])
        self.assertEqual(d["decision"], "none")

    def test_t1_neutral_site_needs_longer_dwell(self):
        self.assertIsNone(run(aw=drifting(web_category="neutral", web_dwell_s=120))["trigger"])
        d = run(aw=drifting(web_category="neutral", web_dwell_s=200, terminal_last_s=300))
        self.assertEqual((d["trigger"], d["why"]), ("T1", "neutral_site"))

    def test_t1_neutral_app(self):
        a = aw_snap(focused_app="slack", focused_class="neutral", focused_for_s=200,
                    terminal_last_s=200)
        d = run(aw=a)
        self.assertEqual((d["trigger"], d["why"]), ("T1", "neutral_app"))

    def test_t1_work_site_is_not_drift(self):
        d = run(aw=drifting(web_domain="claude.ai", web_category="work", web_dwell_s=900))
        self.assertIsNone(d["trigger"])

    def test_t1_busy_too_short(self):
        d = run(cl=claude_snap(busy_for_s=30))
        self.assertEqual((d["trigger"], d["why"]), (None, "busy_too_short"))

    def test_t1_on_terminal_no_trigger(self):
        self.assertIsNone(run(aw=aw_snap())["trigger"])

    def test_t2_idle_drift(self):
        d = run(aw=drifting(web_category="neutral", web_dwell_s=10), cl=idle_claude())
        self.assertEqual((d["trigger"], d["decision"]), ("T2", "nudge"))

    def test_t2_needs_five_idle_minutes(self):
        d = run(cl=idle_claude(idle_for_s=200))
        self.assertEqual((d["trigger"], d["why"]), (None, "idle_too_short"))
        d = run(cl=idle_claude(last_prompt_age_s=200))
        self.assertEqual((d["trigger"], d["why"]), (None, "prompt_too_recent"))

    def test_t2_not_when_on_terminal_or_work(self):
        self.assertIsNone(run(aw=aw_snap(), cl=idle_claude())["trigger"])
        a = drifting(web_category="work")
        self.assertIsNone(run(aw=a, cl=idle_claude())["trigger"])
        a = aw_snap(focused_app="code", focused_class="work", terminal_last_s=500)
        self.assertIsNone(run(aw=a, cl=idle_claude())["trigger"])

    def test_afk_never_triggers(self):
        d = run(aw=drifting(afk=True))
        self.assertEqual((d["trigger"], d["why"], d["decision"]), (None, "afk", "none"))

    def test_aw_unavailable_fails_quiet(self):
        d = run(aw={"ok": False, "error": "URLError"})
        self.assertEqual((d["decision"], d["gate"]), ("suppress", "aw_unavailable"))


class GateTests(unittest.TestCase):
    def test_work_window(self):
        self.assertEqual(run(now=SAT_14)["gate"], "work_window")
        self.assertEqual(run(now=WED_20)["gate"], "work_window")

    def test_warmup(self):
        d = run(aw=drifting(first_active_today=WED_14 - 10 * 60))
        self.assertEqual((d["decision"], d["gate"]), ("suppress", "warmup"))
        d = run(aw=drifting(first_active_today=None))
        self.assertEqual(d["gate"], "warmup")

    def test_blocked_on_user(self):
        d = run(cl=claude_snap(any_blocked_on_user=True))
        self.assertEqual((d["decision"], d["gate"]), ("suppress", "blocked_on_user"))

    def test_typing_guard_terminal(self):
        a = drifting(terminal_last_s=10, web_category="drift")
        d = run(aw=a)
        self.assertEqual((d["decision"], d["gate"]), ("hold", "typing"))

    def test_typing_guard_recent_prompt(self):
        d = run(cl=claude_snap(last_prompt_age_s=30))
        self.assertEqual((d["decision"], d["gate"]), ("hold", "typing"))

    def test_typing_guard_afk_flip(self):
        d = run(aw=drifting(afk_changed_s=5))
        self.assertEqual((d["decision"], d["gate"]), ("hold", "typing"))

    def test_meeting(self):
        d = run(e=env(meeting=True))
        self.assertEqual((d["decision"], d["gate"]), ("suppress", "meeting"))

    def test_dnd(self):
        d = run(e=env(dnd=True))
        self.assertEqual((d["decision"], d["gate"]), ("suppress", "dnd"))

    def test_env_probes_are_lazy(self):
        calls = []
        run(now=SAT_14, e=env(calls=calls))
        self.assertEqual(calls, [])
        run(e=env(calls=calls))
        self.assertEqual(calls, ["meeting", "dnd"])

    def test_env_probe_exception_is_false(self):
        def boom():
            raise OSError("no pactl")
        self.assertEqual(run(e={"meeting": boom, "dnd": boom})["decision"], "nudge")

    def test_daily_cap(self):
        st = policy.new_state()
        for i in range(4):
            policy.record_nudge(st, WED_14 - 10 * 3600 + i * 3 * 3600 / 4)
        st["last_nudge_ts"] = WED_14 - 5 * 3600
        st["day"] = "2026-10-07"
        st["nudges_today"] = 4
        self.assertEqual(run(state=st)["gate"], "daily_cap")

    def test_daily_cap_resets_next_day(self):
        st = policy.new_state()
        st.update(day="2026-10-06", nudges_today=4, last_nudge_ts=WED_14 - 86400)
        d = run(state=st)
        self.assertEqual(d["decision"], "nudge")
        self.assertEqual(st["nudges_today"], 0)

    def test_frequency_cooldown_45_min(self):
        st = policy.record_nudge(policy.new_state(), WED_14 - 30 * 60)
        policy.apply_action(st, "snooze", WED_14 - 30 * 60)
        st["snooze_until"] = None  # isolate the cooldown
        self.assertEqual(run(state=st)["gate"], "cooldown")
        st = policy.record_nudge(policy.new_state(), WED_14 - 46 * 60)
        self.assertEqual(run(state=st)["decision"], "nudge")

    def test_backoff_doubles_after_expiry(self):
        st = policy.record_nudge(policy.new_state(), WED_14 - 60 * 60)
        policy.apply_action(st, "expired", WED_14 - 60 * 60)
        self.assertEqual(st["backoff_level"], 1)
        d = run(state=st)  # 60 min < 90 min
        self.assertEqual((d["decision"], d["gate"]), ("backoff", "backoff"))
        policy.apply_action(st, "expired", WED_14)
        policy.apply_action(st, "expired", WED_14)
        self.assertEqual(st["backoff_level"], 2)  # capped: 45 -> 90 -> 180
        st["last_nudge_ts"] = WED_14 - 181 * 60
        self.assertEqual(run(state=st)["decision"], "nudge")

    def test_accept_resets_backoff(self):
        st = policy.new_state()
        st["backoff_level"] = 2
        policy.apply_action(st, "start", WED_14 - 2 * 3600)
        self.assertEqual(st["backoff_level"], 0)

    def test_drill_cooldown(self):
        st = policy.apply_action(policy.new_state(), "start", WED_14 - 30 * 60)
        self.assertEqual(run(state=st)["gate"], "drill_cooldown")
        st = policy.apply_action(policy.new_state(), "start", WED_14 - 61 * 60)
        self.assertEqual(run(state=st)["decision"], "nudge")

    def test_snooze_then_escalate(self):
        st = policy.new_state()
        policy.apply_action(st, "snooze", WED_14 - 10 * 60)
        self.assertEqual(st["snooze_until"], WED_14 + 20 * 60)
        self.assertEqual(run(state=st)["decision"], "snooze")
        policy.apply_action(st, "snooze", WED_14)
        self.assertEqual(st["snooze_until"], WED_14 + 90 * 60)
        self.assertEqual(run(state=st, now=WED_14 + 60 * 60)["gate"], "snoozed")
        policy.apply_action(st, "start", WED_14 + 2 * 3600)
        self.assertEqual(st["snooze_streak"], 0)

    def test_done_today(self):
        st = policy.apply_action(policy.new_state(), "done", WED_14 - 3600)
        d = run(state=st)
        self.assertEqual((d["decision"], d["gate"]), ("off", "done_today"))
        self.assertEqual(run(state=st, now=WED_14 + 86400)["decision"], "nudge")

    def test_tunable_thresholds(self):
        cfg = policy.config({"drift_dwell_s": 200, "_comment": "ignored"})
        self.assertIsNone(run(cfg=cfg)["trigger"])

    def test_unknown_action_rejected(self):
        with self.assertRaises(ValueError):
            policy.apply_action(policy.new_state(), "bogus", WED_14)


class StatusAndPersistenceTests(unittest.TestCase):
    def test_status_lines(self):
        st = policy.new_state()
        self.assertEqual(policy.status_line(run(), claude_snap(), st, WED_14)[1], "ready")
        self.assertEqual(policy.status_line({"gate": "aw_unavailable"}, {}, st, WED_14)[0],
                         "upskill ?")
        none = {"trigger": None, "decision": "none"}
        self.assertEqual(policy.status_line(none, claude_snap(busy_for_s=180), st, WED_14)[0],
                         "upskill . claude 3m")
        policy.apply_action(st, "snooze", WED_14)
        self.assertEqual(policy.status_line(none, {}, st, WED_14)[0], "upskill zz 30m")
        policy.apply_action(st, "done", WED_14)
        self.assertEqual(policy.status_line(none, {}, st, WED_14)[1], "done")

    def test_state_roundtrip_and_corrupt_file(self):
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "local", "drift-state.json")
            self.assertEqual(policy.load_state(p), policy.new_state())
            st = policy.record_nudge(policy.new_state(), WED_14)
            policy.save_state(p, st)
            self.assertEqual(policy.load_state(p)["nudges_today"], 1)
            with open(p, "w") as f:
                f.write("{not json")
            self.assertEqual(policy.load_state(p), policy.new_state())


if __name__ == "__main__":
    unittest.main()
