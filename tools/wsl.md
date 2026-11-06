# WSL Cheat-Sheet
Windows Subsystem for Linux. Commands run in PowerShell ([PowerShell Cheat-Sheet](../windows/powershell.md)) unless noted.

## Manage Distros
COMMAND | DESCRIPTION
---|---
`wsl --list --verbose` | Installed distros, state and WSL version
`wsl --list --online` | Distros available to install
`wsl --install -d Ubuntu` | Install a distro
`wsl --set-default <DISTRO>` | Default distro
`wsl --set-version <DISTRO> 2` | Convert to WSL 2
`wsl --set-default-version 2` | New distros use WSL 2
`wsl -d <DISTRO> -u root` | Start as root
`wsl --terminate <DISTRO>` | Stop one distro
`wsl --shutdown` | Stop everything (needed after editing `.wslconfig`)
`wsl --unregister <DISTRO>` | Delete a distro and its data
`wsl --update` | Update the WSL kernel

## Backup and Restore WSL
### Backup a WSL Distro
```powershell
wsl --export (distribution) (filename.tar)
```
### Restore a WSL Distro from Backup
```powershell
wsl --import (distribution) (install location) (file location and filename)
```

## Symbolic Links
Replace `<WINUSER>` with your Windows user name.
### Link .ssh folder
```bash
ln -s /mnt/c/Users/<WINUSER>/.ssh ~/.ssh
```

### Link .kube folder
```bash
ln -s /mnt/c/Users/<WINUSER>/.kube ~/.kube
```
SSH insists on strict key permissions, which NTFS mounts do not provide unless `metadata` is enabled (below). Copying keys into `~/.ssh` is often simpler.

