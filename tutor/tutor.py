#!/usr/bin/env python3
"""upskill tutor engine: one CLI that Claude (and you) call for all state changes.

Progress is an append-only event log (state/events.jsonl, merge=union in git) so the
home PC and the work PC can both practise and sync through git without conflicts.
Content (what to practise) lives in tracks/<track>/items.json.

Usage: tutor.py <command> [args]   (run `tutor.py -h`)
"""
import argparse
import json
import os
import re

import subprocess
import sys
from datetime import datetime, timedelta, date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsrs  # noqa: E402

ROOT = Path(os.environ.get("UPSKILL_HOME", Path(__file__).resolve().parent.parent))
STATE = ROOT / "state"
EVENTS = STATE / "events.jsonl"
TRACKS = ROOT / "tracks"
LEVELS = ["assessed", "practised", "demonstrated", "exam-ready"]
STEPS = ["predict", "attempt", "debrief", "explain", "draw", "exit"]


def now():
    override = os.environ.get("UPSKILL_NOW")
    return datetime.fromisoformat(override) if override else datetime.now().astimezone().replace(microsecond=0)


# ---------- storage ----------

def load_events():
    if not EVENTS.exists():
        return []
    out = []
    for line in EVENTS.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass  # a half-merged line must never break a session
    out.sort(key=lambda e: e.get("ts", ""))
    return out


def site():
    """'work' / 'home' label from local/site (gitignored); never the real hostname (public repo)."""
    f = ROOT / "local" / "site"
    return f.read_text().strip() if f.exists() else "unknown"


def emit(event):
    STATE.mkdir(parents=True, exist_ok=True)
    event = {"ts": now().isoformat(), "site": site(), **event}
    with EVENTS.open("a") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event


def load_catalog():
    items, order = {}, []
    for f in sorted(TRACKS.glob("*/items.json")):
        data = json.loads(f.read_text())
        for it in data.get("items", []):
            it.setdefault("track", f.parent.name)
            items[it["id"]] = it
            order.append(it["id"])
    return items, order


def track_priority():
    idx = TRACKS / "index.json"
    if idx.exists():
        return json.loads(idx.read_text()).get("order", [])
    return sorted(p.name for p in TRACKS.iterdir() if p.is_dir()) if TRACKS.exists() else []


# ---------- derived state ----------

def derive(events=None):
    events = load_events() if events is None else events
    cards, attempts, ledger, days = {}, {}, {}, set()
    checkpoint, focus = None, None
    for e in events:
        t = e.get("type")
        ts = datetime.fromisoformat(e["ts"])
        if t == "rate":
            cards[e["item"]] = fsrs.review(cards.get(e["item"], {}), e["rating"], ts)
            days.add(ts.date().isoformat())
        elif t == "attempt":
            attempts.setdefault(e["item"], []).append(e)
            days.add(ts.date().isoformat())
        elif t == "checkpoint":
            checkpoint = None if e.get("clear") else e
        elif t == "ledger":
            ledger[e["concept"]] = {"level": e["level"], "evidence": e.get("evidence", ""), "ts": e["ts"]}
        elif t == "focus":
            focus = e.get("track")
    return {"cards": cards, "attempts": attempts, "ledger": ledger, "days": days,
            "checkpoint": checkpoint, "focus": focus}


def due_items(st, catalog, at=None):
    at = at or now()
    due = [(c["due"], i) for i, c in st["cards"].items()
           if i in catalog and datetime.fromisoformat(c["due"]) <= at]
    return [i for _, i in sorted(due)]


def new_items(st, catalog, order):
    seen = set(st["cards"]) | set(st["attempts"])
    prio = track_priority()
    if st["focus"]:
        prio = [st["focus"]] + [p for p in prio if p != st["focus"]]
    rank = {t: n for n, t in enumerate(prio)}
    fresh = [i for i in order if i not in seen and _prereqs_met(catalog[i], st, catalog)]
    return sorted(fresh, key=lambda i: (rank.get(catalog[i]["track"], 99),
                                        -catalog[i].get("priority", 0), order.index(i)))


def _prereqs_met(item, st, catalog):
    return all(p in st["cards"] for p in item.get("prereqs", []) if p in catalog)


def streak(days, today=None):
    today = today or now().date()
    d = today if today.isoformat() in days else today - timedelta(days=1)
    n = 0
    while d.isoformat() in days:
        n += 1
        d -= timedelta(days=1)
    week = sum(1 for k in range(7) if (today - timedelta(days=k)).isoformat() in days)
    return n, week


