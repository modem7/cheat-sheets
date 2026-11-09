# Sysinternals
Sysinternals is Microsoft's free toolkit of small Windows diagnostic tools: process, disk, network and autostart inspection that goes deeper than Task Manager. Use it alongside [Windows Troubleshooting](windows-troubleshooting.md).

Documentation: [Sysinternals Suite](https://learn.microsoft.com/en-us/sysinternals/downloads/sysinternals-suite)

## Install
COMMAND | DESCRIPTION
---|---
`winget install Microsoft.Sysinternals.Suite` | Install the whole suite with [winget](winget.md)
`https://live.sysinternals.com/<TOOL>.exe` | Run a tool straight from Microsoft's share without installing
`\\live.sysinternals.com\tools` | The same share over WebDAV

The winget package ID is from memory, so confirm it with `winget search sysinternals`. On first run each tool shows an EULA prompt. Add `-accepteula` to skip it in scripts.

## GUI Tools
TOOL | USE
---|---
Process Explorer (`procexp`) | Task Manager replacement: process tree, handles, DLLs, VirusTotal check
Process Monitor (`procmon`) | Live file, registry, process and network activity with filters
Autoruns | Everything that starts at boot or sign-in, and where it is configured
TCPView | Live TCP and UDP endpoints and owning process
RAMMap | Where physical memory is going
Disk2vhd | Image a physical disk to a VHD
Sysmon | Service that logs process creation and network events to the event log
BgInfo | Show system info on the desktop wallpaper
ZoomIt | Screen zoom and annotation

## Command-line Tools
COMMAND | DESCRIPTION
---|---
`psexec \\<COMPUTER> -s cmd` | Run a command remotely, `-s` as SYSTEM
`psexec -s -i cmd` | Local SYSTEM shell (`-i` interactive session)
`pslist` | List processes (`-t` for a tree)
`pskill <NAME_OR_PID>` | Kill a process (**destructive**)
`psservice \\<COMPUTER> query` | Query services remotely
`psloggedon` | Who is signed in
`du -l 1 C:\` | Disk usage per folder (`-l` sets depth)
`handle <NAME>` | Find which process holds a file open
`listdlls <PROCESS>` | DLLs loaded in a process
`accesschk <USER> <PATH>` | Effective permissions on a file, key or service
`streams -s <PATH>` | Show NTFS alternate data streams
`sigcheck -u -e <PATH>` | List unsigned executables
`strings <FILE>` | Print readable text from a binary
`autorunsc -a * -c` | Autoruns as CSV for scripting
`tcpvcon -a` | Console TCPView

## Common Jobs
- **Locked file or "in use":** `handle <FILENAME>`, or Process Explorer, Find, Find Handle or DLL.
- **Slow boot or sign-in:** Autoruns to disable entries, Process Monitor with Options, Enable Boot Logging.
- **Something keeps changing a registry key:** Process Monitor filtered on Path contains the key. See [Windows Registry](registry.md).
- **Unknown connection:** TCPView, then right-click the process for its path and properties.
- **Application cannot find a file or key:** Process Monitor filtered on the process name and Result is `NAME NOT FOUND` or `ACCESS DENIED`.

## Security
PsExec is used by attackers as well as admins, and security tools often flag it. Use it only on machines you administer, and prefer [PowerShell Remoting](powershell-remote.md) where you can.

## Not Verified
Flag details for the command-line tools were written from memory. Run each tool with no arguments to see its own usage text.

## See Also
- [Windows Troubleshooting](windows-troubleshooting.md)
- [Windows Registry](registry.md)
- [winget](winget.md)
- [PowerShell Remoting](powershell-remote.md)
