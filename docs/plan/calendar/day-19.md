# Day 19: TLS: build your own CA

- Course: Course 2, the depth month
- Why: You missed CA rotation order, SNI and mTLS. Building a CA by hand makes chains and trust obvious.
- Minimum version (low-energy day): Do steps 1 to 4: root, intermediate, server certificate, then break the chain.

## Block 1. Subnetting drill (Warm-up, 15 min, where: Browser)

- Do 10 problems at [subnettingpractice.com](https://subnettingpractice.com/).

Done when: 10 problems done.

## Block 2. Read: the TLS handshake and CAs (Learn, 30 min, where: Browser)

- [The Illustrated TLS 1.3 Connection](https://tls13.xargs.org/): click through every step. (20 min)
- [OpenSSL Certificate Authority](https://jamielinux.com/docs/openssl-certificate-authority/) by Jamie Nguyen: skim 'Create the root pair' and 'Create the intermediate pair'. (10 min)

Done when: You can say why intermediates exist.

## Block 3. Lab: a CA, a broken chain, and mutual TLS (Lab, 90 min, where: Ubuntu VM)

- 1. A root CA and an intermediate:

  ```bash
  mkdir -p ~/labs/ca && cd ~/labs/ca
  openssl req -x509 -newkey rsa:2048 -nodes -keyout root.key -out root.crt -days 365 -subj "/CN=Lab Root CA"
  openssl req -newkey rsa:2048 -nodes -keyout int.key -out int.csr -subj "/CN=Lab Intermediate CA"
  printf 'basicConstraints=critical,CA:TRUE,pathlen:0\nkeyUsage=critical,keyCertSign,cRLSign\n' > int.ext
  openssl x509 -req -in int.csr -CA root.crt -CAkey root.key -CAcreateserial -out int.crt -days 180 -extfile int.ext
  ```
- 2. A server certificate for web.lab:

  ```bash
  openssl req -newkey rsa:2048 -nodes -keyout leaf.key -out leaf.csr -subj "/CN=web.lab"
  printf 'subjectAltName=DNS:web.lab\nextendedKeyUsage=serverAuth\n' > leaf.ext
  openssl x509 -req -in leaf.csr -CA int.crt -CAkey int.key -CAcreateserial -out leaf.crt -days 30 -extfile leaf.ext
  echo "127.0.0.1 web.lab" | sudo tee -a /etc/hosts
  ```
- 3. Serve it with the full chain, and verify:

  ```bash
  openssl s_server -accept 8443 -cert leaf.crt -key leaf.key -cert_chain int.crt -www &
  sleep 1
  openssl s_client -connect web.lab:8443 -servername web.lab -CAfile root.crt </dev/null 2>/dev/null | grep 'Verify return code'
  curl -s --cacert root.crt https://web.lab:8443/ | head -3
  kill %1
  ```
- 4. Break it by leaving out the intermediate (your round-one miss):

  ```bash
  openssl s_server -accept 8443 -cert leaf.crt -key leaf.key -www &
  sleep 1
  openssl s_client -connect web.lab:8443 -servername web.lab -CAfile root.crt </dev/null 2>/dev/null | grep 'Verify return code'
  curl --cacert root.crt https://web.lab:8443/
  kill %1
  ```
- Expected: 'unable to get local issuer certificate'. The server has to send the intermediate, because clients only trust the root.
- 5. Mutual TLS: the server checks the client's certificate too:

  ```bash
  openssl req -newkey rsa:2048 -nodes -keyout client.key -out client.csr -subj "/CN=alice"
  printf 'extendedKeyUsage=clientAuth\n' > client.ext
  openssl x509 -req -in client.csr -CA int.crt -CAkey int.key -CAcreateserial -out client.crt -days 30 -extfile client.ext
  cat int.crt root.crt > bundle.crt
  openssl s_server -accept 8443 -cert leaf.crt -key leaf.key -cert_chain int.crt -CAfile bundle.crt -Verify 1 -www &
  sleep 1
  curl -s --cacert root.crt https://web.lab:8443/; echo "exit code $?"            # rejected: no client cert
  curl -s --cacert root.crt --cert client.crt --key client.key https://web.lab:8443/ | head -3
  kill %1
  ```
- 6. Read the certificate's details: `openssl x509 -in leaf.crt -noout -subject -issuer -dates -ext subjectAltName`.
- Clean up: remove the web.lab line from /etc/hosts.

Done when: You saw verify code 0, then 'unable to get local issuer certificate', then mTLS reject and accept.

## Block 4. Prove it (Prove it, 15 min, where: Phone and repo)

- Voice memo: what does 'unable to get local issuer certificate' mean, and how do you fix it?
- Voice memo: the safe order for rotating a root CA without an outage.
- Write and push `cards/19-tls-pki.md`.

Done when: Two voice memos and one card.

## Block 5. CKA: series Days 30–31 (CKA, 120 min, where: YouTube and kind cluster)

- Watch Days 30–31: how DNS works, and DNS in Kubernetes. Do the tasks for [Day 30](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day30) and [Day 31](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day31).
- Extra: run `k run tmp --rm -it --image=busybox:1.36 --restart=Never -- cat /etc/resolv.conf`. Find ndots:5 and the search domains you saw on Day 5.

Done when: Both tasks done, and you found ndots:5 in a real pod.

## Block 6. Apply (Job hunt, 30 min, where: Laptop)

- Apply to 3 roles and log them.

Done when: 3 applications logged.
