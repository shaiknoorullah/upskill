# Day 8: strace and /proc

- Course: Course 2, the depth month
- Why: strace turns 'unknown error' into the exact file or syscall that failed. It's the closest thing Linux has to a universal debugger.
- Minimum version (low-energy day): Do only Lab steps 1 and 2: strace a program that fails with a useless message.

## Block 1. The 60-second checklist from memory (Warm-up, 15 min, where: Ubuntu VM)

- Type the 10 triage commands from Day 7 into the terminal from memory, without looking.
- Compare with your card and fix any you forgot or got out of order.

Done when: All 10 typed from memory.

## Block 2. Read: strace (Learn, 30 min, where: Browser)

- [The strace zine](https://wizardzines.com/zines/strace/) by Julia Evans (free). (15 min)
- On the VM, run `man strace` and read the options -f, -e, -p, -c, -T and -o. (15 min)

Done when: You know what -f, -e and -p do.

## Block 3. Lab: strace and /proc (Lab, 90 min, where: Ubuntu VM)

- 1. What does cat actually do?

  ```bash
  strace -f -e trace=openat,read,write -o /tmp/cat.trace cat /etc/hostname
  less /tmp/cat.trace
  strace -c ls /usr/bin > /dev/null       # a table of syscalls and how long each took
  ```
- 2. Debug an app with a useless error message:

  ```bash
  cat > ~/labs/app.py <<'EOF'
  import sys
  try:
      open("/etc/myapp/conf.yaml")
  except Exception:
      sys.exit("app failed: unknown error")
  EOF
  python3 ~/labs/app.py
  strace -f -e trace=openat -o /tmp/app.trace python3 ~/labs/app.py; grep myapp /tmp/app.trace
  ```
- 3. Attach to a running process, and time a network call:

  ```bash
  sleep 1000 &
  sudo strace -p $!                 # it's blocked in clock_nanosleep. Ctrl-C to detach
  strace -T -e trace=connect curl -s -o /dev/null https://example.com
  ```
- 4. Read a process's life story from /proc:

  ```bash
  P=$(pgrep -n sleep)
  grep -E 'State|PPid|Threads|VmRSS' /proc/$P/status
  ls -l /proc/$P/fd
  grep 'open files' /proc/$P/limits
  tr '\0' ' ' < /proc/$P/cmdline; echo
  ```
- 5. SadServers 'Oaxaca' at [sadservers.com](https://sadservers.com/scenarios). Timebox: 25 minutes.

Done when: strace pointed you straight at the missing /etc/myapp/conf.yaml.

## Block 4. Prove it (Prove it, 15 min, where: Phone and repo)

- Voice memo: an app fails with 'unknown error'. How do you find out why in two minutes?
- Write and push `cards/08-strace-proc.md`.

Done when: One voice memo and one card.

## Block 5. CKA: series Days 1–6 and a fast kubectl (CKA, 120 min, where: YouTube and Ubuntu VM)

- Open the [CKA 2025 playlist](https://www.youtube.com/playlist?list=PLl4APkPHzsUUOkOv3i62UidrLmSB8DcGC) and the [course repo](https://github.com/piyushsachdeva/CKA-2024).
- Watch Days 1–5 at 2x speed. You know most of this, so you're only looking for gaps and the exam angle. (75 min)
- Watch Day 6 and create your kind cluster on lab-ubuntu, following [Day 6's notes](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day06). (30 min)
- Set up kubectl for speed. You'll use this every day:

  ```bash
  echo 'alias k=kubectl' >> ~/.bashrc
  echo 'source <(kubectl completion bash)' >> ~/.bashrc
  echo 'complete -o default -F __start_kubectl k' >> ~/.bashrc
  echo 'export do="--dry-run=client -o yaml"' >> ~/.bashrc
  printf 'set ts=2 sw=2 et\n' >> ~/.vimrc
  source ~/.bashrc && k get nodes
  ```

Done when: `k get nodes` shows your kind cluster.

## Block 6. LinkedIn profile (Job hunt, 30 min, where: Laptop)

- Set your headline to: Platform Engineer | Kubernetes, GitOps (ArgoCD), Terraform | Bare-metal Proxmox and Talos.
- Paste the 3-line summary from your resume session into About.
- Turn on Open to Work, visible to recruiters only.
- Add your bootstrap project to Featured, as a repo link or a short write-up.

Done when: Profile updated.
