# Hardware Inspection
List the PCI and USB devices, CPU, memory, disks and firmware details of a Linux machine with `lspci`, `lsusb`, `lshw`, `dmidecode` and friends. Use it to identify a NIC or GPU for passthrough, check which kernel driver is bound, or confirm RAM speed and slots.

Documentation: [lspci(8)](https://man7.org/linux/man-pages/man8/lspci.8.html) · [lsusb(8)](https://man7.org/linux/man-pages/man8/lsusb.8.html) · [dmidecode(8)](https://man7.org/linux/man-pages/man8/dmidecode.8.html) · [lscpu(1)](https://man7.org/linux/man-pages/man1/lscpu.1.html)

> **Verification:** options were checked against the man pages in Ubuntu 24.04 (`pciutils`, `usbutils`, `lshw`, `dmidecode`, `util-linux`). Output depends on the hardware; most commands need `sudo` for full detail.

## PCI
COMMAND | DESCRIPTION
---|---
`lspci` | List PCI devices
`lspci -nn` | Include numeric vendor and device IDs (`[8086:1234]`)
`lspci -k` | Show the kernel driver in use and available modules
`lspci -v` / `lspci -vv` | Verbose / very verbose (link speed, capabilities; `sudo` for all)
`lspci -s <BUS:SLOT.FUNC>` | One device, e.g. `-s 01:00.0`
`lspci -d <VENDOR>:<DEVICE>` | Filter by ID
`lspci -tv` | Tree view of buses and bridges
`lspci -nnk \| grep -A3 -i vga` | GPU with its driver

## USB
COMMAND | DESCRIPTION
---|---
`lsusb` | List USB devices
`lsusb -t` | Tree with drivers and negotiated speed
`lsusb -v -d <VENDOR>:<PRODUCT>` | Full descriptor for one device

## CPU and Memory
COMMAND | DESCRIPTION
---|---
`lscpu` | CPU model, cores, threads, caches and virtualisation flags
`lscpu -e` | One line per logical CPU
`grep -m1 -oE 'vmx\|svm' /proc/cpuinfo` | Hardware virtualisation support (`vmx` Intel, `svm` AMD)
`free -h` | Memory and swap usage
`sudo dmidecode -t memory` | Installed DIMMs: size, speed, slot, manufacturer
`sudo dmidecode -t processor` | CPU socket and speed data

## Disks
COMMAND | DESCRIPTION
---|---
`lsblk` | Block devices as a tree
`lsblk -f` | Filesystems, labels and UUIDs
`lsblk -o NAME,SIZE,MODEL,SERIAL,ROTA` | Chosen columns (`ROTA` 1 = spinning disk)
`sudo smartctl -a /dev/<DISK>` | SMART health (from `smartmontools`)
`ls -l /dev/disk/by-id/` | Stable device names

## System and Firmware
COMMAND | DESCRIPTION
---|---
`sudo dmidecode -t system` | Manufacturer, model, serial
`sudo dmidecode -t bios` | BIOS version and date
`sudo dmidecode -t baseboard` | Motherboard details
`sudo dmidecode -s system-product-name` | Single string
`sudo lshw -short` | One-line overview of all hardware
`sudo lshw -class network` | One class: `network`, `disk`, `display`, `memory`
`sudo lshw -businfo` | Bus addresses (PCI, USB, SCSI)
`hostnamectl` | OS, kernel and hardware vendor or virtualisation type

## Kernel Modules and Drivers
COMMAND | DESCRIPTION
---|---
`lsmod` | Loaded kernel modules
`modinfo <MODULE>` | Module details and parameters
`sudo dmesg \| grep -i <DEVICE>` | Kernel messages about a device
`ls /sys/bus/pci/devices/` | PCI devices as the kernel sees them

## IOMMU Groups
Check how devices are grouped before PCIe passthrough:

```bash
for g in /sys/kernel/iommu_groups/*; do
  echo "Group ${g##*/}"
  for d in "$g"/devices/*; do lspci -nns "${d##*/}"; done
done
```

## See Also
- [Proxmox GPU and PCIe Passthrough](../proxmox/proxmox-passthrough.md)
- [Linux](linux.md)
- [Storage and Filesystems](storage-and-filesystems.md)
- [ethtool](ethtool.md)
- [Linux Performance Troubleshooting](performance-troubleshooting.md)
