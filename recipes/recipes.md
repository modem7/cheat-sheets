# Recipes
Task-oriented, end-to-end walkthroughs that stitch several cheat sheets together. Each recipe has a goal, prerequisites, numbered steps, a verification step, a rollback or cleanup note and a list of related sheets.

> **Verification:** the recipes were written from the upstream documentation but no command was executed. Check version-specific details (package names, image tags, Helm values) against the linked docs before using them on anything important. Addresses use the documentation ranges (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) and `example.com`.

## Build and Deploy
RECIPE | USE IT WHEN
---|---
[[new-server-checklist]] | You have a fresh Ubuntu server and want it patched, locked down and ready for Docker
[[docker-service-deploy]] | You want a Compose stack behind Traefik with TLS, secrets, healthchecks and updates
[[proxmox-vm-template-and-clone]] | You want repeatable VMs from a cloud-init template on Proxmox
[[k3s-cluster-from-scratch]] | You want a Kubernetes cluster from one node up to HA, with ingress, TLS, storage, GitOps and monitoring
[[wireguard-remote-access]] | You want remote access to your home network over WireGuard

## Troubleshooting
RECIPE | USE IT WHEN
---|---
[[network-troubleshooting]] | Something cannot reach something else and you do not know which layer is at fault
[[dns-troubleshooting]] | A name does not resolve, resolves wrongly or resolves slowly
[[tls-troubleshooting]] | A browser or client complains about a certificate, handshake or protocol

## Recipe Layout
Every recipe follows the same shape, so you can skim for the part you need:

SECTION | CONTENT
---|---
Goal | The end state in one or two sentences
Prerequisites | What you need before step 1
Steps | Numbered, with real commands and `<PLACEHOLDERS>` in capitals
Verify | A check that proves the goal was reached
Rollback / Cleanup | How to undo it or tidy up
Related sheets | Wikilinks to the reference sheets used

## Related Sheets
- [[linux]] · [[docker]] · [[kubernetes]] · [[proxmox-overview]]
- [[tls]] · [[vpn]] · [[nmap]] · [[openssl]] · [[curl]]
