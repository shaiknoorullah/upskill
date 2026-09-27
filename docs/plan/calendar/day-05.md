# Day 5: Networking I: addresses, routes, DNS

- Course: Course 1, the 80/20 week
- Why: Subnetting and ndots were misses, and 'it's always DNS' is the incident you'll debug most often.
- Minimum version (low-energy day): Do only Lab part B: the DNS resolution path.

## Block 1. Shell drill: safe file handling (Warm-up, 20 min, where: Ubuntu VM)

- Read pitfalls 6 to 10 on [Bash Pitfalls](https://mywiki.wooledge.org/BashPitfalls).
- Print the 5 largest files in /var/log, safely handling any filename:

  ```bash
  sudo find /var/log -type f -printf '%s\t%p\n' | sort -nr | head -5
  ```

Done when: You can say why find -printf is safer than parsing ls.

## Block 2. Read: DNS, ndots, name resolution, routes (Learn, 60 min, where: Browser)

- [How DNS works](https://howdns.works/) (a comic). (10 min)
- [Kubernetes DNS resolution and ndots](https://pracucci.com/kubernetes-dns-resolution-ndots-options-and-why-it-may-affect-application-performances.html) by Marco Pracucci. (15 min)
- [resolv.conf(5)](https://man7.org/linux/man-pages/man5/resolv.conf.5.html): read `search` and `options ndots`. (10 min)
- [nsswitch.conf(5)](https://man7.org/linux/man-pages/man5/nsswitch.conf.5.html): read how the `hosts:` line works. (10 min)
- [ip-route(8)](https://man7.org/linux/man-pages/man8/ip-route.8.html): skim the EXAMPLES section. (15 min)

Done when: You can explain what ndots:5 does to a lookup for 'api.github.com'.

## Block 3. Lab: routes, the resolution path, ndots (Lab, 150 min, where: Ubuntu VM)

- A. Addresses and routes (40 min):

  ```bash
  ip -br addr
  ip route
  ip route get 1.1.1.1         # which interface and gateway the kernel picks
  ip neigh                     # the ARP cache
  ss -tulpn                    # what's listening
  ```
- Add a test network and ask the kernel how it would route there:

  ```bash
  sudo ip link add dummy0 type dummy
  sudo ip addr add 10.99.0.1/24 dev dummy0 && sudo ip link set dummy0 up
  ip route get 10.99.0.77
  sudo ip link del dummy0
  ```
- Work out 10.99.0.64/27 on paper first (network, broadcast, first and last host), then check:

  ```bash
  ipcalc 10.99.0.64/27
  ```
- B. The DNS resolution path (60 min):

  ```bash
  grep hosts /etc/nsswitch.conf
  cat /etc/resolv.conf; resolvectl status | head -20
  echo "10.99.0.10 fakehost.lab" | sudo tee -a /etc/hosts
  getent hosts fakehost.lab    # works: nsswitch sends it to /etc/hosts
  dig fakehost.lab             # NXDOMAIN: dig only asks DNS servers
  ```
- Break name resolution the way SadServers 'Jakarta' does, then fix it:

  ```bash
  sudo cp /etc/nsswitch.conf /etc/nsswitch.conf.bak
  sudo sed -i 's/^hosts:.*/hosts: dns/' /etc/nsswitch.conf
  getent hosts fakehost.lab    # fails now
  sudo cp /etc/nsswitch.conf.bak /etc/nsswitch.conf
  ```
- Watch ndots:5 multiply queries. In terminal 1:

  ```bash
  sudo tcpdump -ni any udp port 53
  ```
- In terminal 2, run both commands and count the queries each one causes:

  ```bash
  docker run --rm --dns 1.1.1.1 --dns-search svc.cluster.local --dns-search cluster.local \
    --dns-option ndots:5 ubuntu getent hosts api.github.com
  docker run --rm --dns 1.1.1.1 --dns-search svc.cluster.local --dns-search cluster.local \
    --dns-option ndots:5 ubuntu getent hosts api.github.com.
  ```
- The second one has a trailing dot, which skips the search list entirely.
- C. Tools (45 min):

  ```bash
  dig +short github.com
  dig +trace github.com | less                     # root, then .com, then GitHub's servers
  dig github.com @1.1.1.1 | grep -A1 'ANSWER SECTION'   # run it twice: the TTL counts down
  tracepath -n 1.1.1.1                             # shows the path MTU (pmtu)
  mtr -rwc 10 1.1.1.1
  curl -sv https://example.com -o /dev/null 2>&1 | less   # DNS, connect, TLS, HTTP in order
  ```
- Spend 10 minutes at [messwithdns.net](https://messwithdns.net/): create a record and watch the queries arrive.
- Clean up: remove the fakehost.lab line from /etc/hosts.

Done when: You watched one lookup turn into several with ndots:5, and into one with the trailing dot.

## Block 4. Prove it (Prove it, 30 min, where: Phone and repo)

- Voice memo: a pod runs `curl http://api` with ndots:5. Which DNS queries happen, in order?
- Voice memo: why can `dig` work while the app can't resolve the name, or the other way round?
- Voice memo: usable hosts in a /26, /27 and /28, and why you subtract two.
- Voice memo: what does `ip route get` tell you, and when do you use it?
- Write and push `cards/05-dns-routing.md`.

Done when: Four voice memos recorded and one card pushed.
