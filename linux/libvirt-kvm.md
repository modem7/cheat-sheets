# libvirt and KVM
KVM is the Linux kernel hypervisor and QEMU the emulator that runs the guests. libvirt is the management layer on top: `virsh` is its shell, `virt-install` creates guests, `qemu-img` manages disk images and `virt-manager` is the desktop GUI. Use it for VMs on a single Linux host without Proxmox ([Proxmox VE Overview and Install](../proxmox/proxmox-overview.md)).

Documentation: [libvirt](https://libvirt.org/docs.html) · [virt-manager](https://virt-manager.org/) · `man virsh`, `man virt-install`, `man qemu-img`

> **Verification:** `virsh`, `virt-install`, `virt-clone`, `virt-xml`, `virt-manager`, `virt-viewer` and `qemu-img` options were checked against the man pages shipped with Debian 12 (libvirt 9.0.0, virtinst 4.1.0, QEMU 7.2). No command was run against a live hypervisor. Install package names, default paths and the `default` network XML path are from general knowledge (unverified). Deleting domains, volumes and snapshots is destructive: back up first.

See also: [Hypervisors Compared](../infra/hypervisor-comparison.md) · [VirtualBox](../tools/virtualbox.md) · [Storage and Filesystems](storage-and-filesystems.md) · [LVM](lvm.md) · [ZFS](zfs.md) · [Netplan](netplan.md) · [Hardware Inspection](hardware-inspection.md) · [Linux](linux.md)

---
## Concepts
TERM | MEANING
---|---
Domain | A guest VM. libvirt calls it a domain, defined by XML
Persistent / transient | Persistent domains survive reboot (`define`); transient ones vanish when stopped (`create`)
Network | Virtual network on the host. The usual `default` network is NAT with DHCP
Storage pool | A place libvirt keeps disk images (directory, LVM, NFS, iSCSI and more)
Volume | One disk image or block device inside a pool
`qemu:///system` | System-wide connection, run by root. VMs start at boot and are shared by users in the libvirt group
`qemu:///session` | Per-user connection. No root needed, but limited networking
Internal snapshot | Stored inside the qcow2 file. Simple, needs qcow2
External snapshot | Writes go to a new overlay file. Needed for `--disk-only`

## Install and Check Host
COMMAND | DESCRIPTION
---|---
`grep -Ec '(vmx\|svm)' /proc/cpuinfo` | Non-zero means the CPU has hardware virtualisation (it may still be off in the firmware)
`lsmod \| grep kvm` | KVM modules loaded (`kvm_intel` or `kvm_amd`)
`sudo apt install qemu-kvm libvirt-daemon-system libvirt-clients virtinst virt-manager` | Debian and Ubuntu packages (unverified: package set varies by release)
`sudo systemctl enable --now libvirtd` | Start the daemon. Newer releases may use modular `virt*d` daemons (unverified)
`sudo usermod -aG libvirt $USER` | Let a user manage system VMs without sudo. Log out and in afterwards
`virsh version` | Library, API and hypervisor versions
`virsh -c qemu:///system list --all` | Test the connection
`virsh capabilities` | Host capabilities as XML
`virsh nodeinfo` | Host CPU and memory summary
`virsh domcapabilities` | What the emulator supports (machine types, firmware, CPU models)
`export LIBVIRT_DEFAULT_URI=qemu:///system` | Make `virsh`, `virt-install` and `virt-manager` default to the system connection (unverified)

## virsh Basics
Run `virsh COMMAND` once, or `virsh` for an interactive shell. Use `-c URI` to pick the connection. `DOMAIN` is a name, ID or UUID.

COMMAND | DESCRIPTION
---|---
`virsh list` | Running domains
`virsh list --all` | All domains, including shut off
`virsh list --inactive` | Domains that are not running
`virsh list --name` | Names only, handy for scripts
`virsh dominfo DOMAIN` | State, memory, vCPUs, autostart
`virsh domstate DOMAIN` | Current state
`virsh dumpxml DOMAIN` | Full XML definition
`virsh dumpxml --inactive DOMAIN` | The persistent definition rather than the live one
`virsh edit DOMAIN` | Edit the XML in `$EDITOR`. Validated on save
`virsh define FILE.xml` | Create or update a persistent domain from XML
`virsh domstats DOMAIN` | Statistics (CPU, balloon, block, net)
`virsh vcpucount DOMAIN` | Current and maximum vCPUs
`virsh domifaddr DOMAIN` | Guest IP addresses (from the DHCP lease)
`virsh domifaddr DOMAIN --source agent` | Ask the guest agent instead (needs qemu-guest-agent in the guest). Other sources: `lease`, `arp`
`virsh domiflist DOMAIN` | Virtual NICs and their MAC addresses
`virsh domblklist DOMAIN` | Disks attached to the domain
`virsh domblkinfo DOMAIN vda --human` | Capacity, allocation and physical size of one disk

## Power and Lifecycle
COMMAND | DESCRIPTION
---|---
`virsh start DOMAIN` | Boot a defined domain
`virsh start DOMAIN --console` | Boot and attach to the serial console
`virsh start DOMAIN --paused` | Boot paused
`virsh shutdown DOMAIN` | Graceful shutdown (ACPI or guest agent). Not guaranteed to succeed
`virsh shutdown DOMAIN --mode agent` | Choose the method: `acpi`, `agent`, `initctl`, `signal`, `paravirt`
`virsh reboot DOMAIN` | Graceful reboot
`virsh reset DOMAIN` | Hard reset, like the reset button
`virsh destroy DOMAIN` | Force power off. Does not delete anything despite the name
`virsh destroy DOMAIN --graceful` | Try a graceful stop first
`virsh suspend DOMAIN` / `virsh resume DOMAIN` | Pause and unpause in memory
`virsh managedsave DOMAIN` | Save RAM to disk and stop. The next `start` restores it
`virsh autostart DOMAIN` | Start at host boot
`virsh autostart --disable DOMAIN` | Stop autostarting
`virsh console DOMAIN` | Serial console. Leave with `Ctrl+]`. The guest needs a serial getty
`virsh undefine DOMAIN` | Remove the definition only. Disks stay
`virsh undefine DOMAIN --remove-all-storage` | Remove the definition and its disk volumes. Destructive
`virsh undefine DOMAIN --nvram` | Also remove the UEFI variable store, needed for UEFI guests
`virsh undefine DOMAIN --snapshots-metadata` | Also remove snapshot metadata

## Create Guests with virt-install
Minimum options are `--memory`, storage (`--disk` or `--filesystem`) and an install method. Most options take `opt1=val1,opt2=val2`. Run `virt-install --disk=?` to list the sub-options of any option.

COMMAND | DESCRIPTION
---|---
`virt-install --osinfo list` | Accepted OS names for `--osinfo`
`osinfo-query os` | Fuller OS list (package `libosinfo-bin`)
`--name NAME` | Domain name (`-n`)
`--memory 4096` | RAM in MiB
`--vcpus 4` | Virtual CPUs
`--cpu host-passthrough` | Pass host CPU features through. Other values include `host-model` and named models
`--osinfo ubuntu24.04` | OS being installed; sets sensible device defaults (`--os-variant` is the older name)
`--disk size=20` | New 20 GiB disk in the default pool
`--disk path=PATH,size=20,format=qcow2,bus=virtio` | Explicit path, format and bus
`--disk pool=POOL,size=20` | New volume in a named pool
`--disk PATH` | Use an existing image
`--cdrom FILE.iso` | Install from an ISO (`-c`)
`--location URL_OR_PATH` | Install from a distro tree. Allows `--extra-args` (`-l`)
`--extra-args "console=ttyS0"` | Kernel arguments with `--location`
`--pxe` | Network boot install
`--import` | Skip install, boot an existing disk image
`--install ubuntu24.04` | Fetch install media for a known OS (needs network)
`--unattended` | Unattended install via libosinfo. Combine with `--install` or `--cdrom`
`--cloud-init` | Attach a cloud-init config. Bare form generates a root password and disables the account login (see the man page)
`--network network=default,model=virtio` | Attach to the `default` virtual network (`-w`)
`--network bridge=br0` | Attach to a host bridge
`--network none` | No NIC
`--graphics none` | No graphics, serial console only
`--graphics vnc` | VNC instead of the default SPICE
`--boot uefi` | UEFI firmware
`--machine q35` | Machine type
`--tpm emulator` | Emulated TPM (needed for Windows 11)
`--noautoconsole` | Do not open a console, return at once
`--autostart` | Autostart the guest at host boot
`--transient` | Transient domain, with `--import` or `--boot`
`--noreboot` | Do not reboot after install
`--wait` | Wait for the install to finish. Bare form waits forever; a number is minutes
`--connect qemu:///system` | Use the system daemon
`--print-xml` | Print the XML instead of defining the guest. Still creates storage unless combined with `--dry-run`
`--dry-run` | Go through the steps without creating storage or defining the guest
`--check path_in_use=off` | Disable a validation check

```bash
# Ubuntu server from an ISO, 2 vCPUs, 4 GiB RAM, 20 GiB virtio disk, NAT network
sudo virt-install \
  --connect qemu:///system \
  --name web01 \
  --memory 4096 --vcpus 2 \
  --osinfo ubuntu24.04 \
  --disk size=20,format=qcow2,bus=virtio \
  --network network=default,model=virtio \
  --cdrom /var/lib/libvirt/images/ubuntu-24.04-live-server-amd64.iso \
  --graphics vnc

# Headless: import an existing cloud image
sudo virt-install --name cloud01 --memory 2048 --vcpus 2 \
  --osinfo ubuntu24.04 --import \
  --disk path=/var/lib/libvirt/images/cloud01.qcow2 \
  --network network=default --graphics none --noautoconsole
```

## Clone and Edit
COMMAND | DESCRIPTION
---|---
`virt-clone --original DOMAIN --auto-clone` | Clone a shut-off domain and its disks with generated names (`-o`)
`virt-clone -o DOMAIN -n NEWNAME -f NEW.qcow2` | Clone with an explicit name and disk path
`virt-clone ... --nonsparse` | Do not make the copy sparse
`virt-clone ... --reflink` | Use reflink copies on a filesystem that supports them
`virt-clone ... -m MAC` | Set the new MAC address
`virt-xml DOMAIN --edit --memory 8192` | Change an option in the domain XML without opening an editor
`virt-xml DOMAIN --edit --vcpus 4 --print-diff` | Show what would change
`virt-xml DOMAIN --edit --boot menu=on` | Enable the boot menu
`virt-xml DOMAIN --add-device --disk size=10` | Add a device
`virt-xml DOMAIN --remove-device --disk 2` | Remove the second disk
`virt-xml DOMAIN --edit --update` | Also apply to the running guest where possible (`--update`)
`virt-xml DOMAIN --edit ... --confirm` | Ask before saving

## Live Changes and Devices
Use `--live` for the running guest, `--config` for the persistent definition, `--current` for whichever applies now. Combine `--live --config` to do both.

COMMAND | DESCRIPTION
---|---
`virsh setvcpus DOMAIN 4 --config` | Set vCPU count in the definition (applies at next boot)
`virsh setvcpus DOMAIN 4 --live` | Hot-plug vCPUs (up to the maximum)
`virsh setvcpus DOMAIN 8 --maximum --config` | Raise the maximum
`virsh setmem DOMAIN 2G --live` | Change live memory (balloon) up to the maximum. Size takes a unit suffix
`virsh attach-disk DOMAIN /path/disk.qcow2 vdb --subdriver qcow2 --persistent` | Attach a disk as `vdb` and keep it in the definition
`virsh detach-disk DOMAIN vdb --persistent` | Detach it
`virsh attach-interface DOMAIN network default --model virtio --persistent` | Add a NIC on the `default` network
`virsh detach-interface DOMAIN network --mac MAC --persistent` | Remove a NIC
`virsh attach-device DOMAIN device.xml --persistent` | Attach any device from XML
`virsh change-media DOMAIN sda --eject` | Eject a CD (target name from `domblklist`)
`virsh change-media DOMAIN sda /path/new.iso --insert` | Insert an ISO
`virsh blockresize DOMAIN vda 40G` | Grow a disk while the guest runs. Resize the partition in the guest afterwards
`virsh console DOMAIN` | See Power and Lifecycle

## Networks
COMMAND | DESCRIPTION
---|---
`virsh net-list --all` | Virtual networks and whether they are active and autostarted
`virsh net-info default` | State, autostart and bridge name
`virsh net-dumpxml default` | Network XML
`virsh net-start default` | Start the network
`virsh net-autostart default` | Start it at host boot (`--disable` to undo)
`virsh net-define FILE.xml` | Define a network from XML
`virsh net-edit NETWORK` | Edit the definition
`virsh net-destroy NETWORK` | Stop the network (existing guests lose connectivity)
`virsh net-undefine NETWORK` | Remove the definition
`virsh net-dhcp-leases default` | Current DHCP leases (guest IPs)
`virsh net-update NETWORK add ip-dhcp-host "<host mac='MAC' name='HOST' ip='192.168.122.50'/>" --live --config` | Add a static DHCP reservation. Form is `net-update NETWORK COMMAND SECTION XML` (the example element syntax is unverified)

A NAT network definition looks like this. The `default` network normally uses `192.168.122.0/24`.

```xml
<network>
  <name>labnet</name>
  <forward mode='nat'/>
  <bridge name='virbr10' stp='on' delay='0'/>
  <ip address='192.0.2.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.0.2.100' end='192.0.2.200'/>
    </dhcp>
  </ip>
</network>
```

To put guests on the LAN, create a host bridge (for example with [Netplan](netplan.md)) and use `--network bridge=br0`. A bridged guest talks to the LAN directly; the NAT network does not.

## Storage Pools and Volumes
COMMAND | DESCRIPTION
---|---
`virsh pool-list --all` | Pools and their state
`virsh pool-info POOL` | Capacity and allocation (`--bytes` for exact figures)
`virsh pool-dumpxml POOL` | Pool XML
`virsh pool-define-as POOL dir --target /srv/vms` | Define a directory pool
`virsh pool-build POOL` | Create the target directory or format the backing store
`virsh pool-start POOL` | Activate the pool
`virsh pool-autostart POOL` | Activate at host boot
`virsh pool-refresh POOL` | Rescan after files change outside libvirt
`virsh pool-destroy POOL` | Deactivate. Does not delete data
`virsh pool-undefine POOL` | Remove the definition
`virsh vol-list POOL --details` | Volumes with type, capacity and allocation
`virsh vol-create-as POOL NAME 20G --format qcow2` | New volume
`virsh vol-create-as POOL NAME 20G --format qcow2 --backing-vol BASE.qcow2 --backing-vol-format qcow2` | New volume backed by a base image
`virsh vol-info NAME --pool POOL` | Capacity, allocation, type (`--bytes`, `--physical`)
`virsh vol-path NAME --pool POOL` | Host path of the volume
`virsh vol-clone NAME NEWNAME --pool POOL` | Copy a volume
`virsh vol-resize NAME 40G --pool POOL` | Grow a volume. `--delta` adds, `--shrink` shrinks. Shrinking destroys data beyond the new size
`virsh vol-upload NAME FILE --pool POOL` | Upload a local file into a volume
`virsh vol-delete NAME --pool POOL` | Delete a volume. Destructive

Other pool types (`fs`, `netfs`, `logical`, `disk`, `iscsi`, `scsi`, `zfs` and more) take extra `--source-*` options; see `man virsh` under `pool-create-as`. A directory pool on [LVM](lvm.md), [ZFS](zfs.md) or NFS-mounted storage ([NFS](nfs.md)) is the simplest way to place images on a specific disk.

```bash
sudo mkdir -p /srv/vms
virsh pool-define-as vmstore dir --target /srv/vms
virsh pool-build vmstore
virsh pool-start vmstore
virsh pool-autostart vmstore
```

## Snapshots
Internal snapshots need qcow2 disks. `--disk-only` makes external snapshots. Snapshot metadata is stored by libvirt, so `undefine` needs `--snapshots-metadata` when snapshots exist.

COMMAND | DESCRIPTION
---|---
`virsh snapshot-create-as DOMAIN SNAP "DESCRIPTION"` | Take a snapshot with a name and description
`virsh snapshot-create-as DOMAIN SNAP --disk-only --atomic` | External disk-only snapshot (guest keeps running)
`virsh snapshot-create-as DOMAIN SNAP --disk-only --quiesce` | Ask the guest agent to freeze filesystems first
`virsh snapshot-create-as DOMAIN SNAP --print-xml` | Show the XML without creating anything
`virsh snapshot-list DOMAIN` | List snapshots
`virsh snapshot-list DOMAIN --tree` | Show parent and child relationships
`virsh snapshot-info DOMAIN SNAP` | Details of one snapshot (`--current` for the latest)
`virsh snapshot-dumpxml DOMAIN SNAP` | Snapshot XML
`virsh snapshot-revert DOMAIN SNAP` | Roll back. Discards changes since the snapshot
`virsh snapshot-revert DOMAIN SNAP --running` | Revert and leave the guest running
`virsh snapshot-delete DOMAIN SNAP` | Delete the snapshot. Changes merge into the children
`virsh snapshot-delete DOMAIN SNAP --children` | Delete it and all its children
`virsh snapshot-delete DOMAIN SNAP --metadata` | Delete libvirt's record only, keep the data
`virsh blockcommit DOMAIN vda --active --pivot --verbose` | Merge an external overlay back into its base and pivot to it (see `man virsh` for the full workflow)

## qemu-img
Never run `qemu-img` against an image that a running VM is using. Format and size options go in `-f`, `-O` and `-o`. Run `qemu-img create -f qcow2 -o help` for the options of a format.

COMMAND | DESCRIPTION
---|---
`qemu-img create -f qcow2 DISK.qcow2 20G` | New thin-provisioned qcow2 image
`qemu-img create -f qcow2 -o preallocation=metadata DISK.qcow2 20G` | Preallocate metadata for better speed
`qemu-img create -f qcow2 -b BASE.qcow2 -F qcow2 OVERLAY.qcow2` | Overlay image that records changes against a read-only base
`qemu-img info DISK.qcow2` | Format, virtual size, disk usage, backing file, snapshots
`qemu-img info --backing-chain DISK.qcow2` | Show the whole backing chain
`qemu-img info --output=json DISK.qcow2` | Machine-readable output
`qemu-img check DISK.qcow2` | Check for corruption (`-r leaks` or `-r all` to repair)
`qemu-img convert -p -f raw -O qcow2 IN.img OUT.qcow2` | Convert format with progress
`qemu-img convert -O qcow2 -c IN.qcow2 OUT.qcow2` | Compress while converting
`qemu-img convert -f vmdk -O qcow2 IN.vmdk OUT.qcow2` | Convert a VMware or VirtualBox disk
`qemu-img convert -f vdi -O qcow2 IN.vdi OUT.qcow2` | Convert a VirtualBox VDI
`qemu-img convert -O raw IN.qcow2 OUT.img` | Convert to raw
`qemu-img resize DISK.qcow2 +10G` | Grow by 10 GiB. Resize the partition and filesystem in the guest afterwards
`qemu-img resize --shrink DISK.qcow2 10G` | Shrink. Destructive if the data does not fit
`qemu-img rebase -b NEWBASE.qcow2 -F qcow2 OVERLAY.qcow2` | Change the backing file (`-u` to only change the pointer)
`qemu-img commit DISK.qcow2` | Merge an overlay into its backing file
`qemu-img snapshot -l DISK.qcow2` | List internal snapshots
`qemu-img snapshot -c NAME DISK.qcow2` | Create an internal snapshot
`qemu-img snapshot -a NAME DISK.qcow2` | Apply (revert to) a snapshot
`qemu-img snapshot -d NAME DISK.qcow2` | Delete a snapshot
`qemu-img compare A.qcow2 B.qcow2` | Compare the content of two images
`qemu-img measure -O qcow2 DISK.img` | Required size if converted to another format
`qemu-img map DISK.qcow2` | Show which ranges are allocated
`qemu-img bench DISK.img` | Simple I/O benchmark (`-w` makes it a write test)

## virt-manager and virt-viewer
virt-manager is the GTK desktop app. It connects to local or remote libvirt (File, Add Connection), creates guests with a wizard, and edits hardware under Show virtual hardware details.

COMMAND | DESCRIPTION
---|---
`virt-manager` | Open the manager
`virt-manager -c qemu:///system` | Open with a given connection
`virt-manager --show-domain-console DOMAIN` | Open a guest console directly
`virt-manager --show-domain-editor DOMAIN` | Open the hardware editor
`virt-manager --show-domain-performance DOMAIN` | Open the performance view
`virt-manager --show-host-summary` | Open host details (also holds Virtual Networks and Storage tabs)
`virt-manager --no-fork` | Stay in the foreground
`virt-viewer -c qemu:///system DOMAIN` | Open a lightweight console window for one guest
`virt-viewer -c qemu:///system -w -r DOMAIN` | Wait for the guest to start and reconnect if it restarts
`virt-viewer -c qemu+ssh://USER@HOST/system DOMAIN` | View a guest on a remote host over SSH

Remote management uses connection URIs, for example `virsh -c qemu+ssh://USER@HOST/system list --all`. SSH keys are covered in [OpenSSH Cheat-Sheet](../tools/openssh.md).

## Troubleshooting
SYMPTOM | FIX
---|---
`failed to connect to the hypervisor` or permission denied | Use `-c qemu:///system` or `sudo`, check `libvirtd` is running, and add your user to the `libvirt` group
`virsh list` shows nothing but VMs exist | You are on `qemu:///session`. Use `-c qemu:///system`
Network `default` not active | `virsh net-start default` then `virsh net-autostart default`
Guest has no IP | `virsh net-dhcp-leases default`, then `virsh domifaddr DOMAIN --source agent`. Check the guest requests DHCP
`virsh console` is blank | The guest needs `console=ttyS0` and a serial getty enabled
Cannot undefine a UEFI guest | Add `--nvram`
Cannot undefine, has snapshots | Add `--snapshots-metadata`
Disk image permission denied | Images should sit in a pool the daemon can read (the default is `/var/lib/libvirt/images`). AppArmor or SELinux may block other paths ([SELinux and AppArmor](selinux-apparmor.md))
Snapshot fails on a raw disk | Internal snapshots need qcow2. Use `--disk-only` for external snapshots
Guest slow | Use `--cpu host-passthrough`, virtio disk and NIC, and check KVM is in use with `virsh dumpxml DOMAIN`
Logs | `/var/log/libvirt/qemu/DOMAIN.log` and `journalctl -u libvirtd` (paths unverified)

## See Also
- [VirtualBox](../tools/virtualbox.md)
- [Hypervisors Compared](../infra/hypervisor-comparison.md)
- [Proxmox VE Overview and Install](../proxmox/proxmox-overview.md)
- [Storage and Filesystems](storage-and-filesystems.md)
- [LVM](lvm.md)
- [Netplan](netplan.md)
- [SELinux and AppArmor](selinux-apparmor.md)
- [OpenSSH Cheat-Sheet](../tools/openssh.md)
