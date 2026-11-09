# UniFi Hosting
Where the UniFi Network controller can run: on a console, as UniFi OS Server on your own Linux host, as the legacy Network Server package, or in a community Docker image. Ubiquiti calls UniFi OS Server the new standard for self-hosting and the replacement for the legacy Network Server.

Documentation: [UniFi OS Server](https://help.ui.com/hc/en-us/articles/34210126298775) · [Required Ports Reference](https://help.ui.com/hc/en-us/articles/218506997) · [Install the Network Server](https://help.ui.com/hc/en-us/articles/220066768)

## Options
OPTION | NOTES
---|---
Console (Cloud Gateway, Cloud Key, UNVR) | Hardware running UniFi OS. Simplest, with backups built in
UniFi OS Server | Self-hosted on Linux, licence-free. Not offered as a standalone Docker or Podman container
Legacy Network Server | Debian or Ubuntu package. Network app only, no UniFi OS
Community Docker images | `linuxserver/unifi-network-application`, `jacobalberty/unifi`. Unofficial

## UniFi OS Server
Requirements from the help article: systemd, libc 2.31 or newer, podman 4.9.3 or newer with pasta, slirp4netns 1.2 or newer, Ubuntu 24.04 or newer or Debian 13 or newer, x86-64, 2 GB RAM minimum and 10 GB free disk.

```bash
sudo apt-get update && sudo apt-get install podman slirp4netns
curl -O <LINK_COPIED_FROM_UI_COM_DOWNLOAD>
chmod +x <INSTALLER_FILE>
sudo ./<INSTALLER_FILE>
```

COMMAND | DESCRIPTION
---|---
`sudo systemctl start uosserver` | Start (`stop`, `enable` and `disable` work the same way)
`sudo systemctl status uosserver` | State

- Do not clone a VM that runs it.
- A Windows service is not supported.
- Cloud Gateways (UDM, UCG) cannot be managed by it. Only UXG-series gateways can.
- The captive portal uses port 8444 (it was 8843).
- The web UI is on port 11443 and some helper commands (`uosserver status`, `uosserver shell`) are reported by third-party guides. **Unverified** against Ubiquiti's own pages.

## Legacy Network Server (apt)
Ubiquiti's article, for Debian and Ubuntu:

```bash
sudo apt-get update && sudo apt-get install ca-certificates apt-transport-https
echo 'deb [ arch=amd64,arm64 ] https://www.ui.com/downloads/unifi/debian stable ubiquiti' | sudo tee /etc/apt/sources.list.d/100-ubnt-unifi.list
sudo wget -O /etc/apt/trusted.gpg.d/unifi-repo.gpg https://dl.ui.com/unifi/unifi-repo.gpg
sudo apt-get update && sudo apt-get install unifi -y
```

New installs also need MongoDB. The article names MongoDB 3.6 from the Ubuntu bionic repository, so read the current version of the article for supported releases before copying that line.

COMMAND | DESCRIPTION
---|---
`sudo service unifi start` | Start (`stop`, `restart`, `status`)
`tail -f /usr/lib/unifi/logs/server.log` | Application log (`mongod.log` is alongside)

Ports can be changed only on self-hosted servers, in `<unifi_base>/data/system.properties`, for example `unifi.shutdown.port=8089`.

## Docker (linuxserver)
Unofficial image from LinuxServer.io, plus MongoDB.

```yaml
services:
  unifi-network-application:
    image: lscr.io/linuxserver/unifi-network-application:latest
    restart: unless-stopped
    environment:
      PUID: "1000"
      PGID: "1000"
      TZ: Europe/London
      MONGO_USER: unifi
      MONGO_PASS: ${MONGO_PASS}
      MONGO_HOST: unifi-db
      MONGO_PORT: "27017"
      MONGO_DBNAME: unifi
      MONGO_AUTHSOURCE: admin
    volumes:
      - ./unifi-config:/config
    ports:
      - "8443:8443"
      - "3478:3478/udp"
      - "10001:10001/udp"
      - "8080:8080"
    depends_on:
      - unifi-db

  unifi-db:
    image: docker.io/mongo:<PINNED_TAG>
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASS}
      MONGO_USER: unifi
      MONGO_PASS: ${MONGO_PASS}
      MONGO_DBNAME: unifi
      MONGO_AUTHSOURCE: admin
    volumes:
      - ./unifi-db:/data/db
      - ./init-mongo.sh:/docker-entrypoint-initdb.d/init-mongo.sh:ro
```

- Pin the MongoDB tag and do not use `latest`.
- The init script runs only on the first start, and the `MONGO_*` values in the app container are only read on first run. The init script's contents come from the image's README, so copy it from there.
- Optional ports: `1900/udp`, `8843`, `8880`, `6789`, `5514/udp`. Optional `MEM_LIMIT` and `MEM_STARTUP` tune Java memory.
- Pointing devices at the host needs `set-inform`, see [UniFi Device CLI and Adoption](unifi-device-cli.md).

`jacobalberty/unifi` is another image. It maps one directory to `/unifi` (with `data`, `log`, `cert` and `init.d`) and takes `SYSTEM_IP`, `TZ`, `JVM_MAX_HEAP_SIZE` and `LOTSOFDEVICES`. Check its README for current tags.

## Required Ports
Ubiquiti's reference, for a self-hosted controller:

PORT | USE
---|---
TCP 8080 | Device to controller (inform)
TCP 8443 | Web UI and API (on UniFi OS consoles the UI uses 443)
UDP 3478 | STUN
UDP 10001 | Device discovery
TCP 6789 | Mobile speed test
TCP 8880-8882 | Hotspot portal (HTTP)
TCP 8843 | Hotspot portal (HTTPS)
TCP 8444 | Secure portal for Hotspot
UDP 1900 | Layer 2 discovery
UDP 5514 | Remote syslog
TCP 27117 | Local database (keep local)
TCP 28082 | Packet capture and support file downloads
UDP 10101 | Client fingerprinting
TCP 22 | SSH
TCP 443 | Console UI, API and remote access
UDP 123 | NTP
TCP/UDP 53 | DNS

Do not expose these to the internet. Use [WireGuard or Teleport](unifi-firewall-vpn.md) instead of port forwarding the controller.

## Not Verified
UniFi OS Server's UI port and helper commands, the Docker init script, Site Manager details, and current MongoDB support for the apt install.

## See Also
- [UniFi](unifi.md)
- [UniFi Backups and Migration](unifi-backups.md)
- [UniFi Device CLI and Adoption](unifi-device-cli.md)
- [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md)
