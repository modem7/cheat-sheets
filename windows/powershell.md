# PowerShell Cheat-Sheet
PowerShell is a task automation and configuration management program from Microsoft, consisting of a command-line shell and the associated scripting language.

## Install PowerShell
PowerShell was made open-source and cross-platform with PowerShell Core, and can be installed on multiple operating systems.

### Windows
1. Download MSI Package from the [Official PowerShell Docs](https://docs.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-windows?view=powershell-7.2)
2. Set up PowerShell Profile in [Windows Terminal](windows-terminal.md).
```json
"commandline": "pwsh.exe -nologo",
"name": "Powershell",
"source": "Windows.Terminal.PowershellCore"
```

### Linux (Ubuntu)
```sh
# Update the list of packages
sudo apt-get update
# Install pre-requisite packages.
sudo apt-get install -y wget apt-transport-https software-properties-common
# Download the Microsoft repository GPG keys
wget -q https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb
# Register the Microsoft repository GPG keys
sudo dpkg -i packages-microsoft-prod.deb
# Update the list of packages after we added packages.microsoft.com
sudo apt-get update
# Install PowerShell
sudo apt-get install -y powershell
# Start PowerShell
pwsh
```

## Profile
Set up a PowerShell Profile by opening the profile script :
```powershell
code $PROFILE
```

## (Optional) Set up starship Prompt
You can customize the look and feel of PowerShell with the [Starship Prompt](../tools/starship.md).

## Getting Around
COMMAND | DESCRIPTION
---|---
`$PSVersionTable` | PowerShell version and edition (`Desktop` = Windows PowerShell 5.1, `Core` = 7+)
`Get-Command *service*` | Find commands by name
`Get-Help Get-Service -Examples` | Help with examples (`Update-Help` downloads it, as admin)
`Get-Help about_*` | Conceptual help topics
`Get-Member` | Properties and methods of the objects a command returns
`Get-Alias` / `Get-Alias -Definition Get-ChildItem` | Aliases (`ls`, `dir`, `gci`)
`Get-Module -ListAvailable` | Installed modules
`Install-Module <NAME> -Scope CurrentUser` | Install from the PowerShell Gallery
`Get-History` / `Ctrl`+`R` | Command history and reverse search
`(Get-PSReadLineOption).HistorySavePath` | File holding history across sessions
`Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` | Allow local scripts, require signatures for downloaded ones

Commands are `Verb-Noun` (`Get-`, `Set-`, `New-`, `Remove-`). Run `Get-Verb` for approved verbs. Tab completion works on commands, parameters and values.

## Pipeline and Objects
PowerShell pipes **objects**, not text, so you filter and sort on properties instead of parsing columns. Everything flows left to right through `|`.

```powershell
Get-Process |
  Where-Object CPU -gt 100 |
  Sort-Object CPU -Descending |
  Select-Object -First 5 Name, Id, CPU
```
COMMAND | DESCRIPTION
---|---
`Get-Service \| Get-Member` | Show the object type and its members
`Get-Process \| Select-Object Name, Id, WS` | Choose properties
`Get-Process \| Select-Object -First 5` / `-Last 5` / `-Skip 5` | Pick rows
`Get-Process \| Select-Object -ExpandProperty Name` | Plain values instead of objects
`Get-Process \| Select-Object Name, @{Name='MB'; Expression={[int]($_.WS/1MB)}}` | Calculated property
`Get-Service \| Where-Object Status -eq Running` | Simple filter (PowerShell 3+)
`Get-Service \| Where-Object { $_.Status -eq 'Running' -and $_.Name -like 'W*' }` | Script block filter for complex conditions
`Get-Process \| Where-Object Name -match '^(chrome\|firefox)'` | Regex match
`Get-Process \| Sort-Object WS -Descending` | Sort (`-Unique` to deduplicate)
`Get-ChildItem -Recurse \| Group-Object Extension \| Sort-Object Count -Descending` | Group and count
`Get-ChildItem \| Measure-Object Length -Sum -Average -Maximum` | Count, sum and average
`Get-Process \| ForEach-Object { $_.Name.ToUpper() }` | Run code for each object (`%` alias)
`1..5 \| ForEach-Object { $_ * 2 }` | Ranges and `$_` as the current item
`Get-Process \| ForEach-Object -Parallel { $_.Name } -ThrottleLimit 4` | Parallel loop (PowerShell 7+)
`Get-Process \| Out-GridView` | Interactive filterable table (Windows, needs a GUI)
`Get-Process \| Format-Table Name, Id -AutoSize` | Format for display only (do not pipe formatted output onwards)
`Get-Process \| Format-List *` | All properties of each object
`Get-Process \| Tee-Object -FilePath procs.txt` | Write to a file and keep passing along
`Compare-Object $before $after -Property Name` | Compare two sets (`<=` only in the first, `=>` only in the second)

Filter early (`Where-Object` as far left as possible, or use the cmdlet's own `-Filter` parameter) and format last (`Format-*` output is for the screen, not for more processing).

## Variables and Data
COMMAND | DESCRIPTION
---|---
`$x = 5; $name = "Bob"` | Variables
`"Hello $name"` / `"Value: $($obj.Prop)"` | Expandable string; use `$( )` for expressions
`'literal $name'` | Single quotes: no expansion
`$arr = 1,2,3; $arr += 4; $arr[0]` | Arrays
`$h = @{ a = 1; b = 2 }; $h.a; $h['b']` | Hashtable
`[PSCustomObject]@{ Name='x'; Id=1 }` | Create an object
`$h.GetEnumerator() \| Sort-Object Name` | Iterate a hashtable
`[int]'42'`, `[datetime]'2025-01-31'` | Type casting
`$env:PATH` / `$env:COMPUTERNAME` | Environment variables ([Environment Variables in Windows](environment-variables.md))
`$PSScriptRoot` / `$PWD` / `$HOME` | Script folder, current folder, home folder
`$null`, `$true`, `$false` | Constants
`-eq -ne -gt -lt -like -match -contains -in` | Comparison operators (case-insensitive by default; `-ceq` is case-sensitive)
`-and -or -not` / `!` | Logic
`$a ?? 'default'` / `$a ? 'yes' : 'no'` | Null-coalescing and ternary (PowerShell 7+)

## Files and Data Formats
COMMAND | DESCRIPTION
---|---
`Get-Content file.txt` / `-Tail 20 -Wait` | Read a file / follow it like `tail -f`
`Set-Content file.txt "text"` / `Add-Content file.txt "more"` | Write / append
`Get-ChildItem -Recurse -Filter *.log \| Remove-Item -WhatIf` | Preview a delete first
`Select-String -Path *.log -Pattern 'error'` | grep for PowerShell
`Import-Csv data.csv \| Where-Object Age -gt 30` | CSV to objects
`Export-Csv out.csv -NoTypeInformation` | Objects to CSV
`Get-Content cfg.json -Raw \| ConvertFrom-Json` | JSON to objects ([jq](../tools/jq.md) for the shell)
`$obj \| ConvertTo-Json -Depth 5` | Objects to JSON (default depth is only 2)
`Invoke-RestMethod https://api.example.com/items` | HTTP GET, parsed JSON
`Invoke-WebRequest -Uri <URL> -OutFile file.zip` | Download a file
`Compress-Archive -Path .\dir -DestinationPath out.zip` / `Expand-Archive` | Zip and unzip
`Get-FileHash file.iso -Algorithm SHA256` | Checksum
`Test-Path C:\path` | Does it exist

## Error Handling
PowerShell has **terminating** errors (stop the script, catchable) and **non-terminating** errors (print and continue). Most cmdlet errors are non-terminating, so `try/catch` only sees them if you ask.

```powershell
try {
    Get-Item C:\missing.txt -ErrorAction Stop
    Write-Output "found"
}
catch [System.Management.Automation.ItemNotFoundException] {
    Write-Warning "Not found: $($_.Exception.Message)"
}
catch {
    Write-Error "Unexpected: $_"
    throw                      # rethrow
}
finally {
    Write-Output "cleanup always runs"
}
```
COMMAND | DESCRIPTION
---|---
`-ErrorAction Stop` | Turn a non-terminating error into a catchable one (per command)
`$ErrorActionPreference = 'Stop'` | Do that for the whole script (put at the top)
`-ErrorAction SilentlyContinue` | Ignore errors (also `Continue`, `Inquire`)
`-ErrorVariable err` | Collect errors into `$err` without stopping
`$Error[0]` | Most recent error (`$Error[0] \| Format-List * -Force` for detail)
`$?` / `$LASTEXITCODE` | Success of the last PowerShell command / exit code of the last external program
`throw "message"` | Raise an error
`Write-Warning`, `Write-Verbose`, `Write-Debug` | Other streams (`-Verbose` or `$VerbosePreference` shows them)
`Start-Transcript -Path log.txt` / `Stop-Transcript` | Log everything to a file
`Set-StrictMode -Version Latest` | Error on uninitialised variables and bad property access
`-WhatIf` / `-Confirm` | Preview or confirm a change (on cmdlets that support them)

External programs do not throw: check `$LASTEXITCODE` after calling them (for example `robocopy`, see [Robocopy](robocopy.md)).

## Functions and Scripts
```powershell
function Get-DiskReport {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ComputerName,
        [int]$MinFreeGB = 10
    )
    Get-CimInstance Win32_LogicalDisk -ComputerName $ComputerName -Filter "DriveType=3" |
        Where-Object { ($_.FreeSpace / 1GB) -lt $MinFreeGB } |
        Select-Object DeviceID, @{n='FreeGB'; e={[math]::Round($_.FreeSpace / 1GB, 1)}}
}
```
Save as `script.ps1` and run `.\script.ps1` (the `.\` is required). Use `[CmdletBinding()]` for `-Verbose`, `-ErrorAction` and other common parameters, and `param()` with attributes for validation (`[ValidateSet('a','b')]`, `[ValidateRange(1,10)]`).

## Remoting
Run commands on other machines with `Invoke-Command -ComputerName <SERVER> -ScriptBlock { ... }` or open an interactive session with `Enter-PSSession`. WinRM and SSH setup, sessions and file copy are in [PowerShell Remote Access](powershell-remote.md). Remote output comes back as deserialised objects (properties yes, methods no).

## Scheduled Tasks
COMMAND | DESCRIPTION
---|---
`Get-ScheduledTask` | List tasks (`-TaskName "*backup*"`, `-TaskPath "\Microsoft\Windows\*"`)
`Get-ScheduledTaskInfo -TaskName <NAME>` | Last run time and result code
`Start-ScheduledTask -TaskName <NAME>` / `Stop-ScheduledTask -TaskName <NAME>` | Run or stop now
`Disable-ScheduledTask -TaskName <NAME>` / `Enable-ScheduledTask -TaskName <NAME>` | Disable or enable
`Unregister-ScheduledTask -TaskName <NAME> -Confirm:$false` | Delete a task
`schtasks /query /fo LIST /v` | Classic view of all tasks

Create a daily task that runs a script as SYSTEM:
```powershell
$action  = New-ScheduledTaskAction -Execute "pwsh.exe" -Argument '-NoProfile -ExecutionPolicy Bypass -File "C:\Scripts\backup.ps1"'
$trigger = New-ScheduledTaskTrigger -Daily -At 3am
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)
Register-ScheduledTask -TaskName "Nightly Backup" -Action $action -Trigger $trigger -Settings $settings -User "SYSTEM" -RunLevel Highest
```
Other triggers: `-Weekly -DaysOfWeek Monday -At 6am`, `-AtStartup`, `-AtLogOn`, `-Once -At (Get-Date).AddMinutes(5) -RepetitionInterval (New-TimeSpan -Minutes 15)`. Use `powershell.exe` instead of `pwsh.exe` if PowerShell 7 is not installed. A task's "Last Run Result" of `0` means success.

## Useful One-Liners
COMMAND | DESCRIPTION
---|---
`Get-CimInstance Win32_LogicalDisk \| Select DeviceID, @{n='FreeGB';e={[int]($_.FreeSpace/1GB)}}` | Free disk space
`Get-ChildItem C:\ -Recurse -File -ErrorAction SilentlyContinue \| Sort Length -Desc \| Select -First 10 FullName,Length` | Ten largest files
`Get-HotFix \| Sort InstalledOn -Desc \| Select -First 5` | Recent updates ([Windows Updates](windows-updates.md))
`(Get-Date).AddDays(-7)` | Date arithmetic
`Get-NetTCPConnection -State Listen` | Listening ports ([Windows Networking](windows-networking.md))
`winget upgrade --all` | Upgrade software ([winget](winget.md))
`Get-WinEvent -LogName System -MaxEvents 20` | Event logs ([Windows Troubleshooting](windows-troubleshooting.md))
`Get-ADUser -Filter * -Properties LastLogonDate` | [Active Directory](active-directory.md)

