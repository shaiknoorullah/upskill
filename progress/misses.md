# Misses to re-test

Every item gets re-tested when its calendar day comes up, then again 3 and 7 days later. Mark each re-test with the date and pass/fail. An item leaves this list after two passes in a row.

Round 1 misses (docs/assessment/round1-15q.md) belong here too: preStop vs CSI unmount, SNAT conntrack race, Argo vs HPA replicas, burn-rate math, off-heap OOM, EKS ENI pod limit, moved{} blocks, histograms vs summaries, missing TLS intermediate, deleted-but-open files, ndots:5.

| ID | Topic | Level | Type | What I picked | Covered on | Re-tests |
|---|---|---|---|---|---|---|
| CLD-1 | AWS VPC: what makes a subnet public | foundation | confident miss | Its network ACL allows all inbound traffic | month 2 |  |
| CLD-2 | NAT Gateways | foundation | confident miss | An Internet Gateway attached directly to the private subnet's route table | month 2 |  |
| CLD-4 | IAM roles for compute | foundation | confident miss | A bucket policy that allows requests from the instance's public IP | month 2 |  |
| CLD-5 | IAM evaluation and SCPs | working | confident miss | Yes, but only if the bucket policy also allows the delete | month 2 |  |
| CODE-2 | Bash word splitting | working | confident miss | Bash can't loop over command output without a `while read` loop | warm-ups |  |
| CODE-7 | jq with kubectl output | working | confident miss | `.items / map(.status.phase != "Running") / .metadata.name` | warm-ups |  |
| CODE-8 | Goroutine leaks and context cancellation | senior | confident miss | The HTTP server caches every response body in memory by default | course 3 |  |
| CTR-6 | User namespaces and rootless containers | working | confident miss | Nothing; UID 0 doesn't exist inside the container | 26 |  |
| DS-5 | Cache stampedes | senior | confident miss | More database read replicas to absorb the spike | course 3 |  |
| DS-7 | Capacity planning math | senior | confident miss | 6 | course 3 |  |
| DTL-6 | Rotating a root CA safely | senior | confident miss | Reissue all leaf certs from the new root, then update the trust stores | 19 |  |
| IAC-5 | State structure and blast radius | working | confident miss | Modules can't be reused once everything sits in a single root module | month 2 |  |
| KC-3 | RBAC: ClusterRole bound by a RoleBinding | working | confident miss | Nothing; a ClusterRole needs a ClusterRoleBinding | 15 |  |
| KC-8 | PodDisruptionBudgets and drains | working | confident miss | The pod is evicted and rescheduled; PDBs only cover crashes | 25 |  |
| KN-1 | Service selectors and endpoints | foundation | confident miss | targetPort doesn't match the port the container listens on | 20 |  |
| KN-3 | NetworkPolicy semantics | working | confident miss | Nothing is blocked until you also add a default-deny policy | 16 |  |
| KN-5 | Headless Services | working | confident miss | One virtual IP that load-balances across the pods | 19 |  |
| KN-6 | Gateway API vs Ingress | working | confident miss | Gateway API only handles L4 traffic, while Ingress handles L7 routing | 22 |  |
| KO-2 | Probe design: don't check dependencies | working | confident miss | Nothing, because probes ignore failures that last under 5 minutes | 12 |  |
| KO-4 | Exit codes: 137, 143, 139 | foundation | confident miss | It exited cleanly after receiving SIGTERM | 1 |  |
| KO-7 | ReadWriteOnce and Multi-Attach errors | senior | confident miss | RWO allows one pod cluster-wide, so the new pod has to wait its turn | 18 |  |
| LNX-4 | Page cache vs available memory | foundation | confident miss | No; 'available' includes swap space, and there's plenty | 2 |  |
| LNX-6 | systemd restart policies | working | confident miss | Restart=on-abnormal | 4 |  |
| LNX-8 | OOM killer scoring and Kubernetes QoS | senior | confident miss | The pod with the lowest PriorityClass value, which always goes first | 2 |  |
| NET-4 | MTU and PMTUD black holes | working | confident miss | TCP window scaling is off, which caps each connection at 64 KB | 6, 16 |  |
| NET-5 | Asymmetric routing and policy routing | senior | confident miss | A second default route via eth1 with the same metric as eth0's | 16 |  |
| OBS-1 | Metric types: counters | foundation | confident miss | A histogram with a single bucket | month 2 |  |
| OBS-3 | The four golden signals | foundation | confident miss | Logs, metrics, traces, events | month 2 |  |
| OBS-4 | Error budgets | foundation | confident miss | Capping how many alerts are allowed to page on-call engineers each week | month 2 |  |
| OBS-6 | Distributed tracing | foundation | confident miss | Per-service latency dashboards compared side by side | month 2 |  |
| SEC-2 | OIDC authentication for kubectl | working | confident miss | A session cookie that the identity provider's login page set earlier | month 2 |  |
| SEC-5 | RBAC escalation through pod creation | senior | confident miss | Only Secrets that existing pods in the namespace already mount | 22 |  |
| VIRT-6 | CPU models and live migration | senior | confident miss | The 'host' type pins the VM's vCPUs to specific physical cores | self-study |  |
| CLD-3 | Security Groups vs NACLs | working | didn't know |  | month 2 |  |
| CLD-8 | Zonal storage and scheduling | working | didn't know |  | month 2 |  |
| CODE-3 | Go channels and deadlock | working | didn't know |  | 25 |  |
| CODE-4 | Writing operators with controller-runtime | working | didn't know |  | 24 |  |
| CTR-2 | Dockerfile layer caching | working | wrong guess | apt-get update can't run as root inside a build container | self-study |  |
| DS-8 | Leader election and fencing | senior | didn't know |  | course 3 |  |
| DTL-2 | CNAME at the zone apex | working | didn't know |  | 5 |  |
| DTL-3 | TLS SNI | foundation | wrong guess | Lets the client and server agree on the strongest shared cipher suite | 19 |  |
| DTL-4 | Mutual TLS | foundation | didn't know |  | 19 |  |
| IAC-6 | Ansible idempotency | foundation | didn't know |  | month 2 |  |
| KC-10 | ownerReferences and garbage collection | working | didn't know |  | 24 |  |
| KC-4 | Controllers and level-triggered reconciliation | working | wrong guess | They run as scheduled jobs that re-apply manifests on an interval | 24 |  |
| KC-6 | Admission webhook failure modes | senior | didn't know |  | 23 |  |
| KC-7 | Optimistic concurrency and resourceVersion | senior | didn't know |  | 24 |  |
| KN-2 | externalTrafficPolicy: Local | working | didn't know |  | 20 |  |
| KN-4 | kube-proxy iptables mode at scale | working | didn't know |  | 20 |  |
| KO-8 | Version skew and upgrade order | working | didn't know |  | 25 |  |
| LNX-1 | Signals: SIGTERM vs SIGKILL | foundation | didn't know |  | 1 |  |
| LNX-2 | Zombie processes and reaping | foundation | didn't know |  | 1 |  |
| LNX-3 | Load average and D-state tasks | working | wrong guess | Hypervisor CPU steal is being added into the load average figure | 7 |  |
| LNX-5 | File descriptor limits under systemd | working | didn't know |  | 4 |  |
| LNX-7 | Durability: fsync and the page cache | senior | didn't know |  | 11 |  |
| NET-1 | Subnetting | foundation | wrong guess | 32 | warm-ups |  |
| NET-10 | Reading tcpdump: RST vs timeout | working | wrong guess | The TLS certificate doesn't match the hostname the client requested | 6 |  |
| NET-3 | TCP states: TIME_WAIT | working | didn't know |  | 6 |  |
| OBS-2 | rate() and counter resets | foundation | didn't know |  | month 2 |  |
| OBS-8 | Loki's design and label cardinality | working | didn't know |  | month 2 |  |
| SEC-4 | Pod hardening | working | didn't know |  | 22 |  |
| VIRT-2 | Fencing (STONITH) | working | didn't know |  | self-study |  |
| VIRT-5 | Live migration and storage | working | wrong guess | Local storage migrates faster, because no disk data has to cross the network | self-study |  |
| CTR-3 | PID 1 and signal handling | working | shaky (right, guessed) |  | 1 |  |
| CTR-5 | CPU limits and CFS throttling | senior | shaky (right, guessed) |  | 26 |  |
| KC-9 | CRDs vs operators | working | shaky (right, guessed) |  | 24 |  |
| LNX-9 | File permissions and the execute bit | foundation | shaky (right, guessed) |  | 3 |  |
| SEC-3 | OAuth2 vs OIDC | foundation | shaky (right, guessed) |  | month 2 |  |
