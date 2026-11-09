# Tailscale
**Tailscale** is a zero config **VPN ([VPN (Virtual Private Network)](../networking/vpn.md))** for building secure networks, powered by **[WireGuard](wireguard.md)**. Install on any device in minutes. Remote access from any network or physical location.

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

## Tailscale SSH
Tailscale SSH lets `tailscaled` handle SSH on the node's Tailscale IP, so access follows your tailnet policy and identity instead of per-host keys. It does not replace `sshd`: `sshd_config` and `authorized_keys` are untouched, and `tailscaled` only intercepts port 22 on the Tailscale address. It can be an alternative to a [bastion host](../recipes/ssh-bastion-lxc.md).

Documentation: [Tailscale SSH](https://tailscale.com/kb/1193/tailscale-ssh) · [Access control syntax](https://tailscale.com/kb/1337/acl-syntax)

COMMAND | DESCRIPTION
---|---
`sudo tailscale set --ssh` | Run the SSH server on this node
`sudo tailscale set --ssh=false` | Turn it off
`ssh <USER>@<NODE>` | Connect from any Tailscale device (MagicDNS name or Tailscale IP)

- The SSH server runs on Linux and on macOS (the open-source `tailscaled` build only), v1.24 or later. Not Synology or QNAP.
- The SSH port cannot be changed. Enabling it can drop existing SSH sessions to the Tailscale IP.
- You need two policy entries: a network rule allowing port 22, and an `ssh` rule. `dst` must be a tag, `autogroup:self` or a single user. `src` cannot be `*` or an IP.

```json
"ssh": [
  {
    "action": "check",
    "src": ["autogroup:member"],
    "dst": ["autogroup:self"],
    "users": ["autogroup:nonroot", "root"]
  }
]
```

ACTION | EFFECT
---|---
`accept` | Allow the connection
`check` | Require a recent re-authentication first. `checkPeriod` sets how long it lasts (default 12h, minimum 1m, maximum 168h, or `always`). The ACL page lists `checkPeriod` as a paid-plan feature. Not usable from a tagged source

`check` rules are evaluated before `accept` rules. Session recording can be enforced but how to set it up is *(unverified)*. The `tailscale ssh` subcommand is also *(unverified)*, so use plain `ssh`.

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
