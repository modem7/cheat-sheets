# Linux
Quick reference for everyday Linux administration. Topic-specific sheets: [[linuxbasics]], [[user]], [[grep]], [[sed]], [[awk]], [[mount]], [[nfs]], [[ufw]], [[iptables]].

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
