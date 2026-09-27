# Day 0: Set up everything

- Course: Setup day
- Why: Every bit of setup you finish today is friction you won't hit on the days your brain is looking for an excuse to stop. The laptop becomes your always-on lab server, and the PC, where you sit, also hosts the Kubernetes cluster VMs.
- Minimum version (low-energy day): Set up Incus on the laptop, create lab-ubuntu and install its packages. Everything else can wait until the day it's needed.

## Block 1. Turn the laptop into your lab server (Setup, 60 min, where: Laptop)

- Plug the laptop into power, and into Ethernet if you can. Give it a fixed address with a DHCP reservation on your router, and write that IP down.
- Keep it awake with the lid closed, and let the PC log in over SSH:

  ```bash
  sudo mkdir -p /etc/systemd/logind.conf.d
  printf '[Login]\nHandleLidSwitch=ignore\nHandleLidSwitchExternalPower=ignore\n' | sudo tee /etc/systemd/logind.conf.d/server.conf
  sudo systemctl restart systemd-logind      # may end your graphical session; that's fine
  sudo pacman -S --needed openssh && sudo systemctl enable --now sshd
  ```
- Check hardware virtualization: `lscpu | grep -i virtualization` should show VT-x or AMD-V, and `ls -l /dev/kvm` should exist. If not, turn virtualization on in the BIOS/UEFI settings.
- Install and set up Incus:

  ```bash
  sudo pacman -S --needed incus qemu-full edk2-ovmf
  echo "root:1000000:1000000000" | sudo tee -a /etc/subuid /etc/subgid
  sudo systemctl enable --now incus.socket
  sudo usermod -aG incus-admin $USER
  newgrp incus-admin
  incus admin init --minimal
  incus profile set default security.secureboot=false   # Arch ships no signed UEFI firmware
  ```
- Create the two lab VMs:

  ```bash
  incus launch images:ubuntu/24.04 lab-ubuntu --vm -c limits.cpu=2 -c limits.memory=4GiB -d root,size=40GiB
  incus launch images:rockylinux/9 lab-rocky --vm -c limits.cpu=2 -c limits.memory=2GiB -d root,size=20GiB
  sleep 60; incus list          # both RUNNING, each with an IPv4 address
  ```
- Laptop has 16 GB of RAM or more? Give lab-ubuntu more room: `incus config set lab-ubuntu limits.memory=6GiB && incus restart lab-ubuntu`.
- If Docker also runs on this machine and the VMs get no IPv4 address or no internet, Docker's firewall is blocking the Incus bridge. Fix it with `sudo iptables -I DOCKER-USER -i incusbr0 -j ACCEPT` and `sudo iptables -I DOCKER-USER -o incusbr0 -j ACCEPT` (again after each reboot).
- Create your own user, called me, inside each VM:

  ```bash
  incus exec lab-ubuntu -- sh -c 'useradd -m -s /bin/bash -G sudo me && echo "me ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/me'
  incus exec lab-rocky -- sh -c 'useradd -m -G wheel me && echo "me ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/me'
  ```
- Let the PC in:

  ```bash
  incus config set core.https_address :8443
  incus config trust add pc        # prints a one-time token for the PC
  ```

Done when: `incus list` shows both VMs running, and the laptop stays on with its lid closed.

## Block 2. Set up the PC: your desk and the cluster host (Setup, 25 min, where: PC)

- Install Incus here too. The PC will host the Kubernetes cluster VMs from Day 17:

  ```bash
  sudo pacman -S --needed incus qemu-full edk2-ovmf
  echo "root:1000000:1000000000" | sudo tee -a /etc/subuid /etc/subgid
  sudo systemctl enable --now incus.socket
  sudo usermod -aG incus-admin $USER
  newgrp incus-admin
  incus admin init --minimal
  incus profile set default security.secureboot=false
  ```
- Connect to the laptop and make it the default target:

  ```bash
  incus remote add laptop <paste the token>
  incus remote switch laptop
  incus list              # the laptop's VMs
  incus list local:       # the PC's own VMs (none yet)
  ```
