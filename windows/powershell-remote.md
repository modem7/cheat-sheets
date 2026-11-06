# PowerShell Remote Access
PowerShell Remoting ([[powershell]]) runs commands on other machines over WinRM (HTTP 5985, HTTPS 5986) or SSH (PowerShell 7+, see [[openssh]]).

---
## Enable Remoting on the Target
```powershell
Enable-PSRemoting -Force
```
Workgroup (non-domain) machines also need the client to trust the target:
```powershell
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "<SERVER-IP>" -Force
```

## Open a New Remote Session
```powershell
Enter-PSSession -ComputerName <SERVER> -Credential <USERNAME>
```
Leave it with `Exit-PSSession`.

## Commands
COMMAND | DESCRIPTION
---|---
`Enter-PSSession -ComputerName <SERVER> -Credential (Get-Credential)` | Interactive session
`Enter-PSSession -HostName <HOST> -UserName <USER>` | Interactive session over SSH (PowerShell 7+)
`Invoke-Command -ComputerName <SERVER> -ScriptBlock { Get-Service }` | Run a command once
`Invoke-Command -ComputerName <S1>,<S2> -ScriptBlock { hostname }` | Run on many machines in parallel
`Invoke-Command -ComputerName <SERVER> -FilePath .\script.ps1` | Run a local script remotely
`$s = New-PSSession -ComputerName <SERVER>` | Create a reusable session
`Invoke-Command -Session $s -ScriptBlock { $x = 1 }` | Reuse the session (keeps state)
`Copy-Item -Path .\file.txt -Destination C:\ -ToSession $s` | Copy a file to the remote machine
`Copy-Item -Path C:\file.txt -Destination .\ -FromSession $s` | Copy a file back
`Get-PSSession` | List sessions
`Remove-PSSession $s` | Close a session
`Test-WSMan <SERVER>` | Check WinRM is reachable
`Invoke-Command -ComputerName <SERVER> -ScriptBlock { param($n) "Hi $n" } -ArgumentList "Bob"` | Pass arguments
`Invoke-Command -ComputerName <SERVER> -ScriptBlock { "$using:LocalVar" }` | Use a local variable with `$using:`

## Troubleshooting
- Verify the service: `Get-Service WinRM`
- Check listeners: `winrm enumerate winrm/config/listener`
- Firewall: `Get-NetFirewallRule -DisplayGroup "Windows Remote Management"`
- Use HTTPS (5986) with a valid certificate across untrusted networks.
