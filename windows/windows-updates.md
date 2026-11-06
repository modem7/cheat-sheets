# Windows Updates
Manage Windows Update from the command line with the `PSWindowsUpdate` module ([PowerShell Cheat-Sheet](powershell.md)). Run in an elevated session.

---
## PowerShell
### Install the Module
```powershell
Install-Module -Name PSWindowsUpdate
```
### List all Commands
```powershell
Get-Command -module PSWindowsUpdate
```

### Common Tasks
COMMAND | DESCRIPTION
---|---
`Get-WindowsUpdate` | List available updates
`Install-WindowsUpdate -AcceptAll` | Install all available updates
`Install-WindowsUpdate -AcceptAll -AutoReboot` | Install and reboot if required
`Install-WindowsUpdate -KBArticleID KB5000000` | Install a specific update
`Get-WUHistory` | Update history
`Get-WURebootStatus` | Is a reboot pending?
`Hide-WindowsUpdate -KBArticleID KB5000000` | Hide an update
`Get-WindowsUpdate -ComputerName <SERVER> -AcceptAll -Install` | Update a remote machine (see [PowerShell Remote Access](powershell-remote.md))
`Get-WUInstall` | Older alias of the install command

## Built-in Tools
COMMAND | DESCRIPTION
---|---
`usoclient StartScan` | Trigger a scan
`wuauclt /detectnow` | Legacy scan trigger
`Get-HotFix` | Installed updates
`sconfig` | Server Core menu (option 6 for updates)
`DISM /Online /Cleanup-Image /RestoreHealth` | Repair the component store
`sfc /scannow` | Check and repair system files
`net stop wuauserv && net stop bits` | Stop update services (used when resetting the cache)
