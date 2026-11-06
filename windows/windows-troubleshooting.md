# Windows Troubleshooting
A toolbox for diagnosing and repairing Windows: system file and image repair (`sfc`, `DISM`), disk checks, event log queries, services, performance counters and boot repair. Use an **elevated** PowerShell or Command Prompt ([[powershell]]). Related: [[windows-updates]], [[windows-networking]], [[group-policy]], [[active-directory]].

Documentation: [Windows commands](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands), [Repair a Windows image](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/repair-a-windows-image)

## System File and Image Repair
Run in this order: DISM repairs the component store, then SFC repairs system files from it.

COMMAND | DESCRIPTION
---|---
`DISM /Online /Cleanup-Image /CheckHealth` | Quick check for a flagged corruption
`DISM /Online /Cleanup-Image /ScanHealth` | Deeper scan (a few minutes)
`DISM /Online /Cleanup-Image /RestoreHealth` | Repair the image (uses Windows Update as source)
`DISM /Online /Cleanup-Image /RestoreHealth /Source:WIM:D:\sources\install.wim:1 /LimitAccess` | Repair from a mounted ISO instead of Windows Update (match the edition index)
`sfc /scannow` | Scan and repair protected system files
`sfc /verifyonly` | Scan without repairing
`sfc /scanfile=C:\Windows\System32\<FILE>` | Check one file
`findstr /c:"[SR]" %windir%\Logs\CBS\CBS.log > "%userprofile%\Desktop\sfclogs.txt"` | Extract SFC entries from the CBS log
`DISM /Online /Cleanup-Image /AnalyzeComponentStore` | Component store size and reclaimable space
`DISM /Online /Cleanup-Image /StartComponentCleanup` | Remove superseded components (frees disk space)
`Repair-WindowsImage -Online -RestoreHealth` | PowerShell equivalent of DISM RestoreHealth
`Get-WindowsImage -ImagePath D:\sources\install.wim` | List editions and indexes in an ISO

If `sfc` reports corruption it cannot fix, run `DISM /RestoreHealth` and then `sfc /scannow` again. Logs: `C:\Windows\Logs\CBS\CBS.log` and `C:\Windows\Logs\DISM\dism.log`. Reset stuck updates in [[windows-updates]].

## Disk Checks
COMMAND | DESCRIPTION
---|---
`chkdsk` | Read-only check of the current volume
`chkdsk C: /f` | Fix file system errors (schedules at reboot for the system drive)
`chkdsk C: /r` | Find bad sectors and recover data (implies `/f`, slow)
`chkdsk C: /scan` | Online scan of an NTFS volume (no downtime)
`chkdsk C: /spotfix` | Offline repair of only the issues found by `/scan`
`Repair-Volume -DriveLetter C -Scan` | PowerShell online scan
`Repair-Volume -DriveLetter C -OfflineScanAndFix` | PowerShell offline repair
`Get-Volume` | Volumes with size, free space and health
`Get-Disk` / `Get-PhysicalDisk` | Disks and `HealthStatus`
`Get-PhysicalDisk \| Get-StorageReliabilityCounter \| Select Temperature,Wear,ReadErrorsTotal` | SMART-like counters
`wmic diskdrive get status,model` | Quick SMART status (deprecated, still present on many builds)
`fsutil dirty query C:` | Is the volume flagged dirty
`fsutil volume diskfree C:` | Free space detail
`defrag C: /O` | Optimise (TRIM on SSD, defrag on HDD)
`Optimize-Volume -DriveLetter C -ReTrim -Verbose` | Run TRIM

## Event Logs
`Get-WinEvent` reads event logs and is much faster with `-FilterHashtable` than with `Where-Object`.

COMMAND | DESCRIPTION
---|---
`Get-WinEvent -ListLog *` | All logs (`-ListLog * \| Sort RecordCount -Desc`)
`Get-WinEvent -LogName System -MaxEvents 50` | Latest events
`Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2}` | Critical (1) and Error (2)
`Get-WinEvent -FilterHashtable @{LogName='System'; Level=2; StartTime=(Get-Date).AddHours(-24)}` | Errors in the last 24 hours
`Get-WinEvent -FilterHashtable @{LogName='Application'; ProviderName='.NET Runtime'}` | By provider
`Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4625} -MaxEvents 20` | Failed logons (needs admin)
`Get-WinEvent -FilterHashtable @{LogName='System'; Id=41,6008}` | Unexpected shutdowns
`Get-WinEvent -FilterHashtable @{LogName='System'; Id=1074}` | Planned restart or shutdown (who and why)
`Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-WindowsUpdateClient/Operational'}` | Windows Update history
`Get-WinEvent -ComputerName <PC> -LogName System -MaxEvents 20` | Remote machine
`Get-WinEvent -Path C:\logs\saved.evtx` | Read an exported log
`Get-WinEvent -FilterHashtable @{LogName='System'; Level=2} \| Group-Object ProviderName \| Sort Count -Desc \| Select -First 10` | Noisiest error sources
`wevtutil qe System /c:20 /rd:true /f:text` | Classic query: 20 newest, text format
`wevtutil epl System C:\temp\system.evtx` | Export a log
`wevtutil cl Application` | Clear a log (**destroys evidence**)
`Get-EventLog -LogName System -Newest 20` | Old cmdlet (Windows PowerShell 5.1 only, classic logs)

