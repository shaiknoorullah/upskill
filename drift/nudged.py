#!/usr/bin/env python3
"""upskill drift detector daemon (v1).

Polls ActivityWatch (GET only) and Claude Code session state (read-only) every
20 s, decides whether the user has drifted while Claude works (T1) or gone
idle off-terminal (T2), and offers a 5-minute learning session through mako.

  nudged.py                 run the loop (what the systemd unit starts)
  nudged.py --once          evaluate once, print the decision JSON (no popup)
  nudged.py --once --deliver   ... and actually send the notification
  nudged.py --dry-run       loop, printing one decision line per poll; never writes
                            files, never notifies, never starts anything
  nudged.py --status        print the one-line status
  nudged.py --start         T4 manual: open the upskill tmux window now
"""

import argparse
import datetime as _dt
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import time

DRIFT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DRIFT_DIR)

import aw_probe  # noqa: E402
import claude_state  # noqa: E402
import policy  # noqa: E402

REPO_DIR = os.path.dirname(DRIFT_DIR)
LOCAL_DIR = os.path.join(REPO_DIR, "local")
STATUS_DIR = os.path.expanduser("~/.cache/upskill")
POLL_S = 20
STATUS_FRESH_S = 120

DAEMON_DEFAULTS = {
    "poll_s": POLL_S,
    # "auto" = tmux-cli if on PATH, else tmux. Or "tmux-cli", "tmux".
    "start_backend": "auto",
    # A full shell command overrides the backend. {repo} and {kubeconfig} are substituted.
    "start_command": None,
    "practice_kubeconfig": "{repo}/local/kube/practice.yaml",
    "session_prompt": "/pause",
}


def _run(argv, timeout=5):
    """Run a command, return (rc, stdout). Missing binary -> (127, '')."""
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout
    except FileNotFoundError:
        return 127, ""
    except subprocess.TimeoutExpired:
        return 124, ""


# ------------------------------------------------------------------ env gates

def meeting_active(runner=_run):
    """Mic in use: `pactl list source-outputs short` prints anything."""
    rc, out = runner(["pactl", "list", "source-outputs", "short"])
    return rc == 0 and bool(out.strip())


def dnd_active(runner=_run):
    rc, out = runner(["makoctl", "mode"])
    return rc == 0 and "do-not-disturb" in out


# ------------------------------------------------------------------ delivery

MESSAGES = {
    "T1": ("Claude is busy (~{m} min)", "One 5-minute drill while you wait?"),
    "T2": ("Claude is idle", "Got 5 minutes? One quick drill."),
}


class Notifier:
    """notify-send adapter. Returns start | snooze | done | expired | plain | failed."""

    def __init__(self, runner=None, ttl_s=25):
        self.runner = runner or self._default_runner
        self.ttl_s = ttl_s
        self._actions = None

    @staticmethod
    def _default_runner(argv, timeout):
        try:
            p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
            return p.returncode, p.stdout
        except FileNotFoundError:
            return 127, ""
        except subprocess.TimeoutExpired:
            return 124, ""  # subprocess.run kills the child on timeout

    def supports_actions(self):
        if self._actions is None:
            rc, out = self.runner(["notify-send", "--help"], 5)
            self._actions = rc == 0 and "--action" in out
        return self._actions

    def argv(self, title, body, actions=True):
        a = ["notify-send", "-a", "upskill", "-t", str(int(self.ttl_s * 1000))]
        if actions:
            a += ["--action=start=Start", "--action=snooze=Not now",
                  "--action=done=Done today"]
        return a + [title, body]

    def send(self, title, body):
        if not self.supports_actions():
            rc, _ = self.runner(self.argv(title, body, actions=False), 10)
            return "plain" if rc == 0 else "failed"
        rc, out = self.runner(self.argv(title, body), self.ttl_s + 5)
        if rc == 124:
            return "expired"
        if rc not in (0,):
            return "failed"
        choice = (out or "").strip().splitlines()[-1:] or [""]
        return choice[0] if choice[0] in ("start", "snooze", "done") else "expired"


