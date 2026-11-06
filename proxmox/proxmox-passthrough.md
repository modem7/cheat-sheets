# Proxmox GPU and PCIe Passthrough
Pass a physical PCI device (GPU, HBA, NIC, NVMe) to a VM using VFIO. The device is then unavailable to the host and other guests.

Documentation: [PCI(e) Passthrough](https://pve.proxmox.com/wiki/PCI_Passthrough) · [qm PCI docs](https://pve.proxmox.com/pve-docs/chapter-qm.html#qm_pci_passthrough)

> **Verification:** the `hostpci` syntax, `vfio` module list, `update-initramfs`, `pvesh get /nodes/<NODE>/hardware/pci` and `pvesh create /cluster/mapping/pci` were checked against the docs. **Not verified:** `proxmox-boot-tool refresh` versus `update-grub` for your boot setup, vendor specific quirks and reset bug workarounds. No command was executed. Hardware behaviour varies a lot, expect trial and error.

See also: [Proxmox qm and pct](proxmox-qm-pct.md) · [Proxmox Troubleshooting and One-Liners](proxmox-troubleshooting.md) · [Linux](../linux/linux.md) · [Docker](../docker/docker.md) (GPU in containers is a different route)

---
## Requirements
- CPU and board with IOMMU (VT-d on Intel, AMD-Vi on AMD), enabled in firmware, plus VT-x/AMD-V.
- UEFI boot, VM with machine type `q35` and BIOS `OVMF` (recommended by the docs).
- Device in a usable IOMMU group (ideally alone, or with its own audio function).

---
## Step 1: Enable IOMMU
AMD IOMMU is on by default on current kernels. Intel is on by default on recent kernels too, if it is not, add `intel_iommu=on`. `iommu=pt` is optional and can improve host performance.

Kernel command line:
- GRUB: edit `GRUB_CMDLINE_LINUX_DEFAULT` in `/etc/default/grub`, then `update-grub`.
- systemd-boot (ZFS on UEFI installs): edit `/etc/kernel/cmdline`, then `proxmox-boot-tool refresh`.

COMMAND | DESCRIPTION
---|---
`cat /proc/cmdline` | Check the active kernel options
`dmesg \| grep -e DMAR -e IOMMU` | IOMMU enabled messages
`find /sys/kernel/iommu_groups/ -type l \| sort -V` | List IOMMU groups
`lspci -nnk` | Devices with IDs and the driver in use
`lspci -nnk -s <PCI-ADDR>` | One device (look for `Kernel driver in use: vfio-pci`)

## Step 2: VFIO Modules
`/etc/modules-load.d/vfio.conf` (or `/etc/modules`):
```
vfio
vfio_iommu_type1
vfio_pci
```
Then:
```bash
update-initramfs -u -k all
reboot
```

## Step 3: Bind the Device to vfio-pci (if the host driver grabs it)
Find the vendor:device IDs with `lspci -nn`, then `/etc/modprobe.d/vfio.conf`:
```
options vfio-pci ids=<VENDOR>:<DEVICE>,<VENDOR>:<AUDIO-DEVICE>
```
Optionally blacklist the host driver (`/etc/modprobe.d/blacklist.conf`, for example `blacklist nouveau`, `blacklist nvidia`, `blacklist amdgpu`) and run `update-initramfs -u -k all`.

## Step 4: Attach to the VM
COMMAND | DESCRIPTION
---|---
`qm set <VMID> --machine q35 --bios ovmf` | Machine type and firmware (add an EFI disk: `--efidisk0 <STORAGE>:1`)
`qm set <VMID> --hostpci0 <PCI-ADDR>,pcie=on,x-vga=on` | Pass a GPU (all functions with `<BUS>:<SLOT>`)
`qm set <VMID> --hostpci0 <PCI-ADDR>,pcie=on` | Pass a non-GPU card (HBA, NIC)
`qm set <VMID> --hostpci0 mapping=<NAME>,pcie=on` | Use a cluster resource mapping
`qm set <VMID> --vga none` | Drop the virtual display if the GPU is the only one
`pvesh get /nodes/<NODE>/hardware/pci --pci-class-blacklist ""` | List PCI devices via the API
`pvesh create /cluster/mapping/pci --id <NAME> --map node=<NODE>,path=<PCI-ADDR>,id=<VENDOR>:<DEVICE>` | Create a mapping (allows non-root use and migration planning)

Passthrough VMs cannot be live migrated, and guest memory is pinned. Install the vendor drivers in the guest. NVIDIA consumer cards historically needed hidden-hypervisor tweaks, recent drivers usually do not.

---
## Common Problems
- Empty or merged IOMMU groups: try a different slot or check firmware ACS settings. The ACS override kernel option is a security trade-off.
- Black screen or reset bug (some AMD cards): unbind the card in the guest, reboot the host, or use a vendor-reset module.
- `Kernel driver in use` not `vfio-pci`: IDs wrong or initramfs not rebuilt.
- Cannot start VM, "group not viable": another device in the group is still in use by the host.
- Check `journalctl -b -k | grep -i vfio` and see [Proxmox Troubleshooting and One-Liners](proxmox-troubleshooting.md).

LXC GPU sharing (device nodes and bind mounts) is an alternative that does not take the card away from the host. It is not covered here.
