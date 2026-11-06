# Active Directory
Managing Active Directory Domain Services with the PowerShell `ActiveDirectory` module, plus the classic `dcdiag`, `repadmin` and `ntdsutil` tools for domain controller health. Run from a domain-joined machine with RSAT or on a domain controller, in an elevated PowerShell ([PowerShell Cheat-Sheet](powershell.md)). Related: [Group Policy](group-policy.md), [Windows DNS Server](windows-dns-server.md), [Windows Networking](windows-networking.md), [PowerShell Remote Access](powershell-remote.md).

Documentation: [ActiveDirectory module](https://learn.microsoft.com/en-us/powershell/module/activedirectory/)

## Setup
COMMAND | DESCRIPTION
---|---
`Add-WindowsCapability -Online -Name Rsat.ActiveDirectory.DS-LDS.Tools~~~~0.0.1.0` | Install the AD module on Windows 10/11
`Install-WindowsFeature RSAT-AD-PowerShell` | Install it on Windows Server
`Import-Module ActiveDirectory` | Load the module (usually automatic)
`Get-Command -Module ActiveDirectory` | List all AD cmdlets
`Get-ADDomain` | Domain info: name, functional level, FSMO holders
`Get-ADForest` | Forest info: domains, schema master, naming master
`Get-ADDomainController -Filter *` | All domain controllers
`Get-ADDomainController -Discover` | Which DC would a client find
`Get-ADRootDSE` | Naming contexts and server info

## Users
COMMAND | DESCRIPTION
---|---
`Get-ADUser <SAMACCOUNT>` | Basic user object
`Get-ADUser <SAMACCOUNT> -Properties *` | Every attribute
`Get-ADUser -Identity <SAMACCOUNT> -Properties LastLogonDate,PasswordLastSet,Enabled,MemberOf` | Chosen attributes
`New-ADUser -Name "<FULL NAME>" -SamAccountName <SAM> -UserPrincipalName <SAM>@<DOMAIN> -Path "OU=Users,DC=<DOMAIN>,DC=<TLD>" -AccountPassword (Read-Host -AsSecureString "Password") -Enabled $true` | Create a user (password prompted, never typed in the script)
`Set-ADUser <SAM> -Title "Engineer" -Department "IT"` | Change attributes
`Disable-ADAccount -Identity <SAM>` / `Enable-ADAccount -Identity <SAM>` | Disable or enable
`Unlock-ADAccount -Identity <SAM>` | Unlock a locked-out account
`Move-ADObject -Identity "<DN>" -TargetPath "OU=Disabled,DC=<DOMAIN>,DC=<TLD>"` | Move an object to another OU
`Remove-ADUser <SAM> -Confirm` | Delete a user
`Get-ADUser <SAM> -Properties MemberOf \| Select-Object -ExpandProperty MemberOf` | Groups a user belongs to (distinguished names)
`Search-ADAccount -LockedOut` | All locked-out accounts
`Search-ADAccount -AccountDisabled -UsersOnly` | Disabled users
`Search-ADAccount -PasswordNeverExpires -UsersOnly` | Accounts with a non-expiring password
`Search-ADAccount -AccountInactive -TimeSpan 90.00:00:00 -UsersOnly` | Not logged on for 90 days
`Search-ADAccount -PasswordExpired` | Expired passwords

## Password Reset
```powershell
Set-ADAccountPassword -Identity <SAM> -Reset -NewPassword (Read-Host -AsSecureString "New password")
Set-ADUser -Identity <SAM> -ChangePasswordAtLogon $true
Unlock-ADAccount -Identity <SAM>
```
COMMAND | DESCRIPTION
---|---
`Set-ADAccountPassword -Identity <SAM> -Reset` | Prompts for the new password interactively
`Set-ADUser <SAM> -ChangePasswordAtLogon $true` | Force a change at next logon
`Set-ADUser <SAM> -PasswordNeverExpires $true` | Exempt from expiry (service accounts only)
`Get-ADUser <SAM> -Properties PasswordLastSet,"msDS-UserPasswordExpiryTimeComputed" \| Select Name,PasswordLastSet,@{n='Expires';e={[datetime]::FromFileTime($_."msDS-UserPasswordExpiryTimeComputed")}}` | When the password expires
`Get-ADDefaultDomainPasswordPolicy` | Domain password policy
`Get-ADFineGrainedPasswordPolicy -Filter *` | Fine-grained policies
`Get-ADUserResultantPasswordPolicy <SAM>` | Policy that actually applies to a user

Resetting a password needs the "Reset password" permission on the object. Do not put real passwords in scripts or history.

## Groups
COMMAND | DESCRIPTION
---|---
`Get-ADGroup <NAME> -Properties *` | Group details
`Get-ADGroupMember <GROUP>` | Direct members
`Get-ADGroupMember <GROUP> -Recursive` | Members including nested groups
`New-ADGroup -Name "<NAME>" -GroupScope Global -GroupCategory Security -Path "OU=Groups,DC=<DOMAIN>,DC=<TLD>"` | Create a group (`DomainLocal`, `Global`, `Universal`)
`Add-ADGroupMember -Identity <GROUP> -Members <SAM1>,<SAM2>` | Add members
`Remove-ADGroupMember -Identity <GROUP> -Members <SAM> -Confirm:$false` | Remove a member
`Get-ADPrincipalGroupMembership <SAM> \| Select Name` | Groups of a user or computer
`Get-ADGroup -Filter 'GroupCategory -eq "Security"' \| Select Name,GroupScope` | List security groups
`Get-ADGroupMember "Domain Admins" \| Select Name,objectClass` | Check privileged membership
`Get-ADGroup <GROUP> \| Set-ADGroup -ManagedBy <SAM>` | Set the owner

Group scope rule of thumb: put users in **Global** groups, global groups in **Domain Local** groups, and grant resource permissions to the domain local group.

## OUs
COMMAND | DESCRIPTION
---|---
`Get-ADOrganizationalUnit -Filter *` | All OUs
`Get-ADOrganizationalUnit -Filter 'Name -like "Lab*"' \| Select DistinguishedName` | OUs by name
`New-ADOrganizationalUnit -Name "Servers" -Path "DC=<DOMAIN>,DC=<TLD>" -ProtectedFromAccidentalDeletion $true` | Create an OU
`Set-ADOrganizationalUnit -Identity "<DN>" -ProtectedFromAccidentalDeletion $false` | Allow deletion
`Remove-ADOrganizationalUnit -Identity "<DN>" -Confirm` | Delete an empty OU
`Get-ADObject -SearchBase "OU=Servers,DC=<DOMAIN>,DC=<TLD>" -Filter * -SearchScope OneLevel` | Contents of an OU

## Computers
COMMAND | DESCRIPTION
---|---
`Get-ADComputer <NAME> -Properties *` | Computer object
`Get-ADComputer -Filter * -Properties OperatingSystem,LastLogonDate \| Select Name,OperatingSystem,LastLogonDate` | Inventory
`Get-ADComputer -Filter 'OperatingSystem -like "*Server*"' \| Select Name` | Servers only
`Get-ADComputer -Filter {LastLogonDate -lt $cutoff}` | Stale machines (`$cutoff = (Get-Date).AddDays(-90)`)
`New-ADComputer -Name <NAME> -Path "OU=Servers,DC=<DOMAIN>,DC=<TLD>"` | Pre-stage an account
`Test-ComputerSecureChannel -Verbose` | Check this machine's trust to the domain
`Test-ComputerSecureChannel -Repair -Credential (Get-Credential)` | Repair a broken trust
`Reset-ComputerMachinePassword -Server <DC> -Credential (Get-Credential)` | Reset the machine account password
`Add-Computer -DomainName <DOMAIN> -Credential (Get-Credential) -Restart` | Join a computer to the domain

## Filters
`-Filter` uses PowerShell-style expressions evaluated on the DC (fast). `-LDAPFilter` takes raw LDAP syntax. Piping to `Where-Object` filters on the client (slow for large directories).

EXAMPLE | DESCRIPTION
---|---
`Get-ADUser -Filter *` | Every user
`Get-ADUser -Filter 'Name -like "*smith*"'` | Wildcard on name
`Get-ADUser -Filter 'Enabled -eq $false'` | Disabled users
`Get-ADUser -Filter 'Department -eq "IT" -and Enabled -eq $true'` | Combine conditions
`Get-ADUser -Filter 'mail -like "*"' -Properties mail \| Select Name,mail` | Users with an email address
`Get-ADUser -Filter 'LastLogonDate -lt $d' -Properties LastLogonDate` | Last logon before a date (`$d = (Get-Date).AddDays(-90)`; `LastLogonDate` is only accurate to about 14 days)
`Get-ADUser -Filter 'whenCreated -ge $d' -Properties whenCreated` | Created since a date (with `$d = (Get-Date).AddDays(-7)`)
`Get-ADUser -LDAPFilter '(&(objectCategory=person)(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))'` | Enabled users via LDAP
`Get-ADUser -Filter * -SearchBase "OU=Staff,DC=<DOMAIN>,DC=<TLD>" -SearchScope Subtree` | Limit to an OU
`Get-ADUser -Filter * -Properties MemberOf \| Where-Object { $_.MemberOf -match "VPN" }` | Client-side filter on a property

Request only the properties you need with `-Properties`; `-Properties *` is slow on big result sets.

## Common Reports
```powershell
# Users and their last logon, export to CSV
Get-ADUser -Filter 'Enabled -eq $true' -Properties LastLogonDate,PasswordLastSet |
  Select-Object Name,SamAccountName,LastLogonDate,PasswordLastSet |
  Sort-Object LastLogonDate |
  Export-Csv .\users.csv -NoTypeInformation

# Empty groups
Get-ADGroup -Filter * | Where-Object { -not (Get-ADGroupMember $_) } | Select Name

# Recently changed objects (last 24h)
Get-ADObject -Filter 'whenChanged -ge $d' -Properties whenChanged
```
COMMAND | DESCRIPTION
---|---
`Get-ADUser -Filter * -Properties Created \| Sort Created -Descending \| Select -First 10 Name,Created` | Newest users
`(Get-ADUser -Filter *).Count` | Count of users
`Get-ADObject -Filter 'ObjectClass -eq "user"' -IncludeDeletedObjects` | Includes tombstoned objects (needs the AD Recycle Bin)
`Get-ADOptionalFeature -Filter *` | Is the Recycle Bin enabled
`Restore-ADObject -Identity <GUID>` | Restore a deleted object (Recycle Bin enabled)
`Get-ADReplicationFailure -Target <DC>` | Recent replication failures
`Get-ADReplicationPartnerMetadata -Target <DC>` | Replication partners and last success times

## DC Health: dcdiag
Run on or against a domain controller (`/s:<DC>`). Output marks each test `passed` or `failed`.

COMMAND | DESCRIPTION
---|---
`dcdiag` | Basic health tests on the local DC
`dcdiag /v` | Verbose output
`dcdiag /s:<DC>` | Test a remote DC
`dcdiag /e /q` | All DCs in the enterprise, show only errors (good for a daily check)
`dcdiag /test:dns /v` | DNS health: records, forwarders, delegation
`dcdiag /test:replications` | Replication check
`dcdiag /test:advertising` | Is the DC advertising as a DC
`dcdiag /test:services` | Required services running
`dcdiag /test:netlogons` | Netlogon and SYSVOL shares present
`dcdiag /test:fsmocheck` | FSMO role holders reachable
`dcdiag /test:ridmanager` | RID pool health

## Replication: repadmin
COMMAND | DESCRIPTION
---|---
`repadmin /replsummary` | Replication summary for every DC (look for failures and large deltas)
`repadmin /showrepl` | Inbound partners and last results for this DC
`repadmin /showrepl * /csv \| ConvertFrom-Csv` | All DCs as objects for filtering
`repadmin /queue` | Pending inbound replication
`repadmin /syncall /AdeP` | Force all partitions to sync from all partners
`repadmin /replicate <DEST-DC> <SRC-DC> "DC=<DOMAIN>,DC=<TLD>"` | Force one replication of a partition
`repadmin /kcc` | Recalculate replication topology
`repadmin /showbackup` | When each partition was last backed up
`repadmin /showobjmeta <DC> "<DN>"` | Attribute change metadata for an object
`repadmin /bridgeheads` | Show site bridgeheads

PowerShell equivalents: `Get-ADReplicationFailure`, `Get-ADReplicationPartnerMetadata`, `Sync-ADObject`.

## FSMO Roles
There are five single-master roles: **Schema Master** and **Domain Naming Master** (per forest) and **PDC Emulator**, **RID Master** and **Infrastructure Master** (per domain).

COMMAND | DESCRIPTION
---|---
`netdom query fsmo` | Show all role holders
`Get-ADDomain \| Select PDCEmulator,RIDMaster,InfrastructureMaster` | Domain roles
`Get-ADForest \| Select SchemaMaster,DomainNamingMaster` | Forest roles
`Move-ADDirectoryServerOperationMasterRole -Identity <DC> -OperationMasterRole PDCEmulator,RIDMaster,InfrastructureMaster` | Transfer roles gracefully (add `SchemaMaster,DomainNamingMaster` as needed; numbers 0 to 4 also work)
`Move-ADDirectoryServerOperationMasterRole -Identity <DC> -OperationMasterRole SchemaMaster -Force` | **Seize** a role when the old holder is gone for good

Transfer if the current holder is online. Seize only when it is permanently lost and never bring it back online afterwards (clean its metadata and rebuild). Also check `ntdsutil` (`roles`, `connections`, `seize ...`) if the PowerShell cmdlet cannot reach a DC.

## Authentication and Time
COMMAND | DESCRIPTION
---|---
`nltest /dsgetdc:<DOMAIN>` | Which DC is serving this client
`nltest /sc_verify:<DOMAIN>` | Verify the secure channel to the domain
`nltest /dclist:<DOMAIN>` | List DCs
`klist` | Show Kerberos tickets in this session (`klist purge` to clear)
`w32tm /query /status` | Time source and offset (Kerberos fails past a 5 minute skew)
`w32tm /resync` | Force a time sync
`w32tm /monitor` | Check time across DCs
`setspn -L <ACCOUNT>` | List service principal names
`setspn -Q */<HOST>` | Find who owns an SPN (duplicates break Kerberos)
`Get-ADUser -Filter 'ServicePrincipalName -like "*"' -Properties ServicePrincipalName` | Accounts with SPNs

## Lockouts
```powershell
# Which DC has the lockout, and who is locked
Search-ADAccount -LockedOut | Select Name,LockedOut
# Find the source in the PDC emulator's Security log (event 4740)
$pdc = (Get-ADDomain).PDCEmulator
Get-WinEvent -ComputerName $pdc -FilterHashtable @{LogName='Security'; Id=4740} -MaxEvents 20 |
  Select TimeCreated, @{n='User';e={$_.Properties[0].Value}}, @{n='Source';e={$_.Properties[1].Value}}
```
More event queries in [Windows Troubleshooting](windows-troubleshooting.md).

## Backup and Recovery
COMMAND | DESCRIPTION
---|---
`wbadmin start systemstatebackup -backupTarget:E:` | System State backup of a DC
`wbadmin get versions` | Available backups
`Enable-ADOptionalFeature 'Recycle Bin Feature' -Scope ForestOrConfigurationSet -Target <FOREST-FQDN>` | Enable the AD Recycle Bin (irreversible, forest-wide)
`ntdsutil "activate instance ntds" ifm "create full C:\IFM" quit quit` | Create install-from-media files

Test restores before you need them. Authoritative restores of deleted objects need DSRM and `ntdsutil`.

## Not Verified
Commands were written from the Microsoft documentation and not executed against a live domain. Run destructive ones (`Remove-*`, role seizure) only in a lab first.
