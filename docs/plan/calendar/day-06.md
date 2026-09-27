# Day 6: Networking II: TCP, NAT and firewalls

- Course: Course 1, the 80/20 week
- Why: RST vs timeout, TIME_WAIT and MTU were all misses. Together they explain almost every 'the connection just hangs' incident.
- Minimum version (low-energy day): Do only Lab part B: RST vs timeout.

## Block 1. jq drill on Docker's JSON (Warm-up, 20 min, where: Ubuntu VM)

- Start a web container and query its JSON:

  ```bash
  docker run -d --name web -p 8081:80 nginx
  docker inspect web | jq -r '.[0].NetworkSettings.Networks.bridge.IPAddress'
  docker inspect web | jq '.[0].HostConfig.PortBindings'
  docker inspect web | jq -r '.[0].State | "\(.Status) pid=\(.Pid)"'
  ```
- Leave the web container running. You'll use it in Lab part D.

Done when: Three queries ran.

## Block 2. Read: TIME_WAIT, MTU, the packet flow (Learn, 60 min, where: Browser)

- [Coping with the TCP TIME-WAIT state on busy Linux servers](https://vincent.bernat.ch/en/blog/2014-tcp-time-wait-state-linux) by Vincent Bernat: read through the 'Solutions' section. (25 min)
- [Path MTU discovery in practice](https://blog.cloudflare.com/path-mtu-discovery-in-practice/) (Cloudflare). (15 min)
- [Netfilter on Wikipedia](https://en.wikipedia.org/wiki/Netfilter): study the packet flow diagram until you can sketch PREROUTING, INPUT, FORWARD, OUTPUT and POSTROUTING from memory. (20 min)

Done when: You can sketch the five netfilter hooks on paper.

## Block 3. Lab: handshakes, RSTs, MTU, NAT (Lab, 150 min, where: Ubuntu VM)

- A. Watch a TCP conversation (40 min). Terminal 1:

  ```bash
  sudo tcpdump -ni any 'tcp port 8000'
  ```
- Terminal 2:

  ```bash
  python3 -m http.server 8000 &
  curl -s localhost:8000 >/dev/null
  ss -tan state time-wait | grep 8000
  ```
- In the capture, find the SYN, SYN-ACK, ACK, the request, the response and the FINs. Whichever side sent the first FIN is the side holding TIME-WAIT.
- B. RST vs timeout (40 min). Keep tcpdump running on the port you're testing:

  ```bash
  curl -m 5 localhost:9999          # instant 'Connection refused': the kernel replied with RST
  sudo iptables -I INPUT -p tcp --dport 8000 -j DROP
  curl -m 5 localhost:8000          # hangs, then times out: SYNs silently dropped
  sudo iptables -R INPUT 1 -p tcp --dport 8000 -j REJECT --reject-with tcp-reset
  curl -m 5 localhost:8000          # refused again, this time by the firewall
  sudo iptables -D INPUT 1
  ```
- In tcpdump, an RST shows as flags [R]. The DROP case shows the same SYN sent again and again.
- C. MTU facts (30 min):

  ```bash
  ip link show | grep mtu
  ping -c1 -M do -s 1472 1.1.1.1    # 1472 + 28 header bytes = 1500: fits
  ping -c1 -M do -s 1473 1.1.1.1    # 'message too long': bigger than your MTU
  tracepath -n 1.1.1.1              # the path MTU along the route
  ```
- You'll build a real MTU black hole on Day 16. For now, explain to yourself why a VPN's smaller MTU breaks only big packets.
- D. NAT and conntrack (40 min):

  ```bash
  IP=$(hostname -I | awk '{print $1}')
  sudo iptables -t nat -L -n -v | less     # find MASQUERADE for 172.17.0.0/16 and the DNAT for 8081
  curl -s http://$IP:8081 >/dev/null
  sudo conntrack -L -p tcp --dport 8081    # the reply side shows the container's IP: that's the DNAT
  sudo conntrack -S                        # look at insert_failed and drop
  cat /proc/sys/net/netfilter/nf_conntrack_count /proc/sys/net/netfilter/nf_conntrack_max
  cat /proc/sys/net/ipv4/ip_local_port_range
  ```
- Clean up (5 min):

  ```bash
  docker rm -f web; kill %1
  ```

Done when: You can point to an RST and to repeated SYNs in a capture, and found a DNAT entry in conntrack.

## Block 4. Prove it (Prove it, 30 min, where: Phone and repo)

- Voice memo: a connection is refused instantly vs hangs until timeout. What does each tell you?
- Voice memo: which side ends up in TIME-WAIT, and why do busy proxies run out of ports?
- Voice memo: over a VPN, ping and small requests work but big downloads hang. Why, and how do you fix it?
- Voice memo: how does a request to a published Docker port reach the container?
- Write and push `cards/06-tcp-nat.md`.

Done when: Four voice memos recorded and one card pushed.
