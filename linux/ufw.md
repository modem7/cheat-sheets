# UFW (uncomplicated firewall)
UFW (uncomplicated firewall) is a firewall configuration tool for **Linux ([[linux]])** that runs on top of IPTables ([[iptables]]), included by default within Ubuntu distributions. It provides a streamlined interface for configuring common firewall use cases via the command line.

## Enable UFW

To check if ufw is enabled, run:
```bash
sudo ufw status
```

Allow SSH **before** enabling, or you will lock yourself out of a remote machine:
```bash
sudo ufw allow OpenSSH
```

To enable UFW on your system, run:
```bash
sudo ufw enable
```

If for some reason you need to disable UFW, you can do so with the following command:
```bash
sudo ufw disable
```

## Defaults
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

## Rules
COMMAND | DESCRIPTION
---|---
`sudo ufw allow 80/tcp` | Allow a port and protocol
`sudo ufw allow 443` | Allow a port, TCP and UDP
`sudo ufw allow 6000:6010/tcp` | Allow a port range
`sudo ufw allow from 192.168.1.0/24 to any port 22 proto tcp` | Allow a subnet to a port
`sudo ufw allow in on eth1 to any port 5432` | Allow on one interface
`sudo ufw allow "Nginx Full"` | Allow an application profile
`sudo ufw limit ssh` | Rate-limit (6 attempts per 30 s)
`sudo ufw deny 23` | Deny a port
`sudo ufw reject 25` | Reject with a reply
`sudo ufw delete allow 80/tcp` | Delete a rule
`sudo ufw delete <NUMBER>` | Delete by number from `status numbered`
`sudo ufw insert 1 deny from 203.0.113.9` | Insert at the top
`sudo ufw reset` | Remove all rules and disable
`sudo ufw reload` | Reload the rules

## Block an IP Address/Subnet

```bash
sudo ufw deny from 203.0.113.0/24
```
Block rules must be above allows to win. Use `ufw insert 1 ...` if an allow rule already matches.

## Inspect
COMMAND | DESCRIPTION
---|---
`sudo ufw status verbose` | Rules and default policies
`sudo ufw status numbered` | Rules with numbers
`sudo ufw app list` | Application profiles
`sudo ufw logging on` | Enable logging (`/var/log/ufw.log`)
`sudo ufw show added` | Rules as commands

## Docker Warning
Docker publishes ports through its own iptables rules, which **bypass UFW**. A `-p 8080:80` container is reachable even if UFW denies 8080. Bind to localhost (`-p 127.0.0.1:8080:80`) or manage rules in the `DOCKER-USER` chain. See [[docker-networking]].

## Config Files
PATH | DESCRIPTION
---|---
`/etc/default/ufw` | Default policies, IPv6 on/off
`/etc/ufw/before.rules` | Rules applied before UFW's own (e.g. NAT, ICMP)
`/etc/ufw/applications.d/` | Application profiles