def pick_next(st, catalog, order):
    if st["checkpoint"] and st["checkpoint"]["item"] in catalog:
        return st["checkpoint"]["item"], "resume"
    due = due_items(st, catalog)
    if due:
        return due[0], "review"
    fresh = new_items(st, catalog, order)
    if fresh:
        return fresh[0], "new"
    return None, "empty"


# ---------- checks ----------

def run_check(item, cmd):
    chk = item.get("check", {})
    kind = chk.get("type", "manual")
    if kind == "regex":
        script = TRACKS / item["track"] / chk.get("script", "check.sh")
        r = subprocess.run([str(script), str(chk["n"]), cmd], capture_output=True, text=True, timeout=60)
        out = (r.stdout + r.stderr).strip()
        return ("✅" in out), out
    if kind == "script":
        script = TRACKS / item["track"] / chk["path"]
        r = subprocess.run([str(script), cmd], capture_output=True, text=True, timeout=120)
        return r.returncode == 0, (r.stdout + r.stderr).strip()
    return None, "manual item: Claude grades it in the debrief (no automatic checker)"


# ---------- commands ----------

def cmd_status(a):
    catalog, order = load_catalog()
    st = derive()
    n_due = len(due_items(st, catalog))
    s, week = streak(st["days"])
    nxt, why = pick_next(st, catalog, order)
    parts = ["upskill", f"{n_due} due"]
    if s:
        parts.append(f"{s}d streak")
    parts.append(f"{week}/7 wk")
    if nxt:
        parts.append(("⏸ " if why == "resume" else "▶ ") + nxt)
    line = " · ".join(parts)
    if a.json:
        print(json.dumps({"due": n_due, "streak": s, "week": week, "next": nxt, "why": why, "text": line}))
    else:
        print(line)


def cmd_next(a):
    catalog, order = load_catalog()
    st = derive()
    item_id, why = pick_next(st, catalog, order)
    if not item_id:
        print(json.dumps({"why": "empty", "message": "nothing due and no new items: run forge"}))
        return
    out = {"why": why, "item": catalog[item_id], "card": st["cards"].get(item_id),
           "attempts": st["attempts"].get(item_id, [])[-5:], "checkpoint": st["checkpoint"]}
    print(json.dumps(out, indent=2, ensure_ascii=False))


def cmd_due(a):
    catalog, _ = load_catalog()
    st = derive()
    for i in due_items(st, catalog):
        print(f"{i}\t{st['cards'][i]['due']}\t{catalog[i].get('title', '')}")


def cmd_show(a):
    catalog, _ = load_catalog()
    st = derive()
    if a.item not in catalog:
        sys.exit(f"unknown item {a.item}")
    print(json.dumps({"item": catalog[a.item], "card": st["cards"].get(a.item),
                      "attempts": st["attempts"].get(a.item, []),
                      "ledger": st["ledger"].get(catalog[a.item].get("concept"))}, indent=2, ensure_ascii=False))


def cmd_check(a):
    catalog, _ = load_catalog()
    if a.item not in catalog:
        sys.exit(f"unknown item {a.item}")
    ok, out = run_check(catalog[a.item], a.cmd)
    result = "pass" if ok else ("fail" if ok is False else "manual")
    emit({"type": "attempt", "item": a.item, "cmd": a.cmd, "result": result,
          "why": a.why or "", "prediction": a.predict or "", "confidence": a.confidence,
          "hints": a.hints})
    print(out)
    sys.exit(0 if ok or ok is None else 1)


def cmd_attempt(a):
    emit({"type": "attempt", "item": a.item, "cmd": a.cmd or "", "result": a.result,
          "why": a.why or "", "prediction": a.predict or "", "confidence": a.confidence, "hints": a.hints})
    print("logged")


def cmd_rate(a):
    catalog, _ = load_catalog()
    if a.item not in catalog:
        sys.exit(f"unknown item {a.item}")
    emit({"type": "rate", "item": a.item, "rating": a.rating})
    card = derive()["cards"][a.item]
    print(f"{a.item}: {a.rating} → next review {card['due'][:16]} (stability {card['s']}d)")


def cmd_checkpoint(a):
    if a.action == "get":
        print(json.dumps(derive()["checkpoint"], ensure_ascii=False))
    elif a.action == "clear":
        emit({"type": "checkpoint", "clear": True})
        print("cleared")
    else:
        if not a.item or a.step not in STEPS:
            sys.exit(f"set needs --item and --step in {STEPS}")
        emit({"type": "checkpoint", "item": a.item, "step": a.step, "note": a.note or ""})
        print("saved")


