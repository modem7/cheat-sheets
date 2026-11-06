# Environment Variables in Windows
## How to use them in PowerShell
Environment variables can be used in PowerShell ([PowerShell Cheat-Sheet](powershell.md)) with the prefix `$env:`.

**Example:**
*Variable:* `%APPDATA%`
*In PowerShell:* `$env:APPDATA`

## Read, Set and Remove
COMMAND | DESCRIPTION
---|---
`Get-ChildItem Env:` | List all variables
`$env:PATH -split ';'` | Show PATH entries one per line
`$env:MYVAR = "value"` | Set for the current PowerShell session only
`[Environment]::SetEnvironmentVariable("MYVAR","value","User")` | Set permanently for the user
`[Environment]::SetEnvironmentVariable("MYVAR","value","Machine")` | Set permanently for all users (run as administrator)
`[Environment]::GetEnvironmentVariable("MYVAR","User")` | Read the stored value
`[Environment]::SetEnvironmentVariable("MYVAR",$null,"User")` | Delete a permanent variable
`Remove-Item Env:MYVAR` | Remove from the current session
`setx MYVAR "value"` | Command Prompt way to set permanently (`/M` for machine). Applies to **new** processes only

Permanent variables are not visible to windows that are already open; restart the terminal. `setx` also truncates values over 1024 characters, so use `[Environment]::SetEnvironmentVariable` for a long `PATH`. In Command Prompt use `set` to show and set session variables and `%NAME%` to expand them.

### Add to PATH
```powershell
$old = [Environment]::GetEnvironmentVariable("Path","User")
[Environment]::SetEnvironmentVariable("Path", "$old;C:\Tools", "User")
```
The GUI is under System Properties > Advanced > Environment Variables (`sysdm.cpl`). Package managers such as [Chocolatey](chocolatey.md) add their own entries.

## List of environment variables
Variable | Description
---|---
`%ALLUSERSPROFILE%`|C:\ProgramData
`%APPDATA%`|C:\Users\{username}\AppData\Roaming
`%COMMONPROGRAMFILES%`|C:\Program Files\Common Files
`%COMMONPROGRAMFILES(x86)%`|C:\Program Files (x86)\Common Files
`%CommonProgramW6432%`|C:\Program Files\Common Files
`%COMSPEC%`|C:\Windows\System32\cmd.exe
`%HOMEDRIVE%`|C:\
`%HOMEPATH%`|\Users\{username} (without the drive letter)
`%LOCALAPPDATA%`|C:\Users\{username}\AppData\Local
`%LOGONSERVER%`|\\{domain_logon_server}
`%PATH%`|C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem (plus anything installed)
`%PathExt%`|.com;.exe;.bat;.cmd;.vbs;.vbe;.js;.jse;.wsf;.wsh;.msc
`%PROGRAMDATA%`|C:\ProgramData
`%PROGRAMFILES%`|C:\Program Files
`%ProgramW6432%`|C:\Program Files
`%PROGRAMFILES(X86)%`|C:\Program Files (x86)
`%PROMPT%`|$P$G
`%SystemDrive%`|C:
`%SystemRoot%`|C:\Windows
`%TEMP%`|C:\Users\{username}\AppData\Local\Temp
`%TMP%`|C:\Users\{username}\AppData\Local\Temp
`%USERDOMAIN%`|Userdomain associated with current user.
`%USERDOMAIN_ROAMINGPROFILE%`|Userdomain associated with roaming profile.
`%USERNAME%`|{username}
`%USERPROFILE%`|C:\Users\{username}
`%WINDIR%`|C:\Windows
`%PUBLIC%`|C:\Users\Public
`%PSModulePath%`|PowerShell module search path (user, program files and system modules)
`%OneDrive%`|C:\Users\{username}\OneDrive
`%DriverData%`|C:\Windows\System32\Drivers\DriverData
`%CD%`|Outputs current directory path. (Command Prompt.)
`%CMDCMDLINE%`|Outputs command line used to launch current Command Prompt session. (Command Prompt.)
`%CMDEXTVERSION%`|Outputs the number of current command processor extensions. (Command Prompt.)
`%COMPUTERNAME%`|Outputs the system name.
`%DATE%`|Outputs current date. (Command Prompt.)
`%TIME%`|Outputs time. (Command Prompt.)
`%ERRORLEVEL%`|Outputs the exit status of the previous command. (Command Prompt.)
`%PROCESSOR_ARCHITECTURE%`|CPU architecture, e.g. AMD64 or ARM64
`%PROCESSOR_IDENTIFIER%`|Outputs processor identifier.
`%PROCESSOR_LEVEL%`|Outputs processor level.
`%PROCESSOR_REVISION%`|Outputs processor revision.
`%NUMBER_OF_PROCESSORS%`|Outputs the number of logical processors.
`%RANDOM%`|Outputs random number from 0 through 32767. (Command Prompt.)
`%OS%`|Windows_NT

`%CD%`, `%DATE%`, `%TIME%`, `%ERRORLEVEL%` and `%RANDOM%` are dynamic Command Prompt values and do not exist as `$env:` variables in PowerShell. For WSL variables see [WSL Cheat-Sheet](../tools/wsl.md).