def build_start_command(dcfg, repo=REPO_DIR, which=shutil.which, environ=os.environ):
    """Shell command that opens the 'upskill' tmux window running claude "/pause".

    auto: tmux-cli when it is on PATH and we are inside tmux. Outside tmux
    (systemd, waybar) tmux-cli manages its own detached 'remote-cli-session',
    which the user would never see, so plain tmux is used there instead.
    """
    kube = dcfg["practice_kubeconfig"].format(repo=repo)
    if dcfg.get("start_command"):
        return dcfg["start_command"].format(repo=repo, kubeconfig=kube)
    claude_cmd = "claude %s" % shlex.quote(dcfg["session_prompt"])
    backend = dcfg.get("start_backend", "auto")
    if backend == "auto":
        backend = "tmux-cli" if which("tmux-cli") and environ.get("TMUX") else "tmux"
    if backend == "tmux-cli":
        # tmux-cli: launch a shell first, then send the command into it.
        inner = "cd %s && KUBECONFIG=%s TUTOR=1 %s" % (
            shlex.quote(repo), shlex.quote(kube), claude_cmd)
        return ('pane=$(tmux-cli launch zsh | tail -n 1) && '
                'tmux rename-window -t "$pane" upskill 2>/dev/null; '
                'tmux-cli send %s --pane="$pane"' % shlex.quote(inner))
    return ("tmux select-window -t upskill 2>/dev/null || "
            "tmux new-window -n upskill -c %s -e KUBECONFIG=%s -e TUTOR=1 %s" % (
                shlex.quote(repo), shlex.quote(kube), shlex.quote(claude_cmd)))


def launch(cmd):
    """Run the start command detached. Never called by the tests."""
    subprocess.Popen(["sh", "-c", cmd], stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)


def tutor_status(repo=REPO_DIR, runner=_run):
    path = os.path.join(repo, "tutor", "tutor.py")
    if not os.path.exists(path):
        return None
    rc, out = runner([sys.executable, path, "status"])
    line = (out or "").strip().splitlines()
    return line[0].strip() if rc == 0 and line else None


# ------------------------------------------------------------------ daemon

def _load_json(path):
    try:
        with open(path) as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


