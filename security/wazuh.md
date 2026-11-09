# Wazuh
Wazuh is an open source security platform: agents on your hosts send logs, file integrity changes, vulnerability data and configuration checks to a manager, which stores alerts in an indexer and shows them in a dashboard. Use it as a self-hosted SIEM and endpoint monitor. The quickstart suits roughly 1 to 25 agents on a single host with 4 vCPU and 8 GiB RAM. These notes follow the 4.14 documentation.

Documentation: [Wazuh docs](https://documentation.wazuh.com/current/)

## Components
COMPONENT | ROLE
---|---
Indexer | Stores and searches alerts (OpenSearch based)
Server (manager) | Analyses agent data and applies rules
Dashboard | Web UI
Agent | Runs on each monitored host

## Install (All-in-One)
```bash
curl -sO https://packages.wazuh.com/4.14/wazuh-install.sh
sudo bash ./wazuh-install.sh -a
```

The dashboard user is `admin`, and the password is printed at the end. Recover generated passwords later with:

```bash
sudo tar -O -xvf wazuh-install-files.tar wazuh-install-files/wazuh-passwords.txt
```

Installer flags, read from the script itself (the docs list only a few):

FLAG | MEANING
---|---
`-a` | All-in-one
`-i` | Ignore the hardware check
`-o` | Overwrite an existing install (**erases config and data**)
`-u` | Uninstall
`-g` | Generate config files
`-c <FILE>` | Config file
`-t <TAR>` | Certificates tar
`-s` | Start the indexer cluster
`-wi <NODE>`, `-ws <NODE>`, `-wd <NODE>` | Install the indexer, server or dashboard node
`-p` | Dashboard port (default 443)
`-of` | Offline install
`-v` | Verbose
`-V` | Show version

## Install (Docker)
```bash
sudo sysctl -w vm.max_map_count=262144
git clone https://github.com/wazuh/wazuh-docker.git -b v4.14.10
cd wazuh-docker/single-node
docker compose -f generate-indexer-certs.yml run --rm generator
docker compose up -d
```

Certificates are written to `config/wazuh_indexer_ssl_certs/`. The compose files ship with a documented default admin password, so change it before exposing anything. Make the `sysctl` setting permanent in `/etc/sysctl.d/`.

## Ports
PORT | USE
---|---
1514 TCP | Agent events
1515 TCP | Agent enrolment
514 UDP | Syslog
55000 | Server API
9200 | Indexer
443 | Dashboard

Do not expose 9200 or 55000 to the internet.

## Agents
Debian and Ubuntu:

```bash
sudo apt-get install gnupg apt-transport-https curl
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && sudo chmod 644 /usr/share/keyrings/wazuh.gpg
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | sudo tee /etc/apt/sources.list.d/wazuh.list
sudo apt-get update
sudo WAZUH_MANAGER="<MANAGER_IP_OR_NAME>" apt-get install wazuh-agent
sudo systemctl daemon-reload
sudo systemctl enable --now wazuh-agent
```

Keep the agent version no newer than the manager. To stop the repo upgrading components unexpectedly after install, the docs show commenting it out: `sudo sed -i "s/^deb /#deb /" /etc/apt/sources.list.d/wazuh.list && sudo apt update`.

## Agent and Service Tools
COMMAND | DESCRIPTION
---|---
`/var/ossec/bin/agent_control -l` | List agents (`-lc` connected, `-ln` disconnected)
`/var/ossec/bin/agent_control -i <ID>` | Details for one agent
`/var/ossec/bin/agent_control -R -u <ID>` | Restart an agent
`/var/ossec/bin/agent_control -r -a` | Run syscheck and rootcheck on all agents
`/var/ossec/bin/agent_control -L` | List active responses
`/var/ossec/bin/wazuh-control status` | Daemon status (also `start`, `stop`, `restart`, `reload`)
`sudo systemctl restart wazuh-manager` | Restart the manager (preferred over `wazuh-control`)
`/var/ossec/bin/wazuh-logtest` | Paste a log line and see decoder and rule matching

The docs recommend `systemctl` for service control.

## Configuration
Main file: `/var/ossec/etc/ossec.conf`. Common blocks:

BLOCK | USE
---|---
`syscheck` | File integrity monitoring
`rootcheck` | Rootkit and policy checks
`sca` | Security configuration assessment
`vulnerability-detection` | Manager only
`active-response`, `command` | Automatic responses
`localfile` | Extra log files to read
`remote`, `client` | Manager listener and agent connection
`labels` | Tag agents
`integration` | Send alerts to other services

Validate changes by restarting and reading `/var/ossec/logs/ossec.log`. Alerts are in `/var/ossec/logs/alerts/alerts.json` on the manager.

## Custom Rules
Put rules in `/var/ossec/etc/rules/local_rules.xml`. Custom rule IDs run from 100000 to 120000.

```xml
<group name="custom_rules,">
  <rule id="100010" level="3">
    <program_name>example</program_name>
    <description>Example program logged</description>
  </rule>
</group>
```

Test with `wazuh-logtest`, then restart the manager. The decoder file location was not confirmed.

## API
```bash
TOKEN=$(curl -sk -X POST "https://localhost:55000/security/user/authenticate?raw=true" \
  --user "${WAZUH_API_USER}:${WAZUH_API_PASS}")
curl -sk -H "Authorization: Bearer ${TOKEN}" "https://localhost:55000/"
```

Use a proper certificate rather than `-k` for anything beyond a first test.

## Passwords
```bash
curl -so wazuh-passwords-tool.sh https://packages.wazuh.com/4.14/wazuh-passwords-tool.sh
bash wazuh-passwords-tool.sh -u admin -p '<NEW_PASSWORD>'
```

`-a` changes all indexer passwords. Passwords need 8 to 64 characters with upper case, lower case, a digit and one of `.*+?-`.

## Not Verified
Upgrade steps, the vulnerability detection block, decoder paths, and the API default credentials (installs by script use generated passwords).

## See Also
- [Linux Hardening Recipe](../recipes/network-hardening.md)
- [CrowdSec](crowdsec.md)
- [Lynis and auditd](lynis-and-auditd.md)
- [Nessus and OpenVAS](nessus-openvas.md)
