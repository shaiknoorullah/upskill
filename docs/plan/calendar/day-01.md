# Day 1: Processes and signals

- Course: Course 1, the 80/20 week
- Why: You missed signals, zombies and exit code 137 in the interview, and every pod shutdown in Kubernetes depends on them.
- Minimum version (low-energy day): Do only Lab part C (docker stop with and without --init), then write the card.

## Block 1. Shell drill: word splitting (Warm-up, 20 min, where: Ubuntu VM)

- Read pitfalls 1 to 5 on [Bash Pitfalls](https://mywiki.wooledge.org/BashPitfalls).
- Reproduce pitfall 1, the one you missed in the interview:

  ```bash
  mkdir -p ~/drill && cd ~/drill
  touch "a b.log" c.log
  for f in $(ls *.log); do echo "[$f]"; done   # wrong: prints 3 items
  for f in *.log; do echo "[$f]"; done         # right: prints 2 items
  ```

Done when: You can explain why the first loop printed three items.

## Block 2. Read: signals, zombies and PID 1 (Learn, 60 min, where: Browser)

- [signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html): read 'Signal dispositions' and the 'Standard signals' table. Note the two signals that can't be caught. (20 min)
- [Docker and the PID 1 zombie reaping problem](https://blog.phusion.nl/2015/01/20/docker-and-the-pid-1-zombie-reaping-problem/) by Phusion. (20 min)
- [Exit codes with special meanings](https://tldp.org/LDP/abs/html/exitcodes.html). (5 min)
- On the VM, run `man ps`, type `/PROCESS STATE` and press Enter. Read what R, S, D, Z and T mean. (15 min)

Done when: You can list six signals and name the two that can't be caught.

## Block 3. Lab: signals, zombies and PID 1 (Lab, 150 min, where: Ubuntu VM)

- A. Move a process through its states (35 min):

  ```bash
  sleep 1000 &
  PID=$!
  ps -o pid,ppid,stat,cmd -p $PID       # S = sleeping
  kill -STOP $PID; ps -o stat= -p $PID   # T = stopped
  kill -CONT $PID; ps -o stat= -p $PID
  kill -TERM $PID; wait $PID; echo "exit code: $?"   # 143 = 128 + 15 (SIGTERM)
  ```
- Write a script that handles signals, and run it:

  ```bash
  cat > ~/labs/trap.sh <<'EOF'
  #!/usr/bin/env bash
  trap 'echo "got TERM, cleaning up"; exit 0' TERM
  trap 'echo "ignoring Ctrl-C"' INT
  echo "PID $$"
  while true; do sleep 1; done
  EOF
  chmod +x ~/labs/trap.sh && ~/labs/trap.sh
  ```
- Press Ctrl-C: it's ignored. From a second terminal run `kill -TERM <pid>`: clean exit. Start it again and use `kill -KILL <pid>`: no cleanup message, because SIGKILL can't be trapped.
- B. Make a zombie on purpose (35 min):

  ```bash
  python3 -c 'import os, time
  if os.fork() == 0: os._exit(0)
  time.sleep(600)' &
  PARENT=$!
  sleep 1; ps -o pid,ppid,stat,cmd --ppid $PARENT    # Z = zombie (defunct)
  ```
- Try `kill -9 <zombie pid>`: nothing happens, because it's already dead. Now run `kill $PARENT` and check again: the zombie is gone, because PID 1 adopted and reaped it.
- C. PID 1 inside containers (50 min):

  ```bash
  docker run -d --name nosig ubuntu sleep 600
  time docker stop nosig                          # ~10 s: sleep is PID 1 and ignores SIGTERM
  docker inspect -f '{{.State.ExitCode}}' nosig    # 137 = 128 + 9 (SIGKILL)
  docker run -d --init --name withinit ubuntu sleep 600
  time docker stop withinit                       # fast: tini passes SIGTERM on
  docker inspect -f '{{.State.ExitCode}}' withinit # 143
  docker rm nosig withinit
  ```
- D. Exit codes (20 min). Predict each number before you press Enter:

  ```bash
  bash -c 'exit 3'; echo $?
  printf 'echo hi\n' > ~/labs/noexec.sh; ~/labs/noexec.sh; echo $?   # 126: not executable
  nosuchcommand; echo $?                                          # 127: not found
  sleep 100 & kill -9 $!; wait $!; echo $?                        # 137
  ```

Done when: You watched a process go through S, T and Z, and saw 137 vs 143 from docker stop.

## Block 4. Prove it (Prove it, 30 min, where: Phone and repo)

- Record a voice memo for each question below. Keep each answer under 60 seconds.
- What happens, signal by signal, when Kubernetes deletes a pod?
- What is a zombie, and how do you get rid of one?
- What do exit codes 137 and 143 mean?
- Why does a container's PID 1 need an init like tini?
- Write `cards/01-processes.md` with five headings: states, signals, zombies, PID 1, exit codes. Push it.

Done when: Four voice memos recorded and one card pushed.
