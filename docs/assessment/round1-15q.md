# Round 1: 15 hard questions (Sept 2026, in chat)

Score: 4 of 15.

Right: etcd quorum loss with a 3/2 rack split; bound service-account tokens for Vault; Ceph blocking I/O below min_size; pinning images by digest.

Wrong (what I picked, then the right answer):
- Pod stuck Terminating: blamed the preStop hook; really a CSI volume that wouldn't unmount.
- Intermittent timeouts: blamed MTU; really the SNAT conntrack race (insert_failed).
- ArgoCD fighting an HPA: thought Argo ignores HPA-managed replicas automatically; fix is removing replicas from Git (or ignoreDifferences).
- SLO burn rate: didn't know the math (14.4x over 1h spends 2% of a 30-day budget: 720h / 1h x 2% = 14.4).
- JVM OOMKilled under its heap limit: blamed the cgroup view; really off-heap/native memory.
- EKS pods stuck Pending: said maxPods 110; really the ENI/IP limit (an m5.large fits 29 pods).
- Terraform rename without destroy: picked create_before_destroy; the answer is a moved {} block.
- Averaging p99 from Summaries: you can't; you need histograms.
- TLS works in browsers but not curl: didn't know; a missing intermediate certificate.
- Disk full but du disagrees: said inode exhaustion; really deleted-but-open files.
- Slow DNS in pods: blamed the CoreDNS cache; really ndots:5 search-list expansion.

Pattern: strong on first-principles design, weak on mechanics and diagnosis.
