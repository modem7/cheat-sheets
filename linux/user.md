# User Management
Create, change and remove users and groups, set up sudo and SSH keys, and inspect logins. Debian/Ubuntu `adduser` is a friendlier wrapper around the lower-level `useradd` found on every distribution. See also [Linux](linux.md), [OpenSSH Cheat-Sheet](../tools/openssh.md) and [Linux Basics](linuxbasics.md).

> **Verification:** commands follow the man pages. No command was executed. Always keep a second root session open when changing sudo or SSH settings.

## Users
COMMAND | DESCRIPTION
---|---
`sudo adduser <USER>` | Create a user interactively (Debian/Ubuntu)
`sudo useradd -m -s /bin/bash -G sudo <USER>` | Create with home, shell and groups (any distro; the admin group is `wheel` on RHEL)
`sudo useradd -r -s /usr/sbin/nologin -d /var/lib/<APP> <APP>` | System account for a service
`sudo passwd <USER>` | Set or change a password
`sudo passwd -l <USER>` / `-u <USER>` | Lock / unlock a password
`sudo passwd -e <USER>` | Force a password change at next login
`sudo chage -l <USER>` | Password ageing info
`sudo chage -M 90 <USER>` | Password expires after 90 days
`sudo chage -E 2026-12-31 <USER>` | Account expires on a date
`sudo usermod -aG <GROUP> <USER>` | Add to a group (keep `-a`, without it the other groups are replaced)
`sudo usermod -s /usr/sbin/nologin <USER>` | Disable interactive login
`sudo usermod -L <USER>` | Lock the account
`sudo usermod -l <NEW> <OLD>` | Rename a user (home and group are not renamed)
`sudo usermod -d /new/home -m <USER>` | Move the home directory
`sudo userdel <USER>` | Delete a user, keep the home
`sudo userdel -r <USER>` | Delete the user and home and mail
`sudo deluser <USER> <GROUP>` | Remove a user from a group (Debian)
`sudo gpasswd -d <USER> <GROUP>` | Remove a user from a group (any distro)

New group membership applies at the next login. Use `newgrp <GROUP>` or log out and in. For Docker see [Docker](../docker/docker.md).

## Groups
COMMAND | DESCRIPTION
---|---
`sudo groupadd <GROUP>` | Create a group
`sudo groupadd -r <GROUP>` | System group
`sudo groupmod -n <NEW> <OLD>` | Rename a group
`sudo groupdel <GROUP>` | Delete a group
`groups <USER>` | Groups of a user
`id <USER>` | UID, GID and groups
`getent group <GROUP>` | Members of a group
`getent passwd <USER>` | Account entry (also LDAP, SSSD)

## Inspect Users and Logins
COMMAND | DESCRIPTION
---|---
`whoami` / `id` | Current user
`who` / `w` | Who is logged in and what they run
`last -n 20` | Recent logins
`lastb -n 20` | Failed logins (root)
`lastlog` | Last login per user
`sudo lastlog -u <USER>` | One user
`loginctl list-sessions` | Sessions from systemd-logind
`getent passwd \| awk -F: '$3 >= 1000 {print $1}'` | List normal users
`sudo awk -F: '($2 == "") {print $1}' /etc/shadow` | Accounts with an empty password
`awk -F: '($3 == 0) {print $1}' /etc/passwd` | Accounts with UID 0 (should be only root)
`sudo pkill -KILL -u <USER>` | Kill all of a user's processes

## sudo
COMMAND | DESCRIPTION
---|---
`sudo -l` | What you may run
`sudo -u <USER> <CMD>` | Run as another user
`sudo -i` | Root login shell
`sudo -s` | Root shell with your environment
`sudo visudo` | Edit `/etc/sudoers` safely (syntax check on save)
`sudo visudo -f /etc/sudoers.d/<NAME>` | Edit a drop-in file
`sudo visudo -c` | Check all sudoers files

Examples for `/etc/sudoers.d/deploy` (mode `0440`):
```
# full sudo without a password (use for automation accounts only)
deploy ALL=(ALL) NOPASSWD:ALL

# a few specific commands without a password
deploy ALL=(root) NOPASSWD: /bin/systemctl restart myapp, /bin/systemctl status myapp

# a group
%admins ALL=(ALL) ALL
```
Never edit sudoers with a plain editor. A syntax error locks everyone out of sudo.

## SSH Keys for a User
```bash
sudo install -d -m 700 -o <USER> -g <USER> /home/<USER>/.ssh
echo '<PUBLIC-KEY>' | sudo tee -a /home/<USER>/.ssh/authorized_keys
sudo chown <USER>:<USER> /home/<USER>/.ssh/authorized_keys
sudo chmod 600 /home/<USER>/.ssh/authorized_keys
```
Or, from the client: `ssh-copy-id -i ~/.ssh/id_ed25519.pub <USER>@<HOST>`. Hardening the daemon (`PasswordAuthentication no`, `PermitRootLogin no`) is covered in [OpenSSH Cheat-Sheet](../tools/openssh.md).

## Files and Defaults
PATH | DESCRIPTION
---|---
`/etc/passwd` | Accounts (no passwords)
`/etc/shadow` | Password hashes and ageing, root-readable only
`/etc/group` | Groups and members
`/etc/sudoers`, `/etc/sudoers.d/` | sudo policy
`/etc/login.defs` | Defaults: UID range, password ageing, `UMASK`
`/etc/skel/` | Files copied into new home directories
`/etc/subuid`, `/etc/subgid` | Sub-UID ranges (rootless containers, see [Docker](../docker/docker.md))
`/etc/security/limits.conf` | Per-user resource limits

`sudo vipw` and `sudo vigr` edit `passwd` and `group` with locking.

## Lock Down an Account
```bash
sudo usermod -L -e 1 <USER>          # lock password and expire the account
sudo pkill -KILL -u <USER>           # end running sessions
sudo mv /home/<USER>/.ssh/authorized_keys{,.disabled}
```
