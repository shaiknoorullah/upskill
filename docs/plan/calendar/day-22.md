# Day 22: Capabilities and seccomp

- Course: Course 2, the depth month
- Why: 'Drop ALL capabilities' and 'seccomp RuntimeDefault' are the two pod-security settings interviewers ask about most, and you didn't know them.
- Minimum version (low-energy day): Do only Lab part C: the seccomp profile.

## Block 1. Subnetting drill (Warm-up, 15 min, where: Browser)

- Do 10 problems at [subnettingpractice.com](https://subnettingpractice.com/).

Done when: 10 problems done.

## Block 2. Read: seccomp and capabilities (Learn, 30 min, where: Browser)

- [Seccomp security profiles for Docker](https://docs.docker.com/engine/security/seccomp/). (15 min)
- [Capabilities](https://wiki.archlinux.org/title/Capabilities) (Arch Wiki). (15 min)

Done when: You can say what seccomp filters and what capabilities split up.

## Block 3. Lab: what a container is allowed to do (Lab, 90 min, where: Ubuntu VM)

- A. A container's capabilities (30 min):

  ```bash
  docker run --rm alpine grep Cap /proc/1/status
  capsh --decode=00000000a80425fb                 # use the CapEff value you just got
  docker run --rm --cap-drop ALL alpine grep CapEff /proc/1/status
  docker run --rm alpine ip link add dummy0 type dummy                        # fails
  docker run --rm --cap-add NET_ADMIN alpine ip link add dummy0 type dummy   # works
  ```
- B. Why privileged is dangerous (20 min):

  ```bash
  docker run --rm alpine ls /dev | wc -l
  docker run --rm --privileged alpine ls /dev | wc -l     # every device on the host
  docker run --rm --privileged alpine grep CapEff /proc/1/status
  docker run --rm --security-opt no-new-privileges alpine grep NoNewPrivs /proc/self/status
  ```
- no_new_privs is what `allowPrivilegeEscalation: false` sets in a pod.
- C. A seccomp profile that blocks mkdir (30 min):

  ```bash
  cat > ~/labs/no-mkdir.json <<'EOF'
  {
    "defaultAction": "SCMP_ACT_ALLOW",
    "syscalls": [
      { "names": ["mkdir", "mkdirat"], "action": "SCMP_ACT_ERRNO" }
    ]
  }
  EOF
  docker run --rm --security-opt seccomp=$HOME/labs/no-mkdir.json alpine mkdir /tmp/x   # Operation not permitted
  docker run --rm alpine grep Seccomp /proc/self/status                                  # 2 = filtered
  docker run --rm --security-opt seccomp=unconfined alpine grep Seccomp /proc/self/status  # 0 = off
  ```
- D. Which syscalls does a program need? (10 min):

  ```bash
  strace -f -c -o /tmp/sc.txt ls /; head -20 /tmp/sc.txt
  ```

Done when: Your profile blocked mkdir.

## Block 4. Prove it (Prove it, 15 min, where: Phone and repo)

- Voice memo: what does seccomp RuntimeDefault do, and why turn it on for every pod?
- Voice memo: what is CAP_SYS_ADMIN, and why is a privileged pod basically root on the node?
- Write and push `cards/22-caps-seccomp.md`.

Done when: Two voice memos and one card.

## Block 5. CKA: Gateway API and StatefulSets (CKA, 120 min, where: Browser and kind cluster)

- Gateway API isn't in the video series, but it's on the exam. Read the [migration guide from Ingress](https://gateway-api.sigs.k8s.io/guides/getting-started/migrating-from-ingress/). (20 min)
- Install one Gateway API implementation on kind and route an HTTPRoute to a Service. Envoy Gateway's quickstart works on kind: go to gateway.envoyproxy.io, then Docs, then Quickstart. (60 min)
- Watch series Day 45 (StatefulSets) and do [its task](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day45). (40 min)

Done when: An HTTPRoute serves traffic, and the StatefulSet task is done.

## Block 6. Apply (Job hunt, 30 min, where: Laptop)

- Apply to 3 roles and log them.

Done when: 3 applications logged.
