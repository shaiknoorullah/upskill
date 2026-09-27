# Lab setup: two Arch Linux machines

## Roles
- Laptop: always-on Incus server. Plugged in, lid-close ignored, SSH enabled, fixed IP from a DHCP reservation. Hosts lab-ubuntu (4 GiB, or 6 GiB if the laptop has 16 GB of RAM; 40 GiB disk) and lab-rocky (2 GiB; only needed on Days 17 and 24).
- PC: where I sit. Also runs Incus locally for the kubeadm VMs cp1 (2 GiB), w1 and w2 (1.5 GiB each), from Day 17.
- Incus on the PC has the laptop as a remote called `laptop` and uses it as the default. `local:` means the PC.
- Each lab stays on one machine: VMs on the laptop can't reach VMs on the PC without extra networking.

## Everyday commands (run on the PC)
- `lab` / `rocky`: aliases for `incus exec laptop:lab-ubuntu -- su -l me` and `incus exec laptop:lab-rocky -- su -l me`
- `incus list` (laptop) and `incus list local:` (PC)
- `incus start lab-rocky` / `incus stop lab-rocky`
- `incus start local:cp1 local:w1 local:w2` and `incus stop local:cp1 local:w1 local:w2`
- `incus snapshot create lab-ubuntu <name>` and `incus snapshot restore lab-ubuntu <name>` (a `tools` snapshot is made on Day 0)
- `incus file pull lab-ubuntu/home/me/cpu.svg ~/` to copy files out of a VM
- `ssh <user>@<laptop IP>` for anything on the laptop host itself (the VMs' network is private to the laptop)

## Known gotchas
- Arch has no signed UEFI firmware for VMs: `incus profile set default security.secureboot=false` on both machines.
- Docker on a host sets FORWARD to DROP and can cut the VMs off. Fix: `sudo iptables -I DOCKER-USER -i incusbr0 -j ACCEPT` and the same with `-o incusbr0` (repeat after reboots).
- The Rocky image may ship with SELinux disabled. Day 0 turns it on (config, grubby, autorelabel, reboot).
- If lab-ubuntu's kernel isn't `-generic`, install linux-generic and reboot, or perf and bpftrace may not work.
- Inside lab-ubuntu, Docker also sets FORWARD to DROP, which matters on Day 15 (the steps handle it).

## Full step-by-step
docs/plan/calendar/day-00.md
