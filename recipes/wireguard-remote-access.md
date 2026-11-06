# WireGuard Remote Access
Set up a WireGuard server on a Linux host at home, add laptop and phone clients, choose between full and split tunnel, route and NAT the traffic, and troubleshoot a tunnel that comes up but passes nothing.

Documentation: [WireGuard quickstart](https://www.wireguard.com/quickstart/) · [wg-quick(8)](https://man7.org/linux/man-pages/man8/wg-quick.8.html)

## Goal
From outside, a client reaches the home LAN (`192.0.2.0/24` in this example) through a tunnel `10.8.0.0/24`, over a single UDP port.

## Prerequisites
- A Linux server (Ubuntu 24.04) on the LAN, with a static LAN address, `192.0.2.10`
- A public IP or a DNS name (`vpn.example.com`) and a router port-forward of `51820/udp` to the server. Behind CGNAT you have no inbound path: use a relay or an overlay network such as [[tailscale]]
- Server firewall as in [[new-server-checklist]]
- Interface name of the LAN NIC (`ip -br link`): `eth0` below

## Steps
### 1. Install and generate keys (server)
```bash
sudo apt install -y wireguard qrencode
sudo install -d -m 700 /etc/wireguard
cd /etc/wireguard
wg genkey | sudo tee server.key | wg pubkey | sudo tee server.pub
sudo chmod 600 server.key
```
Repeat on each client (or generate client keys on the server and copy them securely). Private keys never leave their device.

### 2. Enable IP forwarding
```bash
echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-wireguard.conf
sudo sysctl --system
sysctl net.ipv4.ip_forward           # = 1
```

### 3. Server configuration
`/etc/wireguard/wg0.conf` (mode `600`):
```ini
[Interface]
Address = 10.8.0.1/24
ListenPort = 51820
PrivateKey = <SERVER-PRIVATE-KEY>
PostUp   = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -s 10.8.0.0/24 -o eth0 -j MASQUERADE

[Peer]
# laptop
PublicKey = <LAPTOP-PUBLIC-KEY>
AllowedIPs = 10.8.0.2/32
```
`AllowedIPs` on the server is both a routing table and an access list: it names the addresses that peer may use as source. Give each client one `/32`. The NAT rule lets tunnel clients reach LAN hosts that have no return route to `10.8.0.0/24`; if you instead add a static route for `10.8.0.0/24` via the server on your router, you can drop `MASQUERADE` and hosts see real client IPs.

### 4. Firewall (UFW)
```bash
sudo ufw allow 51820/udp
sudo ufw route allow in on wg0 out on eth0     # lets forwarded tunnel traffic through UFW
sudo ufw status verbose
```
UFW's default forward policy is `DROP` (`/etc/default/ufw`), so without the `route` rule traffic through the tunnel dies at the server even with `ip_forward=1`. The `PostUp` `iptables` lines above handle NAT; if you prefer to keep NAT in UFW, put a `*nat` block in `/etc/ufw/before.rules` instead and drop it from `PostUp` ([[ufw]], [[iptables]]).

### 5. Start the tunnel
```bash
sudo systemctl enable --now wg-quick@wg0
sudo wg show
```

### 6. Client configuration
```ini
[Interface]
Address = 10.8.0.2/24
PrivateKey = <LAPTOP-PRIVATE-KEY>
DNS = 192.0.2.53

[Peer]
PublicKey = <SERVER-PUBLIC-KEY>
Endpoint = vpn.example.com:51820
AllowedIPs = 10.8.0.0/24, 192.0.2.0/24
PersistentKeepalive = 25
```
TUNNEL TYPE | CLIENT `AllowedIPs` | RESULT
---|---|---
Split tunnel | `10.8.0.0/24, 192.0.2.0/24` | Only VPN and LAN traffic uses the tunnel, internet traffic goes direct
Full tunnel | `0.0.0.0/0, ::/0` | All traffic goes through home; also set `DNS` and forward IPv6 or disable it on the client

On the client, `AllowedIPs` decides which destinations are sent into the tunnel. For a phone, show the config as a QR code on the server:
```bash
sudo qrencode -t ansiutf8 < phone.conf
```
Treat `phone.conf` as a secret and delete it afterwards.

### 7. Add the client to the server without dropping the tunnel
```bash
sudo wg set wg0 peer <PHONE-PUBLIC-KEY> allowed-ips 10.8.0.3/32
sudo wg-quick save wg0                  # writes the live state into wg0.conf
# or after editing wg0.conf:
sudo wg syncconf wg0 <(sudo wg-quick strip wg0)
```
`wg-quick save` rewrites the file, so back it up first. Details in [[wireguard]].

## Verify
```bash
# client
sudo wg show                         # "latest handshake" within the last minute or two
ping -c 3 10.8.0.1
ping -c 3 192.0.2.10                 # a LAN host
curl -s https://ifconfig.me          # full tunnel shows the home IP
# server
sudo wg show wg0
sudo tcpdump -ni wg0
```
A `latest handshake` line means the keys match and UDP got through. Transfer counters that grow in only one direction mean a return path or firewall problem.

## Troubleshooting
SYMPTOM | CHECK
---|---
No handshake at all | `51820/udp` forwarded on the router and allowed in UFW; endpoint name resolves ([[dns-troubleshooting]]); key mix-ups (client holds the server **public** key and vice versa); `sudo tcpdump -ni eth0 udp port 51820` on the server shows whether packets arrive
Handshake but cannot ping `10.8.0.1` | Peer `AllowedIPs` on the server does not include the client address; client address is outside `10.8.0.0/24`
Can ping the server, not LAN hosts | `net.ipv4.ip_forward`; UFW `route` rule or `FORWARD` rule; NAT rule uses the right interface name; LAN host firewall
Some sites hang, others work | MTU: lower it with `MTU = 1380` in the client `[Interface]` ([[network-troubleshooting]])
Names do not resolve over the tunnel | Set `DNS` in the client config and make sure that resolver is reachable from `10.8.0.0/24` ([[dns-troubleshooting]])
Kernel-level debug | `echo 'module wireguard +p' \| sudo tee /sys/kernel/debug/dynamic_debug/control` then `sudo dmesg -w`; switch off with `-p`

## Rollback / Cleanup
```bash
sudo wg-quick down wg0
sudo systemctl disable --now wg-quick@wg0
sudo ufw delete allow 51820/udp
sudo rm /etc/sysctl.d/99-wireguard.conf && sudo sysctl --system
```
Remove the router port-forward. To revoke one client, delete its `[Peer]` and run `sudo wg set wg0 peer <PUBLIC-KEY> remove`.

## Related Sheets
- [[wireguard]] · [[vpn]] · [[tailscale]]
- [[ufw]] · [[iptables]] · [[linux]] · [[openssh]]
- [[new-server-checklist]] · [[network-troubleshooting]] · [[dns-troubleshooting]]