- From here on, plain `incus` commands go to the laptop. Anything starting with `local:` means the PC itself.
- Add two shortcuts (use ~/.zshrc instead if you run zsh), and an SSH key for the laptop:

  ```bash
  echo "alias lab='incus exec laptop:lab-ubuntu -- su -l me'" >> ~/.bashrc
  echo "alias rocky='incus exec laptop:lab-rocky -- su -l me'" >> ~/.bashrc
  source ~/.bashrc
  ssh-copy-id <your-user>@<laptop IP>
  ```
- Now `lab` drops you into lab-ubuntu and `rocky` into lab-rocky. Every lab in this calendar runs inside a VM, so neither of your real machines ever breaks.

Done when: Typing `lab` on the PC gives you a shell inside lab-ubuntu on the laptop.

## Block 3. Install every tool you'll need this month (Setup, 30 min, where: Both VMs)

- Run `lab`, then `uname -r`. If the kernel name doesn't end in `-generic`, run `sudo apt update && sudo apt install -y linux-generic && sudo reboot`, wait a minute, and run `lab` again.
- Inside lab-ubuntu, paste this whole block:

  ```bash
  mkdir -p ~/labs
  sudo apt update
  sudo DEBIAN_FRONTEND=noninteractive apt install -y build-essential git vim tmux curl jq \
    shellcheck strace ltrace lsof psmisc procps sysstat iotop htop smem tcpdump tshark \
    dnsutils ipcalc iputils-tracepath mtr-tiny netcat-openbsd socat iperf3 nmap conntrack \
    nftables fio lvm2 bpftrace bpfcc-tools linux-tools-generic "linux-tools-$(uname -r)" \
    stress-ng docker.io apparmor-utils auditd libcap2-bin golang-go
  sudo apt install -y --no-install-recommends mdadm smartmontools
  sudo usermod -aG docker $USER
  ```
- Type `exit`, run `lab` again so the docker group applies, then check the three trickiest tools:

  ```bash
  docker run --rm hello-world
  sudo bpftrace -e 'BEGIN { printf("bpftrace ok\n"); exit(); }'
  perf --version
  ```
- Run `rocky`, then install its tools and check SELinux:

  ```bash
  sudo dnf install -y policycoreutils-python-utils setroubleshoot-server httpd audit \
    tcpdump bind-utils jq strace lsof grubby selinux-policy-targeted
  getenforce
  ```
- If getenforce doesn't say Enforcing, turn SELinux on. The relabel takes a few minutes after the reboot:

  ```bash
  sudo sed -i 's/^SELINUX=.*/SELINUX=enforcing/' /etc/selinux/config
  sudo grubby --update-kernel ALL --remove-args selinux
  sudo touch /.autorelabel && sudo reboot
  ```
- Back on the PC: snapshot both VMs, then stop Rocky until Day 17:

  ```bash
  incus snapshot create lab-ubuntu tools
  incus snapshot create lab-rocky tools
  incus stop lab-rocky
  ```
- If a lab ever wrecks a VM, roll it back with `incus snapshot restore lab-ubuntu tools`.

Done when: All three checks print without errors, and Rocky says Enforcing.

## Block 4. Accounts, notes repo and job tracker (Setup, 20 min, where: PC)

- Sign up at [SadServers](https://sadservers.com/scenarios) (Google login), [iximiuz Labs](https://labs.iximiuz.com/) (GitHub login) and [Killercoda](https://killercoda.com/).
- Create a GitHub repo called `linux-cheatcards` with a `cards/` folder, and clone it on the PC into `~/linux-cheatcards`. Every 'Prove it' block ends with a card pushed here.
- Create a Google Sheet called Job tracker with these columns: Company, Role, Link, Date applied, Status, Contact, Next step.

Done when: You can push a commit to the repo from the PC.

## Block 5. Set up this page (Setup, 10 min, where: Phone)

- Open Settings at the bottom of this page. Set Day 1's date and the time you start each day. Every block's time updates to match.
- Add this page to your phone's home screen so it's one tap away.
- Set your phone to turn on Do Not Disturb during your study hours.

Done when: The blocks show your real start times.

## Block 6. Write your four rules (Setup, 10 min, where: Paper)

- Write these four rules on a sticky note and put it on your monitor:
- One thing at a time: this page and the lab. Nothing else open.
- Stuck for 20 minutes? Read the hint or the answer, then move on.
- Low on energy? Do the minimum version of the day. It still counts.
- Missed a day? Tap 'Shift plan by one day' in Settings. Never double up.

Done when: The note is on your screen.
