# Group Policy
Group Policy applies settings to domain users and computers from Group Policy Objects (GPOs) linked to sites, domains and OUs. This sheet covers refreshing and reporting on policy, the GroupPolicy PowerShell module, the ADMX central store and troubleshooting. See [[active-directory]] for the directory itself, [[windows-networking]] for DNS and connectivity problems that break policy, and [[windows-updates]] for update policy.

Documentation: [Group Policy overview](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/hh831791(v=ws.11)), [GroupPolicy module](https://learn.microsoft.com/en-us/powershell/module/grouppolicy/)

## How Policy Applies
- Order (LSDOU): **L**ocal, **S**ite, **D**omain, **OU** (nested OUs applied parent to child). The last applied wins on conflict.
- Computer settings apply at startup, user settings at logon, then both refresh in the background (default every 90 minutes with a random 0 to 30 minute offset; domain controllers every 5 minutes).
- **Enforced** links cannot be overridden by lower levels. **Block Inheritance** on an OU stops non-enforced GPOs from above.
- **Security filtering** (Authenticated Users by default) decides who the GPO applies to. The account must also have Read permission, so keep Read for `Authenticated Users` or `Domain Computers` when you narrow the apply list.
- **WMI filters** limit a GPO by a WMI query (for example an OS version).
- **Loopback processing** applies the computer's user settings regardless of who logs on (kiosks, RDS hosts).

## Refresh and Report
COMMAND | DESCRIPTION
---|---
`gpupdate /force` | Reapply all policy, computer and user
`gpupdate /target:computer /force` | Computer policy only (`/target:user` for user)
`gpupdate /force /boot` | Reapply and restart if a setting needs a reboot
`gpupdate /force /logoff` | Reapply and log off if a setting needs it
`gpresult /r` | Summary of applied GPOs for the current user and computer
`gpresult /r /scope computer` | Computer settings only (needs an elevated prompt)
`gpresult /r /scope user /user <DOMAIN>\<USER>` | Another user's results (admin)
`gpresult /h report.html` | Full HTML report
`gpresult /h report.html /f` | Overwrite an existing file
`gpresult /s <COMPUTER> /h report.html` | Report for a remote computer
`gpresult /v` | Verbose text output
`gpresult /x report.xml` | XML report

Run `gpresult` from an **elevated** prompt to include computer settings. Without elevation the computer section is empty.

## GroupPolicy PowerShell Module
Install with RSAT: `Add-WindowsCapability -Online -Name Rsat.GroupPolicy.Management.Tools~~~~0.0.1.0` (Windows 10/11) or `Install-WindowsFeature GPMC` (Server).

COMMAND | DESCRIPTION
---|---
`Get-GPO -All` | List every GPO
`Get-GPO -Name "<GPO>"` | One GPO with status and timestamps
`New-GPO -Name "<GPO>" -Comment "<TEXT>"` | Create a GPO
`New-GPLink -Name "<GPO>" -Target "OU=Workstations,DC=<DOMAIN>,DC=<TLD>" -LinkEnabled Yes` | Link to an OU (add `-Enforced Yes` to enforce)
`Set-GPLink -Name "<GPO>" -Target "<DN>" -LinkEnabled No` | Disable a link without deleting it
`Remove-GPLink -Name "<GPO>" -Target "<DN>"` | Remove a link
`Get-GPInheritance -Target "<OU-DN>"` | GPOs linked and inherited at a container
`Set-GPInheritance -Target "<OU-DN>" -IsBlocked Yes` | Block inheritance
`Set-GPRegistryValue -Name "<GPO>" -Key "HKLM\Software\Policies\<VENDOR>" -ValueName <NAME> -Type DWord -Value 1` | Set a registry-based policy
`Get-GPRegistryValue -Name "<GPO>" -Key "HKLM\Software\Policies\<VENDOR>"` | Read a policy value
`Set-GPPermission -Name "<GPO>" -TargetName "<GROUP>" -TargetType Group -PermissionLevel GpoApply` | Security filtering (`GpoRead`, `GpoApply`, `GpoEdit`)
`Get-GPOReport -Name "<GPO>" -ReportType Html -Path .\gpo.html` | Settings report (`-All` for every GPO)
`Get-GPResultantSetOfPolicy -Computer <PC> -User <DOMAIN>\<USER> -ReportType Html -Path .\rsop.html` | Resultant set of policy for a computer and user
`Backup-GPO -All -Path D:\GPOBackup` | Back up all GPOs
`Restore-GPO -Name "<GPO>" -Path D:\GPOBackup` | Restore one
`Import-GPO -BackupGpoName "<GPO>" -TargetName "<NEW>" -Path D:\GPOBackup -CreateIfNeeded` | Import a backup into another GPO
`Copy-GPO -SourceName "<A>" -TargetName "<B>"` | Duplicate a GPO
`Rename-GPO -Name "<OLD>" -TargetName "<NEW>"` | Rename
`Remove-GPO -Name "<GPO>"` | Delete (unlink first)
`Invoke-GPUpdate -Computer <PC> -Force` | Push a refresh to a remote computer (needs firewall rules for remote scheduled tasks)

Unlinked GPOs are easy to find: `Get-GPO -All | Where-Object { ($_ | Get-GPOReport -ReportType Xml) -notmatch '<LinksTo>' }`.

## GPMC and Related Consoles
TOOL | OPEN WITH | USE
---|---|---
Group Policy Management (GPMC) | `gpmc.msc` | Create, link, back up, model and view GPOs
Group Policy Management Editor | Right click a GPO, **Edit** | Change settings
Group Policy Modeling | GPMC, **Group Policy Modeling** | "What if" for a user, computer, OU or site
Group Policy Results | GPMC, **Group Policy Results** | Wizard for a real machine and user
Local Group Policy Editor | `gpedit.msc` | Local policy (not on Windows Home)
Resultant Set of Policy | `rsop.msc` | Local read-only view of applied settings
Local Security Policy | `secpol.msc` | Security settings subset
`secedit /export /cfg sec.cfg` | | Export current local security settings

## ADMX Central Store
ADMX files define the settings you see in the editor. By default each admin PC reads its own local copy, so different machines show different settings. A **central store** on SYSVOL gives every admin the same templates.

PATH | CONTENTS
---|---
`C:\Windows\PolicyDefinitions` | Local ADMX (`*.admx`) and `en-US\*.adml` language files
`\\<DOMAIN-FQDN>\SYSVOL\<DOMAIN-FQDN>\Policies\PolicyDefinitions` | Central store (replicates to all DCs)

Create or update it by copying the templates from a current Windows build or the downloaded ADMX package:
```powershell
$dom = $env:USERDNSDOMAIN
$store = "\\$dom\SYSVOL\$dom\Policies\PolicyDefinitions"
New-Item -ItemType Directory -Path $store -Force | Out-Null
Copy-Item "C:\Windows\PolicyDefinitions\*" -Destination $store -Recurse -Force
```
- Keep the `PolicyDefinitions` folder and the `en-US` (or your language) subfolder together.
- Download templates for third parties (Microsoft Edge, Office, Chrome, LAPS in the OS) and drop their `.admx` and `.adml` files in.
- Update the store whenever you introduce a newer Windows version.
- Check SYSVOL replication is healthy first (`dcdiag /test:netlogons`, `repadmin /replsummary`; see [[active-directory]]).

## Troubleshooting
SYMPTOM | CHECK
---|---
Policy not applying | `gpresult /h report.html` and read "Denied GPOs" and its reason (security filtering, WMI filter, disabled link, empty)
Computer settings missing | Run `gpresult` elevated
Slow logon | Event ID 1503 and 1500 in `Applications and Services Logs > Microsoft > Windows > GroupPolicy > Operational`; look for slow links or large scripts
"The processing of Group Policy failed" (Event 1129) | Network or DNS problem at startup: confirm DNS points at a DC, `nltest /dsgetdc:<DOMAIN>`, `Test-ComputerSecureChannel`
Machine in wrong OU | `Get-ADComputer <PC> \| Select DistinguishedName`
GPO linked but nothing happens | Version mismatch between AD and SYSVOL: compare in GPMC under **Details**; check replication
Setting is a preference, not policy | Group Policy Preferences (drive maps, printers, registry items) are item-level targeted and can be reapplied or removed; check the item's "Apply once" and targeting
Different settings on each admin PC | Create the central store
Old or deleted setting persists | Policy "tattoos" do not apply to preferences or non-policy keys; remove with a preference item or script
Group membership not taking effect | Log off and on (users) or reboot (computers) so the access token refreshes: `whoami /groups`

Useful event logs and commands:
```powershell
Get-WinEvent -LogName "Microsoft-Windows-GroupPolicy/Operational" -MaxEvents 30 |
  Select TimeCreated, Id, LevelDisplayName, Message
gpresult /h "$env:TEMP\gp.html" /f; Start-Process "$env:TEMP\gp.html"
```
The Operational event log and `gpresult` are usually enough. See [[windows-troubleshooting]] for more event log queries, and [[windows-dns-server]] for DNS records that machines need to find a DC.

## Good Practice
- One purpose per GPO and descriptive names; avoid editing the **Default Domain Policy** except for password, lockout and Kerberos settings.
- Disable the unused half (user or computer configuration) of a GPO to speed processing.
- Test in a pilot OU before wide linking; use security filtering or WMI filters sparingly.
- Back up with `Backup-GPO -All` before changes, and document each GPO's comment field.
- Link at OU level where possible, not the domain root.
- Do not store passwords in Group Policy Preferences (old cpassword values are trivially decrypted).

## Not Verified
Commands were written from the Microsoft documentation and not executed against a domain. Event IDs and default refresh intervals are from documentation and may differ by Windows version.
