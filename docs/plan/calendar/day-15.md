# Day 15: Container networking by hand

- Course: Course 2, the depth month
- Why: This is exactly how Docker and CNI plugins wire containers together. Build it once and Kubernetes networking questions get much easier.
- Minimum version (low-energy day): Build one namespace that can reach the internet.

## Block 1. Subnetting drill (Warm-up, 15 min, where: Browser)

- Do 10 problems at [subnettingpractice.com](https://subnettingpractice.com/).

Done when: 10 problems done.

## Block 2. Read: container networking (Learn, 30 min, where: Browser)

- [Container Networking Is Simple!](https://iximiuz.com/en/posts/container-networking-is-simple/) by Ivan Velichko: read up to and including the part about the bridge.

Done when: You can say what a veth pair and a bridge each do.

## Block 3. Lab: namespaces, veth, a bridge and NAT (Lab, 90 min, where: Ubuntu VM)

- 1. Two namespaces on one bridge:

  ```bash
  sudo ip netns add ns1 && sudo ip netns add ns2
  sudo ip link add br0 type bridge
  sudo ip addr add 10.200.0.1/16 dev br0 && sudo ip link set br0 up
  for n in 1 2; do
    sudo ip link add veth$n type veth peer name ceth$n
    sudo ip link set ceth$n netns ns$n
    sudo ip link set veth$n master br0 && sudo ip link set veth$n up
    sudo ip -n ns$n addr add 10.200.0.1$n/16 dev ceth$n
    sudo ip -n ns$n link set ceth$n up && sudo ip -n ns$n link set lo up
    sudo ip -n ns$n route add default via 10.200.0.1
  done
  ```
- 2. Docker set the FORWARD chain to DROP, which also blocks bridged traffic. Check, then allow br0:

  ```bash
  sudo iptables -S FORWARD | head -1          # -P FORWARD DROP
  sudo iptables -I FORWARD -i br0 -j ACCEPT
  sudo iptables -I FORWARD -o br0 -j ACCEPT
  sudo ip netns exec ns1 ping -c2 10.200.0.12   # ns1 to ns2 through the bridge
  ```
- 3. Give the namespaces internet access with NAT:

  ```bash
  sudo sysctl -w net.ipv4.ip_forward=1
  sudo iptables -t nat -A POSTROUTING -s 10.200.0.0/16 ! -o br0 -j MASQUERADE
  sudo ip netns exec ns1 ping -c2 1.1.1.1
  ```
- 4. Publish a port from ns1 to the outside world with DNAT:

  ```bash
  sudo ip netns exec ns1 python3 -m http.server 5000 &
  sudo iptables -t nat -A PREROUTING -p tcp --dport 5000 -j DNAT --to-destination 10.200.0.11:5000
  ```
- The VMs' network is private to the laptop, so test from there. On the PC, run `incus list` to get lab-ubuntu's IP, then `ssh <your-user>@<laptop IP> curl -s http://<lab-ubuntu IP>:5000/ | head`. You're looking at a directory listing served from inside ns1.
- 5. Save the whole lab as `~/labs/netns-lab.sh` with `up` and `down` functions, and push it to your repo.
- 6. Tear it all down:

  ```bash
  sudo pkill -f 'http.server 5000'
  sudo ip netns del ns1; sudo ip netns del ns2; sudo ip link del br0
  sudo iptables -t nat -D POSTROUTING -s 10.200.0.0/16 ! -o br0 -j MASQUERADE
  sudo iptables -t nat -D PREROUTING -p tcp --dport 5000 -j DNAT --to-destination 10.200.0.11:5000
  sudo iptables -D FORWARD -i br0 -j ACCEPT; sudo iptables -D FORWARD -o br0 -j ACCEPT
  ```

Done when: The laptop reached the web server running inside ns1.

## Block 4. Prove it (Prove it, 15 min, where: Paper and repo)

- On paper, draw a packet going from ns1 to 1.1.1.1: veth, bridge, routing, POSTROUTING and MASQUERADE, eth0. Photograph it into your repo.
- Write and push `cards/15-container-networking.md`.

Done when: Drawing and card pushed.

## Block 5. CKA: series Days 22–24 (CKA, 120 min, where: YouTube and kind cluster)

- Watch Days 22–24: authorization, RBAC, ClusterRoles and ClusterRoleBindings.
- Do the tasks for [Day 22](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day22), [Day 23](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day23) and [Day 24](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day24).
- Try the case you missed in the interview: bind the `view` ClusterRole with a RoleBinding in one namespace. Then check `k auth can-i list pods --as <user> -n <that namespace>` and the same for another namespace.

Done when: All three tasks done, and can-i shows the permission applies to one namespace only.

## Block 6. Apply and ask for a referral (Job hunt, 30 min, where: Laptop)

- Apply to 3 roles and log them.
- Send one referral message.

Done when: 3 applications and 1 referral message.
