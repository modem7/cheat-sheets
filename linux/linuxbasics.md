# Linux Basics
Network and host configuration on Ubuntu. For everyday commands see [Linux](linux.md).

## Change Hostname

```bash
sudo hostnamectl set-hostname newhostname
```
Also update the `127.0.1.1` line in `/etc/hosts`. Show the result with `hostnamectl`.

## Netplan Basics
Netplan reads YAML from `/etc/netplan/*.yaml` and drives `systemd-networkd` or NetworkManager.

COMMAND | DESCRIPTION
---|---
`ip -br a` | Find the interface name (e.g. `ens3`, `eth0`)
`sudo netplan try` | Apply with automatic rollback after 120 s if you lose connectivity
`sudo netplan apply` | Apply the configuration
`sudo netplan get` | Show the merged config
`sudo netplan generate` | Validate and generate backend config
`sudo chmod 600 /etc/netplan/*.yaml` | Netplan warns if files are world-readable

## Change IP Address in Ubuntu 20.04 LTS
1. Create a new file `/etc/netplan/01-netcfg.yaml`
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    ens3:
      dhcp4: no
      addresses:
        - 192.168.121.221/24
      gateway4: 192.168.121.1
      nameservers:
          addresses: [8.8.8.8, 1.1.1.1]
```
2. Apply changes
```bash
sudo netplan apply
```
## Change IP Address in Ubuntu 22.04 LTS and later
### `gateway4` was deprecated in Ubuntu 22.04 and `routes` is used instead
1. Create a new file `/etc/netplan/01-netcfg.yaml`
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    ens3:
      dhcp4: no
      addresses:
        - 192.168.121.221/24
      routes:
        - to: default
          via: 192.168.121.1
      nameservers:
          addresses: [8.8.8.8, 1.1.1.1]
```
2. Apply changes
```bash
sudo netplan apply
```

## DHCP
```yaml
network:
  version: 2
  ethernets:
    ens3:
      dhcp4: true
```

## Other Basics
COMMAND | DESCRIPTION
---|---
`sudo timedatectl set-timezone Europe/London` | Set the timezone
`timedatectl` | Time, NTP and timezone status
`sudo timedatectl set-ntp true` | Enable time sync
`sudo localectl set-locale LANG=en_GB.UTF-8` | Set the locale
`resolvectl status` | DNS servers in use
`sudo ufw allow OpenSSH && sudo ufw enable` | Basic firewall, see [UFW (uncomplicated firewall)](ufw.md)
`sudo apt update && sudo apt full-upgrade` | Update the system
`sudo reboot` / `sudo poweroff` | Reboot / shut down
`sudo unattended-upgrades --dry-run -d` | Test automatic security updates
`sudo dpkg-reconfigure -plow unattended-upgrades` | Enable automatic security updates
