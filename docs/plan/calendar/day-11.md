# Day 11: Disk I/O and durability

- Course: Course 2, the depth month
- Why: etcd lives or dies on fsync latency, and iowait is the other half of the load-average question you missed.
- Minimum version (low-energy day): Do only Lab part C: the etcd disk test.

## Block 1. The 60-second checklist from memory (Warm-up, 15 min, where: Ubuntu VM)

- Type all 10 triage commands from memory, then check them against your card.

Done when: All 10 from memory.

## Block 2. Read: the USE method and fio (Learn, 30 min, where: Browser)

- [The USE method](https://www.brendangregg.com/usemethod.html) by Brendan Gregg. (20 min)
- Skim [fio's documentation](https://fio.readthedocs.io/) for the rw, bs, iodepth and direct parameters. (10 min)

Done when: You can say what utilization, saturation and errors mean for a disk.

## Block 3. Lab: benchmark the disk and measure fsync (Lab, 90 min, where: Ubuntu VM)

- Keep `iostat -xz 1` running in a second terminal for the whole lab. Watch r/s, w/s, rkB/s, r_await, w_await and %util.
- A. Sequential vs random reads (35 min):

  ```bash
  fio --name=seq --rw=read --bs=1M --size=512M --direct=1 --filename=/tmp/fio.test
  fio --name=rand --rw=randread --bs=4k --size=512M --direct=1 --ioengine=libaio \
    --iodepth=16 --runtime=30 --time_based --filename=/tmp/fio.test
  ```
- Compare MB/s, IOPS and the latency percentiles. Write one sentence on why they're so different.
- B. What durability costs (20 min):

  ```bash
  dd if=/dev/zero of=/tmp/nosync bs=4k count=2000
  dd if=/dev/zero of=/tmp/sync bs=4k count=2000 oflag=dsync
  ```
- C. The etcd disk test (25 min):

  ```bash
  mkdir -p /tmp/etcdtest
  fio --rw=write --ioengine=sync --fdatasync=1 --directory=/tmp/etcdtest \
    --size=22m --bs=2300 --name=etcdtest
  ```
- In the output, find the fsync/fdatasync latency percentiles. etcd wants the 99th percentile under 10 ms. Does your VM's disk pass?
- D. Run `sudo iotop -o` while a fio job runs and see which process is doing the I/O. (10 min)
- Clean up:

  ```bash
  rm -rf /tmp/fio.test /tmp/nosync /tmp/sync /tmp/etcdtest
  ```

Done when: You know your disk's fdatasync p99 and whether etcd would be happy on it.

## Block 4. Prove it (Prove it, 15 min, where: Phone and repo)

- Voice memo: IOPS vs throughput vs latency, and which one etcd cares about most.
- Write and push `cards/11-disk-io.md`.

Done when: One voice memo and one card.

## Block 5. CKA: series Days 14–16 (CKA, 120 min, where: YouTube and kind cluster)

- Watch Days 14–16: taints and tolerations, node affinity, requests and limits.
- Do the tasks for [Day 14](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day14), [Day 15](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day15) and [Day 16](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day16).
- Connect Day 16 to Day 9 of this calendar: which cgroup file does a memory limit set, and which one does a CPU limit set?

Done when: All three tasks done, and you can name the cgroup files.

## Block 6. Apply and ask for a referral (Job hunt, 30 min, where: Laptop)

- Apply to 3 roles and log them.
- Send one referral message to a former colleague or friend at a target company. Four lines: who you are, the role, one proof point, the ask.

Done when: 3 applications and 1 referral message sent.
