# Tailscale
**Tailscale** is a zero config **VPN ([[vpn]])** for building secure networks, powered by **WireGuard ([[wireguard]])**. Install on any device in minutes. Remote access from any network or physical location.

Project Homepage: https://tailscale.com
Documentation: [Tailscale Docs](https://tailscale.com/kb)

---
## Install
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

## Commands
COMMAND | DESCRIPTION
---|---
`sudo tailscale up` | Connect and authenticate
`sudo tailscale up --ssh` | Enable Tailscale SSH
`sudo tailscale up --advertise-routes=192.168.1.0/24` | Act as a subnet router (approve in the admin console)
`sudo tailscale up --advertise-exit-node` | Offer this machine as an exit node
`sudo tailscale up --exit-node=<NODE>` | Use an exit node
`sudo tailscale up --accept-routes` | Accept subnet routes from others (needed on Linux clients)
`sudo tailscale up --reset` | Reset flags to defaults
`tailscale status` | Peers and connection state
`tailscale ip -4` | This node's Tailscale IPv4
`tailscale ping <PEER>` | Test connectivity, shows direct or relay (DERP)
`tailscale netcheck` | NAT and relay diagnostics
`tailscale whois <IP>` | Who owns an address
`tailscale file cp <FILE> <PEER>:` | Send a file (Taildrop)
`tailscale serve 3000` | Share a local port inside your tailnet
`tailscale funnel 3000` | Expose a local port to the public internet
`sudo tailscale down` | Disconnect
`sudo tailscale logout` | Remove this device
`sudo tailscale set --hostname=<NAME>` | Rename

## Subnet Router / Exit Node on Linux
```bash
echo 'net.ipv4.ip_forward = 1' | sudo tee /etc/sysctl.d/99-tailscale.conf
echo 'net.ipv6.conf.all.forwarding = 1' | sudo tee -a /etc/sysctl.d/99-tailscale.conf
sudo sysctl -p /etc/sysctl.d/99-tailscale.conf
```

## Docker
```yaml
services:
  tailscale:
    image: tailscale/tailscale
    hostname: myhost
    environment:
      TS_AUTHKEY: ${TS_AUTHKEY}
      TS_STATE_DIR: /var/lib/tailscale
    volumes:
      - ts-state:/var/lib/tailscale
    devices:
      - /dev/net/tun:/dev/net/tun
    cap_add: [net_admin]
volumes:
  ts-state:
```

## Tips
- Disable key expiry for servers in the admin console.
- Use ACL tags (`tag:server`) rather than personal ownership for machines.
- MagicDNS gives every device a name such as `host.tailnet-name.ts.net`.