def cmd_ledger(a):
    if a.level:
        if a.level not in LEVELS:
            sys.exit(f"level must be one of {LEVELS}")
        if a.level in LEVELS[2:] and not a.evidence:
            sys.exit("demonstrated/exam-ready need --evidence (date + what was shown)")
        emit({"type": "ledger", "concept": a.concept, "level": a.level, "evidence": a.evidence or ""})
    print(json.dumps(derive()["ledger"].get(a.concept), ensure_ascii=False))


def cmd_focus(a):
    emit({"type": "focus", "track": a.track})
    print(f"focus → {a.track}")


def cmd_map(a):
    catalog, order = load_catalog()
    st = derive()
    by_track = {}
    for i in order:
        it = catalog[i]
        if a.track and it["track"] != a.track:
            continue
        by_track.setdefault(it["track"], {}).setdefault(it.get("concept", "-"), []).append(i)
    for track, concepts in by_track.items():
        print(f"## {track}")
        for concept, ids in concepts.items():
            led = st["ledger"].get(concept, {}).get("level", "")
            solid = sum(1 for i in ids if st["cards"].get(i, {}).get("s", 0) >= 21)
            seen = sum(1 for i in ids if i in st["cards"] or i in st["attempts"])
            bar = "★" * solid + "☆" * (seen - solid) + "·" * (len(ids) - seen)
            print(f"  {concept:<28} {bar:<12} {led}")


def cmd_list(a):
    catalog, order = load_catalog()
    for i in order:
        if not a.track or catalog[i]["track"] == a.track:
            print(f"{i}\t{catalog[i].get('kind', '')}\t{catalog[i].get('title', '')}")


MISS_ROW = re.compile(r"^\|\s*([A-Z]+-\d+)\s*\|(.+)\|\s*$")


def cmd_import_misses(a):
    """Turn progress/misses.md rows into review items (track `interview`)."""
    src = Path(a.path)
    items = []
    for line in src.read_text().splitlines():
        m = MISS_ROW.match(line)
        if not m:
            continue
        cols = [c.strip() for c in m.group(2).split("|")]
        topic, level, mtype, picked, covered = (cols + [""] * 6)[:5]
        prio = {"confident miss": 3, "wrong guess": 2, "didn't know": 1}.get(mtype, 0)
        items.append({"id": f"interview/{m.group(1)}", "concept": m.group(1).split("-")[0].lower(),
                      "kind": "miss", "title": topic, "level": level, "miss_type": mtype,
                      "picked_before": picked, "covered_on": covered, "priority": prio,
                      "check": {"type": "manual"}, "minutes": 3})
    out = TRACKS / "interview" / "items.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"track": "interview", "source": str(a.path), "items": items},
                              indent=1, ensure_ascii=False) + "\n")
    print(f"imported {len(items)} misses → {out.relative_to(ROOT)}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="tutor", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status"); s.add_argument("--json", action="store_true"); s.set_defaults(f=cmd_status)
    sub.add_parser("next").set_defaults(f=cmd_next)
    sub.add_parser("due").set_defaults(f=cmd_due)
    s = sub.add_parser("show"); s.add_argument("item"); s.set_defaults(f=cmd_show)
    for name, fn in (("check", cmd_check), ("attempt", cmd_attempt)):
        s = sub.add_parser(name)
        s.add_argument("item")
        s.add_argument("cmd", nargs="?" if name == "attempt" else None)
        if name == "attempt":
            s.add_argument("--result", required=True, choices=["pass", "fail", "partial", "gave-up"])
        s.add_argument("--why"); s.add_argument("--predict")
        s.add_argument("--confidence", type=int, choices=range(1, 6))
        s.add_argument("--hints", type=int, default=0)
        s.set_defaults(f=fn)
    s = sub.add_parser("rate"); s.add_argument("item"); s.add_argument("rating", choices=list(fsrs.RATINGS)); s.set_defaults(f=cmd_rate)
    s = sub.add_parser("checkpoint"); s.add_argument("action", choices=["get", "set", "clear"])
    s.add_argument("--item"); s.add_argument("--step"); s.add_argument("--note"); s.set_defaults(f=cmd_checkpoint)
    s = sub.add_parser("ledger"); s.add_argument("concept"); s.add_argument("--level"); s.add_argument("--evidence"); s.set_defaults(f=cmd_ledger)
    s = sub.add_parser("focus"); s.add_argument("track"); s.set_defaults(f=cmd_focus)
    s = sub.add_parser("map"); s.add_argument("--track"); s.set_defaults(f=cmd_map)
    s = sub.add_parser("list"); s.add_argument("--track"); s.set_defaults(f=cmd_list)
    s = sub.add_parser("import-misses"); s.add_argument("path"); s.set_defaults(f=cmd_import_misses)
    a = p.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    main()
