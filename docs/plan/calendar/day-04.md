# Day 4: systemd, logs and limits

- Course: Course 1, the 80/20 week
- Why: Restart= and LimitNOFILE were two of your confident misses, and they're exactly what SadServers' 'Cape Town' tests.
- Minimum version (low-energy day): Do only Lab part B: too many open files, fixed with a drop-in.

## Block 1. Subnetting drill (Warm-up, 20 min, where: Browser)

- Do 10 problems at [subnettingpractice.com](https://subnettingpractice.com/). Try to beat yesterday's average time.
- Without looking: how many usable hosts are in a /27? (Answer: 30.)

Done when: 10 problems done, faster than Day 2.

## Block 2. Read: units, restarts, limits, the journal (Learn, 60 min, where: Browser)

- [systemd](https://wiki.archlinux.org/title/Systemd) (Arch Wiki): read 'Using units', 'Writing unit files' and 'Drop-in files'. (25 min)
- [systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html): find `Restart=` and study the table of which exits cause a restart. (15 min)
- [systemd.exec](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html): find `LimitNOFILE=` and the table that maps Limit* settings to ulimit. (10 min)
- [systemd/Journal](https://wiki.archlinux.org/title/Systemd/Journal) (Arch Wiki): read 'Filtering output'. (10 min)

Done when: You can say which exits Restart=on-failure restarts.

## Block 3. Lab: a flaky service, an fd hog, a timer (Lab, 150 min, where: Ubuntu VM)

- A. A flaky service (45 min):

  ```bash
  sudo tee /usr/local/bin/flaky.sh >/dev/null <<'EOF'
  #!/usr/bin/env bash
  echo "flaky started"
  sleep 5
  code=$(( RANDOM % 3 ))
  echo "exiting with $code"
  exit $code
  EOF
  sudo chmod +x /usr/local/bin/flaky.sh
  sudo tee /etc/systemd/system/flaky.service >/dev/null <<'EOF'
  [Unit]
  Description=Flaky demo
  [Service]
  ExecStart=/usr/local/bin/flaky.sh
  Restart=on-failure
  RestartSec=2
  EOF
  sudo systemctl daemon-reload && sudo systemctl start flaky
  journalctl -u flaky -f
  ```
- Watch for a few minutes: exits 1 and 2 restart it, exit 0 stops it. Press Ctrl-C to stop watching.
- Run `sudo systemctl edit flaky`. Between the comment lines, add `[Service]` and `Restart=always`, save, then `sudo systemctl restart flaky`. Now even exit 0 restarts.
- Change it to `Restart=on-abnormal`. Exits 1 and 2 no longer restart. Test with a signal: `sudo systemctl kill -s SIGKILL flaky`. That does restart.
- B. Too many open files (50 min):

  ```bash
  sudo tee /usr/local/bin/fdhog.py >/dev/null <<'EOF'
  import time
  files = [open("/dev/null") for _ in range(2000)]
  print("opened", len(files), flush=True)
  time.sleep(3600)
  EOF
  sudo tee /etc/systemd/system/fdhog.service >/dev/null <<'EOF'
  [Service]
  ExecStart=/usr/bin/python3 /usr/local/bin/fdhog.py
  LimitNOFILE=1024
  EOF
  sudo systemctl daemon-reload && sudo systemctl start fdhog
  journalctl -u fdhog -n 20        # OSError: [Errno 24] Too many open files
  ```
- Prove your shell doesn't matter: run `ulimit -n` in your shell, then `sudo systemctl restart fdhog`. It still fails.
- Fix it the right way:

  ```bash
  sudo systemctl edit fdhog        # add [Service] and LimitNOFILE=4096
  sudo systemctl restart fdhog
  grep 'open files' /proc/$(systemctl show -p MainPID --value fdhog)/limits
  ```
- C. Journal fluency (30 min):

  ```bash
  journalctl -b -p err              # errors since boot
  journalctl -u ssh --since "1 hour ago"
  journalctl -k | tail               # kernel messages
  journalctl --disk-usage
  systemd-analyze blame | head
  systemd-analyze critical-chain
  ```
- D. A timer instead of cron (20 min):

  ```bash
  sudo tee /etc/systemd/system/hello.service >/dev/null <<'EOF'
  [Service]
  Type=oneshot
  ExecStart=/usr/bin/logger -t hello "hello from a timer"
  EOF
  sudo tee /etc/systemd/system/hello.timer >/dev/null <<'EOF'
  [Timer]
  OnCalendar=*:0/2
  Persistent=true
  [Install]
  WantedBy=timers.target
  EOF
  sudo systemctl daemon-reload && sudo systemctl enable --now hello.timer
  systemctl list-timers | grep hello
  sleep 150; journalctl -t hello
  ```
- Clean up (5 min):

  ```bash
  sudo systemctl stop flaky fdhog
  sudo systemctl disable --now hello.timer
  ```

Done when: fdhog runs with 4096 open files allowed, and you can say what each Restart= value does.

## Block 4. Prove it (Prove it, 30 min, where: Phone and repo)

- Voice memo: a service must restart when it crashes but not after a clean exit. Which setting, and why not 'always'?
- Voice memo: why doesn't `ulimit -n` in your shell fix a service?
- Voice memo: a service won't start. What are your first three commands?
- Voice memo: where do the limits in /etc/security/limits.conf apply, and where don't they?
- Write and push `cards/04-systemd.md`.

Done when: Four voice memos recorded and one card pushed.