class Daemon:
    def __init__(self, local_dir=LOCAL_DIR, status_dir=STATUS_DIR, repo=REPO_DIR,
                 probe=None, claude=None, env=None, notifier=None, starter=launch,
                 clock=time.time, write=True):
        self.local_dir = local_dir
        self.status_dir = status_dir
        self.repo = repo
        overrides = _load_json(os.path.join(local_dir, "drift-config.json"))
        self.cfg = policy.config(overrides)
        self.dcfg = dict(DAEMON_DEFAULTS)
        self.dcfg.update({k: v for k, v in overrides.items() if k in DAEMON_DEFAULTS})
        self.probe = probe or aw_probe.AWProbe()
        self.claude = claude or claude_state.ClaudeState()
        self.env = env if env is not None else {"meeting": meeting_active, "dnd": dnd_active}
        self.notifier = notifier or Notifier(ttl_s=self.cfg["nudge_ttl_s"])
        self.starter = starter
        self.clock = clock
        self.write = write
        self.state_path = os.path.join(local_dir, "drift-state.json")
        self.log_path = os.path.join(local_dir, "nudges.jsonl")
        self._last_logged = None

    # -- persistence (all no-ops when write=False)
    def _log(self, rec):
        if not self.write:
            return
        os.makedirs(self.local_dir, exist_ok=True)
        rec = dict(rec)
        rec["ts"] = _dt.datetime.fromtimestamp(rec["ts"]).isoformat(timespec="seconds")
        with open(self.log_path, "a") as f:
            f.write(json.dumps(rec, sort_keys=True) + "\n")

    def _save(self, state):
        if self.write:
            policy.save_state(self.state_path, state)

    def _write_status(self, text, cls):
        if not self.write:
            return
        os.makedirs(self.status_dir, exist_ok=True)
        for name, body in (("status", text + "\n"),
                           ("status.json", json.dumps({"text": text, "class": cls,
                                                       "alt": cls}) + "\n")):
            tmp = os.path.join(self.status_dir, name + ".tmp")
            with open(tmp, "w") as f:
                f.write(body)
            os.replace(tmp, os.path.join(self.status_dir, name))

    # -- one poll
    def tick(self, deliver=False):
        now = self.clock()
        state = policy.load_state(self.state_path)
        aw = self.probe.probe()
        cl = self.claude.summary()
        dec = policy.evaluate(aw, cl, state, self.env, now, self.cfg)
        dec["delivered"] = None

        if dec["decision"] == "nudge" and deliver and self.write:
            policy.record_nudge(state, now)
            self._save(state)
            title, body = MESSAGES[dec["trigger"]]
            title = title.format(m=max(1, int(cl.get("busy_for_s", 0) // 60)))
            result = self.notifier.send(title, body)
            dec["delivered"] = result
            if result in ("start", "snooze", "done", "expired", "plain"):
                policy.apply_action(state, result, self.clock(), self.cfg)
            if result == "start":
                self.starter(build_start_command(self.dcfg, self.repo))

        key = (dec["trigger"], dec["decision"], dec["gate"])
        if dec["trigger"] and (key != self._last_logged or dec["delivered"]):
            self._log({k: dec[k] for k in ("ts", "trigger", "decision", "gate",
                                           "category", "delivered")})
            self._last_logged = key
        elif not dec["trigger"]:
            self._last_logged = None

        text, cls = policy.status_line(dec, cl, state, now)
        ts = tutor_status(self.repo)
        if ts:
            # tutor status already starts with "upskill"; keep only the drift part
            text = "%s | %s" % (ts, text[len("upskill"):].strip(" .") or "idle")
        dec["status"] = text
        self._save(state)
        self._write_status(text, cls)
        dec["aw"] = {k: aw.get(k) for k in ("ok", "afk", "focused_app", "focused_class",
                                           "focused_for_s", "terminal_last_s",
                                           "web_category", "web_dwell_s", "error")}
        dec["aw"]["_web_domain"] = aw.get("web_domain")  # stdout only, stripped by default
        dec["claude"] = cl
        return dec

    def manual_start(self, dry_run=False):
        """T4: always allowed, never counted against the caps."""
        cmd = build_start_command(self.dcfg, self.repo)
        if dry_run or not self.write:
            return cmd
        now = self.clock()
        state = policy.load_state(self.state_path)
        policy.apply_action(state, "start", now, self.cfg)
        self._save(state)
        self._log({"ts": now, "trigger": "T4", "decision": "manual", "gate": None,
                   "category": None, "delivered": "start"})
        self.starter(cmd)
        return cmd

    def loop(self, deliver=True, echo=None):
        stop = []
        signal.signal(signal.SIGTERM, lambda *a: stop.append(1))
        while not stop:
            try:
                dec = self.tick(deliver=deliver)
                if echo:
                    echo(dec)
            except Exception as exc:
                print("nudged: tick failed: %s" % type(exc).__name__, file=sys.stderr)
            for _ in range(int(self.dcfg["poll_s"])):
                if stop:
                    break
                time.sleep(1)


def _printable(dec, show_domain=False):
    dec = json.loads(json.dumps(dec))
    dom = dec.get("aw", {}).pop("_web_domain", None)
    if show_domain:
        dec["aw"]["web_domain"] = dom
    return dec


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--once", action="store_true", help="evaluate once and print JSON")
    ap.add_argument("--deliver", action="store_true", help="with --once: actually notify")
    ap.add_argument("--dry-run", action="store_true", help="no writes, no notifications")
    ap.add_argument("--status", action="store_true", help="print the one-line status")
    ap.add_argument("--start", action="store_true", help="T4 manual: open the upskill window")
    ap.add_argument("--show-domain", action="store_true",
                    help="include the current web domain in --once output (stdout only)")
    a = ap.parse_args(argv)

    d = Daemon(write=not a.dry_run)
    if a.start:
        print(d.manual_start(dry_run=a.dry_run))
        return 0
    if a.status:
        p = os.path.join(STATUS_DIR, "status")
        try:
            if time.time() - os.path.getmtime(p) <= STATUS_FRESH_S:
                with open(p) as f:
                    print(f.read().strip())
                return 0
        except OSError:
            pass
        d.write = False
        print(d.tick(deliver=False)["status"])
        return 0
    if a.once:
        dec = d.tick(deliver=a.deliver and not a.dry_run)
        print(json.dumps(_printable(dec, a.show_domain), indent=2))
        return 0
    if a.dry_run:
        d.loop(deliver=False, echo=lambda dec: print(json.dumps(
            {k: dec[k] for k in ("trigger", "why", "decision", "gate", "category")}),
            flush=True))
        return 0
    d.loop(deliver=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
