# Day 25: A container from scratch in Go, part 1

- Course: Course 2, the depth month
- Why: Writing a container runtime yourself is the fastest way to never forget namespaces again, and it's a strong portfolio piece.
- Minimum version (low-energy day): Get to a shell with its own hostname (the UTS namespace).

## Block 1. The 60-second checklist from memory (Warm-up, 15 min, where: Ubuntu VM)

- Type all 10 triage commands from memory, then check them against your card.

Done when: All 10 from memory.

## Block 2. Watch and read: containers from scratch (Learn, 30 min, where: Browser)

- Rewatch the first 20 minutes of [Containers From Scratch](https://www.youtube.com/watch?v=8fi7uSYlOdc).
- Read the introduction of the [iximiuz code-along](https://labs.iximiuz.com/tutorials/build-a-container-from-scratch-in-go-1b92e418).

Done when: You know what the first three steps of the code-along are.

## Block 3. Lab: namespaces in Go (Lab, 90 min, where: iximiuz playground or Ubuntu VM)

- Follow the iximiuz tutorial in its own playground, or on lab-ubuntu (Go is already installed). Build it up step by step: run a command, then add the UTS, PID and mount namespaces.
- Prepare an Alpine root filesystem for the chroot and pivot_root steps:

  ```bash
  mkdir -p ~/rootfs && docker export $(docker create alpine) | tar -C ~/rootfs -xf -
  ```
- Create a GitHub repo called `mini-container`. Commit after each working step, and explain each namespace flag in the README.

Done when: Inside your container, `hostname` and `ps` show isolated results.

## Block 4. Prove it (Prove it, 15 min, where: Phone)

- Voice memo: what does each namespace in your code isolate?

Done when: One voice memo.

## Block 5. CKA: series Day 34, upgrade your kubeadm cluster (CKA, 120 min, where: Cluster VMs on the PC)

- Start the cluster: `incus start local:cp1 local:w1 local:w2`, then open shells with `incus exec local:cp1 -- bash` and so on.
- Follow [Day 34](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day34) on your cp1, w1 and w2 cluster: upgrade the control plane first, then drain, upgrade and uncordon each worker.
- Write down the version-skew rule you missed: kubelets may lag behind the API server, but never run ahead of it.
- When you're done: `incus stop local:cp1 local:w1 local:w2`.

Done when: `kubectl get nodes` shows every node on the new version.

## Block 6. Apply (Job hunt, 30 min, where: Laptop)

- Apply to 3 roles and log them.

Done when: 3 applications logged.
