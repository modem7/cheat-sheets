# VirtualBox
Oracle VirtualBox is a desktop hypervisor for Windows, Linux and macOS. `VBoxManage` is its command-line interface: use it to create, configure, start and script VMs without the GUI. [Vagrant Cheat-Sheet](vagrant.md) uses VirtualBox as its default provider.

Documentation: [VirtualBox User Manual](https://www.virtualbox.org/manual/) · [VBoxManage reference](https://www.virtualbox.org/manual/topics/vboxmanage.html)

> **Verification:** every `VBoxManage` command and option was checked against the official VirtualBox 7.1 User Manual (PDF, chapter 8 synopses and examples). No command was run: VirtualBox could not be installed in the build container. Option spellings changed in 7.x (for example `--os-type`, `--nic-type1`, `--bridge-adapter1`); the manual's own examples still show older forms such as `--ostype`, `--nic1` and `--natpf1`, and whether older spellings are still accepted is unverified. Check `VBoxManage modifyvm` output on your version. Items marked unverified are from general knowledge. Deleting VMs and media is destructive.

See also: [libvirt and KVM](../linux/libvirt-kvm.md) · [Vagrant Cheat-Sheet](vagrant.md) · [Packer](packer.md) · [Hypervisors Compared](../infra/hypervisor-comparison.md) · [WSL Cheat-Sheet](wsl.md)

---
## Concepts
TERM | MEANING
---|---
VM name or UUID | Every command takes `"VM name"` or its UUID, shown by `VBoxManage list vms`
Medium | A disk (VDI, VMDK, VHD), DVD or floppy image registered with VirtualBox
Storage controller | The virtual bus (SATA, IDE, NVMe and so on) that disks attach to
NAT | Default network. Guest reaches out, nothing reaches in unless you add port forwarding
NAT Network | Shared NAT between several VMs, they can talk to each other
Bridged | Guest appears on the physical LAN
Host-only | Guest and host only, no outside access
Internal | VMs on the same named internal network only
Guest Additions | Drivers and tools installed inside the guest (shared folders, clipboard, resize)
Extension Pack | Separate Oracle download adding USB 2/3, RDP, disk encryption and more. Different licence from VirtualBox itself

## Host Basics
COMMAND | DESCRIPTION
---|---
`VBoxManage -V` / `VBoxManage --version` | Installed version
`VBoxManage list vms` | Registered VMs with UUIDs
`VBoxManage list runningvms` | Running VMs
`VBoxManage list --long vms` | Full detail for every VM
`VBoxManage list ostypes` | Valid OS type IDs for `--ostype` and `--os-type`
`VBoxManage list hostinfo` | Host CPU and memory
`VBoxManage list systemproperties` | Defaults, such as the machine folder
`VBoxManage list bridgedifs` | Host interfaces usable for bridged networking
`VBoxManage list hostonlyifs` | Host-only interfaces
`VBoxManage list natnets` | NAT networks
`VBoxManage list hdds` / `dvds` / `floppies` | Registered media
`VBoxManage list extpacks` | Installed extension packs
`VBoxManage list usbhost` | USB devices on the host
`VBoxManage setproperty machinefolder PATH` | Change the default VM folder
`VBoxManage extpack install EXTPACK.vbox-extpack` | Install an extension pack (`--replace` to upgrade)
`VBoxManage extpack uninstall "Oracle VirtualBox Extension Pack"` | Remove it
`VBoxManage extpack cleanup` | Remove stale extension pack files

## Create a VM
`createvm` makes the VM, `modifyvm` sets hardware, `storagectl` and `storageattach` add disks. Create the disk with `createmedium`.

COMMAND | DESCRIPTION
---|---
`VBoxManage createvm --name NAME --platform-architecture x86 --ostype OSTYPE --register` | New VM, registered at once. `--basefolder DIR` chooses where it lives
`VBoxManage modifyvm NAME --memory 4096 --cpus 2 --vram 128` | RAM (MB), CPUs, video memory (MB)
`VBoxManage modifyvm NAME --firmware efi` | UEFI (`bios` is the other main option)
`VBoxManage modifyvm NAME --ioapic on` | Needed for more than one CPU on x86
`VBoxManage modifyvm NAME --boot1 dvd --boot2 disk --boot3 none --boot4 none` | Boot order
`VBoxManage modifyvm NAME --graphicscontroller vmsvga` | Graphics controller (`none`, `vboxvga`, `vmsvga`, `vboxsvga`)
`VBoxManage modifyvm NAME --tpm-type 2.0` | Virtual TPM (`none`, `1.2`, `2.0`, `host`, `swtpm`)
`VBoxManage modifyvm NAME --description "TEXT"` | Description
`VBoxManage modifyvm NAME --groups "/GROUP"` | Put the VM in a group. Empty string removes it
`VBoxManage createmedium disk --filename DISK.vdi --size 20480` | New 20 GB disk (size in MB, or `--sizebyte`). Formats: `VDI`, `VMDK`, `VHD` via `--format`
`VBoxManage createmedium disk --filename DISK.vdi --size 20480 --variant Fixed` | Fixed-size, preallocated disk
`VBoxManage storagectl NAME --name "SATA" --add sata --controller IntelAhci` | Add a SATA controller
`VBoxManage storagectl NAME --name "IDE" --add ide` | Add an IDE controller (often used for the install ISO)
`VBoxManage storageattach NAME --storagectl "SATA" --port 0 --device 0 --type hdd --medium DISK.vdi` | Attach the disk
`VBoxManage storageattach NAME --storagectl "IDE" --port 0 --device 0 --type dvddrive --medium INSTALL.iso` | Attach an ISO
`VBoxManage storageattach NAME --storagectl "IDE" --port 0 --device 0 --type dvddrive --medium emptydrive` | Empty drive
`VBoxManage storageattach NAME --storagectl "IDE" --port 0 --device 0 --medium none` | Remove the medium from the drive (`--forceunmount` if the guest has it locked)

```bash
VM="web01"
VBoxManage createvm --name "$VM" --platform-architecture x86 \
  --ostype Ubuntu_64 --register
VBoxManage modifyvm "$VM" --memory 4096 --cpus 2 --ioapic on \
  --boot1 dvd --boot2 disk --boot3 none --boot4 none
VBoxManage createmedium disk --filename "$HOME/VirtualBox VMs/$VM/$VM.vdi" --size 20480
VBoxManage storagectl "$VM" --name "SATA" --add sata --controller IntelAhci
VBoxManage storageattach "$VM" --storagectl "SATA" --port 0 --device 0 \
  --type hdd --medium "$HOME/VirtualBox VMs/$VM/$VM.vdi"
VBoxManage storagectl "$VM" --name "IDE" --add ide
VBoxManage storageattach "$VM" --storagectl "IDE" --port 0 --device 0 \
  --type dvddrive --medium /path/to/ubuntu.iso
VBoxManage startvm "$VM" --type headless
```

`Ubuntu_64` is an example ID: confirm it with `VBoxManage list ostypes`.

## Unattended Install
COMMAND | DESCRIPTION
---|---
`VBoxManage unattended detect --iso INSTALL.iso` | Show whether the ISO is supported for unattended install
`VBoxManage unattended install NAME --iso INSTALL.iso --user USER --password-file FILE --hostname HOST.example.com --install-additions --start-vm headless` | Install the OS with no interaction. `--start-vm` takes a session type such as `headless` (value list unverified)
`VBoxManage unattended install NAME --iso INSTALL.iso --dry-run` | Show what it would do

The VM must exist, with a disk and storage controller, before `unattended install`.

## Start, Stop and Control
COMMAND | DESCRIPTION
---|---
`VBoxManage startvm NAME` | Start with the GUI window
`VBoxManage startvm NAME --type headless` | Start with no window. Other types: `gui`, `sdl`, `separate`
`VBoxManage controlvm NAME pause` / `resume` | Pause and resume
`VBoxManage controlvm NAME reset` | Hard reset
`VBoxManage controlvm NAME acpipowerbutton` | Press the ACPI power button (graceful shutdown if the guest handles it)
`VBoxManage controlvm NAME shutdown` | Shut down via Guest Additions (`--force` to force)
`VBoxManage controlvm NAME reboot` | Reboot via Guest Additions
`VBoxManage controlvm NAME poweroff` | Pull the plug. The guest may lose data
`VBoxManage controlvm NAME savestate` | Save state to disk and stop
`VBoxManage discardstate NAME` | Throw away a saved state. Unsaved guest state is lost
`VBoxManage controlvm NAME screenshotpng FILE.png` | Screenshot of the guest display
`VBoxManage controlvm NAME setvideomodehint 1920 1080` | Ask the guest to change resolution
`VBoxManage controlvm NAME keyboardputstring "TEXT"` | Type text into the guest
`VBoxManage controlvm NAME clipboard mode bidirectional` | Shared clipboard (`disabled`, `hosttoguest`, `guesttohost`)
`VBoxManage controlvm NAME usbattach UUID_OR_ADDRESS` / `usbdetach` | Attach or detach a host USB device (needs the Extension Pack for USB 2/3)
`VBoxManage controlvm NAME vrde on` | Enable the remote display server (needs the Extension Pack)
`VBoxManage showvminfo NAME` | VM settings and state
`VBoxManage showvminfo NAME --machinereadable` | Same, as `key=value` lines for scripts
`VBoxManage unregistervm NAME` | Remove the VM from VirtualBox, keep its files
`VBoxManage unregistervm NAME --delete` | Also delete its files (disks are kept if shared). Destructive
`VBoxManage unregistervm NAME --delete-all` | Delete all files including media. Destructive

## Networking
Set the adapter type with `--nicN` (N is 1 to 8 in the GUI, check your version) and the attachment options named in the table.

COMMAND | DESCRIPTION
---|---
`VBoxManage modifyvm NAME --nic1 nat` | NAT (the default)
`VBoxManage modifyvm NAME --nic1 bridged --bridge-adapter1 eth0` | Bridged to a host interface (names from `list bridgedifs`)
`VBoxManage modifyvm NAME --nic2 hostonly --host-only-adapter2 vboxnet0` | Host-only (name from `list hostonlyifs`)
`VBoxManage modifyvm NAME --nic2 intnet --intnet2 LABNET` | Internal network
`VBoxManage modifyvm NAME --nic2 natnetwork --nat-network2 NATNET` | NAT Network
`VBoxManage modifyvm NAME --nic-type1 virtio` | Adapter model. Others: `Am79C970A`, `Am79C973`, `82540EM`, `82543GC`, `82545EM`
`VBoxManage modifyvm NAME --mac-address1 auto` | New MAC address. Use it after copying a VM
`VBoxManage modifyvm NAME --cable-connected1 off` | Unplug the virtual cable
`VBoxManage modifyvm NAME --nat-pf1 "ssh,tcp,,2222,,22"` | NAT port forward: host port 2222 to guest port 22. Format `name,tcp\|udp,host-IP,host-port,guest-IP,guest-port`
`VBoxManage modifyvm NAME --natpf1 delete "ssh"` | Delete the rule named `ssh`. The manual shows both `--nat-pf1` and `--natpf1` spellings
`VBoxManage controlvm NAME natpf1 "ssh,tcp,,2222,,22"` | Add a forward to a running VM
`VBoxManage controlvm NAME nic1 null` | Change the attachment of a running VM (`null`, `nat`, `bridged`, `intnet`, `hostonly`, `generic`, `natnetwork`)
`VBoxManage hostonlyif create` | New host-only interface. See also `hostonlynet` below
`VBoxManage hostonlyif ipconfig vboxnet0 --ip 192.168.56.1 --netmask 255.255.255.0` | Set its IP. On Linux, macOS and Solaris only `192.168.56.0/21` is allowed unless `/etc/vbox/networks.conf` permits more
`VBoxManage hostonlyif remove vboxnet0` | Remove it
`VBoxManage hostonlynet add --name NET --netmask 255.255.255.0 --lower-ip 192.168.56.10 --upper-ip 192.168.56.100` | Host-only network with a DHCP range (same address restriction on Linux and macOS)
`VBoxManage hostonlynet remove --name NET` | Remove it
`VBoxManage natnetwork add --netname NATNET --network "192.0.2.0/24" --enable` | New NAT Network
`VBoxManage natnetwork modify --netname NATNET --dhcp on` | Enable its DHCP server
`VBoxManage natnetwork start --netname NATNET` / `stop` | Start or stop it
`VBoxManage natnetwork list` | List NAT networks
`VBoxManage natnetwork remove --netname NATNET` | Delete it
`VBoxManage dhcpserver add --network NET --server-ip IP --lower-ip IP --upper-ip IP --netmask MASK --enable` | DHCP server for an internal network (`--interface IFNAME` for a host-only interface)
`VBoxManage dhcpserver findlease --network NET --mac-address MAC` | Look up a lease

On Linux, macOS and Solaris, create `/etc/vbox/networks.conf` to allow other host-only ranges. Each line starts with `*` followed by the allowed CIDRs, for example `* 10.0.0.0/8 192.168.0.0/16`.

## Snapshots
COMMAND | DESCRIPTION
---|---
`VBoxManage snapshot NAME take SNAP --description "TEXT"` | Take a snapshot. `--live` takes it while running
`VBoxManage snapshot NAME list` | List snapshots (`--details` or `--machinereadable`)
`VBoxManage snapshot NAME showvminfo SNAP` | VM settings at that snapshot
`VBoxManage snapshot NAME restore SNAP` | Revert to a snapshot. Current state is lost
`VBoxManage snapshot NAME restorecurrent` | Revert to the most recent snapshot
`VBoxManage snapshot NAME edit SNAP --name NEWNAME --description "TEXT"` | Rename or re-describe
`VBoxManage snapshot NAME delete SNAP` | Delete a snapshot and merge its data into the next. Needs free disk space

## Clone, Export and Import
COMMAND | DESCRIPTION
---|---
`VBoxManage clonevm NAME --name NEWNAME --register` | Clone and register the copy
`VBoxManage clonevm NAME --name NEWNAME --register --mode all` | Clone including all snapshots (`machine`, `machinechildren`, `all`)
`VBoxManage clonevm NAME --name NEWNAME --snapshot SNAP --register` | Clone from a snapshot
`VBoxManage clonevm NAME --name NEWNAME --register --options keepallmacs` | Keep MAC addresses. Repeat `--options` for `keepdisknames` and `keephwuuids`
`VBoxManage export NAME --output VM.ova` | Export an appliance. Add `--manifest` for a checksum file or `--ovf20` for OVF 2.0
`VBoxManage import VM.ova --dry-run` | Show what would be imported
`VBoxManage import VM.ova --vsys 0 --vmname NEWNAME` | Import and rename the first virtual system
`VBoxManage import VM.ova --options keepallmacs` | Keep MAC addresses. Others: `keepnatmacs`, `importtovdi`
`VBoxManage clonemedium DISK.vdi COPY.vdi` | Copy a disk. `--format VMDK` converts
`VBoxManage clonemedium disk SRC.vdi DST.vmdk --format VMDK` | Convert VDI to VMDK
`VBoxManage convertfromraw IN.img OUT.vdi` | Convert a raw image into a VirtualBox disk
`VBoxManage closemedium disk DISK.vdi` | Unregister a disk (file stays)
`VBoxManage closemedium disk DISK.vdi --delete` | Unregister and delete the file. Destructive
`VBoxManage showmediuminfo disk DISK.vdi` | Size, format, type and which VMs use it
`VBoxManage modifymedium disk DISK.vdi --resize 40960` | Grow a disk (size in MB). Resize partitions in the guest after
`VBoxManage modifymedium disk DISK.vdi --compact` | Compact a dynamic disk (zero free space in the guest first)
`VBoxManage modifymedium disk DISK.vdi --type immutable` | Medium type: `normal`, `writethrough`, `immutable`, `shareable`, `readonly`, `multiattach`
`VBoxManage modifymedium disk DISK.vdi --move NEWPATH` | Move the disk file

To use a VirtualBox disk with [libvirt and KVM](../linux/libvirt-kvm.md), convert it with `qemu-img convert -f vdi -O qcow2 IN.vdi OUT.qcow2`.

## Guest Control and Shared Folders
Needs Guest Additions running in the guest.

COMMAND | DESCRIPTION
---|---
`VBoxManage guestcontrol NAME run --exe /bin/ls --username USER --passwordfile FILE --wait-stdout -- ls -l /tmp` | Run a program in the guest and show its output
`VBoxManage guestcontrol NAME copyto --username USER --passwordfile FILE --target-directory /tmp LOCALFILE` | Copy a file into the guest (`--recursive` for directories)
`VBoxManage guestcontrol NAME copyfrom --username USER --passwordfile FILE --target-directory HOSTDIR /tmp/FILE` | Copy a file out of the guest
`VBoxManage guestcontrol NAME mkdir --username USER --passwordfile FILE /tmp/DIR` | Create a directory in the guest
`VBoxManage guestproperty enumerate NAME` | All guest properties (IP, OS, Additions version)
`VBoxManage guestproperty get NAME /VirtualBox/GuestInfo/Net/0/V4/IP` | One property, here the first NIC's IPv4 address
`VBoxManage guestproperty set NAME PROPERTY VALUE` | Set a property. `unset NAME PROPERTY` removes it
`VBoxManage sharedfolder add NAME --name SHARE --hostpath HOSTDIR --automount` | Share a host folder (`--readonly`, `--transient`, `--auto-mount-point PATH`)
`VBoxManage sharedfolder remove NAME --name SHARE` | Remove it
`VBoxManage setextradata NAME KEY VALUE` | Set extra data (advanced settings)
`VBoxManage getextradata NAME enumerate` | List extra data

Prefer `--passwordfile` over `--password`, which exposes the password in the process list.

## Other
COMMAND | DESCRIPTION
---|---
`VBoxManage modifyvm NAME --autostart-enabled on` | Allow autostart (needs the host autostart service set up, unverified)
`VBoxManage modifyvm NAME --nested-hw-virt on` | Expose virtualisation to the guest
`VBoxManage modifyvm NAME --paravirt-provider kvm` | Paravirtualisation interface. Others: `none`, `default`, `legacy`, `minimal`, `hyperv`
`VBoxManage modifyvm NAME --vrde on` | Remote display server
`VBoxManage modifyvm NAME --snapshot-folder PATH` | Snapshot location
`VBoxManage modifynvram NAME inituefivarstore` | Initialise the UEFI variable store
`VBoxManage modifynvram NAME secureboot --enable` | Enable Secure Boot
`VBoxManage metrics query NAME` | Performance counters
`VBoxManage updatecheck perform` | Check for a new VirtualBox release

## Troubleshooting
SYMPTOM | FIX
---|---
Start fails with a kernel driver error on Linux | The `vboxdrv` module is not loaded. Rebuild it with `sudo rcvboxdrv setup`. With UEFI Secure Boot the kernel modules must be signed (see the manual's Kernel Modules and UEFI Secure Boot section)
VirtualBox fails to start with Hyper-V or WSL2 enabled on Windows | Both want the hypervisor. Disable Hyper-V and the Windows Hypervisor Platform, or accept the slower fallback ([WSL Cheat-Sheet](wsl.md))
`VBoxManage` says the VM is locked | Another session holds it. Close the GUI or run `VBoxManage controlvm NAME poweroff`
VM is not listed after copying its folder | Register it: `VBoxManage registervm /path/NAME.vbox`
Cloned VM clashes on the network | Give it a new MAC with `--mac-address1 auto` and change the guest hostname
No IP via host-only | Check the interface has an IP and that a DHCP server is attached for it
Command option rejected | Spelling differs between 6.x, 7.0 and 7.1. Run `VBoxManage modifyvm` with no arguments to see the usage for your version

## See Also
- [libvirt and KVM](../linux/libvirt-kvm.md)
- [Vagrant Cheat-Sheet](vagrant.md)
- [Packer](packer.md)
- [Hypervisors Compared](../infra/hypervisor-comparison.md)
- [WSL Cheat-Sheet](wsl.md)