Levels: 1 Critical, 2 Error, 3 Warning, 4 Information, 5 Verbose. Useful event IDs:

ID | LOG | MEANING
---|---|---
41 | System | Kernel-Power: restarted without a clean shutdown
6005 / 6006 | System | Event Log service started / stopped (boot and shutdown)
6008 | System | Previous shutdown was unexpected
1074 | System | Shutdown or restart initiated, with reason
7034 / 7036 / 7045 | System | Service crashed / changed state / installed
4624 / 4625 | Security | Successful / failed logon
4740 | Security | Account locked out
1000 / 1002 | Application | Application crash / hang
10016 | System | DCOM permission warning (usually harmless)

## Services
COMMAND | DESCRIPTION
---|---
`Get-Service` | All services
`Get-Service -Name Spooler` | One service
`Get-Service \| Where Status -eq Running` | Running services
`Get-Service \| Where { $_.StartType -eq 'Automatic' -and $_.Status -ne 'Running' }` | Automatic services that are stopped
`Start-Service Spooler` / `Stop-Service Spooler` / `Restart-Service Spooler` | Control a service (`-Force` also stops dependents)
`Set-Service -Name Spooler -StartupType Disabled` | Startup type: `Automatic`, `AutomaticDelayedStart`, `Manual`, `Disabled`
`Get-Service Spooler -DependentServices` / `-RequiredServices` | Dependencies
`Get-CimInstance Win32_Service -Filter "Name='Spooler'" \| Select Name,State,StartMode,StartName,PathName` | Account, path and mode
`sc.exe query Spooler` | Classic query
`sc.exe qc Spooler` | Show the service configuration
`sc.exe config Spooler start= auto` | Set startup (space after `=` is required)
`sc.exe failure Spooler reset= 86400 actions= restart/5000/restart/5000/restart/5000` | Recovery actions
`Get-Process -Name <NAME>` | Running processes
`Stop-Process -Name <NAME> -Force` / `taskkill /IM <EXE> /F` | Kill a process
`Get-Process \| Sort CPU -Desc \| Select -First 10 Name,CPU,Id` | Top CPU users
`Get-Process \| Sort WS -Desc \| Select -First 10 Name,@{n='MB';e={[int]($_.WS/1MB)}}` | Top memory users
`tasklist /svc` | Which services run inside each process
`Get-CimInstance Win32_StartupCommand \| Select Name,Command,Location` | Startup programs
`Get-ScheduledTask \| Where State -ne Disabled` | Active scheduled tasks

## Performance
COMMAND | DESCRIPTION
---|---
`Get-Counter '\Processor(_Total)\% Processor Time'` | CPU usage right now
`Get-Counter '\Memory\Available MBytes'` | Free memory
`Get-Counter '\PhysicalDisk(_Total)\Avg. Disk Queue Length'` | Disk queue (sustained over 2 per spindle is a bottleneck)
`Get-Counter '\Network Interface(*)\Bytes Total/sec'` | Network throughput
`Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval 2 -MaxSamples 10` | Ten samples, two seconds apart
`Get-Counter -ListSet * \| Select CounterSetName` | Available counter sets
`Get-Counter -Counter '\Process(*)\% Processor Time' \| Select -Expand CounterSamples \| Sort CookedValue -Desc \| Select -First 5` | Top processes by CPU
`typeperf "\Processor(_Total)\% Processor Time" -sc 5` | Classic counter sampling
`Get-CimInstance Win32_OperatingSystem \| Select @{n='FreeMB';e={[int]($_.FreePhysicalMemory/1KB)}},@{n='TotalMB';e={[int]($_.TotalVisibleMemorySize/1KB)}}` | Memory summary
`(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime` | Uptime
`Get-ComputerInfo \| Select OsName,OsVersion,CsProcessors,CsTotalPhysicalMemory` | System overview
`perfmon` / `perfmon /rel` / `resmon` | Performance Monitor, Reliability Monitor, Resource Monitor
`logman create counter Baseline -c "\Processor(_Total)\% Processor Time" "\Memory\Available MBytes" -si 15 -o C:\PerfLogs\baseline` | Start a data collector for a baseline
`logman start Baseline` / `logman stop Baseline` | Control it
`taskmgr` | Task Manager

