# WSL Cheat-Sheet
Windows Subsystem for Linux. Commands run in PowerShell ([[powershell]]) unless noted.

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

## Networking
Newer WSL builds support `networkingMode=mirrored`, which removes most port-forwarding needs. Use the manual method below for NAT mode.
### Port Forwarding
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
`code .` | Open in VS Code ([[vscode]])
`wslpath -w <PATH>` / `wslpath -u 'C:\x'` | Convert between Linux and Windows paths
`\\wsl$\<DISTRO>\home\<USER>` | Reach Linux files from Windows

## Linux desktop in WSL2

With WSL2 it's possible to install and run a Linux desktop environment (XFCE). A tutorial on how
to implement that, can be found [here](https://thedatabaseme.de/2022/05/15/shorty-running-xfce-linux-desktop-on-wsl2/).
