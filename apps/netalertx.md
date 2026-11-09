# NetAlertX
NetAlertX scans your network for devices and alerts you when a new or unknown one appears. It descends from Pi.Alert, so this sheet covers both and says which one to run. Use it to spot unknown devices on a VLAN, together with [VLANs](../homelab/vlans.md) and a firewall.

Project: [NetAlertX](https://github.com/jokob-sk/NetAlertX) · [Pi.Alert](https://github.com/pucherot/Pi.Alert)
Documentation: [NetAlertX docs](https://docs.netalertx.com/)

## Pi.Alert or NetAlertX
- **Pi.Alert** uses `arp-scan` (with Pi-hole and dnsmasq optional) and alerts on new devices, reconnects, disconnects and IP changes. It only sends email. Its latest commit was in April 2021, and there is no archive banner, so treat it as unmaintained.
- **NetAlertX** credits the original Pi.Alert author in its README and is actively developed. It is the one to install. Calling it the successor is an inference, because its README does not say so.

## Install (Docker)
From the NetAlertX compose docs:

```yaml
services:
  netalertx:
    image: ghcr.io/netalertx/netalertx:latest
    network_mode: host
    read_only: true
    cap_drop:
      - ALL
    cap_add:
      - NET_ADMIN
      - NET_RAW
      - NET_BIND_SERVICE
      - CHOWN
      - SETUID
      - SETGID
    sysctls:
      net.ipv4.conf.all.arp_ignore: 1
      net.ipv4.conf.all.arp_announce: 2
    environment:
      PORT: 20211
      GRAPHQL_PORT: 20212
    volumes:
      - netalertx_data:/data
      - /etc/localtime:/etc/localtime:ro
    tmpfs:
      - /tmp
    mem_limit: 2048m
    restart: unless-stopped

volumes:
  netalertx_data:
```

- Host networking is needed so it can see your LAN with ARP. There is no `ports:` mapping, and the web UI is on port `20211`.
- The `cap_drop: ALL` line is added here to match the capability list. Check the docs page for the current compose file.
- Config and the database live in the `/data` volume (`config` and `db`). Back it up.
- The README's `docker run` example uses a different GraphQL port, so trust the compose page.
- Pin the image tag rather than `latest` once it works.

## Scanning
Supported discovery sources include `arp-scan`, the Pi-hole database and DHCP, generic DHCP leases, a UniFi import and an SNMP router. An `nmap` scan for services and ports appears in the docs navigation. One device per VLAN is seen only if the scanner has a presence on that VLAN, so run it on a trunk port or add one instance per VLAN. See [UniFi Networks and VLANs](../homelab/vlans.md) for VLAN design.

## Notifications
NetAlertX can send through Apprise (80+ services), email, MQTT, ntfy, Pushover, Pushsafer, Telegram and webhooks. See [Apprise](apprise.md), [ntfy](ntfy.md) and [Notification Services](../homelab/notification-services.md).

## Good Practice
- Mark known devices and name them, so new ones stand out.
- Alert on new devices on IoT and server VLANs first.
- Treat an alert as a prompt to check the switch port, not as proof of an intruder.
- ARP scanning shows devices only on the scanned network, so it will not see traffic across VLANs.

## Not Verified
The Pi.Alert `pialert.conf` keys, the NetAlertX config file name, the `nmap` options and the exact environment variables beyond `PORT`, `GRAPHQL_PORT` and `LISTEN_ADDR`.

## See Also
- [Notification Services](../homelab/notification-services.md)
- [VLANs](../homelab/vlans.md)
- [Network Hardening Recipe](../recipes/network-hardening.md)
- [Pi-hole](../homelab/pihole.md)
