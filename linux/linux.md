# Linux
Quick reference for everyday Linux administration. Topic-specific sheets: [Linux Basics](linuxbasics.md), [User Management](user.md), [Grep](grep.md), [SED Cheat-Sheet](sed.md), [AWK](awk.md), [Mount](mount.md), [NFS](nfs.md), [UFW (uncomplicated firewall)](ufw.md), [IPTables](iptables.md), [nftables](nftables.md), [firewalld](firewalld.md), [ip and ss](ip-and-ss.md), [ethtool](ethtool.md), [Netplan](netplan.md), [systemd](systemd.md), [LVM](lvm.md), [RAID with mdadm](raid-mdadm.md), [Storage and Filesystems](storage-and-filesystems.md), [ZFS](zfs.md), [Disk Usage](disk-usage.md), [Hardware Inspection](hardware-inspection.md), [SELinux and AppArmor](selinux-apparmor.md), [Linux Performance Troubleshooting](performance-troubleshooting.md).

## System Information
COMMAND | DESCRIPTION
---|---
`uname -a` | Kernel and architecture
`cat /etc/os-release` | Distribution and version
`hostnamectl` | Hostname, OS, kernel, virtualisation
`uptime` | Uptime and load averages
`lscpu` | CPU details
`free -h` | Memory usage
`lsblk -f` | Block devices, filesystems and mount points
`df -hT` | Disk usage per filesystem
`du -sh * \| sort -h` | Size of items in the current directory, smallest to largest
`ip -br a` | Brief list of interfaces and addresses
`ss -tulpn` | Listening TCP/UDP sockets and owning processes
`lspci` / `lsusb` | PCI / USB devices

## Processes
COMMAND | DESCRIPTION
---|---
`ps aux --sort=-%mem \| head` | Top memory consumers
`ps -ef --forest` | Process tree
`top` / `htop` | Live process view
`kill <PID>` | Ask a process to terminate (SIGTERM)
`kill -9 <PID>` | Force kill (SIGKILL)
`pkill -f <PATTERN>` | Kill by command-line match
`pgrep -a <NAME>` | Find PIDs by name
`lsof -i :<PORT>` | Which process uses a port
`nohup <CMD> &` | Run a command that survives logout
`jobs`, `fg`, `bg` | Manage shell jobs

## systemd
Units, timers, drop-ins and hardening are in [systemd](systemd.md).

COMMAND | DESCRIPTION
---|---
`systemctl status <UNIT>` | Show unit status
`sudo systemctl enable --now <UNIT>` | Enable at boot and start now
`sudo systemctl restart <UNIT>` | Restart a unit
`sudo systemctl daemon-reload` | Reload unit files after editing
`systemctl --failed` | List failed units
`systemctl list-timers` | List timers
`journalctl -u <UNIT> -f` | Follow a unit's logs
`journalctl -b -p err` | Errors since last boot
`journalctl --since "1 hour ago"` | Recent logs
`journalctl --vacuum-size=500M` | Shrink the journal

## Files and Search
COMMAND | DESCRIPTION
---|---
`find / -name "*.log" -mtime -1 2>/dev/null` | Files named `*.log` changed in the last day
`find . -type f -size +100M` | Files larger than 100 MB
`find . -name "*.tmp" -delete` | Find and delete
`tar -czvf out.tar.gz <DIR>` | Create a gzip tarball
`tar -xzvf out.tar.gz -C <DEST>` | Extract a gzip tarball
`rsync -avzP <SRC>/ <USER>@<HOST>:<DEST>/` | Copy over SSH with progress and resume
`ln -s <TARGET> <LINKNAME>` | Create a symlink
`chmod 640 <FILE>` | Set permissions
`chown -R <USER>:<GROUP> <DIR>` | Change owner recursively
`stat <FILE>` | Detailed file metadata
`tail -f <FILE>` | Follow a file
`less +F <FILE>` | Follow a file, Ctrl-C to scroll back

## Packages
Debian/Ubuntu | RHEL/Fedora | DESCRIPTION
---|---|---
`sudo apt update && sudo apt upgrade` | `sudo dnf upgrade` | Update system
`sudo apt install <PKG>` | `sudo dnf install <PKG>` | Install
`sudo apt remove --purge <PKG>` | `sudo dnf remove <PKG>` | Remove
`apt search <TERM>` | `dnf search <TERM>` | Search
`dpkg -L <PKG>` | `rpm -ql <PKG>` | Files installed by a package
`dpkg -S <FILE>` | `rpm -qf <FILE>` | Package owning a file
`sudo apt autoremove` | `sudo dnf autoremove` | Remove unused dependencies

