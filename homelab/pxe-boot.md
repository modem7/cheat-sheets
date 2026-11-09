# PXE and iPXE Network Boot
PXE lets a machine boot an installer or tool over the network instead of from a USB stick. It is useful for reinstalling servers, running diagnostics and provisioning many machines. This sheet covers the boot flow, a dnsmasq setup and iPXE chainloading. For a ready-made menu of operating systems see [netboot.xyz](netboot-xyz.md). DHCP basics are in [dnsmasq DHCP](dnsmasq-dhcp.md).

Documentation: [iPXE](https://ipxe.org/docs), [dnsmasq man page](https://thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html)

## Boot Flow
1. The client firmware broadcasts a DHCP request.
2. DHCP (or a ProxyDHCP server) replies with a boot server and a file name.
3. The client downloads that file over TFTP.
4. The file (a bootloader such as iPXE) runs and loads a kernel and installer, often over HTTP.

PXE is IPv4 only in dnsmasq. BIOS and UEFI clients need different boot files, so the server must tell them apart by client architecture (DHCP option 93).

## Architecture
FIRMWARE | BOOT FILE
---|---
Legacy BIOS | `undionly.kpxe` (iPXE) or `netboot.xyz.kpxe`
UEFI x64 | `ipxe.efi` (iPXE) or `netboot.xyz.efi`
UEFI arm64 | an arm64 build, e.g. `netboot.xyz-arm64.efi`

Option 93 is an unsigned 16-bit value, with `00:00` meaning BIOS (from the ISC dhcpd howto). The netboot.xyz docs label the vendor class strings `00000` BIOS, `00007` x64 EFI, `0000B` and `00011` arm64. Other numeric option 93 values are not verified here.

## dnsmasq as ProxyDHCP
Keep your router as the DHCP server and let dnsmasq only add the PXE information (ProxyDHCP). The dnsmasq man page describes ProxyDHCP and the `proxy` range mode but gives no full worked example, so this is built from the documented options. Validate with `dnsmasq --test`.

```text
port=0
dhcp-range=192.0.2.0,proxy
enable-tftp
tftp-root=/srv/tftp
dhcp-match=set:bios,option:client-arch,0
dhcp-match=set:efi64,option:client-arch,7
pxe-prompt="Network boot", 5
pxe-service=tag:bios,x86PC,"Boot (BIOS)",undionly.kpxe
pxe-service=tag:efi64,x86-64_EFI,"Boot (UEFI)",ipxe.efi
```

`port=0` turns off dnsmasq's DNS if you only want PXE. `enable-tftp` is deliberately limited to what network booting needs. Paths containing `..` are rejected. Put the boot files in `tftp-root`. Option 93 value 7 for x64 EFI is not verified here (the man page only uses 6 as an example), so test with a real client.

## dnsmasq as the Full DHCP Server
When dnsmasq is your DHCP server, hand out the file name directly. This pattern is the one netboot.xyz documents, matching on DHCP option 60:

```text
enable-tftp
tftp-root=/srv/tftp
dhcp-match=set:bios,60,PXEClient:Arch:00000
dhcp-boot=tag:bios,netboot.xyz.kpxe,,192.0.2.10
dhcp-match=set:efi64,60,PXEClient:Arch:00007
dhcp-boot=tag:efi64,netboot.xyz.efi,,192.0.2.10
```

The last field of `dhcp-boot` is the TFTP server address. If dnsmasq itself serves TFTP, only the file name is needed.

## iPXE Chainloading
Firmware PXE can be buggy, so a common approach is to load iPXE first, then let iPXE fetch the real menu over HTTP. To stop an infinite loop, make DHCP hand out a different file once the client is already running iPXE. The ISC dhcpd form, from the iPXE docs:

```text
option client-arch code 93 = unsigned integer 16;
if option client-arch != 00:00 {
  filename "ipxe.efi";
} else {
  filename "undionly.kpxe";
}
```

In dnsmasq, tag iPXE clients with `dhcp-userclass=set:ipxe,iPXE` (substring matching) and serve them a different file with `dhcp-boot=tag:ipxe,...`. Whether dnsmasq accepts an `http://` URL there is not verified, so an `autoexec.ipxe` file next to the binary on the TFTP server is the documented loop breaker. Do not set `option ipxe.no-pxedhcp 1` if you use a ProxyDHCP server.

## iPXE Script Basics
```text
#!ipxe
dhcp
chain http://boot.example.com/menu.ipxe
```

- A script starts with `#!ipxe`. `dhcp` gets an address, `chain` loads another script or image.
- iPXE ends a script at once if any line fails. Use `||` to handle failures, for example `dhcp || goto retry_dhcp`.
- To bake a script into a binary: `make bin/undionly.kpxe EMBED=demo.ipxe`.
- The `kernel`, `initrd` and `boot` commands are not covered by the pages read here, so see the iPXE command reference.

## Unattended Installs
Ubuntu server installs can be automated with autoinstall data fetched over HTTP, and Proxmox with an answer file. The exact kernel arguments (such as `autoinstall ds=nocloud-net;s=http://...`) were not verified here. See [Proxmox cloud-init](../proxmox/proxmox-cloud-init.md) for image-based provisioning, which is often simpler for VMs.

## Secure Boot
Many network boot binaries are unsigned and will not run with Secure Boot enabled. This is a general caveat that was not checked against the docs here. Either disable Secure Boot for the install or use signed boot media.

## Troubleshooting
SYMPTOM | CHECK
---|---
Client gets no boot file | Firewall allows `67/udp`, `68/udp`, `69/udp` and `4011/udp` (ProxyDHCP) on the server
`PXE-E53: No boot filename received` | DHCP is not handing out a file name. Check tags and `dnsmasq --test`
TFTP timeout | Check `tftp-root` path and permissions, and that `69/udp` is open
Boots then loops back to iPXE | Add the loop breaker, or serve the final script to iPXE clients
Works on BIOS, fails on UEFI (or the reverse) | Wrong boot file for that architecture
Slow downloads | Serve kernel and initrd over HTTP, not TFTP

## See Also
- [netboot.xyz](netboot-xyz.md)
- [dnsmasq DHCP](dnsmasq-dhcp.md)
- [Proxmox cloud-init](../proxmox/proxmox-cloud-init.md)
- [VLANs](vlans.md)
