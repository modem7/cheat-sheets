# Windows Scheduled Tasks
Task Scheduler runs programs and scripts at set times or on events, like cron on Linux ([Cron](../misc/cron.md)). Manage it with the PowerShell `ScheduledTasks` module, `schtasks.exe` or `taskschd.msc`. Commands run in PowerShell ([PowerShell Cheat-Sheet](powershell.md)) and most need an elevated prompt.

Documentation: [ScheduledTasks module](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/), [schtasks](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks)

## PowerShell
COMMAND | DESCRIPTION
---|---
`Get-ScheduledTask` | List tasks
`Get-ScheduledTask -TaskName "<NAME>" \| Get-ScheduledTaskInfo` | Last run time and result
`Get-ScheduledTask -TaskPath "\Microsoft\Windows\*"` | Tasks under a folder
`Start-ScheduledTask -TaskName "<NAME>"` | Run now
`Stop-ScheduledTask -TaskName "<NAME>"` | Stop a running task
`Disable-ScheduledTask -TaskName "<NAME>"` | Disable
`Enable-ScheduledTask -TaskName "<NAME>"` | Enable
`Unregister-ScheduledTask -TaskName "<NAME>" -Confirm:$false` | Delete (**destructive**)
`Export-ScheduledTask -TaskName "<NAME>"` | Output the task as XML
`Register-ScheduledTask -Xml (Get-Content task.xml -Raw) -TaskName "<NAME>"` | Import from XML

## Create a Task
```powershell
$action  = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-NoProfile -File C:\Scripts\backup.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 3am
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "Nightly backup" -Action $action `
  -Trigger $trigger -Principal $principal
```

CMDLET | DESCRIPTION
---|---
`New-ScheduledTaskAction` | What to run (`-Execute`, `-Argument`, `-WorkingDirectory`)
`New-ScheduledTaskTrigger` | When: `-Once`, `-Daily`, `-Weekly`, `-AtStartup`, `-AtLogOn`
`New-ScheduledTaskPrincipal` | Who it runs as and the run level
`New-ScheduledTaskSettingsSet` | Options such as `-StartWhenAvailable`, `-RestartCount`, `-ExecutionTimeLimit`
`Set-ScheduledTask` | Change an existing task
`Register-ScheduledTask` | Create it

Run as `SYSTEM` or a service account for jobs that must run when nobody is signed in. For a named user, pass `-User` and `-Password` to `Register-ScheduledTask` instead of a principal.

## schtasks.exe
COMMAND | DESCRIPTION
---|---
`schtasks /query` | List tasks
`schtasks /query /tn "<NAME>" /v /fo list` | Verbose details for one task
`schtasks /create /tn "<NAME>" /tr "C:\Scripts\run.cmd" /sc daily /st 03:00 /ru SYSTEM` | Create a daily task
`schtasks /create /tn "<NAME>" /tr "C:\Scripts\run.cmd" /sc onstart /ru SYSTEM` | Run at startup
`schtasks /run /tn "<NAME>"` | Run now
`schtasks /end /tn "<NAME>"` | Stop
`schtasks /change /tn "<NAME>" /disable` | Disable (`/enable` to reverse)
`schtasks /delete /tn "<NAME>" /f` | Delete (**destructive**)

Add `/s <COMPUTER>` to any command to target a remote machine.

## Troubleshooting
- A result of `0` (or `0x0`) from `Get-ScheduledTaskInfo` is success. Other codes are in `LastTaskResult`.
- Scripts run with a minimal environment and the task's working directory, so use full paths.
- Task history is off by default. Enable it in `taskschd.msc` (Action, Enable All Tasks History), then read the `Microsoft-Windows-TaskScheduler/Operational` log, see [Windows Troubleshooting](windows-troubleshooting.md).
- "Run whether user is logged on or not" needs the account to have "Log on as a batch job" rights.

## Not Verified
Parameter names and the task history menu path were written from memory. Check `Get-Help <CMDLET> -Full` on your Windows version.

## See Also
- [PowerShell Cheat-Sheet](powershell.md)
- [Windows Troubleshooting](windows-troubleshooting.md)
- [Cron](../misc/cron.md)
- [Healthchecks](../apps/healthchecks.md)
