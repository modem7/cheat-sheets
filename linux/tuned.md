# tuned
`tuned` is a daemon that applies system tuning profiles (CPU governor, sysctl, disk and network settings) on Linux. It is standard on RHEL and Fedora and also packaged for Debian and Ubuntu. Use it to switch a host between balanced, throughput and latency settings, and to set VM guest and host defaults.

Project: [tuned](https://github.com/redhat-performance/tuned)

## Install and Enable
COMMAND | DESCRIPTION
---|---
`sudo dnf install tuned` | RHEL, Fedora
`sudo systemctl enable --now tuned` | Start now and at boot
`tuned-adm active` | Current profile

On Debian and Ubuntu the packages are reported as `tuned`, `tuned-utils`, `tuned-ppd` and `tuned-gtk` (check `apt show tuned`, versions differ by release). tuned conflicts with `power-profiles-daemon` and `cpupower`, so disable those first. `tuned-ppd` provides a compatible interface for desktop power settings and also conflicts with `power-profiles-daemon`. The active profile is stored in `/etc/tuned/active_profile`.

## tuned-adm
COMMAND | DESCRIPTION
---|---
`tuned-adm list` | Available profiles
`tuned-adm active` | Active profile
`tuned-adm profile <NAME>` | Switch to a profile
`tuned-adm profile <A> <B>` | Merge several profiles (later ones win)
`tuned-adm profile_info [<NAME>]` | Describe a profile
`tuned-adm recommend` | Suggest a profile for this machine
`tuned-adm verify` | Check the system still matches the active profile (`-i` ignores errors)
`tuned-adm auto_profile` | Select the recommended profile
`tuned-adm profile_mode` | Show the profile mode
`tuned-adm off` | Turn tuning off

`recommend` uses `/etc/system-release-cpe` and `virt-what`.

## Built-in Profiles
PROFILE | USE
---|---
`balanced` | Default compromise between power and speed
`balanced-battery` | Balanced, for laptops on battery
`powersave` | Save power
`throughput-performance` | Servers, maximum throughput
`accelerator-performance` | Throughput tuned for accelerators
`latency-performance` | Low latency
`network-throughput` | Bulk network transfer
`network-latency` | Low network latency
`desktop` | Interactive desktops
`hpc-compute` | HPC workloads
`virtual-guest` | Inside a VM
`virtual-host` | On a hypervisor
`intel-sst` | Intel Speed Select
`optimize-serial-console` | Serial console responsiveness
`aws` | AWS instances

`virtual-guest` builds on `throughput-performance` with `vm.swappiness=30` and higher dirty page limits. `virtual-host` adds more aggressive dirty page writeback.

## VMs and Proxmox
There is no official Proxmox guidance. A sensible default, inferred from the profile descriptions, is `virtual-guest` in VMs and `virtual-host` on the hypervisor. Compare benchmarks before and after, because a profile that suits one workload can hurt another. See [Performance Troubleshooting](performance-troubleshooting.md).

## Custom Profiles
Put a profile in its own directory with a `tuned.conf`:

```ini
[main]
summary=Throughput with custom swappiness
include=throughput-performance

[sysctl]
vm.swappiness=10
```

LOCATION | NOTES
---|---
`/etc/tuned/profiles/<NAME>/tuned.conf` | Current upstream layout
`/etc/tuned/<NAME>/tuned.conf` | Older layout, still used by older releases
`/usr/lib/tuned/profiles` | Shipped profiles (do not edit)

The path differs between releases, so check `profile_dirs` in `tuned-main.conf` on your system.

- `include=` pulls in another profile.
- Each other section is a plugin, with optional `type=`, `devices=` and `replace=1`.
- Plugins include `audio`, `bootloader`, `cpu`, `disk`, `modules`, `mounts`, `net`, `script`, `scheduler`, `scsi_host`, `selinux`, `sysctl`, `sysfs`, `systemd`, `usb`, `video` and `vm`.
- A `[script]` section runs your script with `script=${i:PROFILE_DIR}/profile.sh`.

After editing, reload with `sudo tuned-adm profile <NAME>` or restart the service.

## Daemon Config and Logs
`/etc/tuned/tuned-main.conf` defaults, as read from the repository:

SETTING | DEFAULT
---|---
`daemon` | `1`
`dynamic_tuning` | `0`
`update_interval` | `10`
`log_file_count` | `2`
`profile_dirs` | `/usr/lib/tuned/profiles,/etc/tuned/profiles`

The default log is `/var/log/tuned/tuned.log`. Dynamic tuning is off by default.

## Not Verified
Exact option syntax for the `[bootloader]` and `[cpu]` plugins, `tuned-ppd` usage, and the custom profile path on your distribution.

## See Also
- [Performance Troubleshooting](performance-troubleshooting.md)
- [systemd](systemd.md)
- [Proxmox VE Overview and Install](../proxmox/proxmox-overview.md)
