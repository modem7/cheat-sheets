# Cheat-Sheets

This Repository **Cheat-Sheets** is my personal knowledge-base. Here you'll find code-snippets, technical documentation, and command reference for various tools, and technologies.

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

[Recipes](recipes/recipes.md) · [DNS Troubleshooting](recipes/dns-troubleshooting.md) · [Docker Service Deploy](recipes/docker-service-deploy.md) · [K3s Cluster from Scratch](recipes/k3s-cluster-from-scratch.md) · [Network Troubleshooting](recipes/network-troubleshooting.md) · [New Server Checklist](recipes/new-server-checklist.md) · [Proxmox VM Template and Clone](recipes/proxmox-vm-template-and-clone.md) · [TLS Troubleshooting](recipes/tls-troubleshooting.md) · [WireGuard Remote Access](recipes/wireguard-remote-access.md)

### Linux

[Linux](linux/linux.md) · [AWK](linux/awk.md) · [Grep](linux/grep.md) · [IPTables](linux/iptables.md) · [Linux Basics](linux/linuxbasics.md) · [LVM](linux/lvm.md) · [Mount](linux/mount.md) · [NFS](linux/nfs.md) · [nftables](linux/nftables.md) · [Linux Performance Troubleshooting](linux/performance-troubleshooting.md) · [RAID with mdadm](linux/raid-mdadm.md) · [SED Cheat-Sheet](linux/sed.md) · [SELinux and AppArmor](linux/selinux-apparmor.md) · [Storage and Filesystems](linux/storage-and-filesystems.md) · [systemd](linux/systemd.md) · [UFW (uncomplicated firewall)](linux/ufw.md) · [User Management](linux/user.md)

### Windows

[Active Directory](windows/active-directory.md) · [Chocolatey](windows/chocolatey.md) · [Environment Variables in Windows](windows/environment-variables.md) · [Group Policy](windows/group-policy.md) · [PowerShell Cheat-Sheet](windows/powershell.md) · [PowerShell Remote Access](windows/powershell-remote.md) · [Robocopy](windows/robocopy.md) · [Windows DNS Server](windows/windows-dns-server.md) · [Windows Networking](windows/windows-networking.md) · [Windows Terminal](windows/windows-terminal.md) · [Windows Troubleshooting](windows/windows-troubleshooting.md) · [Windows Updates](windows/windows-updates.md) · [winget](windows/winget.md)

### macOS

[Google Chrome](macos/chrome-on-macos.md) · [Docker on macOS Silicon](macos/docker-on-macos-silicon.md) · [Homebrew](macos/homebrew.md) · [MacOS keyboard shortcuts](macos/macos-shortcuts.md) · [VSCode shortcuts (macOS)](macos/vscode-macos-shortcuts.md)

### Docker

[Docker](docker/docker.md) · [Docker Cleanup](docker/docker-cleanup.md) · [Docker-Compose](docker/docker-compose.md) · [Dockerfile](docker/docker-file.md) · [Docker Networking](docker/docker-networking.md) · [Docker Registry](docker/docker-registry.md) · [Docker Troubleshooting](docker/docker-troubleshooting.md)

### Kubernetes

[Kubernetes](kubernetes/kubernetes.md) · [K3S](kubernetes/k3s.md) · [Install K3S in High Availability Mode with an embedded Database](kubernetes/k3s-install-ha-embeddeddb.md) · [Install K3S in High Availability Mode](kubernetes/k3s-install-ha-externaldb.md) · [K3S Single-Node Installation](kubernetes/k3s-install-single.md) · [K9s](kubernetes/k9s.md) · [Kind](kubernetes/kind.md) · [Kubectl](kubernetes/kubectl.md) · [Kubernetes Automation](kubernetes/kubernetes-automation.md) · [Kubernetes DNS](kubernetes/kubernetes-dns.md)

### Proxmox

