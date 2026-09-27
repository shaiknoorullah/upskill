# Day 10: LVM and RAID

- Course: Course 2, the depth month
- Why: Growing a full disk on a live server is a classic interview question, and you'll do it for real on your own lab VM.
- Minimum version (low-energy day): Do only the LVM part: create, fill, grow while mounted.

## Block 1. Subnetting drill (Warm-up, 15 min, where: Browser)

- Do 10 problems at [subnettingpractice.com](https://subnettingpractice.com/).

Done when: 10 problems done.

## Block 2. Read: LVM and RAID (Learn, 30 min, where: Browser)

- [LVM](https://wiki.archlinux.org/title/LVM) (Arch Wiki): read 'Background' and 'Resizing'. (20 min)
- [RAID](https://wiki.archlinux.org/title/RAID) (Arch Wiki): read 'RAID levels'. (10 min)

Done when: You can say what a PV, a VG and an LV are.

## Block 3. Lab: LVM and RAID on fake disks (Lab, 90 min, where: Ubuntu VM)

- A. Make three fake disks (5 min):

  ```bash
  for i in 1 2 3; do truncate -s 1G ~/d$i.img; done
  L1=$(sudo losetup -f --show ~/d1.img); L2=$(sudo losetup -f --show ~/d2.img); L3=$(sudo losetup -f --show ~/d3.img)
  echo $L1 $L2 $L3
  ```
- B. LVM: create, fill, then grow while mounted (35 min):

  ```bash
  sudo pvcreate $L1 $L2
  sudo vgcreate labvg $L1 $L2
  sudo lvcreate -n data -L 1G labvg
  sudo mkfs.ext4 -q /dev/labvg/data
  sudo mkdir -p /mnt/lv && sudo mount /dev/labvg/data /mnt/lv
  sudo dd if=/dev/zero of=/mnt/lv/fill bs=1M count=900 status=none; df -h /mnt/lv
  sudo lvextend -r -L +600M /dev/labvg/data; df -h /mnt/lv    # bigger, still mounted
  sudo pvs; sudo vgs; sudo lvs
  ```
- Tear down the LVM setup:

  ```bash
  sudo umount /mnt/lv && sudo vgremove -y labvg && sudo pvremove $L1 $L2
  ```
- C. RAID1: lose a disk, keep the data (45 min). Answer y if mdadm asks to continue:

  ```bash
  sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 $L1 $L2 --run
  cat /proc/mdstat
  sudo mkfs.ext4 -q /dev/md0 && sudo mkdir -p /mnt/md && sudo mount /dev/md0 /mnt/md
  echo "still here" | sudo tee /mnt/md/proof.txt
  sudo mdadm /dev/md0 --fail $L1; cat /proc/mdstat      # one side missing: degraded
  cat /mnt/md/proof.txt                                 # the data is still readable
  sudo mdadm /dev/md0 --remove $L1 && sudo mdadm /dev/md0 --add $L3
  watch -n1 cat /proc/mdstat                            # rebuilding onto the third disk
  ```
- Clean up (5 min):

  ```bash
  sudo umount /mnt/md; sudo mdadm --stop /dev/md0
  sudo losetup -d $L1 $L2 $L3; rm ~/d1.img ~/d2.img ~/d3.img
  ```

Done when: The volume grew while mounted, and proof.txt survived a failed disk.

## Block 4. Prove it (Prove it, 15 min, where: Phone and repo)

- Voice memo: a VM's disk is full. Walk through growing it with no downtime: the hypervisor's virtual disk (on Incus: `incus config device override lab-ubuntu root size=60GiB`), then the partition, the PV, the LV and the filesystem.
- Write and push `cards/10-lvm-raid.md`.

Done when: One voice memo and one card.

## Block 5. CKA: series Days 11–13 (CKA, 120 min, where: YouTube and kind cluster)

- Watch Days 11–13: multi-container pods, DaemonSets, Jobs and CronJobs, static pods and manual scheduling.
- Do the tasks for [Day 11](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day11), [Day 12](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day12) and [Day 13](https://github.com/piyushsachdeva/CKA-2024/tree/main/Resources/Day13).
- Extra: find where kind keeps the static pod manifests. Run `docker ps` to get your control-plane container's name, then `docker exec <name> ls /etc/kubernetes/manifests`.

Done when: All three tasks done.

## Block 6. Apply (Job hunt, 30 min, where: Laptop)

- Apply to 3 roles from your alerts and log each one in the tracker.
- Before each application, spend 5 minutes tailoring the top 3 lines of your resume to the job description.

Done when: 3 applications logged.
