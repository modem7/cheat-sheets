# Disk Usage
Find out what is filling a disk with `df`, `du`, `ncdu` and `lsof`. Start with `df` to see which filesystem is full, then `du` or `ncdu` to find the directory, and check for deleted files that are still held open.

Documentation: [df(1)](https://man7.org/linux/man-pages/man1/df.1.html) · [du(1)](https://man7.org/linux/man-pages/man1/du.1.html) · [ncdu](https://dev.yorhel.nl/ncdu/man)

> **Verification:** options were checked against the GNU coreutils man pages and `ncdu` 1.19 in Ubuntu 24.04. Examples were not run against a full disk.

## Filesystem Space (df)
COMMAND | DESCRIPTION
---|---
`df -h` | Used and free space per filesystem, human-readable
`df -hT` | Add the filesystem type
`df -i` | Inode usage (a full inode table looks like a full disk)
`df -h /var` | The filesystem holding a path
`df -h -x tmpfs -x devtmpfs` | Hide virtual filesystems
`findmnt` | Mount tree with sources and options

## Directory Size (du)
COMMAND | DESCRIPTION
---|---
`du -sh <PATH>` | Total size of one path
`du -h --max-depth=1 <PATH>` | Size of each immediate child
`du -h --max-depth=1 <PATH> \| sort -rh \| head -20` | Largest children first
`sudo du -xh --max-depth=1 /` | Stay on one filesystem (`-x`), skipping other mounts
`du -ah <PATH> \| sort -rh \| head -20` | Largest files and directories
`du -sh --apparent-size <FILE>` | Logical size rather than blocks used (sparse files)
`du -sh --exclude='*.log' <PATH>` | Skip a pattern

## Find Large Files
COMMAND | DESCRIPTION
---|---
`find <PATH> -xdev -type f -size +500M` | Files over 500 MiB on one filesystem
`find <PATH> -xdev -type f -size +500M -exec ls -lh {} +` | Same, with sizes
`find <PATH> -xdev -type f -mtime +365` | Files not modified for a year
`sudo ls -lSh /var/log \| head` | Largest files in a directory, biggest first

## ncdu
Interactive browser. Press `d` to delete (it asks first), `q` to quit.

COMMAND | DESCRIPTION
---|---
`ncdu <PATH>` | Scan and browse
`ncdu -x <PATH>` | Stay on one filesystem
`sudo ncdu -x /` | Whole root filesystem
`ncdu -o <FILE> <PATH>` | Save a scan to a file
`ncdu -f <FILE>` | Browse a saved scan (scan a server, browse elsewhere)

## Space Not Freed After Deleting
COMMAND | DESCRIPTION
---|---
`sudo lsof +L1` | Open files with a link count below 1: deleted but still held by a process
`sudo lsof -nP +L1 \| sort -k7 -rn \| head` | Biggest of those first (size is column 7)
`sudo systemctl restart <SERVICE>` | Releasing the file usually means restarting its owner
`: > <FILE>` | Truncate a log in place instead of deleting it (if running as the right user)

## Common Culprits
LOCATION | CLEAN WITH
---|---
`/var/log`, journal | `journalctl --disk-usage`, then `sudo journalctl --vacuum-size=500M`
Docker | `docker system df`, see [Docker Cleanup](../docker/docker-cleanup.md)
APT cache | `sudo apt clean`
Old kernels | `sudo apt autoremove`
Snapshots (ZFS, LVM) | `zfs list -t snapshot`, see [ZFS](zfs.md); `lvs` for LVM, see [LVM](lvm.md)

## Troubleshooting
SYMPTOM | FIX
---|---
`No space left on device` but `df -h` shows free space | Out of inodes: `df -i`; look for directories with millions of small files
`df` and `du` disagree | Deleted-but-open files (`lsof +L1`), or data hidden under a mount point
`du` slow on a network share | Run it on the file server, or use `ncdu -o` there

## See Also
- [Storage and Filesystems](storage-and-filesystems.md)
- [Docker Cleanup](../docker/docker-cleanup.md)
- [Modern CLI Tools](../tools/modern-cli-tools.md)
- [Linux Performance Troubleshooting](performance-troubleshooting.md)
