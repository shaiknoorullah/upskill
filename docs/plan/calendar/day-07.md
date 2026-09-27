# Day 7: Triage, containers, checkpoint 1

- Course: Course 1, the 80/20 week
- Why: This day ties the week together: a repeatable 60-second triage, load average done right, and what a container really is.
- Minimum version (low-energy day): Do only the checkpoint with Claude.

## Block 1. Subnetting speed round (Warm-up, 20 min, where: Browser)

- Do 10 problems at [subnettingpractice.com](https://subnettingpractice.com/). Target: under 30 seconds each.

Done when: 10 problems at under 30 seconds each.

## Block 2. Read and watch: triage, load, containers (Learn, 75 min, where: Browser)

- [Linux Performance Analysis in 60,000 Milliseconds](https://www.brendangregg.com/Articles/Netflix_Linux_Perf_Analysis_60s.pdf) by Brendan Gregg. Memorize the 10 commands in order. (15 min)
- [Linux Load Averages: Solving the Mystery](https://www.brendangregg.com/blog/2017-08-08/linux-load-averages.html): read the intro, the part about uninterruptible tasks, and the conclusion. (20 min)
- [Containers From Scratch](https://www.youtube.com/watch?v=8fi7uSYlOdc), Liz Rice at GOTO 2018. Watch at 1.25x speed. (35 min)

Done when: You can recite the 10 triage commands in order.

## Block 3. Lab: triage drill, D-state, SadServers (Lab, 120 min, where: Ubuntu VM and browser)

- A. The 60-second drill (30 min). Put some load on the box in terminal 1:

  ```bash
  stress-ng --cpu 2 --io 2 --vm 1 --vm-bytes 512M --timeout 300s
  ```
- In terminal 2, run the checklist in order. Write one line per command about what it tells you:

  ```bash
  uptime
  sudo dmesg -T | tail
  vmstat 1 5
  mpstat -P ALL 1 3
  pidstat 1 3
  iostat -xz 1 3
  free -m
  sar -n DEV 1 3
  sar -n TCP,ETCP 1 3
  top -b -n 1 | head -20
  ```
- B. High load with idle CPUs (30 min). Build a deliberately slow disk and pile writes onto it:

  ```bash
  truncate -s 100M ~/slow.img
  LOOP=$(sudo losetup -f --show ~/slow.img)
  echo "0 $(sudo blockdev --getsz $LOOP) delay $LOOP 0 500" | sudo dmsetup create slow
  for i in 1 2 3 4; do sudo dd if=/dev/zero of=/dev/mapper/slow bs=4k count=60 oflag=direct 2>/dev/null & done
  sleep 5; ps -eo state,pid,cmd | grep '^D'
  uptime; mpstat 1 3             # load climbs while the CPUs sit idle
  ```
- When the dd jobs finish (about 30 seconds), clean up:

  ```bash
  wait; sudo dmsetup remove slow; sudo losetup -d $LOOP; rm ~/slow.img
  ```
- C. SadServers (40 min): solve 'Saint John', 'Saskatoon' and 'Santiago' at [sadservers.com](https://sadservers.com/scenarios), 12 minutes each. If you hit the time limit, read the hint.
- D. Peek at a container's kernel objects (20 min):

  ```bash
  sudo unshare --pid --fork --mount-proc bash -c 'ps aux'   # PID 1 is bash
  docker run -d --name peek nginx
  PID=$(docker inspect -f '{{.State.Pid}}' peek)
  sudo ls -l /proc/$PID/ns
  sudo nsenter -t $PID -n ip addr          # inside the container's network namespace
  cat /proc/$PID/cgroup
  docker rm -f peek
  ```

Done when: You saw D-state processes push the load up while the CPUs were idle.

## Block 4. Checkpoint 1 with Claude (Checkpoint, 30 min, where: Claude chat)

- Open a chat with Claude and send: checkpoint 1.
- Answer 20 rapid-fire questions from memory. No notes.
- Pass mark: 16 out of 20. Anything you miss becomes a warm-up next week.

Done when: Checkpoint done and your score written down.

## Block 5. Resume session (Job hunt, 45 min, where: Claude chat)

- Send Claude your current resume and say: resume day.
- Leave with a new headline, a 3-line summary and your bootstrap project rewritten as achievements.
- Save it as a PDF named `Firstname-Lastname-Platform-Engineer.pdf`.

Done when: A new resume PDF exists.