[Proxmox VE Overview and Install](proxmox/proxmox-overview.md) · [Proxmox Users, Permissions, API Tokens and pvesh](proxmox/proxmox-access-api.md) · [Proxmox Backup and Restore](proxmox/proxmox-backup.md) · [Proxmox Cloud-Init Templates](proxmox/proxmox-cloud-init.md) · [Proxmox Clustering and HA](proxmox/proxmox-cluster-ha.md) · [Proxmox Firewall](proxmox/proxmox-firewall.md) · [Proxmox Networking](proxmox/proxmox-networking.md) · [Proxmox GPU and PCIe Passthrough](proxmox/proxmox-passthrough.md) · [Proxmox qm and pct](proxmox/proxmox-qm-pct.md) · [Proxmox Storage](proxmox/proxmox-storage.md) · [Proxmox Troubleshooting and One-Liners](proxmox/proxmox-troubleshooting.md)

### Homelab

[Homelab](homelab/homelab.md) · [AdGuard Home](homelab/adguard-home.md) · [dnsmasq DHCP and DNS](homelab/dnsmasq-dhcp.md) · [NUT (Network UPS Tools)](homelab/nut-ups.md) · [Pi-hole](homelab/pihole.md) · [Reverse Proxy Patterns](homelab/reverse-proxy-patterns.md) · [Unbound](homelab/unbound.md) · [VLANs](homelab/vlans.md) · [Wake-on-LAN](homelab/wake-on-lan.md)

### Infrastructure

[TrueNAS Scale](infra/truenas-scale.md)

### Cloud

[What is Cloud-Computing?](cloud/what-is-cloud-computing.md)

Provider: [Civo](cloud/provider/civo.md) · [Cloud-Provider Comparison](cloud/provider/cloud-provider-comparison.md)

### Networking

[Generate a DKIM Keypair](networking/create-dkim-keypair.md) · [DNS Encryption](networking/dns-encryption.md) · [DNS over HTTPS (DoH)](networking/dns-over-https.md) · [DNS over TLS (DoT)](networking/dns-over-tls.md) · [Mail Server DNS Records Cheat-Sheet](networking/dns-record-mailserver.md) · [DNS Record Types](networking/dns-record-types.md) · [Ports and Protocols](networking/ports-and-protocols.md) · [SMTP](networking/smtp.md) · [TCP vs UDP](networking/tcp-vs-udp.md) · [TLS (Transport Layer Security)](networking/tls.md) · [TLS Handshake](networking/tls-handshake.md) · [Twisted Pair Cables Cheat-Sheet](networking/twisted-pair-cables.md) · [VPN (Virtual Private Network)](networking/vpn.md)

### Security

[Security](security/security.md) · [authentik](security/authentik.md) · [Container Scanning](security/container-scanning.md) · [CrowdSec](security/crowdsec.md) · [fail2ban](security/fail2ban.md) · [GPG](security/gpg.md) · [Keycloak](security/keycloak.md) · [Secret Scanning](security/secret-scanning.md) · [SOPS and age](security/sops-age.md) · [Vault and OpenBao](security/vault.md)

### Backup

[Backup Strategy](backup/backup.md) · [BorgBackup](backup/borg.md) · [borgmatic](backup/borgmatic.md) · [Database Dumps](backup/database-dumps.md) · [Docker Volume Backup](backup/docker-volume-backup.md) · [rclone](backup/rclone.md) · [restic](backup/restic.md) · [rsync](backup/rsync.md) · [ZFS Snapshots and Replication](backup/zfs-snapshots-backup.md)

### CI/CD

[CI/CD Overview](cicd/cicd.md) · [CI Docker Builds](cicd/ci-docker-builds.md) · [CI Recipes](cicd/ci-recipes.md) · [GitHub Actions](cicd/github-actions.md) · [GitLab CI/CD](cicd/gitlab-ci.md) · [Renovate](cicd/renovate.md) · [Woodpecker CI](cicd/woodpecker-ci.md)

### Scripting

