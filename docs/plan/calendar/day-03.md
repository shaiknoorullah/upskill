# Day 3: Files, disks and permissions

- Course: Course 1, the 80/20 week
- Why: The 'df says full, du says empty' question caught you in round one, and capabilities are what 'drop ALL' in a pod actually means.
- Minimum version (low-energy day): Do only Lab part A: the deleted-but-open file.

## Block 1. jq drill (Warm-up, 20 min, where: Ubuntu VM)

- Pull some real JSON and query it:

  ```bash
  curl -s 'https://api.github.com/repos/kubernetes/kubernetes/releases?per_page=10' > ~/labs/rel.json
  jq -r '.[].tag_name' ~/labs/rel.json
  jq -r '.[] | select(.prerelease | not) | .tag_name' ~/labs/rel.json
  jq -r '.[] | "\(.published_at[0:10]) \(.tag_name)"' ~/labs/rel.json
  ```
- Now write your own: list only releases published in 2026. Hint: `startswith`.

Done when: Three queries ran and you wrote a fourth yourself.

## Block 2. Read: permissions, capabilities, disk space (Learn, 60 min, where: Browser)

- [File permissions and attributes](https://wiki.archlinux.org/title/File_permissions_and_attributes) (Arch Wiki): read 'Viewing permissions', the table of what each bit means on a directory, and the special bits. (25 min)
- [capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html): read the intro, then find CAP_CHOWN, CAP_NET_BIND_SERVICE, CAP_NET_ADMIN and CAP_SYS_ADMIN in the list. (20 min)
- On the VM: read `man df` for the `-i` flag, and in `man lsof` search for `+L`. (15 min)

Done when: You can say what the x bit means on a directory.

## Block 3. Lab: full disks, permissions, capabilities (Lab, 150 min, where: Ubuntu VM)

- A. The disk that's full but empty (40 min). Make a small filesystem and fill it from a process that keeps the file open:

  ```bash
  truncate -s 200M ~/disk.img && mkfs.ext4 -q ~/disk.img
  sudo mkdir -p /mnt/lab && sudo mount -o loop ~/disk.img /mnt/lab && sudo chown $USER /mnt/lab
  nohup bash -c 'exec 3>/mnt/lab/app.log; for i in $(seq 150); do head -c 1M /dev/urandom >&3; done; sleep 3600' >/dev/null 2>&1 &
  sleep 5; df -h /mnt/lab
  ```
- Delete the log and watch df and du disagree:

  ```bash
  rm /mnt/lab/app.log
  df -h /mnt/lab                          # still ~150M used
  du -sh /mnt/lab                         # almost nothing
  sudo lsof -nP +L1 | grep /mnt/lab       # a process still holds it open on fd 3
  ```
- Free the space without killing the process, then clean up:

  ```bash
  sudo sh -c ': > /proc/<pid>/fd/3'     # truncate through /proc
  df -h /mnt/lab                          # space is back
  kill <pid>
  ```
- B. Run out of inodes (25 min):

  ```bash
  truncate -s 50M ~/tiny.img && mkfs.ext4 -q -N 500 ~/tiny.img
  sudo mkdir -p /mnt/tiny && sudo mount -o loop ~/tiny.img /mnt/tiny && sudo chown $USER /mnt/tiny
  for i in $(seq 1000); do touch /mnt/tiny/f$i || break; done
  df -h /mnt/tiny; df -i /mnt/tiny        # space left, inodes at 100%
  ```
- C. Directory permission puzzles (45 min). Before each command, predict: works or 'Permission denied'?

  ```bash
  sudo useradd -m tester
  sudo mkdir -p /srv/perm/d && echo secret | sudo tee /srv/perm/d/file >/dev/null
  sudo chmod 644 /srv/perm/d/file
  sudo chmod 744 /srv/perm/d; sudo -u tester ls /srv/perm/d; sudo -u tester cat /srv/perm/d/file
  sudo chmod 711 /srv/perm/d; sudo -u tester ls /srv/perm/d; sudo -u tester cat /srv/perm/d/file
  ```
- Read the results: r without x lets you list names but not open anything. x without r lets you open a file only if you already know its name.
- The sticky bit and setgid directories:

  ```bash
  ls -ld /tmp                                        # the t at the end is the sticky bit
  touch /tmp/mine; sudo -u tester rm -f /tmp/mine    # Operation not permitted
  sudo groupadd -f devs && sudo mkdir -p /srv/team && sudo chgrp devs /srv/team && sudo chmod 2775 /srv/team
  sudo touch /srv/team/x && ls -l /srv/team          # group is devs: inherited from the directory
  ```
- D. Capabilities (40 min):

  ```bash
  python3 -m http.server 80        # PermissionError: ports below 1024 need a capability
  cp /usr/bin/python3.12 ~/py && sudo setcap 'cap_net_bind_service=+ep' ~/py
  getcap ~/py
  ~/py -m http.server 80           # works without root. Ctrl-C to stop
  rm ~/py
  docker run --rm alpine chown 1 /tmp && echo "chown works"
  docker run --rm --cap-drop ALL alpine chown 1 /tmp    # Operation not permitted
  ```
- Clean up (5 min):

  ```bash
  sudo umount /mnt/lab /mnt/tiny; rm ~/disk.img ~/tiny.img
  ```

Done when: You found the deleted file with lsof and freed the space without a restart.

## Block 4. Prove it (Prove it, 30 min, where: Phone and repo)

- Voice memo: df says the disk is full, du says half. Why, and how do you fix it without a restart?
- Voice memo: what do r, w and x mean on a directory?
- Voice memo: what does 'drop ALL capabilities' do to a pod, and what might break?
- Voice memo: how can a disk be 'full' while df -h shows free space?
- Write and push `cards/03-files-permissions.md`.

Done when: Four voice memos recorded and one card pushed.
