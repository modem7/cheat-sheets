# ZeroTier
ZeroTier creates virtual Ethernet networks between devices, managed from ZeroTier Central or your own controller. Use it when you want a flat layer-2 style network across sites or to join a shared network by ID. Compare it in [Mesh VPN Comparison](../networking/mesh-vpn-comparison.md).

Documentation: [ZeroTier docs](https://docs.zerotier.com/)

## Basics
- Download the client from the [ZeroTier download page](https://www.zerotier.com/download). Linux package commands are on that page (not verified here).
- A network ID is 16 hex characters, for example `6722f92749d059c7`, shown in ZeroTier Central.
- A device that joins is `ACCESS_DENIED` until you authorise it under Members in Central.
- Do not overlap a ZeroTier subnet with your LAN subnets.

## zerotier-cli
Run with `sudo` on Linux and macOS. Add `-j` for JSON.

COMMAND | DESCRIPTION
---|---
`sudo zerotier-cli join <NETWORK_ID>` | Join a network (prints `200 join OK`)
`sudo zerotier-cli leave <NETWORK_ID>` | Leave a network
`sudo zerotier-cli listnetworks` | Joined networks and their status
`zerotier-cli info` | Node ID, version and `ONLINE`/`OFFLINE`/`TUNNELED`
`zerotier-cli peers` | Peers, human readable (`LEAF` is a device, `PLANET` is a root)
`zerotier-cli listpeers` | Peers, script friendly
`sudo zerotier-cli get <NETWORK_ID> <SETTING>` | Read a client setting
`sudo zerotier-cli set <NETWORK_ID> allowGlobal true` | Change a client setting
`zerotier-cli dump` | Write a debug file (may contain IP addresses)

Client settings: `allowManaged`, `allowGlobal`, `allowDefault`, `allowDNS`.

## Join Status and Node State
VALUE | MEANING
---|---
`REQUESTING_CONFIGURATION` | Waiting for the controller
`ACCESS_DENIED` | Authorise the member in Central
`NOT_FOUND` | Wrong network ID
`PORT_ERROR` | Local service problem
`TUNNELED` | UDP 9993 is blocked, using a TCP fallback relay

## Ports
`9993/udp` carries peer traffic. The local service API also listens on `localhost:9993`, which is a different use of the same number.

## Self-hosted Controller (API)
The docs describe this as a low-tech example. The local auth token comes from the ZeroTier home directory (see the [API tokens guide](https://docs.zerotier.com/tokens/), not verified here).

```bash
NODEID=$(sudo zerotier-cli info | cut -d' ' -f3)
curl -X POST "http://localhost:9993/controller/network/${NODEID}______" \
  -H "X-ZT1-AUTH: ${TOKEN}" -d '{}'
```

```bash
curl -X POST "http://localhost:9993/controller/network/${NWID}" \
  -H "X-ZT1-AUTH: ${TOKEN}" \
  -d '{"ipAssignmentPools": [{"ipRangeStart": "10.147.17.1", "ipRangeEnd": "10.147.17.254"}], "routes": [{"target": "10.147.17.0/24", "via": null}], "v4AssignMode": "zt", "private": true}'
```

```bash
curl -X POST "http://localhost:9993/controller/network/${NWID}/member/${MEMID}" \
  -H "X-ZT1-AUTH: ${TOKEN}" -d '{"authorized": true}'
```

Deauthorise a member before deleting it, or a node that is still online can reappear. Back up the ZeroTier home directory, mainly `identity.secret` and `controller.d`. Licence terms for the controller and Central pricing are not verified here, so check them before relying on either.

## Licence Note
The client reports "ZeroTier BSL 1.1" in `zerotier-cli -h` (version 1.14.2), a source-available licence rather than a classic open source one.

## See Also
- [Mesh VPN Comparison](../networking/mesh-vpn-comparison.md)
- [Tailscale](tailscale.md)
- [WireGuard](wireguard.md)
- [Ports and Protocols](../networking/ports-and-protocols.md)
