# NUT (Network UPS Tools)
NUT monitors a UPS and shuts machines down cleanly when the battery runs low. One host (the **server**) is cabled to the UPS by USB or serial and runs a driver plus `upsd`; every other machine runs `upsmon` as a **client** that connects to the server over TCP port 3493 and shuts down when told. Typical homelab use: a Proxmox node or small box owns the USB cable, and NAS, other nodes and VMs follow it.

Documentation: [NUT user manual](https://networkupstools.org/docs/user-manual.chunked/index.html) · [upsmon.conf](https://networkupstools.org/docs/man/upsmon.conf.html) · [nut.conf](https://networkupstools.org/docs/man/nut.conf.html) · [Hardware compatibility list](https://networkupstools.org/stable-hcl.html)

> **Verification:** `MONITOR` line syntax, the `primary`/`secondary` roles, `SHUTDOWNCMD`, and `MODE` values (`none`, `standalone`, `netserver`, `netclient`) were checked against the `upsmon.conf` and `nut.conf` man pages. **Not verified:** systemd unit names, `upsd.conf` `LISTEN`, the `usbhid-ups` example, `upsc`/`upscmd`/`upsrw`/`upsdrvctl`/`nut-scanner` usage, the Proxmox shutdown ordering, and permissions on Debian. No command was executed.

See also: [Homelab](homelab.md) · [Proxmox VE Overview and Install](../proxmox/proxmox-overview.md) · [Proxmox Clustering and HA](../proxmox/proxmox-cluster-ha.md) · [Proxmox qm and pct](../proxmox/proxmox-qm-pct.md) · [Prometheus](../apps/prometheus.md) · [Grafana](../apps/grafana.md) · [UFW (uncomplicated firewall)](../linux/ufw.md) · [Wake-on-LAN](wake-on-lan.md) · [Docker-Compose](../docker/docker-compose.md)

---
## Files and Roles
FILE | ON | PURPOSE
---|---|---
`/etc/nut/nut.conf` | all | `MODE=`: `none` (default, nothing starts), `standalone`, `netserver`, `netclient`
`/etc/nut/ups.conf` | server | Define each UPS and its driver
`/etc/nut/upsd.conf` | server | `upsd` listen addresses, limits
`/etc/nut/upsd.users` | server | Users and their roles (who may monitor, who may change settings)
`/etc/nut/upsmon.conf` | all | What to monitor and how to shut down
`/etc/nut/upssched.conf` | optional | Timer-based events (for example "run on battery 5 minutes, then...")

MODE | USE
---|---
`standalone` | One machine with the UPS cable, no remote clients
`netserver` | Machine with the cable that also serves clients
`netclient` | Machine with no cable, watches a remote server

Terms: the host that is cabled to the UPS and shuts down **last** (it must tell the UPS to cut power) is the `primary`; hosts that only follow are `secondary`. These replaced the older `master` and `slave` names (older versions need the old words, newer ones accept both).

---
## Server Setup
```bash
sudo apt install nut nut-client nut-server
sudo nut-scanner -U                  # find USB UPS devices and print ups.conf stanzas
lsusb | grep -i -E 'apc|cyber|eaton|ups'
```
`/etc/nut/nut.conf`:
```ini
MODE=netserver
```
`/etc/nut/ups.conf`:
```ini
maxretry = 3

[myups]
    driver = usbhid-ups
    port = auto
    desc = "Rack UPS"
    # vendorid = 051d           # restrict to one device if you have several (value from lsusb)
    # pollinterval = 2
```
`/etc/nut/upsd.conf`:
```ini
LISTEN 127.0.0.1 3493
LISTEN 192.168.20.2 3493        # the LAN address clients will use
```
`/etc/nut/upsd.users`:
```ini
[monuser]
    password = <STRONG_PASSWORD>
    upsmon primary               # use "master" on NUT older than 2.8

[remote]
    password = <ANOTHER_PASSWORD>
    upsmon secondary             # use "slave" on NUT older than 2.8

[admin]
    password = <ADMIN_PASSWORD>
    actions = SET
    instcmds = ALL
```
`/etc/nut/upsmon.conf`:
```ini
MONITOR myups@localhost 1 monuser <STRONG_PASSWORD> primary
MINSUPPLIES 1
SHUTDOWNCMD "/sbin/shutdown -h +0"
POLLFREQ 5
POLLFREQALERT 5
HOSTSYNC 15
DEADTIME 15
FINALDELAY 5
NOTIFYCMD /usr/sbin/upssched
NOTIFYFLAG ONBATT SYSLOG+WALL
NOTIFYFLAG LOWBATT SYSLOG+WALL
```
`MONITOR <UPS>[@HOST[:PORT]] <POWERVALUE> <USER> <PASSWORD> primary|secondary`. `POWERVALUE` is how many power supplies of this machine the UPS feeds (usually `1`). `SHUTDOWNCMD` can be written as separate quoted elements on newer versions (2.8.6+); a single string works everywhere. The user's role in `upsd.users` must match the role in `MONITOR`.

Permissions (Debian/Ubuntu): config files should be `root:nut`, mode `0640`, because they contain passwords.
```bash
sudo chown root:nut /etc/nut/*.conf /etc/nut/upsd.users
sudo chmod 640 /etc/nut/*.conf /etc/nut/upsd.users
```
Start:
```bash
sudo upsdrvctl start                                  # start the driver by hand first
sudo systemctl restart nut-driver.target nut-server nut-monitor
sudo systemctl enable nut-server nut-monitor
upsc myups@localhost
```
Unit names vary: on Debian/Ubuntu look at `systemctl list-units 'nut*'` (`nut-server`, `nut-monitor`, `nut-driver@<UPS>` or `nut-driver-enumerator`, `nut-driver.target`).

Open the port to the LAN only: `sudo ufw allow from 192.168.20.0/24 to any port 3493 proto tcp` ([UFW (uncomplicated firewall)](../linux/ufw.md)). NUT's own protocol is not encrypted by default; keep it on a trusted VLAN or use TLS support if your build has it.

---
## Client Setup
On each machine that should follow the UPS:
```bash
sudo apt install nut-client
```
`/etc/nut/nut.conf`:
```ini
MODE=netclient
```
`/etc/nut/upsmon.conf`:
```ini
MONITOR myups@192.168.20.2 1 remote <ANOTHER_PASSWORD> secondary
MINSUPPLIES 1
SHUTDOWNCMD "/sbin/shutdown -h +0"
```
```bash
sudo systemctl enable --now nut-monitor
upsc myups@192.168.20.2 ups.status
```
Order of shutdown on low battery: secondaries log off from the server and shut down, then the primary waits (`HOSTSYNC`) for them before it shuts down and the UPS cuts power. Set the wait with `HOSTSYNC`.

---
## Commands
COMMAND | DESCRIPTION
---|---
`upsc -l [<HOST>]` | List UPSes on a server
`upsc <UPS>@<HOST>` | Show all variables
`upsc <UPS>@<HOST> ups.status` | Status: `OL` online, `OB` on battery, `LB` low battery, `CHRG` charging, `RB` replace battery
`upsc <UPS>@<HOST> battery.charge` | Battery percent
`upsc <UPS>@<HOST> battery.runtime` | Estimated runtime in seconds
`upsc <UPS>@<HOST> ups.load` | Load percent
`upscmd -l <UPS>@<HOST>` | List instant commands the UPS supports
`upscmd -u admin -p <PASS> <UPS>@<HOST> beeper.disable` | Run a command
`upscmd -u admin -p <PASS> <UPS>@<HOST> test.battery.start.quick` | Start a battery self-test
`upsrw -l <UPS>@<HOST>` | List writable variables
`upsrw -s battery.charge.low=30 -u admin -p <PASS> <UPS>@<HOST>` | Set a variable
`upsdrvctl start` / `stop` | Start/stop the driver(s)
`upsd -c reload` | Tell upsd to re-read its config
`upsmon -c reload` | Tell upsmon to re-read its config
`upsmon -c fsd` | Force shutdown sequence now (use with care: it shuts hosts down)
`nut-scanner -U` | Scan USB devices
`nut-scanner -N` | Scan the network (SNMP/XML/NUT) with the right options

`upsc` over TCP needs no login for read-only variables; the commands that change something need a user from `upsd.users`.

---
## Low-Battery Behaviour
OPTION | WHERE | MEANING
---|---|---
`LB` flag | UPS | The UPS itself says "low battery"; upsmon shuts down on it
`override.battery.charge.low`, `override.battery.runtime.low` | `ups.conf` | Make NUT consider "low" earlier than the UPS does, to leave time for slow shutdowns (Proxmox with many VMs)
`MINSUPPLIES` | `upsmon.conf` | Minimum healthy power supplies before shutdown (redundant PSU setups)
`FINALDELAY` | `upsmon.conf` | Seconds between the last warning and the shutdown
`HOSTSYNC` | `upsmon.conf` | How long the primary waits for secondaries
`POLLFREQ`, `POLLFREQALERT` | `upsmon.conf` | Poll interval normally and when on battery

Example: shut down once runtime falls below 10 minutes, in `ups.conf`:
```ini
[myups]
    driver = usbhid-ups
    port = auto
    override.battery.runtime.low = 600
    override.battery.charge.low = 40
```
Not every driver honours `override.*`; check the driver's man page (`man usbhid-ups`).

---
## Proxmox and Virtual Machines
- Install NUT on the **node** that has the USB cable and run `netserver` mode; other nodes and a NAS run `netclient`. See [Proxmox VE Overview and Install](../proxmox/proxmox-overview.md) and [Proxmox Clustering and HA](../proxmox/proxmox-cluster-ha.md).
- A node shutdown by `shutdown -h now` stops guests following their "Start/Shutdown order" and timeouts; set sensible shutdown timeouts per guest (`qm set <VMID> --startup order=1,down=60`, see [Proxmox qm and pct](../proxmox/proxmox-qm-pct.md)).
- Do not pass the USB UPS through to a VM if the node should survive or coordinate; if you must, pass it to a single VM and make that VM the server, and mind that it stops first.
- In a cluster, losing quorum while nodes shut down one after another is normal; plan which node shuts down last and whether to expect fencing/HA to react.
- Power-on after the outage: set BIOS "Restore on AC power loss: power on", and use [Wake-on-LAN](wake-on-lan.md) for machines that stay off.

---
## Docker Compose (NUT server)
USB passthrough needs the device mapped in. Image and config paths differ by image, so read the image README before use.
```yaml
services:
  nut:
    image: <NUT_SERVER_IMAGE>:<TAG>
    restart: unless-stopped
    devices:
      - /dev/bus/usb:/dev/bus/usb
    ports:
      - "192.168.20.2:3493:3493"
    volumes:
      - ./nut:/etc/nut:ro
```
Running NUT on the host is usually simpler and more reliable than in a container, because the shutdown must act on the host.

---
## Metrics and Alerts
- **Prometheus:** use a NUT exporter that talks to port 3493 (see [Prometheus](../apps/prometheus.md)), then graph `battery.charge`, `ups.load`, `ups.status` in [Grafana](../apps/grafana.md).
- **Notifications:** `upsmon` runs `NOTIFYCMD` for events (`ONLINE`, `ONBATT`, `LOWBATT`, `COMMBAD`, `SHUTDOWN`); `upssched` can wait a few minutes before reacting. Example `upssched.conf`:
```ini
CMDSCRIPT /usr/local/bin/ups-event.sh
PIPEFN /run/nut/upssched.pipe
LOCKFN /run/nut/upssched.lock
AT ONBATT * START-TIMER onbatt-warn 60
AT ONLINE * CANCEL-TIMER onbatt-warn
```

---
## Troubleshooting
SYMPTOM | CHECK
---|---
`upsc` says `Error: Data stale` | Driver not running or crashed: `sudo upsdrvctl start`, `journalctl -u nut-driver@myups` (or `nut-driver.target`)
`Can't claim USB device` | Permissions or another process owns it. Replug, check udev rules in the package (`/lib/udev/rules.d/62-nut-usbups.rules`), `sudo udevadm trigger`, or `user`/`group` in `ups.conf`
`Connection refused` from a client | `LISTEN` address in `upsd.conf` missing, `nut-server` not running, or firewall blocks 3493
`Login failed` / `Access denied` | Username or password mismatch; role in `upsd.users` does not match the `MONITOR` line; remember `primary`/`secondary` versus `master`/`slave` on older NUT
UPS shows `OL` but `RB` | Battery needs replacement
Shutdown never happens | `upsmon` not running (`MODE=none` in `nut.conf`), or `SHUTDOWNCMD` fails; test with `upsmon -c fsd` **on a test machine only**
Everything shuts down on a short blip | `override.battery.*.low` too high, or UPS reports `LB` early; lengthen delays with `upssched` timers
UPS powers off before secondaries finish | Raise `HOSTSYNC`, make the primary last, set `override.battery.runtime.low` larger
Config changes ignored | `sudo systemctl restart nut-server nut-monitor` and re-run `upsdrvctl start`; `upsd -c reload`
Unit names not found | `systemctl list-units 'nut*'`; names differ between Debian releases and between packages
Run in foreground to debug | `sudo upsdrvctl -D start` (extra `-D` for more detail), `sudo upsd -D`, `sudo upsmon -D`
