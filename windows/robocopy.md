# Robocopy
`robocopy` (Robust File Copy) is the built-in Windows tool for copying and mirroring folder trees, with retries, logging, multithreading and permission handling. Run it from `cmd` or PowerShell ([[powershell]]). On Linux the equivalent is `rsync`; see [[linuxbasics]].

Syntax: `robocopy <SOURCE> <DEST> [FILES] [OPTIONS]`. It copies the **contents** of the source folder into the destination folder.

Documentation: [robocopy reference](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/robocopy)

## Common Commands
COMMAND | DESCRIPTION
---|---
`robocopy C:\src D:\dst` | Copy files in the top folder only
`robocopy C:\src D:\dst /E` | Copy subfolders including empty ones
`robocopy C:\src D:\dst /S` | Copy subfolders, skip empty ones
`robocopy C:\src D:\dst *.docx *.xlsx /S` | Only matching files
`robocopy C:\src D:\dst /E /XF *.tmp *.log` | Exclude files
`robocopy C:\src D:\dst /E /XD node_modules .git` | Exclude directories
`robocopy C:\src D:\dst /E /MT:16` | Multithreaded copy with 16 threads (default 8)
`robocopy C:\src D:\dst /E /COPYALL` | Copy data, attributes, timestamps, ACLs, owner and auditing info (needs admin)
`robocopy C:\src D:\dst /E /DCOPY:DAT` | Also keep directory timestamps
`robocopy C:\src D:\dst /E /L` | **Dry run**: list what would happen, copy nothing
`robocopy C:\src D:\dst /E /Z` | Restartable mode (survives network drops, slower)
`robocopy C:\src D:\dst /E /ZB` | Restartable, fall back to backup mode if access is denied
`robocopy C:\src D:\dst /E /J` | Unbuffered I/O, faster for very large files
`robocopy C:\src D:\dst /E /SL` | Copy symbolic links as links, not their targets
`robocopy C:\src D:\dst /E /XJ` | Skip junction points (avoids loops such as profile folders)
`robocopy \\<SERVER>\share D:\dst /E /COPY:DAT /R:2 /W:5` | Copy from a network share with sensible retries

## Copy vs Mirror
MODE | COMMAND | EFFECT
---|---|---
Copy (safe) | `robocopy src dst /E` | Adds new and changed files; never deletes in the destination
Move | `robocopy src dst /E /MOVE` | Copies, then deletes files and folders from the source (`/MOV` moves files only)
Mirror | `robocopy src dst /MIR` | Makes dst identical to src, **deleting** anything in dst that is not in src
Purge | `robocopy src dst /E /PURGE` | Deletes destination files and folders that no longer exist in the source (`/MIR` is `/E /PURGE`)

`/MIR` is `/E /PURGE`. **A wrong destination, or an empty or unavailable source, can wipe the destination.** Always do a dry run first and double check the argument order:
```powershell
robocopy C:\data E:\backup\data /MIR /L /NP /NJH /NJS   # preview only
robocopy C:\data E:\backup\data /MIR /R:2 /W:5 /XA:SH /LOG+:C:\Logs\mirror.log
```
A mirror is not a backup: deletions and corruption replicate too, so keep versioned backups as well. Never mirror onto the root of a drive unless you mean it: `/MIR` can delete protected `System Volume Information` content, so exclude it with `/XD "System Volume Information" '$RECYCLE.BIN'`.

## Retries and Timing
OPTION | DESCRIPTION
---|---
`/R:<N>` | Retries on a failed copy (default is 1,000,000, which can look like a hang)
`/W:<S>` | Seconds between retries (default 30)
`/REG` | Save `/R` and `/W` as defaults in the registry
`/TBD` | Wait for share names to be defined (retry error 67)
`/MON:<N>` | Monitor the source and rerun after N changes
`/MOT:<M>` | Monitor and rerun every M minutes
`/RH:hhmm-hhmm` | Run only within a time window (run hours)
`/IPG:<MS>` | Inter-packet gap in ms to throttle bandwidth on slow links
`/MAXAGE:<N>` / `/MINAGE:<N>` | Exclude files older or newer than N days (or a `YYYYMMDD` date)
`/MAX:<BYTES>` / `/MIN:<BYTES>` | Exclude files larger or smaller than a size
`/XO` | Exclude older files (do not overwrite newer destination files)
`/XC` / `/XN` | Exclude changed / newer files
`/FFT` | Assume FAT file times (2 second granularity), useful for NAS and Linux shares
`/COMPRESS` | Request SMB compression (Windows 11 and Server 2022, SMB 3.1.1)

Always set `/R` and `/W` for unattended jobs, for example `/R:3 /W:10`.

## What Gets Copied
`/COPY:<flags>` picks the file info (default `DAT`): **D** data, **A** attributes, **T** timestamps, **S** NTFS security (ACLs), **O** owner, **U** auditing.