[Scripting](scripting/scripting.md) · [Bash](scripting/bash.md) · [Bash Recipes](scripting/bash-recipes.md) · [Make](scripting/make.md) · [pre-commit](scripting/pre-commit.md) · [Python and uv](scripting/python-uv.md) · [ShellCheck and shfmt](scripting/shellcheck-shfmt.md)

### Databases

[MariaDB Cheat-Sheet](databases/mariadb.md) · [MySQL](databases/mysql.md) · [MySQL and MariaDB Replication](databases/mysql-replication.md) · [PostgreSQL Cheat-Sheet](databases/postgres.md) · [PostgreSQL Backup and Replication](databases/postgres-backup-replication.md) · [Redis](databases/redis.md) · [SQLite Cheat-Sheet](databases/sqlite.md)

### Apps

[Argo CD](apps/argocd.md) · [Cert-Manager](apps/cert-manager.md) · [Dockhand](apps/dockhand.md) · [Grafana](apps/grafana.md) · [KASM Workspaces](apps/kasm.md) · [Longhorn](apps/longhorn.md) · [Nginx](apps/nginx.md) · [Portainer](apps/portainer.md) · [Prometheus](apps/prometheus.md) · [Rancher](apps/rancher.md) · [Tailscale](apps/tailscale.md) · [Teleport](apps/teleport.md) · [Traefik](apps/traefik.md) · [WireGuard](apps/wireguard.md)

### Tools

[Ansible Cheat-Sheet](tools/ansible.md) · [Ansible-Playbook Cheat-Sheet](tools/ansible-playbook.md) · [Aptly](tools/aptly.md) · [AWS CLI](tools/aws-cli.md) · [Azure CLI (az)](tools/azure-cli.md) · [Bitwarden Cheat-Sheet](tools/bitwarden.md) · [Certutil](tools/certutil.md) · [curl](tools/curl.md) · [Datree](tools/datree.md) · [Docker Desktop](tools/docker-desktop.md) · [ffmpeg](tools/ffmpeg.md) · [gcloud (Google Cloud CLI)](tools/gcloud.md) · [Git](tools/git.md) · [Git Recipes](tools/git-recipes.md) · [Gitea (and Forgejo)](tools/gitea.md) · [GitHub and the gh CLI](tools/github-cli.md) · [GitLab and the glab CLI](tools/gitlab.md) · [Go and Rust Toolchains](tools/go-rust-toolchains.md) · [Helm Cheat-Sheet](tools/helm.md) · [iTerm2](tools/iterm2.md) · [Joplin](tools/joplin.md) · [jq](tools/jq.md) · [Logseq](tools/logseq.md) · [Modern CLI Tools](tools/modern-cli-tools.md) · [NMap](tools/nmap.md) · [Node.js and npm](tools/node-npm.md) · [Obsidian](tools/obsidian.md) · [OpenSSH Cheat-Sheet](tools/openssh.md) · [OpenSSL](tools/openssl.md) · [Packer](tools/packer.md) · [Starship Prompt](tools/starship.md) · [Terraform](tools/terraform.md) · [tmux](tools/tmux.md) · [Vagrant Cheat-Sheet](tools/vagrant.md) · [VSCode (Visual Studio Code)](tools/vscode.md) · [WSL Cheat-Sheet](tools/wsl.md) · [yt-dlp](tools/yt-dlp.md)

### Misc

[256 Color Codes Cheat-Sheet](misc/color-codes.md) · [Cron](misc/cron.md) · [HTTP Status Codes](misc/http-status-codes.md) · [Markdown](misc/markdown.md) · [Regex](misc/regex.md) · [SSL Certificates Cheat-Sheet](misc/ssl-certs.md) · [SSL Security Cheat-Sheet](misc/ssl-security.md)

### Docs

[Contributing](docs/CONTRIBUTING.md) · [Sheet template](docs/_template.md)
<!-- index:end -->

## Contributing
Keep one topic per file, use the `COMMAND | DESCRIPTION` table layout, and avoid empty stubs. If a file only has a title, either fill it in or don't commit it.
