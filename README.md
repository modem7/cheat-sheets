# Cheat-Sheets

This Repository **Cheat-Sheets** is my personal knowledge-base. Here you'll find code-snippets, technical documentation, and command reference for various tools, and technologies.

This was inspired by https://github.com/ChristianLempa/cheat-sheets

## How to Use
- Each sheet is a single Markdown file in a topic folder. Commands are in `COMMAND | DESCRIPTION` tables so they are quick to scan.
- Placeholders are written in capitals, e.g. `<HOST>` or `CONTAINER`. Replace them before running.
- `[[name]]` links are Obsidian-style wikilinks to another sheet. On GitHub, use the index below.
- Search all sheets: `grep -ril "keyword" .` or `rg "keyword"`.
- Adding or changing a sheet? See [CONTRIBUTING](docs/CONTRIBUTING.md).

## Index

### Linux
[Linux](linux/linux.md) · [Linux Basics](linux/linuxbasics.md) · [User Management](linux/user.md) · [Grep](linux/grep.md) · [Sed](linux/sed.md) · [Awk](linux/awk.md) · [Mount](linux/mount.md) · [NFS](linux/nfs.md) · [UFW](linux/ufw.md) · [iptables](linux/iptables.md)

### Docker
[Docker](docker/docker.md) · [Dockerfile](docker/docker-file.md) · [Docker Compose](docker/docker-compose.md) · [Docker Networking](docker/docker-networking.md)

### Kubernetes
[Kubernetes](kubernetes/kubernetes.md) · [kubectl](kubernetes/kubectl.md) · [Kubernetes DNS](kubernetes/kubernetes-dns.md) · [Automation and GitOps](kubernetes/kubernetes-automation.md) · [k9s](kubernetes/k9s.md) · [kind](kubernetes/kind.md)

K3s: [K3s](kubernetes/k3s.md) · [Single node](kubernetes/k3s-install-single.md) · [HA embedded DB](kubernetes/k3s-install-ha-embeddeddb.md) · [HA external DB](kubernetes/k3s-install-ha-externaldb.md)

### Networking
[TLS](networking/tls.md) · [TLS Handshake](networking/tls-handshake.md) · [VPN](networking/vpn.md) · [DNS Encryption](networking/dns-encryption.md) · [DNS over TLS](networking/dns-over-tls.md) · [DNS over HTTPS](networking/dns-over-https.md) · [DNS Record Types](networking/dns-record-types.md) · [Mail Server DNS Records](networking/dns-record-mailserver.md) · [Create DKIM Keypair](networking/create-dkim-keypair.md) · [SMTP](networking/smtp.md) · [TCP vs UDP](networking/tcp-vs-udp.md) · [Twisted Pair Cables](networking/twisted-pair-cables.md)

### Tools
[Git](tools/git.md) · [GitHub CLI](tools/github-cli.md) · [GitLab](tools/gitlab.md) · [Gitea](tools/gitea.md) · [curl](tools/curl.md) · [jq](tools/jq.md) · [tmux](tools/tmux.md) · [OpenSSH](tools/openssh.md) · [OpenSSL](tools/openssl.md) · [Certutil](tools/certutil.md) · [Nmap](tools/nmap.md) · [Ansible](tools/ansible.md) · [Ansible Playbooks](tools/ansible-playbook.md) · [Terraform](tools/terraform.md) · [Helm](tools/helm.md) · [Datree](tools/datree.md) · [Vagrant](tools/vagrant.md) · [Aptly](tools/aptly.md) · [Azure CLI](tools/azure-cli.md) · [AWS CLI](tools/aws-cli.md) · [gcloud](tools/gcloud.md) · [Modern CLI Tools](tools/modern-cli-tools.md) · [Docker Desktop](tools/docker-desktop.md) · [Obsidian](tools/obsidian.md) · [Logseq](tools/logseq.md) · [Joplin](tools/joplin.md) · [Bitwarden](tools/bitwarden.md) · [Starship](tools/starship.md) · [VSCode](tools/vscode.md) · [iTerm2](tools/iterm2.md) · [WSL](tools/wsl.md)

### Apps
[Argo CD](apps/argocd.md) · [cert-manager](apps/cert-manager.md) · [Dockhand](apps/dockhand.md) · [Grafana](apps/grafana.md) · [Prometheus](apps/prometheus.md) · [Kasm](apps/kasm.md) · [Longhorn](apps/longhorn.md) · [Nginx](apps/nginx.md) · [Portainer](apps/portainer.md) · [Rancher](apps/rancher.md) · [Tailscale](apps/tailscale.md) · [Teleport](apps/teleport.md) · [Traefik](apps/traefik.md) · [WireGuard](apps/wireguard.md)

### Databases
[MariaDB](databases/mariadb.md) · [MySQL](databases/mysql.md) · [PostgreSQL](databases/postgres.md) · [SQLite](databases/sqlite.md)

### Infrastructure and Cloud
[Proxmox Overview and Install](proxmox/proxmox-overview.md) · [qm and pct](proxmox/proxmox-qm-pct.md) · [Storage](proxmox/proxmox-storage.md) · [Networking](proxmox/proxmox-networking.md) · [Backup and Restore](proxmox/proxmox-backup.md) · [Clustering and HA](proxmox/proxmox-cluster-ha.md) · [Cloud-Init](proxmox/proxmox-cloud-init.md) · [PCIe Passthrough](proxmox/proxmox-passthrough.md) · [Users, API and pvesh](proxmox/proxmox-access-api.md) · [Firewall](proxmox/proxmox-firewall.md) · [Troubleshooting](proxmox/proxmox-troubleshooting.md) · [TrueNAS SCALE](infra/truenas-scale.md) · [What is Cloud Computing?](cloud/what-is-cloud-computing.md) · [Cloud Provider Comparison](cloud/provider/cloud-provider-comparison.md) · [Civo](cloud/provider/civo.md)

### Windows
[PowerShell](windows/powershell.md) · [PowerShell Remoting](windows/powershell-remote.md) · [Chocolatey](windows/chocolatey.md) · [Windows Terminal](windows/windows-terminal.md) · [Environment Variables](windows/environment-variables.md) · [Windows DNS Server](windows/windows-dns-server.md) · [Windows Updates](windows/windows-updates.md)

### macOS
[macOS Shortcuts](macos/macos-shortcuts.md) · [VSCode Shortcuts](macos/vscode-macos-shortcuts.md) · [Chrome on macOS](macos/chrome-on-macos.md) · [Homebrew](macos/homebrew.md) · [Docker on Apple Silicon](macos/docker-on-macos-silicon.md)

### Misc
[HTTP Status Codes](misc/http-status-codes.md) · [Color Codes](misc/color-codes.md) · [Markdown](misc/markdown.md) · [SSL Certs](misc/ssl-certs.md) · [SSL Security](misc/ssl-security.md)

## Contributing
Keep one topic per file, use the `COMMAND | DESCRIPTION` table layout, and avoid empty stubs. If a file only has a title, either fill it in or don't commit it.
