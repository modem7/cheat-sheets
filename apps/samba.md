# Samba
Samba serves SMB/CIFS file shares from Linux so Windows, macOS and Linux clients can mount them. Use it for a home NAS-style share on a plain Linux box; for NFS shares between Linux hosts see [NFS](../linux/nfs.md).

Documentation: [smb.conf(5)](https://www.samba.org/samba/docs/current/man-html/smb.conf.5.html) · [Samba wiki](https://wiki.samba.org/index.php/Main_Page)
Project: [Samba](https://www.samba.org/)

> **Verification:** options and parameters were checked against the `smb.conf`, `smbclient`, `smbpasswd`, `pdbedit`, `smbstatus` and `testparm` man pages in Ubuntu 24.04. No share was served to real clients. Package and service names are Debian and Ubuntu; Fedora and RHEL use `samba` and the `smb` service (unverified here).

## Install and Service
COMMAND | DESCRIPTION
---|---
`sudo apt install samba smbclient` | Install the server and client tools
`sudo systemctl enable --now smbd` | Start the file server now and at boot
`sudo systemctl restart smbd` | Apply `smb.conf` changes
`testparm` | Check `smb.conf` syntax and print the effective config
`testparm -s` | Same, without waiting for Enter
`testparm -s --parameter-name='server min protocol'` | Show one parameter
`sudo ss -tlnp \| grep -E ':(139\|445)'` | SMB listening on TCP 139 and 445

## Users
Samba keeps its own password database; each user must already exist as a Linux account.

COMMAND | DESCRIPTION
---|---
`sudo smbpasswd -a <USER>` | Add a Samba user and set its password
`sudo smbpasswd <USER>` | Change a password
`sudo smbpasswd -d <USER>` / `sudo smbpasswd -e <USER>` | Disable / enable
`sudo smbpasswd -x <USER>` | Delete a Samba user
`sudo pdbedit -L` | List Samba users
`sudo pdbedit -L -v` | Details per user

## Share Configuration
Edit `/etc/samba/smb.conf`, then run `testparm` and restart `smbd`.

```ini
[global]
   workgroup = WORKGROUP
   server min protocol = SMB2

[media]
   path = /srv/media
   read only = yes
   guest ok = no
   valid users = @media

[projects]
   path = /srv/projects
   read only = no
   valid users = @staff
   force group = staff
   create mask = 0660
   directory mask = 0770
```

PARAMETER | MEANING
---|---
`path` | Directory to share
`read only = yes` / `no` | Read-only or writable
`valid users` | Who may connect; `@group` for a Linux group
`guest ok` | Allow anonymous access (avoid for anything private)
`browseable = no` | Hide the share from browse lists
`force user`, `force group` | Files are created as this user or group
`create mask`, `directory mask` | Permissions for new files and directories
`hosts allow` | Restrict by client address
`server min protocol` | Lowest SMB version accepted

Permissions on the directory still apply: the Linux user needs filesystem access as well as share access.

```bash
sudo mkdir -p /srv/projects
sudo chgrp staff /srv/projects
sudo chmod 2770 /srv/projects
```

## Test from a Client
COMMAND | DESCRIPTION
---|---
`smbclient -L //<SERVER> -U <USER>` | List shares on a server
`smbclient //<SERVER>/<SHARE> -U <USER>` | Interactive FTP-like session
`smbclient //<SERVER>/<SHARE> -U <USER> -c 'ls'` | Run one command
`sudo mount -t cifs //<SERVER>/<SHARE> /mnt/share -o username=<USER>,uid=1000,gid=1000` | Mount on Linux (needs `cifs-utils`; prompts for the password)
`sudo mount -t cifs //<SERVER>/<SHARE> /mnt/share -o credentials=/root/.smbcreds` | Credentials from a root-only file

The credentials file holds `username=` and `password=` lines; `chmod 600` it.

## Monitor
COMMAND | DESCRIPTION
---|---
`sudo smbstatus` | Connections, open files and locks
`sudo smbstatus -S` | Shares in use
`sudo smbstatus -p` | Connected processes
`sudo smbstatus -L` | Locked files

## Firewall
Allow SMB (TCP 445) only from the LAN. With [UFW (uncomplicated firewall)](../linux/ufw.md):

```bash
sudo ufw allow from 192.0.2.0/24 to any port 445 proto tcp
```

## Troubleshooting
SYMPTOM | FIX
---|---
`NT_STATUS_LOGON_FAILURE` | Wrong password, or the user is not in the Samba database (`pdbedit -L`)
`NT_STATUS_ACCESS_DENIED` | Share `valid users` or filesystem permissions; check both
Share not visible | `browseable`, workgroup name, or the firewall; connect directly by `\\SERVER\SHARE`
Windows cannot connect with an old client | Do not lower `server min protocol` to SMB1; update the client
New files owned by the wrong user | Use `force user` or `force group`, and the setgid bit on the directory
Config change ignored | `testparm`, then `sudo systemctl restart smbd`

## See Also
- [NFS](../linux/nfs.md)
- [Mount](../linux/mount.md)
- [Storage and Filesystems](../linux/storage-and-filesystems.md)
- [UFW (uncomplicated firewall)](../linux/ufw.md)
- [User Management](../linux/user.md)
