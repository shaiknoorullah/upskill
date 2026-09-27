# Day 2: Memory and the OOM killer

- Course: Course 1, the 80/20 week
- Why: You were confidently wrong on 'free vs available' and on how the OOM killer picks a victim. Both come up every time a pod gets OOMKilled.
- Minimum version (low-energy day): Do only Lab part B: OOM-kill a container and find the evidence.

## Block 1. Subnetting drill (Warm-up, 20 min, where: Browser)

- Do 10 problems at [subnettingpractice.com](https://subnettingpractice.com/). Write down your average time per problem.
- Memorize this table: /24 = 254 hosts, /25 = 126, /26 = 62, /27 = 30, /28 = 14, /29 = 6, /30 = 2.

Done when: 10 problems done and your average time noted.

## Block 2. Read: page cache, OOM killer, memory cgroups (Learn, 60 min, where: Browser)

- [linuxatemyram.com](https://www.linuxatemyram.com/). (5 min)
- [Node-pressure eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/): read 'Node out of memory behavior' and the oom_score_adj table for each QoS class. (20 min)
- [cgroup v2 docs](https://docs.kernel.org/admin-guide/cgroup-v2.html): find the 'Memory' section and read memory.current, memory.max and memory.events. (35 min)

Done when: You can explain what 'available' means and how kubelet ranks pods for the OOM killer.

## Block 3. Lab: page cache and OOM kills (Lab, 150 min, where: Ubuntu VM)

- A. Watch the page cache grow and drop (35 min):

  ```bash
  free -m                          # note buff/cache and available
  dd if=/dev/urandom of=~/big.img bs=1M count=1024
  free -m                          # buff/cache grew, available barely moved
  grep -E 'MemTotal|MemFree|MemAvailable|^Cached|Dirty' /proc/meminfo
  sudo sh -c 'sync; echo 1 > /proc/sys/vm/drop_caches'
  free -m                          # the cache is gone: it was never really 'used'
  ```
- B. OOM-kill a container (60 min). First, a memory hog:

  ```bash
  cat > ~/labs/hog.py <<'EOF'
  import time
  chunks = []
  while True:
      chunks.append(bytearray(10 * 1024 * 1024))
      time.sleep(0.2)
  EOF
  docker run -d --name hog -m 100m --memory-swap 100m -v ~/labs:/labs python:3-slim \
    sh -c "python3 /labs/hog.py; echo python died; sleep 600"
  sleep 10; docker logs hog
  ```
- Find the evidence in two places:

  ```bash
  sudo dmesg -T | grep -i -A3 'out of memory'
  CID=$(docker inspect -f '{{.Id}}' hog)
  cat /sys/fs/cgroup/system.slice/docker-$CID.scope/memory.max
  cat /sys/fs/cgroup/system.slice/docker-$CID.scope/memory.events    # look for oom_kill 1
  ```
- Now make python itself PID 1, so the whole container dies:

  ```bash
  docker run --name hog2 -m 100m --memory-swap 100m -v ~/labs:/labs python:3-slim python3 /labs/hog.py
  docker inspect -f '{{.State.OOMKilled}} {{.State.ExitCode}}' hog2    # true 137
  ```
- C. How the kernel picks a victim (35 min):

  ```bash
  ps -eo pid,comm,rss --sort=-rss | head -5
  cat /proc/<pid>/oom_score /proc/<pid>/oom_score_adj     # use a PID from the list
  sleep 3000 & echo 1000 | sudo tee /proc/$!/oom_score_adj
  cat /proc/$!/oom_score                                  # now it's first in line
  ```
- Match this to the Kubernetes table you read: Guaranteed pods get -997, BestEffort pods get 1000.
- D. Clean up (5 min):

  ```bash
  docker rm -f hog hog2; rm ~/big.img; kill %sleep
  ```

Done when: You saw oom_kill in memory.events and 'true 137' from docker inspect.

## Block 4. Prove it (Prove it, 30 min, where: Phone and repo)

- Voice memo: free says 200 MB free, but 40 GB available. Is that a problem?
- Voice memo: what happens when a pod goes over its memory limit, step by step?
- Voice memo: which process does the kernel kill first on a Kubernetes node, and why?
- Voice memo: what counts against a container's memory limit? Include heap, native memory, page cache and tmpfs.
- Write and push `cards/02-memory.md`.

Done when: Four voice memos recorded and one card pushed.
