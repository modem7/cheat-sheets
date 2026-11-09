# Cheat-Sheets

[![Lint](https://github.com/modem7/cheat-sheets/actions/workflows/lint.yml/badge.svg)](https://github.com/modem7/cheat-sheets/actions/workflows/lint.yml)
[![Secret and IP scan](https://github.com/modem7/cheat-sheets/actions/workflows/secret-scan.yml/badge.svg)](https://github.com/modem7/cheat-sheets/actions/workflows/secret-scan.yml)
[![Pages](https://github.com/modem7/cheat-sheets/actions/workflows/pages.yml/badge.svg)](https://github.com/modem7/cheat-sheets/actions/workflows/pages.yml)
[![Last commit](https://img.shields.io/github/last-commit/modem7/cheat-sheets)](https://github.com/modem7/cheat-sheets/commits/master)
[![Licence: MIT](https://img.shields.io/github/license/modem7/cheat-sheets)](LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](docs/CONTRIBUTING.md)

This Repository **Cheat-Sheets** is my personal knowledge-base. Here you'll find code-snippets, technical documentation, and command reference for various tools, and technologies.

**Browse it online: [modem7.github.io/cheat-sheets](https://modem7.github.io/cheat-sheets/)**

This was inspired by https://github.com/ChristianLempa/cheat-sheets

## How to Use
- Each sheet is a single Markdown file in a topic folder. Commands are in `COMMAND | DESCRIPTION` tables so they are quick to scan.
- Placeholders are written in capitals, e.g. `<HOST>` or `CONTAINER`. Replace them before running.
- Sheets link to each other with standard relative Markdown links (e.g. `[Docker](../docker/docker.md)`), so they work on GitHub, in any editor and on the Hugo site.
- The index below is generated: run `python3 scripts/gen-index.py` after adding or retitling a sheet.
- Search all sheets: `grep -ril "keyword" .` or `rg "keyword"`.
- Adding or changing a sheet? See [CONTRIBUTING](docs/CONTRIBUTING.md).

<!-- index:start -->
## Index

### Recipes

[Recipes](recipes/recipes.md) · [Automate Container Updates Safely](recipes/automate-container-updates.md) · [DNS Troubleshooting](recipes/dns-troubleshooting.md) · [Docker Service Deploy](recipes/docker-service-deploy.md) · [Expose a Service with Cloudflare Tunnel](recipes/expose-service-cloudflare-tunnel.md) · [K3s Cluster from Scratch](recipes/k3s-cluster-from-scratch.md) · [Migrate a Docker Service Between Hosts](recipes/migrate-docker-service-between-hosts.md) · [Monitor a Homelab with Prometheus and Grafana](recipes/monitor-homelab-prometheus-grafana.md) · [Network Hardening Recipe](recipes/network-hardening.md) · [Network Troubleshooting](recipes/network-troubleshooting.md) · [New Server Checklist](recipes/new-server-checklist.md) · [Off-Site Docker Host Backup with restic](recipes/offsite-docker-host-backup.md) · [Proxmox VM Template and Clone](recipes/proxmox-vm-template-and-clone.md) · [Restore-Test a Backup](recipes/restore-test-a-backup.md) · [SSH Bastion Host in an LXC](recipes/ssh-bastion-lxc.md) · [Single Sign-On with authentik](recipes/sso-with-authentik.md) · [TLS Troubleshooting](recipes/tls-troubleshooting.md) · [WireGuard Remote Access](recipes/wireguard-remote-access.md)

### Linux

[Linux](linux/linux.md) · [AWK](linux/awk.md) · [Btrfs](linux/btrfs.md) · [Ceph](linux/ceph.md) · [chrony](linux/chrony.md) · [Disk Usage](linux/disk-usage.md) · [ethtool](linux/ethtool.md) · [firewalld](linux/firewalld.md) · [Grep](linux/grep.md) · [Hardware Inspection](linux/hardware-inspection.md) · [ip and ss](linux/ip-and-ss.md) · [IPTables](linux/iptables.md) · [journalctl](linux/journalctl.md) · [libvirt and KVM](linux/libvirt-kvm.md) · [Linux Basics](linux/linuxbasics.md) · [logrotate](linux/logrotate.md) · [LVM](linux/lvm.md) · [mergerfs](linux/mergerfs.md) · [Mount](linux/mount.md) · [Netplan](linux/netplan.md) · [NFS](linux/nfs.md) · [nftables](linux/nftables.md) · [Linux Performance Troubleshooting](linux/performance-troubleshooting.md) · [RAID with mdadm](linux/raid-mdadm.md) · [SED Cheat-Sheet](linux/sed.md) · [SELinux and AppArmor](linux/selinux-apparmor.md) · [smartctl](linux/smartctl.md) · [SnapRAID](linux/snapraid.md) · [Storage and Filesystems](linux/storage-and-filesystems.md) · [systemd](linux/systemd.md) · [tuned](linux/tuned.md) · [UFW (uncomplicated firewall)](linux/ufw.md) · [User Management](linux/user.md) · [XFS](linux/xfs.md) · [ZFS](linux/zfs.md)

### Windows

[Active Directory](windows/active-directory.md) · [Chocolatey](windows/chocolatey.md) · [Environment Variables in Windows](windows/environment-variables.md) · [Group Policy](windows/group-policy.md) · [PowerShell Cheat-Sheet](windows/powershell.md) · [PowerShell Remote Access](windows/powershell-remote.md) · [Windows Registry](windows/registry.md) · [Robocopy](windows/robocopy.md) · [Windows Scheduled Tasks](windows/scheduled-tasks.md) · [Sysinternals](windows/sysinternals.md) · [Windows DNS Server](windows/windows-dns-server.md) · [Windows Networking](windows/windows-networking.md) · [Windows Terminal](windows/windows-terminal.md) · [Windows Troubleshooting](windows/windows-troubleshooting.md) · [Windows Updates](windows/windows-updates.md) · [winget](windows/winget.md)

### macOS

[Google Chrome](macos/chrome-on-macos.md) · [Docker on macOS Silicon](macos/docker-on-macos-silicon.md) · [Homebrew](macos/homebrew.md) · [MacOS keyboard shortcuts](macos/macos-shortcuts.md) · [VSCode shortcuts (macOS)](macos/vscode-macos-shortcuts.md)

### Docker

[Docker](docker/docker.md) · [Buildah](docker/buildah.md) · [Docker Buildx](docker/buildx.md) · [Docker Cleanup](docker/docker-cleanup.md) · [Docker-Compose](docker/docker-compose.md) · [Dockerfile](docker/docker-file.md) · [Docker Networking](docker/docker-networking.md) · [Docker Registry](docker/docker-registry.md) · [Docker Troubleshooting](docker/docker-troubleshooting.md) · [OCI Images](docker/oci-images.md) · [Podman](docker/podman.md)

### Container Distros

[Container Distros](distros/distros.md) · [Alpine Linux](distros/alpine.md) · [Amazon Linux](distros/amazon-linux.md) · [Debian](distros/debian.md) · [Fedora](distros/fedora.md) · [Ubuntu](distros/ubuntu.md)

### Kubernetes

[Kubernetes](kubernetes/kubernetes.md) · [K3S](kubernetes/k3s.md) · [Install K3S in High Availability Mode with an embedded Database](kubernetes/k3s-install-ha-embeddeddb.md) · [Install K3S in High Availability Mode](kubernetes/k3s-install-ha-externaldb.md) · [K3S Single-Node Installation](kubernetes/k3s-install-single.md) · [K9s](kubernetes/k9s.md) · [Kind](kubernetes/kind.md) · [Kubectl](kubernetes/kubectl.md) · [Kubernetes Automation](kubernetes/kubernetes-automation.md) · [Kubernetes DNS](kubernetes/kubernetes-dns.md) · [Kubernetes Workloads](kubernetes/kubernetes-workloads.md)

### Proxmox

[Proxmox VE Overview and Install](proxmox/proxmox-overview.md) · [Proxmox Users, Permissions, API Tokens and pvesh](proxmox/proxmox-access-api.md) · [Proxmox Backup and Restore](proxmox/proxmox-backup.md) · [Proxmox Cloud-Init Templates](proxmox/proxmox-cloud-init.md) · [Proxmox Clustering and HA](proxmox/proxmox-cluster-ha.md) · [Proxmox Firewall](proxmox/proxmox-firewall.md) · [Proxmox Networking](proxmox/proxmox-networking.md) · [Proxmox GPU and PCIe Passthrough](proxmox/proxmox-passthrough.md) · [Proxmox qm and pct](proxmox/proxmox-qm-pct.md) · [Proxmox Storage](proxmox/proxmox-storage.md) · [Proxmox Troubleshooting and One-Liners](proxmox/proxmox-troubleshooting.md)

### Homelab

[Homelab](homelab/homelab.md) · [AdGuard Home](homelab/adguard-home.md) · [apcupsd](homelab/apcupsd.md) · [BIND 9](homelab/bind9.md) · [dnsmasq DHCP and DNS](homelab/dnsmasq-dhcp.md) · [netboot.xyz](homelab/netboot-xyz.md) · [Notification Services](homelab/notification-services.md) · [NUT (Network UPS Tools)](homelab/nut-ups.md) · [Pi-hole](homelab/pihole.md) · [PXE and iPXE Network Boot](homelab/pxe-boot.md) · [Reverse Proxy Patterns](homelab/reverse-proxy-patterns.md) · [Unbound](homelab/unbound.md) · [VLANs](homelab/vlans.md) · [Wake-on-LAN](homelab/wake-on-lan.md)

### Infrastructure

[VMware ESXi](infra/esxi.md) · [Hypervisors Compared](infra/hypervisor-comparison.md) · [NAS Operating Systems Compared](infra/nas-os-comparison.md) · [OpenMediaVault](infra/openmediavault.md) · [TrueNAS Community Edition](infra/truenas-community-edition.md) · [UniFi NAS](infra/unifi-nas.md) · [Unraid](infra/unraid.md) · [XCP-ng](infra/xcp-ng.md)

### Cloud

[What is Cloud-Computing?](cloud/what-is-cloud-computing.md)

Provider: [Amazon Web Services](cloud/provider/amazon-web-services.md) · [Backblaze B2](cloud/provider/backblaze-b2.md) · [Civo](cloud/provider/civo.md) · [Cloud-Provider Comparison](cloud/provider/cloud-provider-comparison.md) · [Cloudflare](cloud/provider/cloudflare.md) · [DigitalOcean](cloud/provider/digitalocean.md) · [Google Cloud](cloud/provider/google-cloud.md) · [Hetzner Cloud](cloud/provider/hetzner-cloud.md) · [Oracle Cloud](cloud/provider/oracle-cloud.md)

### Networking

[Generate a DKIM Keypair](networking/create-dkim-keypair.md) · [dig](networking/dig.md) · [DNS Encryption](networking/dns-encryption.md) · [DNS over HTTPS (DoH)](networking/dns-over-https.md) · [DNS over TLS (DoT)](networking/dns-over-tls.md) · [Mail Server DNS Records Cheat-Sheet](networking/dns-record-mailserver.md) · [DNS Record Types](networking/dns-record-types.md) · [DNSSEC](networking/dnssec.md) · [Mesh VPN Comparison](networking/mesh-vpn-comparison.md) · [Ports and Protocols](networking/ports-and-protocols.md) · [SMTP](networking/smtp.md) · [socat and netcat](networking/socat-and-netcat.md) · [TCP vs UDP](networking/tcp-vs-udp.md) · [TLS (Transport Layer Security)](networking/tls.md) · [TLS Handshake](networking/tls-handshake.md) · [Twisted Pair Cables Cheat-Sheet](networking/twisted-pair-cables.md) · [VPN (Virtual Private Network)](networking/vpn.md)

### UniFi

[UniFi](unifi/unifi.md) · [UniFi API and Automation](unifi/unifi-api-automation.md) · [UniFi Backups and Migration](unifi/unifi-backups.md) · [UniFi Device CLI and Adoption](unifi/unifi-device-cli.md) · [UniFi Firewall and VPN](unifi/unifi-firewall-vpn.md) · [UniFi Hosting](unifi/unifi-hosting.md) · [UniFi Networks and VLANs](unifi/unifi-networks-vlans.md) · [UniFi Protect](unifi/unifi-protect.md) · [UniFi Routing and WAN](unifi/unifi-routing-wan.md) · [UniFi WiFi](unifi/unifi-wifi.md)

### Security

[Security](security/security.md) · [Application Security Tools](security/appsec-tools.md) · [ASPM](security/aspm.md) · [Authelia](security/authelia.md) · [authentik](security/authentik.md) · [ClamAV](security/clamav.md) · [Container Scanning](security/container-scanning.md) · [CrowdSec](security/crowdsec.md) · [fail2ban](security/fail2ban.md) · [GPG](security/gpg.md) · [Keycloak](security/keycloak.md) · [Lynis and auditd](security/lynis-and-auditd.md) · [Nessus and OpenVAS](security/nessus-openvas.md) · [Secret Scanning](security/secret-scanning.md) · [Snyk](security/snyk.md) · [SOPS and age](security/sops-age.md) · [SSH Hardening](security/ssh-hardening.md) · [Vault and OpenBao](security/vault.md) · [Wazuh](security/wazuh.md)

### Backup

[Backup Strategy](backup/backup.md) · [BorgBackup](backup/borg.md) · [BorgBase](backup/borgbase.md) · [borgmatic](backup/borgmatic.md) · [Database Dumps](backup/database-dumps.md) · [Docker Volume Backup](backup/docker-volume-backup.md) · [rclone](backup/rclone.md) · [restic](backup/restic.md) · [rsync](backup/rsync.md) · [ZFS Snapshots and Replication](backup/zfs-snapshots-backup.md)

### CI/CD

[CI/CD Overview](cicd/cicd.md) · [CI Docker Builds](cicd/ci-docker-builds.md) · [CI Recipes](cicd/ci-recipes.md) · [CircleCI](cicd/circleci.md) · [Concourse CI](cicd/concourse.md) · [Drone CI](cicd/drone-ci.md) · [Flux CD](cicd/flux.md) · [GitHub Actions](cicd/github-actions.md) · [GitLab CI/CD](cicd/gitlab-ci.md) · [Jenkins](cicd/jenkins.md) · [Renovate](cicd/renovate.md) · [Tekton](cicd/tekton.md) · [Woodpecker CI](cicd/woodpecker-ci.md)

### Scripting

[Scripting](scripting/scripting.md) · [Bash](scripting/bash.md) · [Bash Recipes](scripting/bash-recipes.md) · [Fish](scripting/fish.md) · [Make](scripting/make.md) · [Nushell](scripting/nushell.md) · [pip and pipx](scripting/pip-and-pipx.md) · [pre-commit](scripting/pre-commit.md) · [Python and uv](scripting/python-uv.md) · [Shell Comparison](scripting/shell-comparison.md) · [ShellCheck and shfmt](scripting/shellcheck-shfmt.md) · [Zsh](scripting/zsh.md)

### AI

[AI](ai/ai.md) · [Aider](ai/aider.md) · [Claude API and SDKs](ai/claude-api.md) · [Claude Code](ai/claude-code.md) · [Codex, Gemini and Copilot CLIs](ai/coding-agent-clis.md) · [Hugging Face CLI and Model Formats](ai/hugging-face.md) · [llama.cpp](ai/llama-cpp.md) · [LLM Glossary](ai/llm-glossary.md) · [LM Studio](ai/lm-studio.md) · [Model Context Protocol (MCP)](ai/mcp.md) · [Ollama](ai/ollama.md) · [Open WebUI and Self-Hosted AI Stacks](ai/open-webui.md) · [OpenAI API](ai/openai-api.md) · [Prompting and Context Engineering](ai/prompting-patterns.md)

### Databases

[MariaDB Cheat-Sheet](databases/mariadb.md) · [MongoDB](databases/mongodb.md) · [MySQL](databases/mysql.md) · [MySQL and MariaDB Replication](databases/mysql-replication.md) · [PostgreSQL Cheat-Sheet](databases/postgres.md) · [PostgreSQL Backup and Replication](databases/postgres-backup-replication.md) · [Redis](databases/redis.md) · [SQL](databases/sql.md) · [SQLite Cheat-Sheet](databases/sqlite.md)

### Apps

[Alertmanager](apps/alertmanager.md) · [Apprise](apps/apprise.md) · [APT Cacher NG](apps/apt-cacher-ng.md) · [Argo CD](apps/argocd.md) · [Arr Stack](apps/arr-stack.md) · [Beszel](apps/beszel.md) · [Cert-Manager](apps/cert-manager.md) · [cloudflared](apps/cloudflared.md) · [Dockhand](apps/dockhand.md) · [Dozzle](apps/dozzle.md) · [Elastic Stack](apps/elastic-stack.md) · [ESPHome](apps/esphome.md) · [Gotify](apps/gotify.md) · [Grafana](apps/grafana.md) · [Graylog](apps/graylog.md) · [HAProxy](apps/haproxy.md) · [Headscale](apps/headscale.md) · [Healthchecks](apps/healthchecks.md) · [Home Assistant](apps/home-assistant.md) · [Immich](apps/immich.md) · [Jellyfin](apps/jellyfin.md) · [KASM Workspaces](apps/kasm.md) · [Komodo](apps/komodo.md) · [Loki and Grafana Alloy](apps/loki-alloy.md) · [Longhorn](apps/longhorn.md) · [MinIO](apps/minio.md) · [NetAlertX](apps/netalertx.md) · [NetBird](apps/netbird.md) · [NetBox](apps/netbox.md) · [Nextcloud](apps/nextcloud.md) · [Nginx](apps/nginx.md) · [ntfy](apps/ntfy.md) · [Passbolt](apps/passbolt.md) · [Pocket ID](apps/pocket-id.md) · [Portainer](apps/portainer.md) · [Prometheus](apps/prometheus.md) · [Pushover](apps/pushover.md) · [Rancher](apps/rancher.md) · [Samba](apps/samba.md) · [Squid](apps/squid.md) · [Syncthing](apps/syncthing.md) · [Tailscale](apps/tailscale.md) · [Teleport](apps/teleport.md) · [Traefik](apps/traefik.md) · [Uptime Kuma](apps/uptime-kuma.md) · [Vaultwarden](apps/vaultwarden.md) · [WireGuard](apps/wireguard.md) · [ZeroTier](apps/zerotier.md)

### Tools

[1Password CLI Cheat-Sheet](tools/1password-cli.md) · [Ansible Cheat-Sheet](tools/ansible.md) · [Ansible-Playbook Cheat-Sheet](tools/ansible-playbook.md) · [Aptly](tools/aptly.md) · [AWS CLI](tools/aws-cli.md) · [Azure CLI (az)](tools/azure-cli.md) · [Bitwarden Cheat-Sheet](tools/bitwarden.md) · [Certutil](tools/certutil.md) · [Chef](tools/chef.md) · [Cloudsmith CLI](tools/cloudsmith-cli.md) · [curl](tools/curl.md) · [Datree](tools/datree.md) · [direnv](tools/direnv.md) · [Docker Desktop](tools/docker-desktop.md) · [ffmpeg](tools/ffmpeg.md) · [gcloud (Google Cloud CLI)](tools/gcloud.md) · [Git](tools/git.md) · [Git Recipes](tools/git-recipes.md) · [Git Troubleshooting](tools/git-troubleshooting.md) · [Gitea (and Forgejo)](tools/gitea.md) · [GitHub and the gh CLI](tools/github-cli.md) · [GitLab and the glab CLI](tools/gitlab.md) · [Go and Rust Toolchains](tools/go-rust-toolchains.md) · [gopass Cheat-Sheet](tools/gopass.md) · [Helm Cheat-Sheet](tools/helm.md) · [iperf3](tools/iperf3.md) · [iTerm2](tools/iterm2.md) · [Joplin](tools/joplin.md) · [jq](tools/jq.md) · [LastPass CLI Cheat-Sheet](tools/lastpass-cli.md) · [Logseq](tools/logseq.md) · [Mermaid](tools/mermaid.md) · [Modern CLI Tools](tools/modern-cli-tools.md) · [msmtp](tools/msmtp.md) · [nano](tools/nano.md) · [NMap](tools/nmap.md) · [Node.js and npm](tools/node-npm.md) · [Obsidian](tools/obsidian.md) · [OpenSSH Cheat-Sheet](tools/openssh.md) · [OpenSSL](tools/openssl.md) · [Packer](tools/packer.md) · [pass Cheat-Sheet](tools/pass.md) · [Puppet Cheat-Sheet](tools/puppet.md) · [REST APIs](tools/rest-api.md) · [Salt Cheat-Sheet](tools/salt.md) · [Starship Prompt](tools/starship.md) · [tcpdump](tools/tcpdump.md) · [Terraform](tools/terraform.md) · [Terraform State and Modules](tools/terraform-state-and-modules.md) · [tmux](tools/tmux.md) · [Vagrant Cheat-Sheet](tools/vagrant.md) · [Vim](tools/vim.md) · [VirtualBox](tools/virtualbox.md) · [VSCode (Visual Studio Code)](tools/vscode.md) · [Wireshark and tshark](tools/wireshark-tshark.md) · [WSL Cheat-Sheet](tools/wsl.md) · [yq](tools/yq.md) · [yt-dlp](tools/yt-dlp.md)

### Misc

[256 Color Codes Cheat-Sheet](misc/color-codes.md) · [Cron](misc/cron.md) · [HTTP Status Codes](misc/http-status-codes.md) · [Markdown](misc/markdown.md) · [Regex](misc/regex.md) · [SSL Certificates Cheat-Sheet](misc/ssl-certs.md) · [SSL Security Cheat-Sheet](misc/ssl-security.md)

### Docs

[Contributing](docs/CONTRIBUTING.md) · [Sheet template](docs/_template.md)
<!-- index:end -->

## Contributing
Keep one topic per file, use the `COMMAND | DESCRIPTION` table layout, and avoid empty stubs. If a file only has a title, either fill it in or don't commit it.
