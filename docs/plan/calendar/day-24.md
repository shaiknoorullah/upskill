# Day 24: SELinux on Rocky

- Course: Course 2, the depth month
- Why: A 403 on a file with correct permissions is usually SELinux. Knowing restorecon beats 'setenforce 0' in any interview.
- Minimum version (low-energy day): Do Lab parts A and B only.

## Block 1. Subnetting drill (Warm-up, 15 min, where: Browser)

- Do 10 problems at [subnettingpractice.com](https://subnettingpractice.com/).

Done when: 10 problems done.

## Block 2. Read: SELinux (Learn, 30 min, where: Browser and Rocky VM)

- [The SELinux Coloring Book](https://github.com/mairin/selinux-coloring-book). (15 min)
- Start Rocky from the PC with `incus start lab-rocky`, open it with `rocky`, then run `man semanage-fcontext` and read the EXAMPLES section. (15 min)

Done when: You can say what a type label is.

## Block 3. Lab: break a web server with a label, then fix it (Lab, 90 min, where: Rocky VM)

- A. Look around (15 min):

  ```bash
  getenforce; sestatus
  sudo systemctl enable --now httpd && sudo firewall-cmd --add-service=http
  ls -Z /var/www/html; ps -eZ | grep httpd | head -2; id -Z
  ```
- B. Break it with the wrong label (35 min):

  ```bash
  echo hello | sudo tee /root/index.html
  sudo mv /root/index.html /var/www/html/
  curl -s -o /dev/null -w '%{http_code}\n' localhost/index.html     # 403
  ls -Z /var/www/html/index.html                                    # admin_home_t: wrong label
  sudo ausearch -m AVC -ts recent | tail -5
  sudo sealert -a /var/log/audit/audit.log | head -30
  sudo restorecon -v /var/www/html/index.html
  curl -s localhost/index.html                                      # hello
  ```
- C. A label rule that survives a relabel (20 min):

  ```bash
  sudo mkdir -p /srv/site && echo site | sudo tee /srv/site/index.html
  ls -Z /srv/site
  sudo semanage fcontext -a -t httpd_sys_content_t '/srv/site(/.*)?'
  sudo restorecon -Rv /srv/site && ls -Z /srv/site
  ```
- D. Booleans (20 min):

  ```bash
  getsebool -a | grep httpd_can_network_connect
  sudo semanage boolean -l | grep httpd_can_network_connect
  ```
- Say out loud when you'd run `sudo setsebool -P httpd_can_network_connect on`: a reverse proxy that needs to talk to a backend.
- Done for today: `incus stop lab-rocky`.

Done when: You fixed the 403 with restorecon, not setenforce 0.

## Block 4. Prove it (Prove it, 15 min, where: Phone and repo)

- Voice memo: a file has 644 permissions but the web server returns 403 on RHEL. What do you check?
- Voice memo: why you never run `setenforce 0` in production.
- Write and push `cards/24-selinux.md`.

Done when: Two voice memos and one card.

## Block 5. CKA: CRDs, operators and reconciliation (CKA, 120 min, where: Browser and kind cluster)

- Read [Custom Resources](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) on kubernetes.io. (20 min)
- Install cert-manager with Helm and watch a controller reconcile (60 min):

  ```bash
  helm repo add jetstack https://charts.jetstack.io && helm repo update
  helm install cert-manager jetstack/cert-manager -n cert-manager --create-namespace --set crds.enabled=true
  k get crd | grep cert-manager
  cat <<'EOF' | k apply -f -
  apiVersion: cert-manager.io/v1
  kind: Issuer
  metadata: {name: selfsigned}
  spec: {selfSigned: {}}
  ---
  apiVersion: cert-manager.io/v1
  kind: Certificate
  metadata: {name: demo}
  spec:
    secretName: demo-tls
    dnsNames: [demo.lab]
    issuerRef: {name: selfsigned}
  EOF
  sleep 10; k get certificate demo; k get secret demo-tls
  k delete secret demo-tls; sleep 10; k get secret demo-tls     # the controller recreated it
  ```
- That last line is level-triggered reconciliation, which you missed in the interview. Write one sentence explaining it. (20 min)
- Run `k get certificaterequest -o yaml | grep -A6 ownerReferences`. That's the wiring garbage collection uses. (20 min)

Done when: The Secret came back on its own.

## Block 6. Apply (Job hunt, 30 min, where: Laptop)

- Apply to 3 roles and log them.

Done when: 3 applications logged.
