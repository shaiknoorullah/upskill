# Day 23: AppArmor and auditd

- Course: Course 2, the depth month
- Why: Mandatory access control is how even a root process gets told no. Ubuntu uses AppArmor, and your containers already run under it.
- Minimum version (low-energy day): Do only Lab part A: aa-status and the docker-default profile.

## Block 1. jq on kubectl (Warm-up, 15 min, where: kind cluster)

- Which pods run as root?

  ```bash
  k get pods -A -o json | jq -r '.items[] | select(.spec.securityContext.runAsNonRoot != true) | .metadata.namespace + "/" + .metadata.name'
  ```

Done when: Query ran.

## Block 2. Read: AppArmor (Learn, 30 min, where: Browser)

- [AppArmor](https://wiki.archlinux.org/title/AppArmor) (Arch Wiki): read 'Usage', 'Creating new profiles', and the part about reading log messages.

Done when: You can say what complain mode and enforce mode do.

## Block 3. Lab: profile a script, then audit a file (Lab, 90 min, where: Ubuntu VM)

- A. What's already confined (15 min):

  ```bash
  sudo aa-status | head -20
  docker run --rm alpine cat /proc/1/attr/current      # docker-default (enforce)
  ```
- B. Profile a script (45 min). Create it:

  ```bash
  sudo tee /usr/local/bin/reader.sh >/dev/null <<'EOF'
  #!/usr/bin/env bash
  cat /etc/hostname
  head -1 /etc/shadow
  EOF
  sudo chmod +x /usr/local/bin/reader.sh
  sudo /usr/local/bin/reader.sh           # root can read both files
  ```
- Run `sudo aa-genprof /usr/local/bin/reader.sh`. In a second terminal, run `sudo /usr/local/bin/reader.sh`. Back in the first, press S to scan. Allow /etc/hostname, deny /etc/shadow, then press F to finish.
- Run `sudo /usr/local/bin/reader.sh` again. Root now gets 'Permission denied' on /etc/shadow.
- C. Complain vs enforce (15 min):

  ```bash
  sudo aa-complain /usr/local/bin/reader.sh; sudo /usr/local/bin/reader.sh   # allowed, but logged
  sudo journalctl -k --since "5 min ago" | grep -i apparmor | tail -3
  sudo aa-enforce /usr/local/bin/reader.sh
  ```
- D. Audit who touches /etc/passwd (15 min):

  ```bash
  sudo auditctl -w /etc/passwd -p wa -k passwd-watch
  sudo touch /etc/passwd
  sudo ausearch -k passwd-watch -i | tail -5
  sudo auditctl -D
  ```

Done when: Root got 'Permission denied' on /etc/shadow because of your profile.

## Block 4. Prove it (Prove it, 15 min, where: Phone and repo)

- Voice memo: AppArmor vs SELinux, in two sentences each.
- Voice memo: complain vs enforce, and where you see denials.
- Write and push `cards/23-apparmor-audit.md`.

Done when: Two voice memos and one card.

## Block 5. CKA: series Days 43–44 (CKA, 120 min, where: YouTube and kind cluster)

- Watch Days 43–44: Helm and Kustomize. Do the tasks for [Day 43](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day43) and [Day 44](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day44).
- Exam habit: during the exam you can use kubernetes.io. Practise finding its Kustomize page in under 30 seconds.

Done when: Both tasks done.

## Block 6. Apply and ask for a referral (Job hunt, 30 min, where: Laptop)

- Apply to 3 roles and log them.
- Send one referral message.

Done when: 3 applications and 1 referral message.
