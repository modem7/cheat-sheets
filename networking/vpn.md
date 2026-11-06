# VPN (Virtual Private Network)
A VPN creates an encrypted tunnel between devices or networks so traffic can cross an untrusted network safely.

Related: [WireGuard](../apps/wireguard.md), [Tailscale](../apps/tailscale.md), [TLS (Transport Layer Security)](tls.md), [OpenSSH Cheat-Sheet](../tools/openssh.md)

## Common Uses
USE | DESCRIPTION
---|---
Remote access | A client connects into a home or office network
Site-to-site | Two networks joined permanently through gateways
Privacy | Route traffic through a provider's exit node
Mesh | Every device talks directly to every other device (Tailscale, Nebula)

## Protocols Compared
PROTOCOL | TRANSPORT | NOTES
---|---|---
WireGuard | UDP (default 51820) | Tiny codebase, fast, modern crypto, static config. See [WireGuard](../apps/wireguard.md)
OpenVPN | UDP or TCP 1194 | Mature, flexible, TLS based, runs over TCP 443 to pass strict firewalls
IPsec / IKEv2 | UDP 500, 4500, ESP | Built into most OSes, standard for site-to-site
L2TP/IPsec | UDP 1701 + IPsec | Legacy, avoid for new setups
SSTP | TCP 443 | Windows only, passes firewalls
PPTP | TCP 1723 | Broken, never use

## Concepts
TERM | MEANING
---|---
Full tunnel | All client traffic goes through the VPN (`AllowedIPs = 0.0.0.0/0`)
Split tunnel | Only specific subnets go through the VPN
Road warrior | Roaming client connecting to a fixed server
Exit node | Peer that forwards your internet traffic
MTU | Tunnel overhead reduces MTU. WireGuard commonly uses 1420. Lower it if large packets stall
Keepalive | Periodic packet that holds NAT mappings open (`PersistentKeepalive = 25`)

## Server Prerequisites on Linux
COMMAND | DESCRIPTION
---|---
`echo 'net.ipv4.ip_forward=1' \| sudo tee /etc/sysctl.d/99-vpn.conf && sudo sysctl --system` | Enable IP forwarding
`sudo iptables -t nat -A POSTROUTING -s <VPN-SUBNET> -o <WAN-IF> -j MASQUERADE` | NAT VPN clients to the internet, see [IPTables](../linux/iptables.md)
`sudo ufw allow 51820/udp` | Open the WireGuard port, see [UFW (uncomplicated firewall)](../linux/ufw.md)

## Troubleshooting
SYMPTOM | CHECK
---|---
Tunnel up, no traffic | IP forwarding, NAT/firewall rules, `AllowedIPs`
Handshake never completes | Port blocked, wrong keys, wrong endpoint, clock skew (IPsec/OpenVPN)
Some sites hang, others work | MTU problem. Try a lower MTU
DNS not resolving | Client DNS setting, DNS leak, push the VPN's DNS
Drops behind NAT | Add keepalive

COMMAND | DESCRIPTION
---|---
`sudo wg show` | WireGuard peers, last handshake and transfer
`ip route get <IP>` | Which interface a destination uses
`ping -M do -s 1372 <HOST>` | Test path MTU (1372 + 28 = 1400 bytes)
`sudo tcpdump -ni <IF> udp port 51820` | Watch tunnel packets arrive
