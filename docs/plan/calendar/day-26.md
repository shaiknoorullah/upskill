# Day 26: A container from scratch, part 2: cgroups

- Course: Course 2, the depth month
- Why: You guessed right on CPU throttling but couldn't explain it. Today you'll measure it.
- Minimum version (low-energy day): Do only Lab part C: the throttling experiment.

## Block 1. jq on kubectl (Warm-up, 15 min, where: kind cluster)

- Requests and limits for every container:

  ```bash
  k get pods -A -o json | jq -r '.items[] | .metadata.name as $p | .spec.containers[] | $p + " " + (.resources | tostring)'
  ```

Done when: Query ran.

## Block 2. Read: CPU and PID controllers (Learn, 30 min, where: Browser)

- [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html): read the CPU section (cpu.max, cpu.stat) and the PID section (pids.max).

Done when: You can explain quota and period.

## Block 3. Lab: limits for your container, then measure throttling (Lab, 90 min, where: Ubuntu VM)

- A. Add cgroup v2 limits to your Go container, following the tutorial: pids.max = 20 and memory.max = 100M. Inside the container, run `for i in $(seq 50); do sleep 100 & done`. After about 20 processes you'll see 'Resource temporarily unavailable'. (30 min)
- B. Add a user namespace so root inside the container maps to your normal user outside. Check with `id` inside, and `ps -o user,pid,cmd` outside. (30 min)
- C. Measure CPU throttling (30 min):

  ```bash
  sudo systemd-run --unit=cpu20 -p CPUQuota=20% stress-ng --cpu 1 --timeout 60s
  sleep 20; cat /sys/fs/cgroup/system.slice/cpu20.service/cpu.max    # 20000 100000
  cat /sys/fs/cgroup/system.slice/cpu20.service/cpu.stat             # nr_throttled and throttled_usec
  docker run -d --name cpu02 --cpus 0.2 alpine sh -c 'while :; do :; done'
  sleep 20; cat /sys/fs/cgroup/system.slice/docker-$(docker inspect -f '{{.Id}}' cpu02).scope/cpu.stat
  docker rm -f cpu02
  ```
- Work it out: with a 100 ms period and a 20% quota, how long can the process run in each period before it's paused?

Done when: You watched nr_throttled climb and can explain quota and period with numbers.

## Block 4. Prove it (Prove it, 15 min, where: Phone and repo)

- Voice memo: explain CPU throttling with numbers, and why it hurts p99 latency even when average CPU is low.
- Write and push `cards/26-cgroups.md`.

Done when: One voice memo and one card.

## Block 5. CKA: series Day 35, etcd backup and restore (CKA, 120 min, where: Cluster VMs on the PC)

- Start the cluster: `incus start local:cp1 local:w1 local:w2`.
- Follow [Day 35](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day35) on your kubeadm cluster: take a snapshot, break something, restore it.
- Afterwards, list everything you'd need to rebuild the cluster from scratch, beyond the snapshot itself.
- When you're done: `incus stop local:cp1 local:w1 local:w2`.

Done when: The restore worked and your list is written.

## Block 6. Apply and follow up (Job hunt, 30 min, where: Laptop)

- Apply to 3 roles and log them.
- Follow up on any application older than 7 days.

Done when: 3 applications and follow-ups sent.
