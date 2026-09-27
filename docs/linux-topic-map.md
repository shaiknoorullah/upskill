# Linux topic map

❗ = missed or guessed in the interviews. Done means: explain it out loud, show it on a VM, and break and fix it.

## 1. Processes and signals
- ❗ fork/exec, PID/PPID, states R S ❗D Z T, zombies vs orphans, reaping
- ❗ SIGTERM vs SIGKILL (which can't be caught), SIGINT, SIGHUP, SIGSTOP/SIGCONT, SIGCHLD, SIGPIPE, SIGSEGV, `trap`
- ❗ PID 1 rules in containers (tini, dumb-init)
- Exit codes 0, 1, 126, 127, 128+n (130, ❗137, 139, 143)
- Threads vs processes, nice, scheduler, run queue, context switches, affinity; job control; /proc/<pid>
- Tools: ps -eo, top/htop, pstree, pgrep/pkill, strace, ltrace, lsof, pidstat

## 2. Memory
- Virtual memory, page faults, RSS/VSZ/PSS, mmap
- ❗ page cache and "available" vs "free", dirty pages and writeback
- Swap and swappiness; overcommit; ❗ OOM killer, oom_score_adj, cgroup OOM vs system OOM
- ❗ what counts against a container limit (heap, native, page cache, tmpfs)
- Tools: free, vmstat, /proc/meminfo, smaps, pmap, smem, slabtop, PSI

## 3. Files, filesystems and storage
- Directory layout, inodes, dentries, file descriptors, links, devices, udev
- ❗ df vs du (deleted-but-open files, `lsof +L1`), inode exhaustion, reserved blocks
- ❗ fsync, O_DIRECT, journaling (why etcd cares)
- ext4, XFS, Btrfs/ZFS, tmpfs, overlayfs; mounts, bind mounts, propagation (CSI)
- GPT, LVM, mdadm, LUKS; IOPS vs throughput vs latency, iowait
- Tools: df, du, lsblk, findmnt, fdisk/parted, mkfs, fsck, iostat, iotop, fio, smartctl

## 4. systemd, logging and boot
- UEFI, GRUB, kernel + initramfs, systemd, targets, rescue mode
- Unit types; Wants/Requires/After; ❗ Restart=; ❗ LimitNOFILE; drop-ins; daemon-reload
- Sockets, timers, slices; journalctl filters; logrotate (and deleted-but-open logs)
- Tools: systemctl, journalctl, systemd-analyze, systemd-cgls/cgtop

## 5. Users, permissions and security
- passwd/shadow/group, sudoers; ❗ rwx on directories, umask; setuid, setgid, sticky; ACLs, chattr
- ❗ capabilities (SYS_ADMIN, NET_ADMIN, NET_RAW, NET_BIND_SERVICE), no_new_privs
- AppArmor (Ubuntu) vs SELinux (RHEL); ❗ seccomp and RuntimeDefault; PAM, auditd, SSH hardening, host firewalls

## 6. Limits, cgroups and namespaces
- ❗ ulimits vs systemd limits, fs.file-max, prlimit
- cgroup v2: cpu.max (❗ CFS throttling), cpu.weight, memory.max/high/events, io.max, pids.max, PSI
- How Kubernetes requests and limits map to cgroups
- The 8 namespaces; ❗ user namespaces and rootless; a container = namespaces + cgroups + overlayfs + caps + seccomp + LSM
- Tools: unshare, nsenter, lsns, ip netns, crictl, ctr

## 7. Networking concepts
- Ethernet, ARP/NDP, VLANs, bridges, LACP, DHCP; ❗ subnetting
- Routing, longest-prefix match, ❗ policy routing, rp_filter, ECMP
- ❗ TCP states (TIME_WAIT, CLOSE_WAIT), queues, ❗ RST vs timeout, port exhaustion
- ❗ MTU, PMTUD, MSS clamping; ❗ NAT and conntrack
- Netfilter hooks, iptables vs nftables, kube-proxy; eBPF/XDP basics
- netns, veth, bridges, VXLAN/Geneve, WireGuard
- ❗ DNS path (hosts, nsswitch, resolv.conf, ndots), glibc vs musl; ❗ TLS (SNI, chains, mTLS)

## 8. Networking tools
ip, ss, ethtool, ping, mtr, tracepath, dig, getent, resolvectl, tcpdump, tshark/Wireshark, curl -v, nc, socat, iperf3, nmap, iptables/nft, conntrack, openssl s_client/x509, key sysctls

## 9. Performance and troubleshooting method
- ❗ load average (runnable + D state); CPU breakdown incl. steal
- USE method; the 60-second checklist; PSI; perf, flame graphs, eBPF tools
- Incident patterns: disk full, too many open files, OOM, high load with idle CPU, port exhaustion, DNS, zombies, failed services, LSM denials, clock skew

## 10. Shell and utilities
- ❗ quoting and word splitting, set -euo pipefail, redirection, trap
- grep, sed, awk, sort, uniq, xargs, find, ❗ jq, yq; tar, rsync; SSH config and tunnels; apt/dnf; vim, tmux

## 11. Kernel and system basics
Syscalls, /proc and /sys, modules (overlay, br_netfilter), sysctl, chrony, shared libraries, hardware info