OPTION | DESCRIPTION
---|---
`/COPY:DAT` | Default: data, attributes, timestamps
`/COPY:DATS` | Add ACLs
`/COPYALL` | Same as `/COPY:DATSOU`
`/SEC` | Same as `/COPY:DATS`
`/DCOPY:DAT` | Copy directory data, attributes and timestamps (`T` is important for folder dates)
`/NOCOPY` | Copy no file info (use with `/PURGE`)
`/A+:R` / `/A-:R` | Add or remove the read-only attribute on copied files
`/XA:SH` | Exclude system and hidden files
`/IT` | Include tweaked files (same size and time, different attributes)
`/SECFIX` | Fix ACLs on all files, even skipped ones
`/TIMFIX` | Fix timestamps on all files, even skipped ones

For a full file server migration with permissions: `robocopy <SRC> <DST> /MIR /COPYALL /DCOPY:DAT /R:3 /W:5 /MT:16 /XJ /LOG:C:\Logs\migrate.log /TEE /NP`.

## Logging and Output
OPTION | DESCRIPTION
---|---
`/LOG:<FILE>` | Write output to a file (overwrites)
`/LOG+:<FILE>` | Append to an existing log
`/UNILOG:<FILE>` / `/UNILOG+:<FILE>` | Unicode log (use when file names contain non-ASCII characters)
`/TEE` | Also print to the console
`/NP` | No progress percentage (keeps logs clean)
`/NFL` / `/NDL` | No file names / no directory names in the log
`/NJH` / `/NJS` | No job header / no job summary
`/V` | Verbose, show skipped files
`/FP` | Full path names in the output
`/BYTES` | Print sizes in bytes
`/ETA` | Show estimated time of arrival
`/L` | List only (no changes)

## Exit Codes
The exit code is a bit field, so it is a **sum**. Codes 0 to 7 are success or partial success; 8 and above indicate failures.

CODE | MEANING
---|---
0 | Nothing copied, no differences
1 | Files copied successfully
2 | Extra files or directories in the destination that are not in the source
3 | 1 + 2: files copied and extras detected
4 | Mismatched files or directories (same name, different type)
5 | 1 + 4
6 | 2 + 4
7 | 1 + 2 + 4: files copied, extras and mismatches
8 | Some files or directories could **not** be copied (failures after retries)
16 | Fatal error: nothing was copied (bad path, bad syntax, access denied)

Add them: 9 means files copied plus failures. In scripts treat `-ge 8` as an error:
```powershell
robocopy C:\src D:\dst /E /R:2 /W:5 /LOG:C:\Logs\job.log /NP
if ($LASTEXITCODE -ge 8) { Write-Error "Robocopy failed with code $LASTEXITCODE"; exit $LASTEXITCODE }
else { $global:LASTEXITCODE = 0 }   # reset so schedulers and CI do not see 1 to 7 as failure
```
In batch files use `if %ERRORLEVEL% GEQ 8 (echo failed)`.

## Scheduled Backup Example
```powershell
$roboArgs = '"D:\Data" "\\<NAS>\backup\Data" /MIR /R:3 /W:10 /MT:8 /XJ /NP /LOG+:"C:\Logs\backup.log"'
$action  = New-ScheduledTaskAction -Execute "robocopy.exe" -Argument $roboArgs
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName "NightlyRobocopy" -Action $action -Trigger $trigger -User "SYSTEM" -RunLevel Highest
```
Scheduled tasks are covered in [[powershell]].

## Troubleshooting
SYMPTOM | FIX
---|---
Looks hung | Too many retries on a locked file: set `/R:2 /W:5`
`ERROR 5 (0x00000005) Access is denied` | Run elevated, use `/ZB` or `/B`, check NTFS and share permissions
`ERROR 32` file in use | Close the program or use VSS snapshots for open files; robocopy has no built-in VSS support
`ERROR 123` / `ERROR 3` path problems | Check quoting and trailing backslash: `"C:\path with spaces\"` ends the quote early; write `"C:\path with spaces\\"` or drop the trailing `\`
Copies everything every time | Time-stamp granularity: add `/FFT` for NAS or FAT; use `/DCOPY:T`
Long paths (over 260 characters) | Robocopy handles long paths; use `\\?\` prefix if needed and enable long paths in Windows
Source and destination swapped | Always test with `/L` first; sources go first

## Alternatives
TOOL | USE
---|---
`xcopy` | Legacy, fewer options, no mirror
`Copy-Item -Recurse` | Simple PowerShell copies, no retries or mirror
`rsync` (via [[wsl]]) | Delta transfers over SSH ([[openssh]])
`robocopy` | Large trees, permissions, mirrors, resumable network copies

## Not Verified
Options and exit codes were written from the Microsoft documentation and not executed. `/COMPRESS` needs recent Windows and SMB versions.
