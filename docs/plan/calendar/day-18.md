# Day 18: TCP queues, port exhaustion, Wireshark

- Course: Course 2, the depth month
- Why: Full accept queues and exhausted source ports cause mysterious timeouts in production. You'll cause both on purpose.
- Minimum version (low-energy day): Do only Lab part B: port exhaustion.

## Block 1. The 60-second checklist from memory (Warm-up, 15 min, where: Ubuntu VM)

- Type all 10 triage commands from memory, then check them against your card.

Done when: All 10 from memory.

## Block 2. Read: SYN and accept queues (Learn, 30 min, where: Browser)

- [SYN packet handling in the wild](https://blog.cloudflare.com/syn-packet-handling-in-the-wild/) (Cloudflare).

Done when: You can say what the SYN queue and the accept queue each hold.

## Block 3. Lab: overflow a queue, run out of ports, read a capture (Lab, 90 min, where: Ubuntu VM)

- A. Overflow an accept queue (30 min):

  ```bash
  cat > ~/labs/noaccept.py <<'EOF'
  import socket, time
  s = socket.socket()
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind(("0.0.0.0", 7000))
  s.listen(5)
  time.sleep(3600)
  EOF
  python3 ~/labs/noaccept.py &
  for i in $(seq 20); do nc -w 3 localhost 7000 </dev/null & done; sleep 1
  ss -lnt 'sport = :7000'          # Recv-Q = queued connections, Send-Q = the backlog
  nstat -az | grep -E 'ListenOverflows|ListenDrops'
  pkill -f noaccept.py
  ```
- B. Run out of source ports (35 min):

  ```bash
  docker run -d --name web -p 8081:80 nginx
  IP=$(hostname -I | awk '{print $1}')
  sudo sysctl -w net.ipv4.ip_local_port_range="40000 40100"
  for i in $(seq 300); do curl -s -o /dev/null -w '%{http_code}\n' http://$IP:8081/ || echo FAIL; done | sort | uniq -c
  ss -tan state time-wait | wc -l
  sudo sysctl -w net.ipv4.ip_local_port_range="32768 60999"
  ```
- Why it failed: every connection to the same IP and port needs its own source port, and closed ones sit in TIME-WAIT for 60 seconds.
- C. Read a capture like a pro (25 min):

  ```bash
  sudo tcpdump -ni any -w /tmp/web.pcap port 8081 &
  sleep 2; for i in $(seq 20); do curl -s -o /dev/null http://$IP:8081/; done
  sudo pkill tcpdump
  tshark -r /tmp/web.pcap -q -z conv,tcp | head -20
  tshark -r /tmp/web.pcap -Y 'tcp.flags.reset == 1 || tcp.analysis.retransmission'
  ```
- On the PC, pull the capture out with `incus file pull lab-ubuntu/tmp/web.pcap ~/` and open it in Wireshark (`sudo pacman -S wireshark-qt`). Look at Statistics, Conversations, then Analyze, Expert Information.
- Clean up: `docker rm -f web`.

Done when: ListenOverflows went up, and curl failed once the port range ran out.

## Block 4. Prove it (Prove it, 15 min, where: Phone and repo)

- Voice memo: the symptoms and fixes of a full accept queue vs source port exhaustion.
- Write and push `cards/18-tcp-queues-ports.md`.

Done when: One voice memo and one card.

## Block 5. CKA: series Days 28–29 (CKA, 120 min, where: YouTube and kind cluster)

- If yesterday's kubeadm cluster isn't finished: `incus start local:cp1 local:w1 local:w2`, finish it, then `incus stop local:cp1 local:w1 local:w2`.
- Watch Days 28–29: Docker storage and Kubernetes storage. Do the tasks for [Day 28](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day28) and [Day 29](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day29).
- Write this down: ReadWriteOnce means one node, not one pod. ReadWriteOncePod means one pod. You missed this in the interview.

Done when: Both tasks done.

## Block 6. Apply and ask for a referral (Job hunt, 30 min, where: Laptop)

- Apply to 3 roles and log them.
- Send one referral message.

Done when: 3 applications and 1 referral message.
