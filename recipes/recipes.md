# Recipes
Task-oriented, end-to-end walkthroughs that stitch several cheat sheets together. Each recipe has a goal, prerequisites, numbered steps, a verification step, an optional troubleshooting table, a rollback or cleanup note and a list of related sheets.

> **Verification:** the older recipes were written from the upstream documentation and no command was executed. The newer recipes (backup, restore test, Cloudflare Tunnel, migration, monitoring, update automation and authentik) each carry their own verification note saying what was and was not run. Check version-specific details (package names, image tags, Helm values) against the linked docs before using them on anything important. Addresses use the documentation ranges (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) and `example.com`.

## Build and Deploy
RECIPE | USE IT WHEN
---|---
[New Server Checklist](new-server-checklist.md) | You have a fresh Ubuntu server and want it patched, locked down and ready for Docker
[Docker Service Deploy](docker-service-deploy.md) | You want a Compose stack behind Traefik with TLS, secrets, healthchecks and updates
[Proxmox VM Template and Clone](proxmox-vm-template-and-clone.md) | You want repeatable VMs from a cloud-init template on Proxmox
[K3s Cluster from Scratch](k3s-cluster-from-scratch.md) | You want a Kubernetes cluster from one node up to HA, with ingress, TLS, storage, GitOps and monitoring
[WireGuard Remote Access](wireguard-remote-access.md) | You want remote access to your home network over WireGuard

## Backup and Operations
RECIPE | USE IT WHEN
---|---
[Off-Site Docker Host Backup with restic](offsite-docker-host-backup.md) | You want nightly encrypted backups of a Docker host to Backblaze B2 or a Storage Box
[Restore-Test a Backup](restore-test-a-backup.md) | You want proof that a backup restores from a clean machine, and how long it takes
[Migrate a Docker Service Between Hosts](migrate-docker-service-between-hosts.md) | You are moving a Compose stack, its volumes and its database to another host
[Monitor a Homelab with Prometheus and Grafana](monitor-homelab-prometheus-grafana.md) | You want dashboards and alerts, including an alert for when alerting stops
[Automate Container Updates Safely](automate-container-updates.md) | You want Renovate pull requests and Diun notices instead of blind auto-updates
[Zsh with antidote, Oh My Zsh and Powerlevel10k](zsh-antidote-omz-p10k.md) | You want a fast, reproducible Zsh set-up with plugins, a themed prompt and shared history

## Access and Identity
RECIPE | USE IT WHEN
---|---
[Expose a Service with Cloudflare Tunnel](expose-service-cloudflare-tunnel.md) | You want a public web app without opening ports or publishing your home IP
[Single Sign-On with authentik](sso-with-authentik.md) | You want one login for Grafana (OIDC) and for apps with no SSO (forward auth)

## Troubleshooting
RECIPE | USE IT WHEN
---|---
[Network Troubleshooting](network-troubleshooting.md) | Something cannot reach something else and you do not know which layer is at fault
[DNS Troubleshooting](dns-troubleshooting.md) | A name does not resolve, resolves wrongly or resolves slowly
[TLS Troubleshooting](tls-troubleshooting.md) | A browser or client complains about a certificate, handshake or protocol

## Recipe Layout
Every recipe follows the same shape, so you can skim for the part you need:

SECTION | CONTENT
---|---
Goal | The end state in one or two sentences
Prerequisites | What you need before step 1
Steps | Numbered, with real commands and `<PLACEHOLDERS>` in capitals
Verify | A check that proves the goal was reached
Troubleshooting | Common failures and fixes (optional)
Rollback / Cleanup | How to undo it or tidy up
Related Sheets | Links to the reference sheets used

## Related Sheets
- [Linux](../linux/linux.md) · [Docker](../docker/docker.md) · [Kubernetes](../kubernetes/kubernetes.md) · [Proxmox VE Overview and Install](../proxmox/proxmox-overview.md)
- [TLS (Transport Layer Security)](../networking/tls.md) · [VPN (Virtual Private Network)](../networking/vpn.md) · [NMap](../tools/nmap.md) · [OpenSSL](../tools/openssl.md) · [curl](../tools/curl.md)
- [Security](../security/security.md) · [Backup Strategy](../backup/backup.md) · [Scripting](../scripting/scripting.md) · [Homelab](../homelab/homelab.md) · [CI/CD Overview](../cicd/cicd.md)
