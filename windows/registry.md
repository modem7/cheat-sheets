# Windows Registry
The registry is Windows' configuration database. Edit it from PowerShell, `reg.exe` or `regedit`. Wrong edits can break Windows or stop it booting, so export the key first. Commands run in PowerShell ([PowerShell Cheat-Sheet](powershell.md)) unless noted, and most changes under `HKLM` need an elevated prompt.

Documentation: [reg](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/reg), [about_Registry_Provider](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_registry_provider)

## Hives
HIVE | SHORT | HOLDS
---|---|---
`HKEY_LOCAL_MACHINE` | `HKLM` | Machine-wide settings
`HKEY_CURRENT_USER` | `HKCU` | Settings for the signed-in user
`HKEY_CLASSES_ROOT` | `HKCR` | File associations and COM (merged view)
`HKEY_USERS` | `HKU` | All loaded user profiles
`HKEY_CURRENT_CONFIG` | `HKCC` | Current hardware profile

PowerShell exposes `HKLM:` and `HKCU:` as drives, for example `HKLM:\SOFTWARE`.

## Value Types
TYPE | `-PropertyType` | `reg` type
---|---|---
String | `String` | `REG_SZ`
Expandable string | `ExpandString` | `REG_EXPAND_SZ`
Multi-string | `MultiString` | `REG_MULTI_SZ`
32-bit number | `DWord` | `REG_DWORD`
64-bit number | `QWord` | `REG_QWORD`
Binary | `Binary` | `REG_BINARY`

## PowerShell
COMMAND | DESCRIPTION
---|---
`Get-ChildItem HKLM:\SOFTWARE\<VENDOR>` | List subkeys
`Get-ItemProperty HKLM:\SOFTWARE\<KEY>` | Show all values in a key
`Get-ItemPropertyValue HKLM:\SOFTWARE\<KEY> -Name <VALUE>` | Read one value
`Test-Path HKLM:\SOFTWARE\<KEY>` | Does the key exist
`New-Item -Path HKCU:\SOFTWARE\<KEY>` | Create a key
`New-ItemProperty -Path HKCU:\SOFTWARE\<KEY> -Name <VALUE> -PropertyType DWord -Value 1` | Create a value
`Set-ItemProperty -Path HKCU:\SOFTWARE\<KEY> -Name <VALUE> -Value 0` | Change a value
`Rename-ItemProperty -Path <KEY> -Name <OLD> -NewName <NEW>` | Rename a value
`Remove-ItemProperty -Path <KEY> -Name <VALUE>` | Delete a value (**destructive**)
`Remove-Item -Path <KEY> -Recurse` | Delete a key and its subkeys (**destructive**)
`Get-ChildItem HKLM:\SOFTWARE -Recurse -ErrorAction SilentlyContinue \| Where-Object Name -like '*<TEXT>*'` | Search key names (slow)

`Set-ItemProperty` does not create a missing value with a type. Use `New-ItemProperty` first, or add `-Force`.

## reg.exe
Works in `cmd` and PowerShell. Use `/f` to skip the confirmation prompt.

COMMAND | DESCRIPTION
---|---
`reg query "HKLM\SOFTWARE\<KEY>"` | Show a key's values
`reg query "HKLM\SOFTWARE\<KEY>" /v <VALUE>` | Show one value
`reg query "HKLM\SOFTWARE" /s /f <TEXT>` | Search recursively
`reg add "HKCU\SOFTWARE\<KEY>" /v <VALUE> /t REG_DWORD /d 1 /f` | Add or overwrite a value
`reg delete "HKCU\SOFTWARE\<KEY>" /v <VALUE> /f` | Delete a value (**destructive**)
`reg delete "HKCU\SOFTWARE\<KEY>" /f` | Delete a key (**destructive**)
`reg copy "<SRC_KEY>" "<DEST_KEY>" /s /f` | Copy a key
`reg export "HKLM\SOFTWARE\<KEY>" backup.reg` | Export to a `.reg` file
`reg import backup.reg` | Import a `.reg` file
`reg save "HKLM\SOFTWARE\<KEY>" backup.hiv` | Save a key as a binary hive file
`reg restore "HKLM\SOFTWARE\<KEY>" backup.hiv` | Restore from a hive file (**destructive**)
`reg load HKU\TempHive C:\Users\<USER>\NTUSER.DAT` | Load an offline user hive
`reg unload HKU\TempHive` | Unload it (close handles first)
`reg compare "<KEY1>" "<KEY2>" /s` | Diff two keys

## Back Up Before Editing
```powershell
reg export "HKLM\SOFTWARE\<KEY>" "$env:USERPROFILE\Desktop\key-backup.reg"
```

For wider changes create a restore point first with `Checkpoint-Computer -Description "Before registry edit"` (needs System Protection enabled and an elevated prompt).

## Other Users and Remote
- `reg load` brings in another user's `NTUSER.DAT` while they are signed out. Edit under `HKU\TempHive`, then `reg unload`.
- Add `\\<COMPUTER>` to the key path to query a remote machine's `HKLM` or `HKU` with `reg query` (needs the Remote Registry service and admin rights).
- Offline Windows image: `reg load HKLM\OFFLINE <MOUNT>\Windows\System32\config\SOFTWARE`, then `reg unload HKLM\OFFLINE`.

## Common Locations
KEY | PURPOSE
---|---
`HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` | Programs started at sign-in for all users
`HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` | Programs started at sign-in for one user
`HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall` | Installed programs (add `WOW6432Node` for 32-bit)
`HKLM\SYSTEM\CurrentControlSet\Services` | Services and drivers
`HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment` | System environment variables
`HKCU\Environment` | User environment variables
`HKLM\SOFTWARE\Policies` | Policy-set values ([Group Policy](group-policy.md))
`HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion` | Windows version and build

## 32-bit and 64-bit Views
32-bit programs on 64-bit Windows are redirected to `HKLM\SOFTWARE\WOW6432Node`. Use `reg query ... /reg:64` or `/reg:32` to pick a view explicitly.

## Not Verified
`reg` exit codes, remote registry details, and the `Checkpoint-Computer` requirements were written from memory and not checked against the docs.

## See Also
- [PowerShell Cheat-Sheet](powershell.md)
- [Group Policy](group-policy.md)
- [Environment Variables](environment-variables.md)
- [Windows Troubleshooting](windows-troubleshooting.md)
