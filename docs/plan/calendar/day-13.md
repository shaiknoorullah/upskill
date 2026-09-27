# Day 13: Timed troubleshooting and bpftrace

- Course: Course 2, the depth month
- Why: Today you use everything from Days 1 to 12 under time pressure, the way a real troubleshooting round feels.
- Minimum version (low-energy day): Do only 'Cape Town'.

## Block 1. jq on kubectl (Warm-up, 15 min, where: kind cluster)

- Two harder queries:

  ```bash
  k get pods -A -o json | jq -r '.items[] | select(any(.status.containerStatuses[]?; .restartCount > 0)) | .metadata.name'
  k get nodes -o json | jq -r '.items[] | .metadata.name + " cpu=" + .status.allocatable.cpu + " mem=" + .status.allocatable.memory'
  ```

Done when: Both queries ran.

## Block 2. Read: bpftrace (Learn, 30 min, where: Browser and Ubuntu VM)

- [A thorough introduction to bpftrace](https://brendangregg.com/blog/2019-08-19/bpftrace.html) by Brendan Gregg. Read it and run the first 5 one-liners from its tutorial section on the VM.

Done when: 5 one-liners ran.

## Block 3. Lab: three scenarios against the clock (Lab, 90 min, where: Browser)

- Rule for every scenario: run your 60-second checklist before you change anything.
- SadServers 'Cape Town' (30 min).
- SadServers 'Manhattan' (30 min).
- SadServers 'Kihei' (30 min).
- If you hit the time limit, read the hint, finish it, and note what you missed.

Done when: Three scenarios attempted, each within 30 minutes.

## Block 4. Prove it (Prove it, 15 min, where: Repo)

- Write a 3-line postmortem for each scenario in `cards/13-postmortems.md`: symptom, cause, fix. Push it.

Done when: Three postmortems pushed.

## Block 5. CKA: series Days 20–21 (CKA, 120 min, where: YouTube and kind cluster)

- Watch Days 20–21: how TLS works, and TLS in Kubernetes.
- Do the tasks for [Day 20](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day20) and [Day 21](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day21).
- Extra: read your cluster's API server certificate. Replace the container name with yours from `docker ps`:

  ```bash
  docker exec kind-control-plane ls /etc/kubernetes/pki
  docker exec kind-control-plane cat /etc/kubernetes/pki/apiserver.crt | openssl x509 -noout -subject -dates -ext subjectAltName
  ```

Done when: Both tasks done and you've read the API server's SANs.

## Block 6. Post and apply (Job hunt, 30 min, where: Laptop)

- Publish LinkedIn post #1 from yesterday's draft.
- Apply to 2 roles and log them.

Done when: Post published and 2 applications logged.
