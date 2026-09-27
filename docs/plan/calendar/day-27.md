# Day 27: systemd hardening and your scripts

- Course: Course 2, the depth month
- Why: systemd's sandboxing is the Linux-native version of Pod Security, and three clean scripts prove you can automate.
- Minimum version (low-energy day): Harden one unit and push one script.

## Block 1. Bash pitfalls (Warm-up, 15 min, where: Browser)

- Read pitfalls 16 to 20 on [Bash Pitfalls](https://mywiki.wooledge.org/BashPitfalls).

Done when: Five pitfalls read.

## Block 2. Read: systemd sandboxing (Learn, 30 min, where: Browser)

- [systemd.exec](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html): read the 'Sandboxing' section: ProtectSystem, ProtectHome, PrivateTmp, NoNewPrivileges and CapabilityBoundingSet.

Done when: You can name five sandboxing options.

## Block 3. Lab: harden a service, then write three scripts (Lab, 90 min, where: Ubuntu VM)

- A. Score a service (10 min):

  ```bash
  sudo tee /etc/systemd/system/web.service >/dev/null <<'EOF'
  [Service]
  ExecStart=/usr/bin/python3 -m http.server 8090 --directory /srv
  EOF
  sudo systemctl daemon-reload && sudo systemctl start web
  systemd-analyze security web | tail -1          # the exposure score, probably UNSAFE
  ```
- B. Harden it one option at a time (30 min). With `sudo systemctl edit web`, add each option below, restart, check the site still works (`curl -s localhost:8090 | head -3`), and rerun the score: NoNewPrivileges=yes, ProtectSystem=strict, ProtectHome=yes, PrivateTmp=yes, CapabilityBoundingSet=, RestrictAddressFamilies=AF_INET AF_INET6, DynamicUser=yes, MemoryMax=200M, CPUQuota=50%.
- Check the cgroup file your MemoryMax set: `cat /sys/fs/cgroup/system.slice/web.service/memory.max`.
- C. Scripting capstone (50 min). In a new repo called `ops-scripts`, write these three scripts:
- `logtop.sh`: the top 10 client IPs and status codes from an nginx access log, using awk, sort and uniq.
- `healthcheck.sh URL`: curl with 3 retries and backoff, `set -euo pipefail`, a trap that cleans up temp files, and exit code 0 or 1.
- `node-prep.sh`: idempotent Kubernetes node prep. Load overlay and br_netfilter, set the three required sysctls, and turn swap off, checking each before changing it.
- Run `shellcheck` on each until it's clean, then push. Afterwards, stop the demo service: `sudo systemctl stop web`.

Done when: The exposure score dropped and three clean scripts are pushed.

## Block 4. Prove it (Prove it, 15 min, where: Phone)

- Voice memo: name five systemd sandboxing options and what each one blocks.

Done when: One voice memo.

## Block 5. CKA: series Days 36–37 (CKA, 120 min, where: YouTube and clusters)

- Watch Days 36–37: monitoring and logging, and troubleshooting application failures. Do the tasks for [Day 36](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day36) and [Day 37](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day37).

Done when: Both tasks done.

## Block 6. Post and apply (Job hunt, 30 min, where: Laptop)

- Publish LinkedIn post #3: 'I wrote a tiny container runtime in Go', with a link to your repo.
- Apply to 2 roles and log them.

Done when: Post published and 2 applications logged.
