# Desktop integration snippets (apply later, via the dots repo)

These files are **not installed by anything in this repo**. Apply them through
the chezmoi dots repo **after the dotfiles cutover is finished**. Until then,
the drift detector can still be run by hand (`drift/nudged.py --once --dry-run`).

| File | chezmoi target | What it does |
|---|---|---|
| `upskill-nudged.service` | `dot_config/systemd/user/upskill-nudged.service` | systemd user unit that runs `~/upskill/drift/nudged.py` (polls every 20 s, `Restart=on-failure`, localhost only). Enable with `systemctl --user enable --now upskill-nudged` once applied. |
| `mako-upskill.conf` | append to `dot_config/mako/config` | `[app-name=upskill]` rule: 25 s timeout, one visible at a time, `layer=top` (never over fullscreen), mouse buttons mapped to Start / Done today / Not now. |
| `waybar-upskill.jsonc` | merge into `dot_config/waybar/config.jsonc` | `custom/upskill` module: reads `~/.cache/upskill/status.json` every 30 s; click runs `nudged.py --start`, which opens or jumps to the tmux `upskill` window. Add `"custom/upskill"` to a modules array. |
| `waybar-upskill.css` | append to `dot_config/waybar/style.css` | Styles for the module's classes (`ready`, `busy`, `snoozed`, `done`, `unknown`, `off`). |
| `tmux-upskill.conf` | `dot_config/tmux/upskill.conf` plus `source-file -q ~/.config/tmux/upskill.conf` in tmux.conf | Status-right segment from `~/.cache/upskill/status`, and **prefix + U** to open the `upskill` window with `KUBECONFIG=$HOME/upskill/local/kube/practice.yaml` and `TUTOR=1`. |

## Personal or work?

This machine is org-managed (the chezmoi `orgManaged` flag is true). Decide
where these belong before applying:

- **personal** profile: the default choice. The detector is a personal
  learning aid; keep it out of anything the org profile pushes.
- **work / orgManaged** profile: only if you want it on the managed laptop.
  Then wrap the files in `{{ if .orgManaged }}` (or the inverse) templates so
  that one profile does not silently enable it on the other.

Either way:

- **Disclose any new software to the IT inventory.** The daemon itself is a
  stdlib Python script with no new packages, but it depends on ActivityWatch
  (aw-server-rust, awatcher, the browser web watcher) reading window and
  browser activity. If any of those are not already in the inventory, list
  them before enabling the unit.
- Nothing here sends data off the machine. ActivityWatch is read with GET
  requests on localhost only; titles and URLs are reduced to a category in
  memory and never written to disk.

## Before enabling

1. Create `~/upskill/local/drift-rules.json` with your real work domains
   (start from `drift/drift-rules.example.json`). It is gitignored; never
   commit employer or internal domains.
2. Create the practice kubeconfig at `~/upskill/local/kube/practice.yaml`
   (for example from a kind cluster). If it does not exist, `kubectl` in the
   upskill window simply has no cluster, which fails closed.
3. Check that your shell rc files do not unconditionally re-export
   `KUBECONFIG`. If they do, any shell started inside the upskill window
   (including Claude's Bash tool, which snapshots your rc) points back at the
   work cluster. Guard it, e.g. `[ -n "$TUTOR" ] || export KUBECONFIG=...`.
4. Run `python3 ~/upskill/drift/nudged.py --once --dry-run` and check the
   decision looks sane.
5. Test the mako actions once by hand:
   `python3 ~/upskill/drift/nudged.py --once --deliver` while a trigger is
   active (or temporarily lower the thresholds in `local/drift-config.json`).