## File Permissions
Advanced settings configuration in WSL: [WSL Config Parameters](https://docs.microsoft.com/en-us/windows/wsl/wsl-config)

**Example /etc/wsl.conf** (per distro, run `wsl --shutdown` to apply)
```
[automount]
enabled = true
options = "metadata,uid=1000,gid=1000,umask=077,fmask=11,case=off"
mountFsTab = true

[interop]
enabled = false
appendWindowsPath = false
```

**Example %UserProfile%\\.wslconfig** (global, WSL 2)
```
[wsl2]
memory=8GB
processors=4
swap=2GB
networkingMode=mirrored
```

## Resource Limits (`.wslconfig`)
WSL 2 runs in one lightweight VM, shared by all distros. Limits go in `%UserProfile%\.wslconfig` on Windows (not inside the distro). Run `wsl --shutdown` and wait a few seconds for changes to apply.

```ini
[wsl2]
memory=8GB                 # default: 50% of Windows RAM
processors=4               # default: all logical processors
swap=4GB                   # 0 disables swap
swapFile=D:\\wsl\\swap.vhdx
vmIdleTimeout=60000        # ms before the idle VM stops
localhostForwarding=true   # NAT mode: reach WSL services at localhost
nestedVirtualization=true  # run KVM or Docker in WSL (Windows 11)

[experimental]
autoMemoryReclaim=gradual  # return unused cache to Windows (or dropcache, disabled)
sparseVhd=true             # new distro disks shrink automatically
```
OPTION | DESCRIPTION
---|---
`memory` / `processors` / `swap` | Caps for the VM (`vmmem` or `vmmemWSL` in Task Manager)
`autoMemoryReclaim` | Give cached memory back to Windows instead of holding it
`sparseVhd` | Disk image releases freed space (applies to newly created distros; convert existing ones below)
`kernel` | Path to a custom kernel
`kernelCommandLine` | Extra kernel parameters
`guiApplications` | Set `false` to disable WSLg

Disk and memory housekeeping:
COMMAND | DESCRIPTION
---|---
`wsl --manage <DISTRO> --set-sparse true` | Make an existing distro's disk sparse so it reclaims space (shut it down first)
`wsl --manage <DISTRO> --resize 200GB` | Grow the virtual disk (recent WSL versions)
`wsl --shutdown` then `Optimize-VHD -Path <PATH>\ext4.vhdx -Mode Full` | Compact the disk (Hyper-V module, admin PowerShell)
`wsl --system -d <DISTRO> df -h` | Check disk use inside the VM
`wsl --status` / `wsl --version` | WSL settings and component versions
`sudo sh -c 'echo 1 > /proc/sys/vm/drop_caches'` | Drop the Linux page cache (inside the distro, if memory looks stuck)

## systemd in WSL
Recent WSL versions (check `wsl --version`; needs WSL 0.67.6 or newer from the Store build) can run systemd as PID 1, so `systemctl`, services and snap work. Enable it per distro in `/etc/wsl.conf` (inside Linux):
```ini
[boot]
systemd=true
command="service cron start"   # optional: run a command at distro start
```
Then restart the distro from PowerShell: `wsl --shutdown`.

COMMAND | DESCRIPTION
---|---
`systemctl is-system-running` | Check systemd is up (`running` or `degraded`)
`systemctl list-units --failed` | Failed units (a few failures in WSL are normal)
`sudo systemctl enable --now docker` | Start Docker or any service at distro start ([Docker](../docker/docker.md))
`ps -p 1 -o comm=` | Shows `systemd` when enabled
`systemctl --user status` | User services

Notes: the distro still stops when its last terminal closes and the idle timer elapses; services only run while the VM runs. Keep it alive with `wsl -d <DISTRO> --exec sleep infinity` in a hidden task, or a scheduled task at logon. Newer Ubuntu images enable systemd by default. See [Linux Basics](../linux/linuxbasics.md) for systemd commands.

## Networking Modes
Set the mode in `.wslconfig` under `[wsl2]` with `networkingMode=`.

MODE | BEHAVIOUR
---|---
`NAT` (default) | WSL has its own virtual subnet and IP, which changes on restart. Windows reaches WSL at `localhost` when `localhostForwarding=true`. Other LAN machines cannot reach it without port forwarding
`mirrored` | WSL mirrors the Windows network interfaces: same IP as the host, IPv6 supported, VPN friendly, LAN machines reach WSL services directly, and `127.0.0.1` works both ways. Needs Windows 11 22H2 or later
`virtioproxy` | Used when NAT cannot be used (some VPN or restricted setups); shares the host network through a proxy
`bridged` | Deprecated; use mirrored

Companion settings:
```ini
[wsl2]
networkingMode=mirrored
dnsTunneling=true      # resolve names through Windows, helps with VPN and split DNS
autoProxy=true         # use the Windows proxy settings
firewall=true          # apply Windows firewall rules to WSL traffic

[experimental]
hostAddressLoopback=true   # NAT mode: reach Windows from WSL via the host IP
```
In mirrored mode inbound connections from the LAN are filtered by the **Hyper-V firewall**. Allow them in an elevated PowerShell:
```powershell
Set-NetFirewallHyperVVMSetting -Name '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -DefaultInboundAction Allow
# or open only one port
New-NetFirewallHyperVRule -Name "WSL-8080" -DisplayName "WSL 8080" -Direction Inbound -VMCreatorId '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -Protocol TCP -LocalPorts 8080
```
COMMAND | DESCRIPTION
---|---
`wsl hostname -I` | The distro's IP address (NAT mode)
`ip route show default` | Gateway inside WSL (NAT mode: this is the Windows host)
`cat /etc/resolv.conf` | DNS servers WSL uses
`ip addr show eth0` | Interface and IP
`Get-NetFirewallHyperVVMSetting -PolicyStore ActiveStore` | Current Hyper-V firewall state for WSL
`curl.exe http://localhost:8080` | Test a WSL service from Windows

Windows networking commands are in [Windows Networking](../windows/windows-networking.md). If DNS breaks, set `generateResolvConf = false` under `[network]` in `/etc/wsl.conf` and write your own `/etc/resolv.conf`, or use `dnsTunneling`. If you see a `/etc/resolv.conf` that points at a stale IP, run `wsl --shutdown`.

### Port Forwarding (NAT mode)
**Find IP Address**
```powershell
bash.exe -c "ifconfig eth0 | grep 'inet '"
```

**Add PortForwarding** (use the WSL IP found above as `$remoteaddr`)
```powershell
$port = 8080
$remoteaddr = "172.20.10.2"

netsh interface portproxy add v4tov4 listenport=$port connectport=$port connectaddress=$remoteaddr

netsh advfirewall firewall add rule name=$port dir=in action=allow protocol=TCP localport=$port
```

**Delete PortForwarding**
```PowerShell
$port = 8080

netsh interface portproxy delete v4tov4 listenport=$port
netsh advfirewall firewall delete rule name=$port
```

**Show PortForwardings**
```powershell
netsh interface portproxy show v4tov4
```

## Useful Interop
COMMAND | DESCRIPTION
---|---
`explorer.exe .` | Open the current Linux folder in Explorer
`code .` | Open in VS Code ([VSCode (Visual Studio Code)](vscode.md))
`wslpath -w <PATH>` / `wslpath -u 'C:\x'` | Convert between Linux and Windows paths
`\\wsl$\<DISTRO>\home\<USER>` | Reach Linux files from Windows

## Linux desktop in WSL2

With WSL2 it's possible to install and run a Linux desktop environment (XFCE). A tutorial on how
to implement that, can be found [here](https://thedatabaseme.de/2022/05/15/shorty-running-xfce-linux-desktop-on-wsl2/).

## Not Verified
The resource, systemd and networking sections were written from the Microsoft WSL documentation and not executed. Options such as `autoMemoryReclaim`, `sparseVhd`, `dnsTunneling` and `wsl --manage --resize` need a recent WSL release (`wsl --update`).
