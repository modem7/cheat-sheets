# IPTables
Iptables is a user-space utility program that allows a system administrator to configure the IP packet filter rules of the **Linux ([[linux]])** kernel firewall, implemented as different Netfilter modules. The filters are organized in different tables, which contain chains of rules for how to treat network traffic packets. Different kernel modules and programs are currently used for different protocols; iptables applies to IPv4, ip6tables to IPv6, arptables to ARP, and ebtables to Ethernet frames.

For a simpler front end see [[ufw]]. Modern distributions use `nftables` underneath (`iptables-nft`), and the commands below still work.

## Concepts
TERM | MEANING
---|---
Tables | `filter` (default, allow/deny), `nat` (address translation), `mangle` (packet edits), `raw`
Chains | `INPUT` (to this host), `OUTPUT` (from this host), `FORWARD` (routed through), `PREROUTING`, `POSTROUTING`
Targets | `ACCEPT`, `DROP` (silent), `REJECT` (with reply), `LOG`, `MASQUERADE`, `DNAT`, `SNAT`
Order | Rules are checked top to bottom, first match wins

## Inspect
COMMAND | DESCRIPTION
---|---
`sudo iptables -L -n -v --line-numbers` | List filter rules with counters and numbers
`sudo iptables -t nat -L -n -v` | List NAT rules
`sudo iptables -S` | Rules as commands
`sudo iptables-save` | Dump everything

## Manage Rules
COMMAND | DESCRIPTION
---|---
`sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT` | Append: allow SSH
`sudo iptables -I INPUT 1 -s <IP> -j DROP` | Insert at the top: block an IP
`sudo iptables -A INPUT -s <CIDR> -p tcp --dport 443 -j ACCEPT` | Allow a subnet to a port
`sudo iptables -D INPUT <LINE-NUMBER>` | Delete by number
`sudo iptables -D INPUT -p tcp --dport 22 -j ACCEPT` | Delete by specification
`sudo iptables -P INPUT DROP` | Default policy: drop (set accept rules first or you lock yourself out)
`sudo iptables -F` | Flush all rules (resets nothing about policy)
`sudo iptables -Z` | Zero counters

## A Minimal Host Firewall
```bash
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p icmp -j ACCEPT
sudo iptables -P INPUT DROP
```

## NAT and Forwarding
COMMAND | DESCRIPTION
---|---
`sudo sysctl -w net.ipv4.ip_forward=1` | Enable routing
`sudo iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o eth0 -j MASQUERADE` | Share an internet connection (NAT)
`sudo iptables -t nat -A PREROUTING -p tcp --dport 8080 -j DNAT --to-destination 192.168.1.10:80` | Port forward
`sudo iptables -A FORWARD -d 192.168.1.10 -p tcp --dport 80 -j ACCEPT` | Allow the forwarded traffic

## Persist and Restore
COMMAND | DESCRIPTION
---|---
`sudo apt install iptables-persistent` | Debian/Ubuntu persistence package
`sudo netfilter-persistent save` | Save current rules
`sudo iptables-save > /etc/iptables/rules.v4` | Save manually
`sudo iptables-restore < /etc/iptables/rules.v4` | Restore

## Notes
- Test remotely with a safety net: `sudo iptables-apply` or schedule `at now + 5 minutes` a flush.
- Docker manages its own chains (`DOCKER`, `DOCKER-USER`). Put your own rules in `DOCKER-USER`, see [[docker-networking]].
- Log dropped packets: `sudo iptables -A INPUT -j LOG --log-prefix "DROP: " --log-level 4` (put it before the final drop).
