# netboot.xyz
netboot.xyz lets you boot many operating system installers and utilities from one small network boot menu, built on iPXE. Use it to reinstall homelab machines without USB sticks. It can boot from a tiny ISO or USB image, or from a PXE setup on your network. See [PXE and iPXE](pxe-boot.md) for the underlying flow.

Documentation: [netboot.xyz](https://netboot.xyz/docs/)

## Supported
x86 (32 and 64-bit) and arm64, with legacy BIOS and UEFI.

## Boot Files
FILE | USE
---|---
`netboot.xyz.kpxe` | Legacy BIOS
`netboot.xyz-undionly.kpxe` | Legacy BIOS, uses the NIC's own PXE stack
`netboot.xyz.efi` | UEFI x64
`netboot.xyz-snp.efi`, `netboot.xyz-snponly.efi` | UEFI x64 with SNP drivers
`netboot.xyz-arm64.efi`, `netboot.xyz-arm64-snp.efi`, `netboot.xyz-arm64-snponly.efi` | UEFI arm64

Download them from the [netboot.xyz downloads page](https://netboot.xyz/downloads/). ISO and USB image names were not verified here. In a VM (see [Proxmox](../proxmox/proxmox-overview.md)) attach the ISO and boot from it (the Proxmox steps were not checked against the docs).

## Run Your Own Server (Docker)
The container serves a web UI, TFTP and an assets server. It **does not run a DHCP server**.

```bash
docker run -d --name=netbootxyz \
  -e MENU_VERSION=2.0.84 \
  -e NGINX_PORT=80 \
  -e WEB_APP_PORT=3000 \
  -p 3000:3000 \
  -p 69:69/udp \
  -p 8080:80 \
  -v /local/path/to/config:/config \
  -v /local/path/to/assets:/assets \
  --restart unless-stopped \
  ghcr.io/netbootxyz/netbootxyz
```

PORT | USE
---|---
`3000/tcp` | Web UI
`69/udp` | TFTP (boot files)
`8080/tcp` | Assets over NGINX (host port mapped to container port 80)

The image is also on Docker Hub as `netbootxyz/netbootxyz`. `/config` holds menu files and web app settings, and `/assets` holds downloaded installers. To serve installers locally instead of from the internet, set `live_endpoint` in `local-vars.ipxe`, for example `http://192.0.2.50:8080`. Do not expose the web UI to untrusted networks.

## Point DHCP at It
BIOS and UEFI clients need different files, so match the client type. dnsmasq, from the netboot.xyz docs:

```text
dhcp-match=set:bios,60,PXEClient:Arch:00000
dhcp-boot=tag:bios,netboot.xyz.kpxe,,SERVER_IP_ADDRESS
dhcp-match=set:efi64,60,PXEClient:Arch:00007
dhcp-boot=tag:efi64,netboot.xyz.efi,,SERVER_IP_ADDRESS
```

For arm64 match `PXEClient:Arch:0000B` and `PXEClient:Arch:00011` and serve `netboot.xyz-arm64.efi`. On a router or generic DHCP server, set `next-server` to the TFTP server and `filename` to `netboot.xyz.kpxe` (BIOS) or `netboot.xyz.efi` (UEFI). On the TFTP page the dnsmasq form is:

```text
enable-tftp
tftp-root=/var/lib/tftpboot
dhcp-boot=netboot.xyz.kpxe
```

The docs also say `dhcp-option=66,"0.0.0.0"` is read as the dnsmasq host's address, but the dnsmasq man page says a quoted value is sent as a literal string. These two readings conflict, so test before relying on either. See [dnsmasq DHCP](dnsmasq-dhcp.md).

## Custom Menus
Set `custom_generate_menus: true` and `custom_templates_dir` when building with the Ansible route, and the menu then loads `custom/custom.ipxe`. The Ansible route is the documented way to self-host a menu. The `docker build` route only generates static output. The custom menu page itself was not read here.

## Tips
- Boot a new VM or a spare machine first to prove DHCP, TFTP and the menu work before relying on it.
- Keep the menu version pinned (`MENU_VERSION`) and update on purpose.
- Network installs download from the internet or your assets server, so a slow link makes them slow.

## See Also
- [PXE and iPXE](pxe-boot.md)
- [dnsmasq DHCP](dnsmasq-dhcp.md)
- [Proxmox VM Template and Clone](../recipes/proxmox-vm-template-and-clone.md)
- [New Server Checklist](../recipes/new-server-checklist.md)
