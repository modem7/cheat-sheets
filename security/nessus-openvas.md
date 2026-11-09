# Nessus and OpenVAS
Vulnerability scanners that probe hosts across the network for missing patches and misconfiguration. Nessus is Tenable's commercial scanner with a limited free tier. Greenbone Community Edition (OpenVAS) is the open source alternative. Only scan machines you own or have permission to scan.

Documentation: [Nessus](https://docs.tenable.com/nessus/) · [Greenbone Community Edition](https://greenbone.github.io/docs/latest/)

## Nessus Essentials
The free tier is for non-commercial use and covers 5 hosts. Tenable's current licence pages give 5 hosts per scan and across unique hosts (hosts not scanned for 90 days drop off the count). Older documentation said 16, so check the current terms. The marketing page also says plugin updates are delayed and that compliance checks, reporting and export are not included.

## Install (Debian and Ubuntu)
```bash
sudo dpkg -i Nessus-<VERSION>-debian6_amd64.deb
sudo systemctl start nessusd
```

Open `https://localhost:8834` and complete setup with your activation code. Enable at boot with `sudo systemctl enable nessusd` (the official page only shows `start`).

## nessuscli
Located at `/opt/nessus/sbin/nessuscli`.

COMMAND | DESCRIPTION
---|---
`nessuscli update` | Update plugins (or pass a `.tar.gz` for offline)
`nessuscli adduser <USER>` | Create a user
`nessuscli lsuser` | List users
`nessuscli chpasswd <USER>` | Change a password
`nessuscli fetch --register <ACTIVATION_CODE>` | Register
`nessuscli fix --list` | List settings (`--secure` for secure settings)

`update --all` is mentioned in some guides but was not on the official page.

## Nessus Agents
```bash
sudo dpkg -i NessusAgent-<VERSION>-debian6_amd64.deb
sudo /sbin/service nessusagent start
sudo /opt/nessus_agent/sbin/nessuscli agent link --key=<KEY> --name=<NAME> --groups="All" --host=<HOST> --port=8834
```

Scan templates, export formats and plugin feeds were not researched.

## Greenbone Community Edition
Container setup from the Greenbone docs:

```bash
export DOWNLOAD_DIR=$HOME/greenbone-community-edition
mkdir -p $DOWNLOAD_DIR
curl -f -O -L https://greenbone.github.io/docs/latest/_static/compose.yaml --output-dir "$DOWNLOAD_DIR"
docker compose -f $DOWNLOAD_DIR/compose.yaml pull
docker compose -f $DOWNLOAD_DIR/compose.yaml up -d
docker compose -f $DOWNLOAD_DIR/compose.yaml logs -f
```

The UI is at `https://127.0.0.1`, bound to localhost only. Set the admin password before first use:

```bash
docker compose -f $DOWNLOAD_DIR/compose.yaml exec -u gvmd gvmd gvmd --user=admin --new-password='<NEW_PASSWORD>'
```

The default login is `admin` with the default password, so change it. Wait for the vulnerability feed data to load before you scan, or results will be empty. To reach it from another machine use an SSH tunnel or a [reverse proxy](../homelab/reverse-proxy-patterns.md) with authentication.

## Choosing
NEED | USE
---|---
Free, self-hosted, open source | Greenbone Community Edition
Polished UI and wide plugin coverage, small lab | Nessus Essentials (5 hosts)
Agent-based endpoint data, alerting | [Wazuh](wazuh.md)
Quick local checks of a Linux host | [Lynis and auditd](lynis-and-auditd.md)

## Scanning Safely
- Start with a single test host. Aggressive scans can crash fragile devices such as printers and old IoT.
- Use credentialed scans for accurate patch results.
- Run scans from a known IP and tell the people who watch your alerts.
- Keep the scanner off the internet.

## Not Verified
Nessus scan templates and export formats, Greenbone feed update commands, and plugin delay details.

## See Also
- [Wazuh](wazuh.md)
- [Lynis and auditd](lynis-and-auditd.md)
- [Network Hardening Recipe](../recipes/network-hardening.md)
- [Container Scanning](container-scanning.md)
