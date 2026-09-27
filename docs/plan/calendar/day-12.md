# Day 12: perf, flame graphs and eBPF tools

- Course: Course 2, the depth month
- Why: Finding what's burning CPU in two minutes is a senior signal, and it's how you'll explain CPU throttling later in the month.
- Minimum version (low-energy day): Do only `perf top` and one flame graph.

## Block 1. Bash pitfalls (Warm-up, 15 min, where: Ubuntu VM)

- Read pitfalls 11 to 15 on [Bash Pitfalls](https://mywiki.wooledge.org/BashPitfalls) and reproduce one of them in the terminal.

Done when: One pitfall reproduced.

## Block 2. Read: perf and flame graphs (Learn, 30 min, where: Browser)

- [perf examples](https://www.brendangregg.com/perf.html): read the intro and the one-liners. (15 min)
- [Flame graphs](https://www.brendangregg.com/flamegraphs.html): read how to read one. (15 min)

Done when: You know what the width of a flame graph box means.

## Block 3. Lab: find the hot code (Lab, 90 min, where: Ubuntu VM)

- A. Find the hot code (30 min):

  ```bash
  stress-ng --cpu 1 --cpu-method matrixprod --timeout 120s &
  sudo perf top                          # q to quit
  sudo perf record -F 99 -a -g -- sleep 20
  sudo perf report --stdio | head -40
  ```
- B. Your first flame graph (30 min):

  ```bash
  git clone https://github.com/brendangregg/FlameGraph ~/FlameGraph
  sudo perf script | ~/FlameGraph/stackcollapse-perf.pl | ~/FlameGraph/flamegraph.pl > ~/cpu.svg
  ```
- On the PC, pull the file out of the VM with `incus file pull lab-ubuntu/home/me/cpu.svg ~/` and open it in a browser. Click into the widest tower.
- C. eBPF tools (30 min). Run each, and trigger it from another terminal:

  ```bash
  sudo execsnoop-bpfcc             # every new process
  sudo opensnoop-bpfcc -T          # every file open
  sudo biolatency-bpfcc 5 1        # run yesterday's fio in another terminal
  sudo tcpconnect-bpfcc            # every outbound TCP connection
  ```

Done when: You have cpu.svg and can say which function was hottest.

## Block 4. Prove it (Prove it, 15 min, where: Phone and repo)

- Voice memo: a box is at 100% CPU. What do you run in the first two minutes?
- Write and push `cards/12-perf.md`.

Done when: One voice memo and one card.

## Block 5. CKA: series Days 17–19 (CKA, 120 min, where: YouTube and kind cluster)

- Watch Days 17–19: autoscaling, probes, ConfigMaps and Secrets.
- Do the tasks for [Day 17](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day17), [Day 18](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day18) and [Day 19](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day19).
- After Day 18, write one sentence on why a liveness probe should never check the database. You missed this in the interview.

Done when: All three tasks done, plus your liveness sentence.

## Block 6. Apply and draft a post (Job hunt, 30 min, where: Laptop)

- Apply to 3 roles and log them.
- Draft LinkedIn post #1: 'I spent a week breaking Linux on purpose. Here are 5 things I learned.' Don't post it yet.

Done when: 3 applications and a draft.
