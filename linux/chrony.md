# chrony
chrony is the NTP client and server used on most modern Linux distributions to keep the clock accurate. Correct time matters for TLS certificates, Kerberos, logs, [Ceph](ceph.md) and cluster software. Use `chronyc` to see whether the clock is synchronised.

Documentation: [chrony](https://chrony-project.org/documentation.html), [chrony.conf](https://chrony-project.org/doc/latest/chrony.conf.html), [chronyc](https://chrony-project.org/doc/latest/chronyc.html)

## Check Status
COMMAND | DESCRIPTION
---|---
`chronyc tracking` | Offset, stratum, frequency error and leap status
`chronyc sources -v` | Time sources with explanations of each column
`chronyc sourcestats` | Statistics per source (NP, NR, Span, Frequency, Offset, Std Dev)
`chronyc activity` | How many sources are online, offline or unresolved
`sudo chronyc makestep` | Step the clock now
`chronyc waitsync [MAX_TRIES]` | Block until synchronised (for boot scripts)
`timedatectl` | System clock, time zone and whether NTP is active

In `sources -v` the `Reach` column is octal, and `377` means the last 8 polls all succeeded. A Reference ID of `7F7F0101` with no name means chrony is in local mode and **not** synchronised. A low `System time` offset in `tracking` is what you want.

## Client Configuration
`/etc/chrony/chrony.conf` (Debian and Ubuntu) or `/etc/chrony.conf` (Fedora and RHEL). Directives are not case-sensitive, and when one is repeated only the last takes effect. Comment lines start with `!`, `;`, `#` or `%`.

```text
pool pool.ntp.org iburst maxsources 3
driftfile /var/lib/chrony/drift
makestep 1.0 3
rtcsync
```

DIRECTIVE | MEANING
---|---
`pool <NAME> iburst` | Use a pool of servers (`maxsources` defaults to 4)
`server <NAME> iburst` | Use one server. Options include `prefer`, `minpoll`, `maxpoll`, `nts`
`makestep 1.0 3` | Step the clock if off by more than 1 second, but only during the first 3 updates
`rtcsync` | Keep the hardware clock in sync
`driftfile <PATH>` | Save the measured clock drift
`allow <SUBNET>` | Serve time to clients (without this chrony is client-only)

`makestep` replaces the deprecated `initstepslew`. After editing, restart the service (`sudo systemctl restart chrony` on Debian and Ubuntu, `chronyd` on Fedora and RHEL).

## Serve Time to Your LAN
Run one machine as the local NTP server and point everything else at it. This helps when the internet is down or devices (cameras, IoT) need a time source.

```text
pool pool.ntp.org iburst maxsources 3
allow 192.0.2.0/24
local stratum 8
rtcsync
```

`local stratum 8` lets the server keep serving time to the LAN if its upstream is unreachable. Use `local stratum 8 orphan` where several servers should agree among themselves. Open `123/udp` on the server's firewall. Point clients at it with `server ntp.lan.example.com iburst` (see [Ports and Protocols](../networking/ports-and-protocols.md)).

## timedatectl and systemd-timesyncd
Only one time service should run. If `chrony` is installed, `systemd-timesyncd` is normally disabled, and `timedatectl` then reports on chrony (the interaction is distro behaviour and was not checked against the docs here).

COMMAND | DESCRIPTION
---|---
`timedatectl set-ntp true` | Turn on network time synchronisation
`timedatectl set-timezone Europe/London` | Set the time zone
`timedatectl list-timezones` | Valid zone names

## VMs
Guests usually follow the host or a hypervisor time source. On [Proxmox](../proxmox/proxmox-overview.md), still run chrony in guests and keep the Proxmox hosts synchronised, since cluster and [Ceph](ceph.md) problems often start with clock skew (the Proxmox notes were not checked here).

## See Also
- [Linux](linux.md)
- [Ceph](ceph.md)
- [Proxmox Cluster and HA](../proxmox/proxmox-cluster-ha.md)
- [Systemd](systemd.md)
