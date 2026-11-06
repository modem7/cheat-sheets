# WireGuard
WireGuard® is an extremely simple yet fast and modern **VPN ([VPN (Virtual Private Network)](../networking/vpn.md))** that utilizes state-of-the-art cryptography. It aims to be faster, simpler, leaner, and more useful than IPsec, while avoiding the massive headache. It intends to be considerably more performant than OpenVPN. WireGuard is designed as a general purpose VPN for running on embedded interfaces and super computers alike, fit for many different circumstances.

Documentation: [wireguard.com](https://www.wireguard.com/quickstart/)

---
## Install and Keys
```bash
sudo apt install wireguard
wg genkey | tee privatekey | wg pubkey > publickey
chmod 600 privatekey
```
Pre-shared key (optional extra layer): `wg genpsk`

## Server Config `/etc/wireguard/wg0.conf`
```ini
[Interface]
Address = 10.8.0.1/24
ListenPort = 51820
PrivateKey = <SERVER-PRIVATE-KEY>
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
PublicKey = <CLIENT-PUBLIC-KEY>
AllowedIPs = 10.8.0.2/32
```
Enable forwarding: `echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-wg.conf && sudo sysctl --system`, and open `51820/udp`.

## Client Config
```ini
[Interface]
Address = 10.8.0.2/24
PrivateKey = <CLIENT-PRIVATE-KEY>
DNS = 1.1.1.1

[Peer]
PublicKey = <SERVER-PUBLIC-KEY>
Endpoint = vpn.example.com:51820
AllowedIPs = 0.0.0.0/0, ::/0     # full tunnel; use e.g. 10.8.0.0/24,192.168.1.0/24 for split tunnel
PersistentKeepalive = 25
```

## Commands
COMMAND | DESCRIPTION
---|---
`sudo wg-quick up wg0` / `down wg0` | Bring the interface up or down
`sudo systemctl enable --now wg-quick@wg0` | Start at boot
`sudo wg show` | Peers, last handshake, transfer counters
`sudo wg syncconf wg0 <(wg-quick strip wg0)` | Apply config changes without dropping the tunnel
`sudo wg set wg0 peer <PUBKEY> remove` | Remove a peer live
`qrencode -t ansiutf8 < client.conf` | QR code for the mobile app

## Troubleshooting

With this command you can enable the debug logging in WireGuard:

```bash
echo 'module wireguard +p' | sudo tee /sys/kernel/debug/dynamic_debug/control
```

And the same command with -p can disable it again:

```bash
echo 'module wireguard -p' | sudo tee /sys/kernel/debug/dynamic_debug/control
```
View the output with `sudo dmesg -wH` or `journalctl -k -f`.

SYMPTOM | CHECK
---|---
No handshake | Port 51820/udp reachable, keys paired correctly, `Endpoint` correct
Handshake but no traffic | `AllowedIPs` on both ends, IP forwarding, NAT rule, firewall ([UFW (uncomplicated firewall)](../linux/ufw.md), [IPTables](../linux/iptables.md))
Large transfers stall | Lower `MTU = 1380` in `[Interface]`
Stops after idle | `PersistentKeepalive = 25` on the client behind NAT
