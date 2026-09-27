# Day 9: Memory pressure: PSI, memory.high, memory.max

- Course: Course 2, the depth month
- Why: memory.high and pressure stall information are how modern kernels and Kubernetes reason about memory, and interviewers love the difference between throttling and killing.
- Minimum version (low-energy day): Do only Lab part B: memory.high vs memory.max.

## Block 1. jq on kubectl (Warm-up, 15 min, where: kind cluster)

- Run each one, then change one detail and run it again:

  ```bash
  k get pods -A -o json | jq -r '.items[] | .metadata.namespace + "/" + .metadata.name'
  k get pods -A -o json | jq -r '.items[].spec.containers[].image' | sort -u
  k get pods -A -o json | jq -r '.items[] | select(.status.phase != "Running") | .metadata.name'
  ```

Done when: Three queries ran and you modified one yourself.

## Block 2. Read: pressure stall information (Learn, 30 min, where: Browser)

- [PSI docs](https://docs.kernel.org/accounting/psi.html) on kernel.org. (15 min)
- [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html): reread memory.high vs memory.max, then read memory.pressure. (15 min)

Done when: You can say what 'some' and 'full' mean in PSI.

## Block 3. Lab: where memory goes and how limits bite (Lab, 90 min, where: Ubuntu VM)

- A. Where memory really goes (25 min):

  ```bash
  dd if=/dev/urandom of=~/big.img bs=1M count=512
  fincore ~/big.img                 # how much of the file is in the page cache
  cat ~/big.img > /dev/null; fincore ~/big.img
  sudo grep -E 'Rss|Pss' /proc/$(pgrep -n containerd)/smaps_rollup
  sudo pmap -x $(pgrep -n containerd) | tail -3
  rm ~/big.img
  ```
- B. memory.high throttles (20 min). Start a job just over its soft limit:

  ```bash
  sudo systemd-run --unit=memhigh -p MemoryHigh=200M -p MemoryMax=300M -p MemorySwapMax=0 \
    stress-ng --vm 1 --vm-bytes 250M --vm-keep --timeout 60s
  watch -n1 cat /sys/fs/cgroup/system.slice/memhigh.service/memory.events /sys/fs/cgroup/system.slice/memhigh.service/memory.pressure
  ```
- The 'high' counter climbs and pressure rises, but nothing gets killed. Let it finish (60 seconds), then Ctrl-C.
- C. memory.max kills (20 min). Now go over the hard limit:

  ```bash
  sudo systemd-run --unit=memmax -p MemoryHigh=200M -p MemoryMax=300M -p MemorySwapMax=0 \
    stress-ng --vm 1 --vm-bytes 350M --vm-keep --timeout 60s
  watch -n1 cat /sys/fs/cgroup/system.slice/memmax.service/memory.events
  ```
- Watch oom_kill go up. stress-ng restarts its worker every time the kernel kills it. Afterwards, look at `sudo dmesg -T | grep -i oom | tail -3`.
- D. Swap facts (15 min):

  ```bash
  swapon --show
  cat /proc/sys/vm/swappiness
  cat /proc/pressure/memory
  ```

Done when: You saw memory.high throttle without killing, and memory.max kill.

## Block 4. Prove it (Prove it, 15 min, where: Phone and repo)

- Voice memo: memory.high vs memory.max, and which one a Kubernetes memory limit sets. (A limit sets memory.max.)
- Write and push `cards/09-memory-pressure.md`.

Done when: One voice memo and one card.

## Block 5. CKA: series Days 7–10 (CKA, 120 min, where: YouTube and kind cluster)

- Watch Days 7–10 at 1.5x: Pods, ReplicaSets and Deployments, Services, Namespaces.
- Do the tasks for [Day 8](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day08) and [Day 9](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day09) using only `k` and imperative commands like `k create deploy`, `k expose` and `$do`.
- Time yourself: each task under 5 minutes.

Done when: Both tasks done, each under 5 minutes.

## Block 6. Job sites and alerts (Job hunt, 30 min, where: Laptop)

- Update your [Naukri](https://www.naukri.com/) and [Instahyre](https://www.instahyre.com/) profiles with the new resume.
- Create job alerts for DevOps Engineer, Platform Engineer, Kubernetes and SRE, in Hyderabad and Remote.
- Add 5 target companies to your job tracker.

Done when: Alerts are on and 5 companies are in the tracker.