## Memory and Crash Analysis
COMMAND | DESCRIPTION
---|---
`mdsched.exe` | Windows Memory Diagnostic (reboots to test RAM)
`Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='Microsoft-Windows-WER-SystemErrorReporting'}` | Bugcheck (blue screen) records
`Get-ChildItem C:\Windows\Minidump` | Crash dump files
`Get-WmiObject Win32_PageFileUsage` | Page file use (or `Get-CimInstance Win32_PageFileUsage`)
`msinfo32` | System information viewer
`dxdiag` | Display and sound diagnostics
`systeminfo` | OS, hotfixes, boot time and hardware summary
`Get-HotFix \| Sort InstalledOn -Desc \| Select -First 10` | Recent updates (see [[windows-updates]])

Analyse dumps with WinDbg or WhoCrashed. For a bluescreen code lookup, note the stop code and the faulting driver from the dump.

## Boot Repair
Start from Windows installation media (boot, **Repair your computer**, **Troubleshoot**, **Command Prompt**) or Advanced Startup (`shutdown /r /o /t 0`). In WinRE the Windows drive letter may not be `C:`, so check with `diskpart`, `list vol` or `dir`.

COMMAND | DESCRIPTION
---|---
`bootrec /fixmbr` | Write a new master boot record (BIOS/MBR systems)
`bootrec /fixboot` | Write a new boot sector (may say access denied on UEFI; use `bcdboot` instead)
`bootrec /scanos` | Look for Windows installations
`bootrec /rebuildbcd` | Rebuild the Boot Configuration Data store
`bcdboot C:\Windows /s S: /f UEFI` | Recreate boot files on the EFI System Partition (letter `S:` assigned with `diskpart`)
`bcdedit /enum all` | Show boot entries
`bcdedit /set {default} safeboot minimal` | Next boots go to Safe Mode (`bcdedit /deletevalue {default} safeboot` to undo)
`bcdedit /set {default} bootmenupolicy legacy` | Enable the F8-style boot menu
`diskpart` | Partition tool (`list disk`, `sel disk 0`, `list vol`, `sel vol 2`, `assign letter=S`)
`sfc /scannow /offbootdir=C:\ /offwindir=C:\Windows` | Repair system files from WinRE
`DISM /Image:C:\ /Cleanup-Image /RestoreHealth /Source:D:\sources\install.wim:1` | Repair an offline image
`DISM /Image:C:\ /Cleanup-Image /RevertPendingActions` | Roll back a stuck pending update
`chkdsk C: /f` | Fix the file system from WinRE
`msconfig` | Choose a diagnostic or safe boot, hide Microsoft services to find a culprit

**EFI repair sequence** (UEFI, GPT disk):
```text
diskpart
 list disk
 sel disk 0
 list vol            (find the FAT32 volume of about 100-500 MB)
 sel vol 2
 assign letter=S
 exit
bcdboot C:\Windows /s S: /f UEFI
```
Other recovery: `systemreset`, **Reset this PC**, System Restore (`rstrui.exe`), `wbadmin` backups, and Safe Mode from Advanced Startup. BitLocker-encrypted drives need the recovery key before `bootrec` or `chkdsk` can access them (`manage-bde -status`, `manage-bde -unlock D: -RecoveryPassword <KEY>`).

## Quick Triage Checklist
1. `Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2; StartTime=(Get-Date).AddHours(-24)}` for recent errors.
2. `Get-Service | Where { $_.StartType -eq 'Automatic' -and $_.Status -ne 'Running' }` for failed services.
3. `Get-Volume` for free space (a full system drive breaks many things).
4. `DISM /Online /Cleanup-Image /RestoreHealth` then `sfc /scannow`.
5. `Get-Counter` for CPU, memory and disk pressure; `Get-Process` for the culprit.
6. [[windows-networking]] for connectivity and DNS; [[windows-updates]] for update problems.
7. Check the Reliability Monitor (`perfmon /rel`) for a timeline of crashes and installs.

## Not Verified
Commands were written from the Microsoft documentation and not executed. Run repairs on a test machine first and keep a backup before `chkdsk /r`, `bootrec` or `bcdedit` changes.
