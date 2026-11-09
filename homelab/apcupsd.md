# apcupsd
apcupsd monitors APC UPSes (USB, serial, SNMP or network) and shuts the host down cleanly when the battery runs low. One host owns the cable and runs the daemon; other hosts can read its status over the built-in Network Information Server (NIS, TCP port 3551). For vendor-neutral UPS software see [NUT (Network UPS Tools)](nut-ups.md).

Project: [apcupsd](http://www.apcupsd.org/)
Documentation: [apcupsd(8)](https://manpages.debian.org/apcupsd.8)

> **Verification:** Not run against a live UPS. Config directive names and `apcaccess` usage follow the apcupsd manual from memory; check `man apcupsd.conf`, `man apcaccess` and `man apcupsd` on your version. Items marked (unverified) in particular need checking. Third-party tools (exporters, REST wrappers) are named as examples only.

See also: [NUT (Network UPS Tools)](nut-ups.md) · [Homelab](homelab.md) · [REST APIs](../tools/rest-api.md) · [Prometheus](../apps/prometheus.md) · [Grafana](../apps/grafana.md) · [UFW (uncomplicated firewall)](../linux/ufw.md) · [Wake-on-LAN](wake-on-lan.md)

---
## Files and Roles
FILE | PURPOSE
---|---
`/etc/apcupsd/apcupsd.conf` | Main configuration
`/etc/default/apcupsd` | Debian/Ubuntu: set `ISCONFIGURED=yes` or the service will not start
`/etc/apcupsd/onbattery`, `offbattery` | Scripts run when the UPS goes on or off battery
`/etc/apcupsd/commfailure`, `commok` | Scripts run when communication with the UPS is lost or restored
`/etc/apcupsd/doshutdown` | Script run when shutdown is triggered
`/etc/apcupsd/apccontrol` | Dispatcher that runs the event scripts above
`/var/log/apcupsd.events` | Event log

---
## Install and Start
```bash
sudo apt install apcupsd
sudoedit /etc/default/apcupsd        # ISCONFIGURED=yes
sudoedit /etc/apcupsd/apcupsd.conf
sudo systemctl enable --now apcupsd
apcaccess status
```

---
## Configuration
Local USB UPS (`/etc/apcupsd/apcupsd.conf`):
```ini
UPSNAME rack-ups
UPSCABLE usb
UPSTYPE usb
DEVICE
LOCKFILE /var/lock
POLLTIME 60
ONBATTERYDELAY 6
BATTERYLEVEL 20
MINUTES 5
TIMEOUT 0
NETSERVER on
NISIP 127.0.0.1
NISPORT 3551
```
Leave `DEVICE` empty for USB so apcupsd autodetects it.

DIRECTIVE | MEANING
---|---
`UPSCABLE` | `usb`, `smart`, `simple`, or `ether` for network
`UPSTYPE` | `usb`, `apcsmart`, `net` (client of another apcupsd), `snmp`, `pcnet`, `modbus`
`DEVICE` | Empty for USB, serial port for serial, `<HOST>:3551` for `net`
`BATTERYLEVEL` | Shut down when charge falls to this percent
`MINUTES` | Shut down when estimated runtime falls to this many minutes
`TIMEOUT` | Shut down after this many seconds on battery (`0` disables)
`ONBATTERYDELAY` | Seconds on battery before the `onbattery` event fires
`NETSERVER` | `on` enables the NIS server for remote `apcaccess` and clients
`NISIP` | Address NIS listens on; default is loopback only
`NISPORT` | NIS port, default `3551`

Shutdown fires on whichever of `BATTERYLEVEL`, `MINUTES` or `TIMEOUT` is reached first.

Network client (a second machine that follows the host that owns the cable):
```ini
UPSNAME follower
UPSCABLE ether
UPSTYPE net
DEVICE 192.0.2.10:3551
```

Allow the LAN only, on the server: `sudo ufw allow from 192.0.2.0/24 to any port 3551 proto tcp` ([UFW (uncomplicated firewall)](../linux/ufw.md)). NIS is unauthenticated and unencrypted; keep it on a trusted VLAN and set `NISIP` to a specific address, not `0.0.0.0`, where you can.

---
## Commands
COMMAND | DESCRIPTION
---|---
`apcaccess` | Show full status of the local UPS (same as `apcaccess status`)
`apcaccess status <HOST>:3551` | Query a remote apcupsd NIS server
`apcaccess -h <HOST>:3551` | Same, using the option form
`apcaccess status \| grep -E 'STATUS\|LOADPCT\|BCHARGE\|TIMELEFT'` | Pick out the useful lines
`apcaccess -u` | Print values without units (easier to parse) (unverified on older versions)
`sudo apctest` | Interactive hardware test and calibration (stop the daemon first: `sudo systemctl stop apcupsd`)
`sudo systemctl restart apcupsd` | Re-read the configuration
`journalctl -u apcupsd` | Daemon log
`tail -f /var/log/apcupsd.events` | Watch power events
`man apcupsd.conf` | Every directive for your version

---
## Status Fields
FIELD | MEANING
---|---
`STATUS` | `ONLINE`, `ONBATT`, `COMMLOST`, plus flags such as `LOWBATT`, `REPLACEBATT`, `CHARGING`
`LINEV` | Input line voltage
`LOADPCT` | Load as percent of capacity
`BCHARGE` | Battery charge percent
`TIMELEFT` | Estimated runtime remaining, in minutes
`BATTV` | Battery voltage
`NUMXFERS` | Number of transfers to battery since start
`TONBATT` | Seconds on battery in the current event
`CUMONBATT` | Cumulative seconds on battery
`LASTXFER` | Reason for the last transfer to battery
`SELFTEST` | Result of the last self-test
`MBATTCHG` | Configured shutdown charge percent
`MINTIMEL` | Configured shutdown runtime in minutes

Fields present vary by model and connection.

---
## Event Scripts
Create `/etc/apcupsd/onbattery` with your own actions, which override the stock script of the same name. The scripts run as root, so keep them short and quote everything.
```bash
#!/bin/sh
logger -t apcupsd "UPS on battery"
curl -fsS -m 10 -d "UPS on battery" https://ntfy.example.com/ups || true
exit 0
```
Exit code `0` lets apcupsd carry on with its default action; exit `99` skips it (unverified; check `man apccontrol`).

---
## Reading It over HTTP (REST)
apcupsd has no built-in REST or HTTP API: its protocol is the NIS text protocol on TCP port 3551, read by `apcaccess`. To get at it from scripts or dashboards, use a wrapper. See [REST APIs](../tools/rest-api.md) for calling the result.

APPROACH | NOTES
---|---
`apcaccess` plus a script | Parse `apcaccess status` in a cron job or [Prometheus](../apps/prometheus.md) textfile collector
apcupsd exporter for Prometheus | Third-party exporter that queries port 3551 and serves `/metrics` over HTTP, then graph in [Grafana](../apps/grafana.md)
Home Assistant APC UPS Daemon integration | Reads NIS directly; no wrapper needed
Small web service | A few lines of Python or shell that run `apcaccess` and return JSON

Turn `apcaccess` into JSON in shell:
```bash
apcaccess status | awk -F' *: ' '{printf "%s\"%s\":\"%s\"", sep, $1, $2; sep=","} BEGIN{printf "{"} END{print "}"}'
```
Then query it like any API, for example `curl -s http://HOST:8080/ups | jq '{status: .STATUS, charge: .BCHARGE}'`. Values keep their units (`100.0 Percent`); use `apcaccess -u` or strip them in the wrapper.

---
## Troubleshooting
SYMPTOM | CHECK
---|---
Service exits straight away | `ISCONFIGURED=yes` in `/etc/default/apcupsd`; `journalctl -u apcupsd`
`STATUS : COMMLOST` | USB cable or `UPSTYPE`/`UPSCABLE` mismatch; `lsusb`, replug, check `DEVICE` is empty for USB
`apcaccess` says it cannot connect | Daemon not running, `NETSERVER on` missing, or `NISIP` not the address you query
Remote `apcaccess` times out | `NISIP` bound to loopback, or firewall blocks 3551
Shuts down too early or too late | `BATTERYLEVEL`, `MINUTES` and `TIMEOUT`; whichever is hit first wins
Config changes ignored | `sudo systemctl restart apcupsd`
Event scripts do not run | Executable bit, shebang, and that the filename matches a stock event name
Need low-level test | `sudo systemctl stop apcupsd && sudo apctest`
