# Day 16: MTU black holes and policy routing

- Course: Course 2, the depth month
- Why: MTU tripped you up in both interview rounds. Today you build the black hole yourself and fix it two ways.
- Minimum version (low-energy day): Do only Lab part A.

## Block 1. jq on kubectl (Warm-up, 15 min, where: kind cluster)

- Find containers with no limits:

  ```bash
  k get pods -A -o json | jq -r '.items[] | .metadata.name as $p | .spec.containers[] | select(.resources.limits == null) | $p + "/" + .name'
  ```
- Which of these pods would be BestEffort? (Only pods with no requests or limits on any container.)

Done when: Query ran and you answered the question.

## Block 2. Read: PMTU and routing rules (Learn, 30 min, where: Browser)

- Reread [Path MTU discovery in practice](https://blog.cloudflare.com/path-mtu-discovery-in-practice/). (10 min)
- [Rules: the routing policy database](https://berthub.eu/lartc/lartc.rpdb.html) from the Linux Advanced Routing HOWTO. (20 min)

Done when: You can say what `ip rule` adds on top of the routing table.

## Block 3. Lab: break MTU, fix it twice, then policy routing (Lab, 90 min, where: Ubuntu VM)

- A. Build a small network with a router in the middle (15 min):

  ```bash
  for n in a r b; do sudo ip netns add $n; sudo ip -n $n link set lo up; done
  sudo ip link add a0 type veth peer name r0
  sudo ip link add r1 type veth peer name b0
  sudo ip link set a0 netns a; sudo ip link set r0 netns r
  sudo ip link set r1 netns r; sudo ip link set b0 netns b
  sudo ip -n a addr add 10.1.0.2/24 dev a0; sudo ip -n r addr add 10.1.0.1/24 dev r0
  sudo ip -n r addr add 10.2.0.1/24 dev r1; sudo ip -n b addr add 10.2.0.2/24 dev b0
  sudo ip -n a link set a0 up; sudo ip -n r link set r0 up
  sudo ip -n r link set r1 up; sudo ip -n b link set b0 up
  sudo ip -n a route add default via 10.1.0.1; sudo ip -n b route add default via 10.2.0.1
  sudo ip netns exec r sysctl -qw net.ipv4.ip_forward=1
  sudo ip netns exec a ping -c1 10.2.0.2
  ```
- B. Serve a small and a big file from b, then shrink the router's MTU (15 min):

  ```bash
  mkdir -p /tmp/www && echo hi > /tmp/www/small.txt && head -c 2M /dev/urandom > /tmp/www/big.bin
  sudo ip netns exec b python3 -m http.server 8000 --directory /tmp/www &
  sudo ip -n r link set r1 mtu 1200
  sudo ip netns exec a curl -s -m 5 http://10.2.0.2:8000/small.txt               # works
  sudo ip netns exec a curl -s -m 10 -o /dev/null http://10.2.0.2:8000/big.bin || echo "hung"
  ```
- That's a black hole: small requests work, big ones hang, and nothing reports an error. Explain why in one sentence before you move on.
- C. Fix 1: clamp the TCP MSS on the router (10 min):

  ```bash
  sudo ip netns exec r iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
  sudo ip netns exec a curl -s -m 10 -o /dev/null -w '%{http_code}\n' http://10.2.0.2:8000/big.bin    # 200
  ```
- D. Fix 2 (10 min): remove the clamp by running the same iptables command with `-D` instead of `-A`, confirm it hangs again, then set b's MTU to match with `sudo ip -n b link set b0 mtu 1200` and test again.
- Tear down:

  ```bash
  sudo pkill -f 'http.server 8000'
  for n in a r b; do sudo ip netns del $n; done
  ```
- E. Policy routing (35 min):

  ```bash
  sudo ip link add e1 type dummy && sudo ip link add e2 type dummy
  sudo ip addr add 10.10.1.2/24 dev e1 && sudo ip addr add 10.10.2.2/24 dev e2
  sudo ip link set e1 up && sudo ip link set e2 up
  ip route get 8.8.8.8 from 10.10.2.2          # main table: leaves via your real uplink
  sudo ip route add default via 10.10.2.1 dev e2 table 100
  sudo ip rule add from 10.10.2.2 table 100
  ip rule show; ip route show table 100
  ip route get 8.8.8.8 from 10.10.2.2          # now it leaves via e2
  sudo ip rule del from 10.10.2.2 table 100; sudo ip link del e1; sudo ip link del e2
  ```

Done when: You made big downloads hang, fixed them two ways, and steered traffic with a routing rule.

## Block 4. Prove it (Prove it, 15 min, where: Phone and repo)

- Voice memo: explain the MTU black hole and both fixes.
- Voice memo: a server with two NICs answers on the wrong interface. What's happening, and how does policy routing fix it?
- Write and push `cards/16-mtu-policy-routing.md`.

Done when: Two voice memos and one card.

## Block 5. CKA: series Days 25–26 and NetworkPolicy recipes (CKA, 120 min, where: YouTube and kind cluster)

- Watch Days 25–26: service accounts and network policies.
- kind's default network plugin ignores NetworkPolicies. Install Calico as shown in [Day 26](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day26) before testing any policy.
- Work through recipes 01 to 06 in [kubernetes-network-policy-recipes](https://github.com/ahmetb/kubernetes-network-policy-recipes). Before applying each one, predict which traffic it blocks.

Done when: Six recipes done, with a prediction written before each.

## Block 6. Apply and set up freelancing (Job hunt, 30 min, where: Laptop)

- Apply to 3 roles and log them.
- Create a freelance profile on [Upwork](https://www.upwork.com/) or [Contra](https://contra.com/) with one offer: 'Kubernetes and GitOps setup on bare metal or cloud'.

Done when: 3 applications and a live freelance profile.