## Networking
COMMAND | DESCRIPTION
---|---
`ping -c 4 <HOST>` | Test reachability
`traceroute <HOST>` / `mtr <HOST>` | Trace the route
`dig <DOMAIN> +short` | DNS lookup
`curl -I <URL>` | Fetch response headers only
`curl -fsSL <URL> -o <FILE>` | Download quietly, fail on HTTP errors
`wget -c <URL>` | Download with resume
`nc -zv <HOST> <PORT>` | Test whether a TCP port is open
`sudo tcpdump -i any port <PORT>` | Capture traffic on a port

## Handy Shell Tricks
COMMAND | DESCRIPTION
---|---
`!!` | Repeat the last command
`sudo !!` | Repeat the last command with sudo
`Ctrl-R` | Reverse history search
`cd -` | Return to the previous directory
`<CMD> \| tee <FILE>` | Show output and save it
`<CMD> > out.log 2>&1` | Redirect stdout and stderr
`watch -n 2 <CMD>` | Re-run a command every 2 seconds
`xargs -I{} <CMD> {}` | Run a command per input line

## Logs and Diagnostics
COMMAND | DESCRIPTION
---|---
`dmesg -T \| tail` | Kernel messages with readable timestamps
`journalctl -k -b` | Kernel log this boot
`last -n 10` / `lastb -n 10` | Recent logins / failed logins
`sudo tail -f /var/log/syslog` | System log on Debian/Ubuntu (`/var/log/messages` on RHEL)
`sudo tail -f /var/log/auth.log` | Auth log on Debian/Ubuntu (`/var/log/secure` on RHEL)
`lsof +D <DIR>` | Processes using files under a directory
`lsmod \| grep <NAME>` | Is a kernel module loaded
`sudo sysctl -a \| grep <KEY>` | Kernel parameters
`sudo sysctl -w net.ipv4.ip_forward=1` | Set at runtime (persist in `/etc/sysctl.d/*.conf`, load with `sudo sysctl --system`)
`ulimit -n` | Open file limit of this shell

Deeper dives: [Linux Performance Troubleshooting](performance-troubleshooting.md), [Storage and Filesystems](storage-and-filesystems.md).

## Scheduling
COMMAND | DESCRIPTION
---|---
`crontab -e` | Edit your cron jobs
`crontab -l` | List them
`sudo crontab -u <USER> -l` | Another user's jobs
`systemctl list-timers` | systemd timers, see [systemd](systemd.md)
`echo "<CMD>" \| at now + 10 minutes` | One-off job (`atq` lists, `atrm <ID>` removes)

Cron fields: `minute hour day-of-month month day-of-week command`. Example: `30 2 * * 1-5 /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1` runs at 02:30 on weekdays. Use full paths in cron: its `PATH` is minimal.

## Time and Locale
COMMAND | DESCRIPTION
---|---
`timedatectl` | Time, zone and NTP status
`sudo timedatectl set-timezone Europe/London` | Set the timezone
`sudo timedatectl set-ntp true` | Enable network time
`chronyc tracking` | Clock offset when using chrony
`locale -a` / `sudo update-locale LANG=en_GB.UTF-8` | Locales (Debian/Ubuntu)

## Swap and Memory
COMMAND | DESCRIPTION
---|---
`swapon --show` | Swap devices
`sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile` | Create a swap file (not on Btrfs or ZFS without extra steps)
`echo '/swapfile none swap sw 0 0' \| sudo tee -a /etc/fstab` | Make it permanent
`sudo swapoff -a` | Disable swap
`sudo sysctl vm.swappiness=10` | Prefer RAM over swap (persist in `/etc/sysctl.d/`)

## SSH Quick Reference
Full detail in [OpenSSH Cheat-Sheet](../tools/openssh.md).

COMMAND | DESCRIPTION
---|---
`ssh-keygen -t ed25519 -C "<COMMENT>"` | Create a key
`ssh-copy-id <USER>@<HOST>` | Install your public key
`ssh -J <JUMPHOST> <USER>@<HOST>` | Connect through a jump host
`ssh -L 8080:localhost:80 <USER>@<HOST>` | Local port forward
`scp -r <DIR> <USER>@<HOST>:<DEST>` | Copy over SSH (prefer `rsync`)

## Archives and Compression
COMMAND | DESCRIPTION
---|---
`tar -cf - <DIR> \| zstd -T0 > out.tar.zst` | Fast multi-threaded compression
`tar --zstd -xf out.tar.zst` | Extract zstd archive
`tar -tf out.tar.gz` | List contents
`zip -r out.zip <DIR>` / `unzip out.zip -d <DEST>` | Zip files
`gzip -k <FILE>` / `gunzip <FILE>.gz` | Gzip, keep the original with `-k`

## Safety Habits
- Run `sudo !!` only after reading the command you are repeating.
- Preview destructive globs first: `ls <PATTERN>` before `rm <PATTERN>`.
- Use `set -euo pipefail` at the top of bash scripts.
- Edit config in `/etc` with a backup: `sudo cp -a <FILE> <FILE>.bak`.
