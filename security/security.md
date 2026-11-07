# Security
Overview of the security and secrets cheat sheets, with a hardening checklist for a homelab or small self-hosted environment. The aim is layered defence: keep secrets out of Git, put identity in one place, block abuse automatically, and scan what you build.

## Sheets in This Section
SHEET | USE IT FOR
---|---
[SOPS and age](sops-age.md) | Encrypt secrets (`.env`, YAML) so they can live in Git
[Vault and OpenBao](vault.md) | Central secret store with policies, dynamic credentials (Vault / OpenBao)
[GPG](gpg.md) | Keys, signing, encryption, Git commit signing, backups
[authentik](authentik.md) | Self-hosted SSO, OIDC and forward-auth
[Keycloak](keycloak.md) | Self-hosted SSO, OIDC, SAML and federation
[CrowdSec](crowdsec.md) | Log-driven intrusion prevention with community blocklists and bouncers
[fail2ban](fail2ban.md) | Simple host-based log-driven IP bans
[Secret Scanning](secret-scanning.md) | gitleaks, TruffleHog, GitHub push protection
[Container Scanning](container-scanning.md) | Trivy, Grype and Syft for images and IaC
[Lynis and auditd](lynis-and-auditd.md) | Host hardening audit and Linux audit logging

## Related Sheets Elsewhere
SHEET | USE IT FOR
---|---
[OpenSSL](../tools/openssl.md) | Certificates, CSRs, key conversion
[OpenSSH Cheat-Sheet](../tools/openssh.md) | SSH keys, hardening `sshd_config`
[Bitwarden Cheat-Sheet](../tools/bitwarden.md) | Password manager and CLI
[1Password CLI Cheat-Sheet](../tools/1password-cli.md) | `op` read, run and inject secrets
[pass Cheat-Sheet](../tools/pass.md) | GPG and git password store
[gopass Cheat-Sheet](../tools/gopass.md) | Team password store with recipients and OTP
[LastPass CLI Cheat-Sheet](../tools/lastpass-cli.md) | `lpass` login, show, export
[TLS (Transport Layer Security)](../networking/tls.md) | TLS configuration
[SSL Security Cheat-Sheet](../misc/ssl-security.md) | TLS security testing and settings
[UFW (uncomplicated firewall)](../linux/ufw.md) | Simple host firewall
[IPTables](../linux/iptables.md) | Low-level firewall rules
[Tailscale](../apps/tailscale.md) | Private mesh VPN instead of exposing ports
[Teleport](../apps/teleport.md) | Short-lived certificates for SSH and Kubernetes access
[Cert-Manager](../apps/cert-manager.md) | Automated certificates in Kubernetes

## Choosing Tools
NEED | PICK
---|---
Secrets in a Git repo (GitOps, `.env`) | [SOPS and age](sops-age.md)
Many apps and services fetching secrets at runtime, dynamic credentials | [Vault and OpenBao](vault.md)
One login for all apps, small setup | [authentik](authentik.md)
Enterprise features, SAML, large ecosystem | [Keycloak](keycloak.md)
Ban brute-force on one host, minimal setup | [fail2ban](fail2ban.md)
Shared threat intel, multiple hosts or proxies | [CrowdSec](crowdsec.md)

## Hardening Checklist
### Access
- [ ] SSH: key-only auth, `PasswordAuthentication no`, `PermitRootLogin no`, non-default users ([OpenSSH Cheat-Sheet](../tools/openssh.md))
- [ ] Prefer a VPN or mesh ([Tailscale](../apps/tailscale.md), [WireGuard](../apps/wireguard.md)) over exposing admin ports to the internet
- [ ] Single sign-on with MFA for web UIs ([authentik](authentik.md) or [Keycloak](keycloak.md)); passkeys or TOTP for everything else
- [ ] Unique passwords in a manager ([Bitwarden Cheat-Sheet](../tools/bitwarden.md)); no shared admin accounts
- [ ] Least privilege: scoped API tokens, Vault policies, Kubernetes RBAC ([Kubernetes](../kubernetes/kubernetes.md))

### Network
- [ ] Default-deny firewall on every host ([UFW (uncomplicated firewall)](../linux/ufw.md), [IPTables](../linux/iptables.md)); remember Docker published ports bypass UFW
- [ ] Publish container ports on `127.0.0.1` and expose services through a reverse proxy ([Traefik](../apps/traefik.md), [Nginx](../apps/nginx.md))
- [ ] Valid TLS everywhere, HSTS on public sites ([TLS (Transport Layer Security)](../networking/tls.md), [SSL Security Cheat-Sheet](../misc/ssl-security.md), [Cert-Manager](../apps/cert-manager.md))
- [ ] Automatic bans for abuse ([CrowdSec](crowdsec.md) or [fail2ban](fail2ban.md)), with your own IPs allowlisted
- [ ] Separate networks/VLANs for IoT, guests and servers

### Secrets
- [ ] No plaintext secrets in Git: [SOPS and age](sops-age.md) or [Vault and OpenBao](vault.md); `.env` in `.gitignore`
- [ ] Secret scanning in pre-commit **and** CI ([Secret Scanning](secret-scanning.md)); GitHub push protection on
- [ ] Rotate on a schedule and immediately after any leak; revoke before cleaning history
- [ ] Back up age/GPG/Vault unseal keys offline, separately from the data ([GPG](gpg.md))

### Hosts and Containers
- [ ] Unattended security updates on (`unattended-upgrades`); reboot for kernel fixes
- [ ] Pin image versions or digests, update via Renovate, scan images ([Container Scanning](container-scanning.md))
- [ ] Run as non-root, `read_only`, `cap_drop: [ALL]`, `no-new-privileges` ([Docker-Compose](../docker/docker-compose.md))
- [ ] Don't mount `/var/run/docker.sock` into containers unless required (it is root on the host)
- [ ] Minimal installed packages and services; `ss -tulpn` to audit listening ports
- [ ] Audit logs shipped off-host and watched ([Prometheus](../apps/prometheus.md), [Grafana](../apps/grafana.md))

### Recovery
- [ ] Tested, encrypted, off-site backups (3-2-1) and a documented restore procedure
- [ ] Break-glass admin account stored offline; recovery codes saved
- [ ] Know how to revoke: SSH keys, GPG subkeys, API tokens, certificates

## Quick Audit Commands
COMMAND | DESCRIPTION
---|---
`ss -tulpn` | Listening ports and owning processes
`sudo ufw status verbose` | Firewall state
`sudo journalctl -u ssh --since "1 day ago" \| grep -i "failed"` | Recent SSH failures
`last -n 20` / `lastb -n 20` | Recent logins / failed logins
`sudo sshd -T \| grep -E "passwordauthentication\|permitrootlogin"` | Effective SSH settings
`apt list --upgradable` | Pending updates
`docker ps --format '{{.Names}}\t{{.Ports}}'` | Which containers publish ports
`nmap -sV <HOST>` | External view of open services ([NMap](../tools/nmap.md); only scan hosts you own)
