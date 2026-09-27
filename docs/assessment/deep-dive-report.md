# Platform deep-dive results
Saved 2026-09-23 15:50 UTC

Part 1: 124/124 answered, 61 right (49% of answered).
Known 56, shaky (right but guessed) 5, confident misses (wrong but sure) 33, gaps (wrong guess or don't know) 30.

## By area: right/answered, then F/W/S = foundation, working, senior
- Linux internals: 1/9 | F 1/4, W 0/3, S 0/2 | confident misses: 3
- Networking: 5/10 | F 3/4, W 0/3, S 2/3 | confident misses: 2
- DNS & TLS: 3/7 | F 1/3, W 1/2, S 1/2 | confident misses: 1
- Containers: 5/7 | F 3/3, W 1/3, S 1/1 | confident misses: 1
- Kubernetes core: 4/10 | F 3/3, W 1/5, S 0/2 | confident misses: 2
- Kubernetes networking: 1/7 | F 0/1, W 0/5, S 1/1 | confident misses: 4
- Kubernetes operations: 6/10 | F 4/5, W 1/3, S 1/2 | confident misses: 3
- GitOps & CI/CD: 8/8 | F 3/3, W 4/4, S 1/1
- Terraform & Ansible: 5/7 | F 3/4, W 1/2, S 1/1 | confident misses: 1
- Observability & SRE: 4/10 | F 1/6, W 2/3, S 1/1 | confident misses: 4
- Cloud (AWS): 2/8 | F 0/3, W 1/4, S 1/1 | confident misses: 4
- Security & identity: 5/8 | F 3/3, W 2/4, S 0/1 | confident misses: 2
- Distributed systems: 5/8 | F 3/3, W 2/2, S 0/3 | confident misses: 2
- Scripting & code: 3/8 | F 2/2, W 1/5, S 0/1 | confident misses: 3
- Virtualization & bare metal: 4/7 | F 2/2, W 2/4, S 0/1 | confident misses: 1

## Misses: !! = wrong but sure, x = wrong guess, ? = didn't know
- ? [LNX-1, foundation] Signals: SIGTERM vs SIGKILL
- ? [LNX-2, foundation] Zombie processes and reaping
- !! [LNX-4, foundation] Page cache vs available memory | picked: No; 'available' includes swap space, and there's plenty
- x [LNX-3, working] Load average and D-state tasks | picked: Hypervisor CPU steal is being added into the load average figure
- ? [LNX-5, working] File descriptor limits under systemd
- !! [LNX-6, working] systemd restart policies | picked: Restart=on-abnormal
- ? [LNX-7, senior] Durability: fsync and the page cache
- !! [LNX-8, senior] OOM killer scoring and Kubernetes QoS | picked: The pod with the lowest PriorityClass value, which always goes first
- x [NET-1, foundation] Subnetting | picked: 32
- ? [NET-3, working] TCP states: TIME_WAIT
- !! [NET-4, working] MTU and PMTUD black holes | picked: TCP window scaling is off, which caps each connection at 64 KB
- x [NET-10, working] Reading tcpdump: RST vs timeout | picked: The TLS certificate doesn't match the hostname the client requested
- !! [NET-5, senior] Asymmetric routing and policy routing | picked: A second default route via eth1 with the same metric as eth0's
- x [DTL-3, foundation] TLS SNI | picked: Lets the client and server agree on the strongest shared cipher suite
- ? [DTL-4, foundation] Mutual TLS
- ? [DTL-2, working] CNAME at the zone apex
- !! [DTL-6, senior] Rotating a root CA safely | picked: Reissue all leaf certs from the new root, then update the trust stores
- x [CTR-2, working] Dockerfile layer caching | picked: apt-get update can't run as root inside a build container
- !! [CTR-6, working] User namespaces and rootless containers | picked: Nothing; UID 0 doesn't exist inside the container
- !! [KC-3, working] RBAC: ClusterRole bound by a RoleBinding | picked: Nothing; a ClusterRole needs a ClusterRoleBinding
- x [KC-4, working] Controllers and level-triggered reconciliation | picked: They run as scheduled jobs that re-apply manifests on an interval
- !! [KC-8, working] PodDisruptionBudgets and drains | picked: The pod is evicted and rescheduled; PDBs only cover crashes
- ? [KC-10, working] ownerReferences and garbage collection
- ? [KC-6, senior] Admission webhook failure modes
- ? [KC-7, senior] Optimistic concurrency and resourceVersion
- !! [KN-1, foundation] Service selectors and endpoints | picked: targetPort doesn't match the port the container listens on
- ? [KN-2, working] externalTrafficPolicy: Local
- !! [KN-3, working] NetworkPolicy semantics | picked: Nothing is blocked until you also add a default-deny policy
- ? [KN-4, working] kube-proxy iptables mode at scale
- !! [KN-5, working] Headless Services | picked: One virtual IP that load-balances across the pods
- !! [KN-6, working] Gateway API vs Ingress | picked: Gateway API only handles L4 traffic, while Ingress handles L7 routing
- !! [KO-4, foundation] Exit codes: 137, 143, 139 | picked: It exited cleanly after receiving SIGTERM
- !! [KO-2, working] Probe design: don't check dependencies | picked: Nothing, because probes ignore failures that last under 5 minutes
- ? [KO-8, working] Version skew and upgrade order
- !! [KO-7, senior] ReadWriteOnce and Multi-Attach errors | picked: RWO allows one pod cluster-wide, so the new pod has to wait its turn
- ? [IAC-6, foundation] Ansible idempotency
- !! [IAC-5, working] State structure and blast radius | picked: Modules can't be reused once everything sits in a single root module
- !! [OBS-1, foundation] Metric types: counters | picked: A histogram with a single bucket
- ? [OBS-2, foundation] rate() and counter resets
- !! [OBS-3, foundation] The four golden signals | picked: Logs, metrics, traces, events
- !! [OBS-4, foundation] Error budgets | picked: Capping how many alerts are allowed to page on-call engineers each week
- !! [OBS-6, foundation] Distributed tracing | picked: Per-service latency dashboards compared side by side
- ? [OBS-8, working] Loki's design and label cardinality
- !! [CLD-1, foundation] AWS VPC: what makes a subnet public | picked: Its network ACL allows all inbound traffic
- !! [CLD-2, foundation] NAT Gateways | picked: An Internet Gateway attached directly to the private subnet's route table
- !! [CLD-4, foundation] IAM roles for compute | picked: A bucket policy that allows requests from the instance's public IP
- ? [CLD-3, working] Security Groups vs NACLs
- !! [CLD-5, working] IAM evaluation and SCPs | picked: Yes, but only if the bucket policy also allows the delete
- ? [CLD-8, working] Zonal storage and scheduling
- !! [SEC-2, working] OIDC authentication for kubectl | picked: A session cookie that the identity provider's login page set earlier
- ? [SEC-4, working] Pod hardening
- !! [SEC-5, senior] RBAC escalation through pod creation | picked: Only Secrets that existing pods in the namespace already mount
- !! [DS-5, senior] Cache stampedes | picked: More database read replicas to absorb the spike
- !! [DS-7, senior] Capacity planning math | picked: 6
- ? [DS-8, senior] Leader election and fencing
- !! [CODE-2, working] Bash word splitting | picked: Bash can't loop over command output without a `while read` loop
- ? [CODE-3, working] Go channels and deadlock
- ? [CODE-4, working] Writing operators with controller-runtime
- !! [CODE-7, working] jq with kubectl output | picked: `.items | map(.status.phase != "Running") | .metadata.name`
- !! [CODE-8, senior] Goroutine leaks and context cancellation | picked: The HTTP server caches every response body in memory by default
- ? [VIRT-2, working] Fencing (STONITH)
- x [VIRT-5, working] Live migration and storage | picked: Local storage migrates faster, because no disk data has to cross the network
- !! [VIRT-6, senior] CPU models and live migration | picked: The 'host' type pins the VM's vCPUs to specific physical cores

## Shaky: right, but guessed
- [LNX-9, foundation] File permissions and the execute bit
- [CTR-3, working] PID 1 and signal handling
- [CTR-5, senior] CPU limits and CFS throttling
- [KC-9, working] CRDs vs operators
- [SEC-3, foundation] OAuth2 vs OIDC

## Experience
- Used in production (47): Proxmox cluster with HA; Ceph or Longhorn storage; Talos Linux; Managed switches and VLAN design; Firewalls (pfSense, OPNsense, nftables); BGP with MetalLB or Cilium; VPNs (WireGuard, IPsec); HAProxy or keepalived load balancing; Cilium or another CNI, configured beyond defaults; Ingress controllers or Gateway API; cert-manager; Writing Helm charts; Kustomize overlays; Kyverno or OPA Gatekeeper policies; Autoscaling (HPA, KEDA, Cluster Autoscaler, Karpenter); A tested etcd backup and restore; Velero backups; ArgoCD; GitHub Actions; Jenkins; Argo Rollouts or Flagger; Running a container registry (Harbor); Image signing (cosign); Terraform: writing reusable modules; Terraform: remote state and multiple environments; Ansible roles; Packer images; Crossplane or Cluster API; Prometheus and Alertmanager; Grafana dashboards; Loki or the ELK stack; Tracing (OpenTelemetry, Tempo, Jaeger); Keycloak, Dex or Authentik; SSO/OIDC login for kubectl or internal tools; HashiCorp Vault or OpenBao; External Secrets or SOPS; NetworkPolicies in production; Pod Security Standards; Postgres operations (CloudNativePG, Patroni); Redis; Kafka, NATS or RabbitMQ; Object storage (MinIO, S3); AWS; Azure; TypeScript/Node; Building internal CLIs or tools; Backstage or another developer portal
- Lab or side project (3): Other Kubernetes distros (kubeadm, k3s, RKE2); Service mesh (Istio, Linkerd); Bash scripting
- Only read about it (8): PXE or automated bare-metal provisioning; Upgrading a production cluster; Defining SLOs for a service; Being on call; Leading an incident; Writing a postmortem; Go; Python
- Never touched it (3): Writing an operator or custom controller; GCP; Managed Kubernetes (EKS, GKE, AKS)
- Not rated (2): Flux; GitLab CI

## Written answers

### 1. Your 20-minute bootstrap
(skipped)

### 2. An incident
(skipped)

### 3. Something you over-engineered
(skipped)

### 4. kubectl apply, all the way down
(skipped)

### 5. curl from inside a pod
(skipped)

### 6. Your identity layer
(skipped)

### 7. Design: a platform for 15 teams
(skipped)
