# nftables
`nftables` is the modern Linux packet filter and the successor to `iptables`, `ip6tables`, `arptables` and `ebtables`. One tool (`nft`) and one syntax cover IPv4, IPv6, ARP and bridge traffic, with sets and maps for fast matching. Debian 10+, Ubuntu 20.10+ and RHEL 8+ use it as the kernel backend; the `iptables` command there is often `iptables-nft`, a translation layer ([[iptables]]). [[ufw]] and `firewalld` can also sit on top.

Documentation: [nftables wiki](https://wiki.nftables.org/wiki-nftables/index.php/Main_Page) · [Quick reference](https://wiki.nftables.org/wiki-nftables/index.php/Quick_reference-nftables_in_10_minutes) · `man nft`

> **Verification:** syntax follows the nftables wiki and `man nft`. No command was executed. A bad ruleset applied over SSH can lock you out: keep a second session open or use the timed rollback below.

See also: [[iptables]] · [[ufw]] · [[docker-networking]] · [[linux]] · [[systemd]]

---
## Concepts
TERM | MEANING
---|---
Table | Container for chains, one per address family: `ip`, `ip6`, `inet` (both), `arp`, `bridge`, `netdev`
Chain | List of rules. A **base chain** is attached to a netfilter hook (`input`, `forward`, `output`, `prerouting`, `postrouting`)
Rule | Match expressions followed by a verdict (`accept`, `drop`, `reject`, `jump`, `counter`, `log`, `masquerade`, `dnat`)
Set / map | Named collection of addresses, ports or pairs, matched in one rule
Priority | Order between chains on the same hook (lower runs first). `filter` is 0
Policy | Default verdict of a base chain: `accept` or `drop`

Unlike iptables there are no built-in tables. You create them.

---
## Inspect
COMMAND | DESCRIPTION
---|---
`sudo nft list ruleset` | Everything
`sudo nft list tables` | Tables
`sudo nft list table inet filter` | One table
`sudo nft list chain inet filter input` | One chain
`sudo nft -a list ruleset` | Show rule **handles** (needed to delete a rule)
`sudo nft list ruleset -n` | Numeric ports and addresses
`sudo nft monitor` | Watch changes live
`sudo nft monitor trace` | Trace packets marked with `meta nftrace set 1`

---
## A Minimal Host Firewall
`/etc/nftables.conf`:
```nft
#!/usr/sbin/nft -f

flush ruleset

table inet filter {
  set trusted {
    type ipv4_addr
    flags interval
    elements = { 192.168.1.0/24 }
  }

  chain input {
    type filter hook input priority 0; policy drop;

    iif "lo" accept
    ct state established,related accept
    ct state invalid drop

    ip protocol icmp accept
    ip6 nexthdr icmpv6 accept

    tcp dport 22 ip saddr @trusted accept
    tcp dport { 80, 443 } accept

    counter log prefix "nft-drop: " level warn limit rate 5/minute
  }

  chain forward {
    type filter hook forward priority 0; policy drop;
  }

  chain output {
    type filter hook output priority 0; policy accept;
  }
}
```
```bash
sudo nft -c -f /etc/nftables.conf        # check syntax only
sudo nft -f /etc/nftables.conf           # load
sudo systemctl enable --now nftables     # load at boot (Debian/Ubuntu/RHEL)
```
Careful: `flush ruleset` also removes the chains that Docker and libvirt create. Restart Docker after loading or limit the flush to your own table (`flush table inet filter`). See [[docker-networking]].

Safe test over SSH:
```bash
sudo nft -f /etc/nftables.conf && sleep 60 && echo "kept" || true
# if you got locked out, a scheduled revert helps:
echo 'nft flush ruleset' | sudo at now + 5 minutes
```

---
## Manage Rules at Runtime
COMMAND | DESCRIPTION
---|---
`sudo nft add table inet filter` | Create a table
`sudo nft add chain inet filter input '{ type filter hook input priority 0; policy drop; }'` | Create a base chain (quote the braces)
`sudo nft add rule inet filter input tcp dport 22 accept` | Append a rule
`sudo nft insert rule inet filter input tcp dport 22 accept` | Insert at the top
`sudo nft add rule inet filter input position 5 tcp dport 8080 accept` | Add after the rule with handle 5
`sudo nft delete rule inet filter input handle 7` | Delete by handle (see `nft -a list`)
`sudo nft flush chain inet filter input` | Empty a chain
`sudo nft delete chain inet filter input` | Delete a chain (must be empty)
`sudo nft delete table inet filter` | Delete a table and everything in it
`sudo nft flush ruleset` | Remove all rules
`sudo nft -f <FILE>` | Load a file (atomic: all or nothing)
`sudo nft list ruleset \| sudo tee /etc/nftables.conf` | Save the live ruleset

---
## Matching Cheat Sheet
EXPRESSION | MATCHES
---|---
`ip saddr 10.0.0.0/8` | IPv4 source
`ip daddr 192.168.1.10` | IPv4 destination
`ip6 saddr fd00::/8` | IPv6 source
`tcp dport 22` / `udp dport 53` | Destination port
`tcp dport { 80, 443, 8000-8100 }` | Port set and range
`tcp flags syn` | SYN packets
`iif "eth0"` / `oif "eth0"` | Input / output interface
`iifname "wg*"` | Interface by name pattern (also works for interfaces not yet created)
`ct state new` | Connection state: `new`, `established`, `related`, `invalid`
`meta l4proto { tcp, udp }` | Protocol
`ip protocol icmp` | ICMP
`limit rate 10/second burst 20 packets` | Rate limit
`meta mark 0x1` | Packet mark
`counter` | Count packets and bytes on that rule
`log prefix "text: "` | Log to the kernel log

---
## Sets and Dynamic Blocklists
```bash
# a set of blocked IPs with timeouts
sudo nft add set inet filter blocklist '{ type ipv4_addr; flags timeout; timeout 1h; }'
sudo nft add rule inet filter input ip saddr @blocklist drop

sudo nft add element inet filter blocklist '{ 203.0.113.9 }'                   # default timeout
sudo nft add element inet filter blocklist '{ 198.51.100.7 timeout 24h }'
sudo nft delete element inet filter blocklist '{ 203.0.113.9 }'
sudo nft list set inet filter blocklist
```
Put the `drop` rule before your accept rules. Tools like fail2ban and CrowdSec can use nftables sets as the ban backend.

SSH brute-force rate limit using a meter:
```nft
tcp dport 22 ct state new meter ssh-limit { ip saddr limit rate 5/minute } accept
tcp dport 22 drop
```

---
## NAT and Port Forwarding
```nft
table inet nat {
  chain prerouting {
    type nat hook prerouting priority dstnat; policy accept;
    tcp dport 8080 dnat ip to 192.168.1.10:80
  }
  chain postrouting {
    type nat hook postrouting priority srcnat; policy accept;
    oifname "eth0" ip saddr 10.0.0.0/24 masquerade
  }
}
```
Also enable forwarding: `sudo sysctl -w net.ipv4.ip_forward=1` (persist in `/etc/sysctl.d/99-forward.conf`) and allow the traffic in the `forward` chain:
```nft
ip daddr 192.168.1.10 tcp dport 80 ct status dnat accept
```
Use `nat` in a separate table (`inet nat` works for IPv4 and IPv6 on kernel 5.2+).

---
## iptables to nftables
COMMAND | DESCRIPTION
---|---
`iptables --version` | `(nf_tables)` means the nft backend, `(legacy)` the old one
`sudo iptables-save \| iptables-restore-translate -f -` | Translate a saved ruleset to nft syntax
`sudo iptables-translate -A INPUT -p tcp --dport 22 -j ACCEPT` | Translate one rule
`sudo ip6tables-save \| ip6tables-restore-translate -f -` | IPv6 version
`sudo nft list ruleset` | Shows `iptables-nft` rules too (in tables named `filter`, `nat`)
`sudo update-alternatives --config iptables` | Switch legacy / nft on Debian and Ubuntu

IPTABLES | NFTABLES
---|---
`-A INPUT -p tcp --dport 22 -j ACCEPT` | `add rule inet filter input tcp dport 22 accept`
`-m conntrack --ctstate ESTABLISHED,RELATED` | `ct state established,related`
`-i eth0` | `iif "eth0"` or `iifname "eth0"`
`-j DROP` / `-j REJECT` | `drop` / `reject`
`-j LOG --log-prefix "x"` | `log prefix "x"`
`-t nat -A POSTROUTING -j MASQUERADE` | `add rule ip nat postrouting masquerade`
`-m multiport --dports 80,443` | `tcp dport { 80, 443 }`
`-m set --match-set NAME src` (ipset) | `ip saddr @NAME` (native sets)

Do not mix `iptables-legacy` and nft rules on one host: packets pass both and debugging gets confusing. Pick one.

## Notes
- Counters on a rule (`counter`) are the quickest debugging tool: list the chain and see which rules match.
- Debian ships the loader unit `nftables.service` that reads `/etc/nftables.conf`. RHEL reads `/etc/sysconfig/nftables.conf`, which includes files under `/etc/nftables/`.
- `firewalld` and `ufw` own their own tables. Editing the live set by hand will be overwritten when they reload.
