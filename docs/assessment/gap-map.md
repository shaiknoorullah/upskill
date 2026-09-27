# Gap map (from two interviews, September 2026)

## Headline
- Deep-dive, 124 questions: 61 right (49%). Foundation 65%, working level 37%, senior 43%.
- Calibration: when I said "sure" I was right 63% of the time (56 of 89), which gave 33 confident misses.
- Round 1, 15 hard questions: 4 right.
- Pattern: architect instincts and wide hands-on breadth (47 tools rated "production"), but the day-to-day mechanics in the middle are weak. Teach and test the working level hardest.

## Ranked gaps
1. Linux internals: 1 of 9. Signals, zombies, page cache vs available, systemd Restart= and LimitNOFILE, load average and D state, fsync, OOM scoring, deleted-but-open files.
2. Kubernetes networking: 1 of 7, with 4 confident misses. Service endpoints, NetworkPolicy semantics, headless Services, Gateway API, externalTrafficPolicy, kube-proxy modes.
3. AWS: 2 of 8, none right at foundation. Public subnets, NAT, instance roles, SCPs, SG vs NACL, zonal EBS.
4. Observability: 1 of 6 at foundation. Counters, rate(), golden signals, error budgets, burn rates (missed in both rounds), tracing, Loki labels, histograms vs summaries.
5. Kubernetes core and operations at working level: RBAC binding scope, PDBs and drains, reconciliation, ownerReferences, webhook failurePolicy, resourceVersion, exit code 137, probe design, version skew, RWO vs RWOP.
6. Code: 3 of 8. Bash word splitting, jq, Go channels, goroutine leaks, controller-runtime.
7. Networking, DNS and TLS: subnetting, TIME_WAIT, RST vs timeout, policy routing, SNI, mTLS, CA rotation, missing intermediates. MTU caught me in both rounds (blamed wrongly once, missed once). ndots:5 and the conntrack SNAT race from round 1.

## Resume landmines
Rated "production" but answered wrong or didn't know. Interviewers dig into the resume, so these come first:
NetworkPolicies; Gateway API and Ingress; Prometheus, Loki and tracing; SSO/OIDC login for kubectl (I built an identity layer); AWS; Terraform multi-environment state; Ansible idempotency; Proxmox HA fencing and CPU types; Kyverno's webhook failure mode; Pod Security Standards.

## Verified strengths
GitOps and CI/CD 8 of 8; Terraform 5 of 7; containers 5 of 7; distributed-systems foundations. Senior-level judgement on ECMP rehashing, port exhaustion, VPC endpoint costs, Thanos dedup, Terraform provider staging, etcd quorum and workload identity.

## Experience inventory (self-rated)
- Production (47 items), including Proxmox HA, Ceph/Longhorn, Talos, Cilium, ArgoCD, Terraform, Ansible, Prometheus, Loki, tracing, Keycloak/OIDC, Vault, NetworkPolicies, AWS and Azure.
- Lab or side project: kubeadm/k3s/RKE2, service mesh, Bash scripting.
- Only read about: PXE provisioning, upgrading a production cluster, defining SLOs, on-call, leading an incident, writing a postmortem, Go, Python.
- Never: writing an operator, GCP, managed Kubernetes.
- The seven written interview answers were skipped. The project deep-dive (my bootstrap) is untested and needs rehearsal.
