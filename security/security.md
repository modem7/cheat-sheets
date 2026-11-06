# Security
Overview of the security and secrets cheat sheets, with a hardening checklist for a homelab or small self-hosted environment. The aim is layered defence: keep secrets out of Git, put identity in one place, block abuse automatically, and scan what you build.

## Sheets in This Section
SHEET | USE IT FOR
---|---
[[sops-age]] | Encrypt secrets (`.env`, YAML) so they can live in Git
[[vault]] | Central secret store with policies, dynamic credentials (Vault / OpenBao)
[[gpg]] | Keys, signing, encryption, Git commit signing, backups
[[authentik]] | Self-hosted SSO, OIDC and forward-auth
[[keycloak]] | Self-hosted SSO, OIDC, SAML and federation
[[crowdsec]] | Log-driven intrusion prevention with community blocklists and bouncers
[[fail2ban]] | Simple host-based log-driven IP bans
[[secret-scanning]] | gitleaks, TruffleHog, GitHub push protection
[[container-scanning]] | Trivy, Grype and Syft for images and IaC

## Related Sheets Elsewhere
SHEET | USE IT FOR
---|---
[[openssl]] | Certificates, CSRs, key conversion
[[openssh]] | SSH keys, hardening `sshd_config`
[[bitwarden]] | Password manager and CLI
[[tls]] | TLS configuration
[[ssl-security]] | TLS security testing and settings
[[ufw]] | Simple host firewall
[[iptables]] | Low-level firewall rules
[[tailscale]] | Private mesh VPN instead of exposing ports
[[teleport]] | Short-lived certificates for SSH and Kubernetes access
[[cert-manager]] | Automated certificates in Kubernetes

## Choosing Tools
NEED | PICK
---|---
Secrets in a Git repo (GitOps, `.env`) | [[sops-age]]
Many apps and services fetching secrets at runtime, dynamic credentials | [[vault]]
One login for all apps, small setup | [[authentik]]
Enterprise features, SAML, large ecosystem | [[keycloak]]
Ban brute-force on one host, minimal setup | [[fail2ban]]
Shared threat intel, multiple hosts or proxies | [[crowdsec]]

## Hardening Checklist
### Access
- [ ] SSH: key-only auth, `PasswordAuthentication no`, `PermitRootLogin no`, non-default users ([[openssh]])
- [ ] Prefer a VPN or mesh ([[tailscale]], [[wireguard]]) over exposing admin ports to the internet
- [ ] Single sign-on with MFA for web UIs ([[authentik]] or [[keycloak]]); passkeys or TOTP for everything else
- [ ] Unique passwords in a manager ([[bitwarden]]); no shared admin accounts
- [ ] Least privilege: scoped API tokens, Vault policies, Kubernetes RBAC ([[kubernetes]])

### Network
- [ ] Default-deny firewall on every host ([[ufw]], [[iptables]]); remember Docker published ports bypass UFW
- [ ] Publish container ports on `127.0.0.1` and expose services through a reverse proxy ([[traefik]], [[nginx]])
- [ ] Valid TLS everywhere, HSTS on public sites ([[tls]], [[ssl-security]], [[cert-manager]])
- [ ] Automatic bans for abuse ([[crowdsec]] or [[fail2ban]]), with your own IPs allowlisted
- [ ] Separate networks/VLANs for IoT, guests and servers

### Secrets
- [ ] No plaintext secrets in Git: [[sops-age]] or [[vault]]; `.env` in `.gitignore`
- [ ] Secret scanning in pre-commit **and** CI ([[secret-scanning]]); GitHub push protection on
- [ ] Rotate on a schedule and immediately after any leak; revoke before cleaning history
- [ ] Back up age/GPG/Vault unseal keys offline, separately from the data ([[gpg]])

### Hosts and Containers
- [ ] Unattended security updates on (`unattended-upgrades`); reboot for kernel fixes
- [ ] Pin image versions or digests, update via Renovate, scan images ([[container-scanning]])
- [ ] Run as non-root, `read_only`, `cap_drop: [ALL]`, `no-new-privileges` ([[docker-compose]])
- [ ] Don't mount `/var/run/docker.sock` into containers unless required (it is root on the host)
- [ ] Minimal installed packages and services; `ss -tulpn` to audit listening ports
- [ ] Audit logs shipped off-host and watched ([[prometheus]], [[grafana]])

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
`nmap -sV <HOST>` | External view of open services ([[nmap]]; only scan hosts you own)
