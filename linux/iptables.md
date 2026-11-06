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

## Matching and Targets
COMMAND | DESCRIPTION
---|---
`sudo iptables -A INPUT -p tcp -m multiport --dports 80,443 -j ACCEPT` | Several ports in one rule
`sudo iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --set` | Record new SSH connections
`sudo iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m recent --update --seconds 60 --hitcount 4 -j DROP` | Drop an IP after 4 new SSH connections in 60 s (place before the ACCEPT)
`sudo iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 5/s -j ACCEPT` | Rate-limit ping
`sudo iptables -A INPUT -m state --state INVALID -j DROP` | Drop invalid packets
`sudo iptables -A INPUT -i eth0 -m mac --mac-source <MAC> -j ACCEPT` | Match a MAC address
`sudo iptables -A OUTPUT -m owner --uid-owner <USER> -j DROP` | Block a local user's outgoing traffic
`sudo iptables -N <CHAIN>` | Create a custom chain
`sudo iptables -A INPUT -j <CHAIN>` | Jump into it
`sudo iptables -X <CHAIN>` | Delete an empty custom chain

## ipset for Large Blocklists
COMMAND | DESCRIPTION
---|---
`sudo ipset create blocklist hash:net` | Create a set
`sudo ipset add blocklist 203.0.113.0/24` | Add an entry
`sudo ipset create temp hash:ip timeout 3600` | Entries expire after an hour
`sudo iptables -I INPUT -m set --match-set blocklist src -j DROP` | One rule for the whole set
`sudo ipset save > /etc/ipset.conf` | Save (restore with `ipset restore < /etc/ipset.conf`)

On nftables, native sets replace ipset, see [[nftables]].

## IPv6
`ip6tables` has the same syntax and its own rule set. A host with IPv6 and only `iptables` rules is open on IPv6. Mirror the rules, and allow ICMPv6 or neighbour discovery breaks:
```bash
sudo ip6tables -A INPUT -p ipv6-icmp -j ACCEPT
sudo ip6tables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
```
Persist with `ip6tables-save > /etc/iptables/rules.v6`.

## Docker and the DOCKER-USER Chain
Docker inserts rules in the `FORWARD` chain and evaluates `DOCKER-USER` first. Restrict published ports there:
```bash
# Only 192.168.1.0/24 may reach containers on eth0
sudo iptables -I DOCKER-USER -i eth0 ! -s 192.168.1.0/24 -j DROP
# Allow established return traffic first
sudo iptables -I DOCKER-USER -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
```
`-I` inserts at the top, so the second command ends up first, which is the intended order. Docker's rules match the destination port after DNAT, so use `-m conntrack --ctorigdstport <PORT>` to match the published port. These rules are not persisted by Docker: save them with `netfilter-persistent` or a systemd unit. See [[docker-networking]] and [[nftables]].

## Notes
- Check which backend is active: `iptables --version` shows `(nf_tables)` or `(legacy)`.
- Test remotely with a safety net: `sudo iptables-apply` or schedule `at now + 5 minutes` a flush.
- Docker manages its own chains (`DOCKER`, `DOCKER-USER`). Put your own rules in `DOCKER-USER`, see [[docker-networking]].
- Log dropped packets: `sudo iptables -A INPUT -j LOG --log-prefix "DROP: " --log-level 4` (put it before the final drop).
