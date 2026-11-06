# New Server Checklist
Take a fresh Ubuntu 24.04 server from first login to a patched, key-only, firewalled host with Docker installed.

Documentation: [Ubuntu Server docs](https://documentation.ubuntu.com/server/) · [Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

## Goal
A host with a named sudo user, SSH key login only, a default-deny firewall, automatic security updates, correct time and hostname, and Docker Engine with the Compose plugin.

## Prerequisites
- A fresh Ubuntu 24.04 server with root (or initial sudo) access and a public IP or LAN address (`192.0.2.10` below)
- An SSH key pair on your workstation (`ssh-keygen -t ed25519`, see [OpenSSH Cheat-Sheet](../tools/openssh.md))
- Console access (hypervisor or provider) in case you lock yourself out

> **Keep your first SSH session open** while you change SSH or firewall settings. Test with a second session before closing the first.

## Steps
### 1. Update the system
```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y curl ca-certificates vim ufw
sudo reboot   # only if /var/run/reboot-required exists
```

### 2. Create your user and give it sudo
```bash
sudo adduser <USER>
sudo usermod -aG sudo <USER>
```
See [User Management](../linux/user.md) for more account commands.

### 3. Install your SSH key
From your workstation:
```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub <USER>@192.0.2.10
ssh <USER>@192.0.2.10          # must work without a password prompt for the key
```

### 4. Harden SSH
Put the settings in a drop-in. `sshd` uses the **first** value it reads for each keyword and `/etc/ssh/sshd_config.d/*.conf` is read in alphabetical order, so a `00-` prefix wins over files such as the cloud image's `50-cloud-init.conf`.
```bash
sudo tee /etc/ssh/sshd_config.d/00-hardening.conf >/dev/null <<'EOF'
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
AllowUsers <USER>
EOF
sudo sshd -t && sudo systemctl reload ssh
sudo sshd -T | grep -Ei 'permitrootlogin|passwordauthentication|allowusers'
```
On Ubuntu the unit is `ssh` (not `sshd`). If you also change the `Port`, see the note under Verify.

### 5. Firewall with UFW
Allow SSH **before** enabling ([UFW (uncomplicated firewall)](../linux/ufw.md)):
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH            # or: sudo ufw limit ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```
Only open 80 and 443 if the host will serve web traffic. Docker publishes ports through its own `iptables` rules and **bypasses UFW**. Do not rely on UFW to hide a container port you published with `-p`; bind it to `127.0.0.1` (`-p 127.0.0.1:8080:80`) or keep it off the host ([Docker Networking](../docker/docker-networking.md), [IPTables](../linux/iptables.md)).

### 6. Automatic security updates
```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
sudo unattended-upgrade --dry-run --debug
```
Settings live in `/etc/apt/apt.conf.d/20auto-upgrades` and `/etc/apt/apt.conf.d/50unattended-upgrades`. Set `Unattended-Upgrade::Automatic-Reboot "true";` (and optionally `Automatic-Reboot-Time "04:00";`) in the latter only if you accept unattended reboots.

### 7. Hostname and time
```bash
sudo hostnamectl set-hostname <HOSTNAME>
sudo timedatectl set-timezone Europe/London
sudo timedatectl set-ntp true
timedatectl            # "System clock synchronized: yes"
```
Add the hostname to `/etc/hosts` next to `127.0.1.1` so `sudo` does not warn about resolution. A wrong clock breaks TLS ([TLS Troubleshooting](tls-troubleshooting.md)).

### 8. Brute-force protection (optional)
A log-watching banning tool such as `fail2ban` complements key-only SSH by cutting log noise:
```bash
sudo apt install -y fail2ban
sudo tee /etc/fail2ban/jail.local >/dev/null <<'EOF'
[sshd]
enabled = true
backend = systemd
maxretry = 5
bantime = 1h
EOF
sudo systemctl enable --now fail2ban
sudo fail2ban-client status sshd
```
Key-only SSH already makes password guessing futile, so treat this as optional.

### 9. Install Docker Engine
Use Docker's apt repository, not the distribution `docker.io` package ([Docker](../docker/docker.md)):
```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker <USER>      # log out and in again
```
Members of the `docker` group are effectively root on the host. Only add trusted users.

### 10. Limit container log growth
```bash
sudo tee /etc/docker/daemon.json >/dev/null <<'EOF'
{
  "log-driver": "local",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
EOF
sudo systemctl restart docker
```
New containers pick this up; recreate existing ones.

## Verify
```bash
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no <USER>@192.0.2.10   # must be refused
sudo ufw status verbose
systemctl is-active ssh docker unattended-upgrades
docker run --rm hello-world
docker compose version
```
If you changed the SSH `Port`, Ubuntu 24.04 uses socket activation: edit the port via `systemctl edit ssh.socket` (a `ListenStream=` override) or disable the socket and use the service directly, and allow the new port in UFW first. Test from a second session.

## Rollback / Cleanup
- SSH locked you out: use the console, remove `/etc/ssh/sshd_config.d/00-hardening.conf`, then `sudo systemctl reload ssh`.
- Firewall problem: `sudo ufw disable` from the console, fix the rules, enable again.
- Remove Docker: `sudo apt purge docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin` (data stays in `/var/lib/docker` until you delete it).

## Related Sheets
- [OpenSSH Cheat-Sheet](../tools/openssh.md) · [User Management](../linux/user.md) · [UFW (uncomplicated firewall)](../linux/ufw.md) · [IPTables](../linux/iptables.md) · [Linux](../linux/linux.md) · [Linux Basics](../linux/linuxbasics.md)
- [Docker](../docker/docker.md) · [Docker-Compose](../docker/docker-compose.md) · [Docker Networking](../docker/docker-networking.md)
- [Docker Service Deploy](docker-service-deploy.md) · [TLS Troubleshooting](tls-troubleshooting.md)
- [fail2ban](../security/fail2ban.md) · [Security](../security/security.md) · [Backup Strategy](../backup/backup.md) · [restic](../backup/restic.md) · [Bash](../scripting/bash.md) · [Homelab](../homelab/homelab.md)
