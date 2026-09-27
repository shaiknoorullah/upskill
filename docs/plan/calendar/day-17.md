# Day 17: VXLAN tunnels and conntrack

- Course: Course 2, the depth month
- Why: Pod traffic between nodes rides a VXLAN tunnel, and a full conntrack table silently drops packets. You'll build and break both.
- Minimum version (low-energy day): Do only Lab part A: the VXLAN tunnel.

## Block 1. Subnetting drill (Warm-up, 15 min, where: Browser)

- Do 10 problems at [subnettingpractice.com](https://subnettingpractice.com/).

Done when: 10 problems done.

## Block 2. Read: VXLAN on Linux (Learn, 30 min, where: Browser)

- [VXLAN & Linux](https://vincent.bernat.ch/en/blog/2017-vxlan-linux) by Vincent Bernat: read 'Basic usage' and the unicast sections.

Done when: You can say what VNI 42 and UDP 4789 mean.

## Block 3. Lab: a tunnel between your VMs, then a full conntrack table (Lab, 90 min, where: Both VMs)

- Start Rocky first: `incus start lab-rocky`. Get both VMs' IPs with `incus list`. In each VM, find the main interface name with `ip -br addr`. Below, replace ETH with it, and the IPs with your two VMs' IPs.
- A. On lab-ubuntu (45 min for all of part A):

  ```bash
  sudo ip link add vx0 type vxlan id 42 remote ROCKY_IP dstport 4789 dev ETH
  sudo ip addr add 192.168.42.1/24 dev vx0 && sudo ip link set vx0 up
  ```
- On lab-rocky:

  ```bash
  sudo firewall-cmd --add-port=4789/udp
  sudo ip link add vx0 type vxlan id 42 remote UBUNTU_IP dstport 4789 dev ETH
  sudo ip addr add 192.168.42.2/24 dev vx0 && sudo ip link set vx0 up
  ```
- Back on lab-ubuntu, test it and look inside the tunnel:

  ```bash
  ping -c3 192.168.42.2
  sudo tcpdump -ni ETH -c 6 udp port 4789        # ICMP wrapped inside UDP
  ip -d link show vx0 | head -3                  # mtu 1450: 50 bytes of overhead
  ```
- Break it the way a cloud security group would: on lab-rocky run `sudo firewall-cmd --remove-port=4789/udp`. The VMs still ping each other, but the tunnel is dead. That's 'pods on the same node work, pods across nodes don't'.
- Clean up on both VMs: `sudo ip link del vx0`. Then, from the PC: `incus stop lab-rocky`.
- B. Fill the conntrack table (45 min). Write down the first number this prints:

  ```bash
  cat /proc/sys/net/netfilter/nf_conntrack_max
  docker run -d --name web -p 8081:80 nginx
  IP=$(hostname -I | awk '{print $1}')
  sudo sysctl -w net.netfilter.nf_conntrack_max=128
  for i in $(seq 400); do curl -s -o /dev/null -m 2 http://$IP:8081/ & done; wait
  sudo dmesg -T | grep -i 'table full' | tail -3
  sudo conntrack -S | head -3
  ```
- Restore the original value and clean up:

  ```bash
  sudo sysctl -w net.netfilter.nf_conntrack_max=<the number you wrote down>
  docker rm -f web
  ```

Done when: The tunnel died while the VMs could still ping, and dmesg said 'table full'.

## Block 4. Prove it (Prove it, 15 min, where: Phone and repo)

- Voice memo: pods on the same node can talk, but cross-node traffic fails. What do you check first?
- Voice memo: what does 'nf_conntrack: table full, dropping packet' mean, and how do you fix it?
- Write and push `cards/17-vxlan-conntrack.md`.

Done when: Two voice memos and one card.

## Block 5. CKA: series Day 27, build a real kubeadm cluster (CKA, 120 min, where: Cluster VMs on the PC)

- Create three small VMs on the PC itself (`local:` means the PC):

  ```bash
  incus launch images:ubuntu/24.04 local:cp1 --vm -c limits.cpu=2 -c limits.memory=2GiB -d root,size=20GiB
  for n in w1 w2; do
    incus launch images:ubuntu/24.04 local:$n --vm -c limits.cpu=2 -c limits.memory=1536MiB -d root,size=20GiB
  done
  sleep 60; incus list local:
  ```
- Open a shell on each node with `incus exec local:cp1 -- bash` (then w1 and w2).
- Follow [Day 27](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day27): container runtime, kubeadm init, network plugin, then join the workers.
- If it runs over, finish it in tomorrow's CKA slot. You'll use this cluster for upgrades and etcd backups later.
- When you stop for the day, free the PC's memory: `incus stop local:cp1 local:w1 local:w2`.

Done when: `kubectl get nodes` shows 3 Ready nodes.

## Block 6. Apply and follow up (Job hunt, 30 min, where: Laptop)

- Apply to 3 roles and log them.
- Follow up on any application older than 7 days with a short message to the recruiter or hiring manager.

Done when: 3 applications and follow-ups sent.
