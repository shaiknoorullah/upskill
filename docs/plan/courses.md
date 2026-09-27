# The three courses

Back to back: Course 1 (1 week), Course 2 (compressed into Days 8–30 of the calendar), Course 3 (3 months). Kubernetes (CKA) runs alongside from Day 8. Keep applying for jobs from week 2; the courses don't gate applications.

Every day follows the same shape: Learn (at most an hour), Do (the lab, most of the day), Prove (explain out loud, write a one-page cheat card). Stuck 20 minutes: take the hint.

## Course 1: the 80/20 week (Days 1–7, 4–5 h a day)
Goal: stop missing foundation questions and triage any box in five minutes.
- Day 1 processes and signals; Day 2 memory and the OOM killer; Day 3 files, disks, permissions, capabilities; Day 4 systemd, logs, limits; Day 5 addressing, routing, DNS and ndots; Day 6 TCP, RST vs timeout, MTU, NAT and conntrack; Day 7 the 60-second triage, load average and D state, containers from the kernel's view, checkpoint 1.
- Exit bar: explain every ❗ topic in under a minute; recite the 60-second checklist; at least 16/20 on checkpoint 1.

## Course 2: the depth month (Days 8–30, about 2.5 h Linux + 2 h CKA + 30 min job hunt)
Goal: rebuild things by hand until they're automatic.
- Week A (Days 8–13): strace and /proc, PSI and memory.high vs memory.max, LVM and RAID, disk I/O and fsync, perf and flame graphs, bpftrace, timed SadServers.
- Week B (Days 15–20): container networking by hand, an MTU black hole and policy routing, VXLAN and conntrack exhaustion, TCP queues and port exhaustion, your own CA with a broken chain and mTLS, timed network scenarios.
- Week C (Days 22–27): capabilities and seccomp, AppArmor and auditd, SELinux, a container runtime in Go with cgroups v2 and user namespaces, CFS throttling measured, systemd hardening, three ShellCheck-clean scripts.
- Gauntlets on Days 14, 21 and 28; rehearsal on Day 29; checkpoint 2 (live troubleshooting) and booking the CKA on Day 30.
- Exit bar: most SadServers mediums inside the time limit; namespace, bridge and NAT networking from memory; OOM and throttling demonstrated with cgroup files; one AppArmor and one seccomp profile written; pass the live mock.

## Course 3: the senior quarter (after the CKA, 8–10 h a week)
- Month 1, kernel internals and performance: the scheduler (CFS, then EEVDF), interrupts and softirqs, NUMA, steal; page tables, THP, reclaim, writeback, memcg internals; perf, on-CPU and off-CPU flame graphs, ftrace, your own bpftrace tools. Read Gregg's Systems Performance and Liz Rice's Learning eBPF. Capstone: load-test a real service, find the bottleneck with USE and eBPF, fix it, publish the write-up.
- Month 2, the network stack at scale: NIC to NAPI to softirq to netfilter to routing to socket; ring buffers, GRO/TSO, qdiscs and tc netem, socket buffers, BBR vs CUBIC, SYN/accept queue internals; containerlab with FRR for BGP and ECMP, VXLAN/EVPN basics, nftables sets and flowtables, conntrack tuning, XDP, WireGuard. Capstone: a repo that reproduces five production failures (MTU black hole, conntrack exhaustion, asymmetric routing, SNAT port exhaustion, ndots amplification).
- Month 3, storage, security, runtimes, senior operations: block layer and I/O schedulers, io_uring, fsync semantics on ext4 vs XFS; threat-model a node, CIS hardening with Lynis, auditd, real SELinux/AppArmor policies, secure boot and TPM; the OCI spec, runc and containerd internals, the systemd cgroup driver, gVisor and Kata trade-offs; two real postmortems, capacity math, immutable vs mutable fleets. Capstone: a mini container runtime in Go with a design doc.
- Exit bar: trace a syscall and a packet end to end; a flame-graph performance analysis; defend a node OS strategy; three published portfolio pieces; pass a full senior loop.

## Month two, outside the Linux track (from the gap map)
Observability (PromQL, SLOs and burn rates, Loki, tracing), AWS (VPC, IAM, EKS; Cantrill's SAA-C03 course), OIDC for kubectl with kubelogin, Terraform state structure, Ansible idempotency.
