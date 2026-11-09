# Network Hardening Recipe
A layered checklist for hardening a homelab network: segment it, lock down the edge and the hosts, then add detection and regular scanning. Each step points at the sheet that has the commands. Work through it in order and test after each step so you do not lock yourself out.

> **Verification:** this recipe links to existing sheets and adds no new commands of its own. Check the commands in each linked sheet before running them.

## Goal
Untrusted devices cannot reach your servers or management interfaces, only the services you intend are reachable, remote access goes through a VPN, and you are alerted when something unusual happens.

## Prerequisites
- A router or firewall you control, and ideally VLAN-capable switches and access points.
- A second way in (console or out-of-band) before you change firewall or SSH settings.
- A tested [backup](restore-test-a-backup.md) of router and host configs.

## Steps
1. **Take stock.** List devices and open services so you know what you are protecting. Scan your own network from inside, for example with `nmap`, and note anything unexpected.
2. **Segment.** Put management, trusted clients, servers, IoT, cameras and guests on separate VLANs with default-deny rules between them. See [VLANs](../homelab/vlans.md).
3. **Lock the edge.** Close all inbound ports you do not need. Expose web services through a [Cloudflare Tunnel](expose-service-cloudflare-tunnel.md) or a [reverse proxy](../homelab/reverse-proxy-patterns.md) with authentication, not raw port forwards.
4. **Use a VPN for remote access.** Reach management interfaces only over [WireGuard](wireguard-remote-access.md) or a mesh VPN ([Mesh VPN Comparison](../networking/mesh-vpn-comparison.md)).
5. **Harden DNS.** Use a filtering resolver ([Pi-hole](../homelab/pihole.md), [AdGuard Home](../homelab/adguard-home.md)) and encrypted upstreams, see [DNS over HTTPS](../networking/dns-over-https.md) and [DNSSEC](../networking/dnssec.md).
6. **Harden each host.** Key-only SSH ([SSH Hardening](../security/ssh-hardening.md)), a host firewall ([UFW](../linux/ufw.md) or [nftables](../linux/nftables.md)), and automatic security updates. Follow the [New Server Checklist](new-server-checklist.md).
7. **Add login protection.** [fail2ban](../security/fail2ban.md) or [CrowdSec](../security/crowdsec.md), and single sign-on with [Authelia](../security/authelia.md) in front of web apps.
8. **Audit.** Run [Lynis and auditd](../security/lynis-and-auditd.md) on hosts and review the results.
9. **Detect.** Collect logs and alerts with [Wazuh](../security/wazuh.md), and send alerts to your phone through [Notification Services](../homelab/notification-services.md).
10. **Scan for vulnerabilities.** Use [Nessus and OpenVAS](../security/nessus-openvas.md) for hosts and [Container Scanning](../security/container-scanning.md) for images.
11. **Review regularly.** Repeat the inventory, check firewall rules, rotate secrets and test restores.

## Verify
- From an IoT or guest VLAN, you cannot reach servers, management interfaces or other VLANs.
- An external port scan of your public IP shows only what you meant to expose.
- SSH password login is refused, and a banned test IP is blocked.
- You receive a test alert on your phone.

## Roll Back
Keep a console or out-of-band connection open while you change firewall and SSH rules, and restore the saved router configuration if you lose access. Make changes one at a time.

## Not Verified
This recipe has not been run end to end. pfSense and OPNsense are not covered yet.

## See Also
- [New Server Checklist](new-server-checklist.md)
- [Network Troubleshooting](network-troubleshooting.md)
- [Wazuh](../security/wazuh.md)
- [VLANs](../homelab/vlans.md)
