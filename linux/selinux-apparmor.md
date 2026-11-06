# SELinux and AppArmor
Two Linux Mandatory Access Control systems. **SELinux** (RHEL, Fedora, Rocky, Alma) labels every file and process and applies a policy. **AppArmor** (Ubuntu, Debian, SUSE) confines programs with per-path profiles. Both limit what a compromised service can reach, even when it runs as root. Use permissive or complain mode to debug; do not switch them off.

Documentation: [Red Hat SELinux guide](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_selinux/index) · [Ubuntu AppArmor](https://documentation.ubuntu.com/server/how-to/security/apparmor/) · [AppArmor wiki](https://gitlab.com/apparmor/apparmor/-/wikis/home)

> **Verification:** commands follow the distribution documentation and man pages. No command was executed. Package names differ by distribution.

See also: [systemd](systemd.md) · [Linux](linux.md) · [Docker](../docker/docker.md) · [UFW (uncomplicated firewall)](ufw.md)

---
## SELinux

### Status and Modes
COMMAND | DESCRIPTION
---|---
`getenforce` | `Enforcing`, `Permissive` or `Disabled`
`sestatus` | Mode, policy, config file mode
`sudo setenforce 0` | Permissive until reboot (logs denials, blocks nothing)
`sudo setenforce 1` | Enforcing again
`sudo grubby --update-kernel ALL --args selinux=0` | Disable at boot (not recommended)

Persistent mode: `SELINUX=enforcing|permissive|disabled` in `/etc/selinux/config`. Moving from `disabled` to `enforcing` triggers a full relabel on the next boot (`sudo touch /.autorelabel`).

### Contexts
A context looks like `user:role:type:level`. The **type** (for example `httpd_sys_content_t`) is what policy matches.

COMMAND | DESCRIPTION
---|---
`ls -Z <PATH>` | File contexts
`ps -eZ \| grep <NAME>` | Process contexts
`id -Z` | Your own context
`sudo restorecon -Rv <PATH>` | Reset file contexts to the policy default
`sudo semanage fcontext -a -t httpd_sys_content_t "/srv/www(/.*)?"` | Persistent rule for a path
`sudo semanage fcontext -l \| grep <PATH>` | List rules
`sudo chcon -t <TYPE> <FILE>` | Temporary change (lost on relabel). Prefer `semanage` + `restorecon`

Typical fix for a web root in a non-standard place:
```bash
sudo semanage fcontext -a -t httpd_sys_content_t "/srv/www(/.*)?"
sudo restorecon -Rv /srv/www
```
Package: `policycoreutils-python-utils` (RHEL 8+) provides `semanage`.

### Booleans and Ports
COMMAND | DESCRIPTION
---|---
`getsebool -a \| grep httpd` | List booleans
`sudo setsebool -P httpd_can_network_connect on` | Allow httpd outbound connections (`-P` persists)
`sudo setsebool -P httpd_can_network_connect_db on` | Allow httpd to reach a database
`sudo semanage boolean -l` | Booleans with descriptions
`sudo semanage port -l \| grep http` | Ports labelled for a service
`sudo semanage port -a -t http_port_t -p tcp 8081` | Allow a service on a non-standard port
`sudo semanage port -a -t ssh_port_t -p tcp 2222` | Same for SSH

### Read Denials
COMMAND | DESCRIPTION
---|---
`sudo ausearch -m AVC -ts recent` | Recent denials
`sudo ausearch -m AVC -ts today \| audit2why` | Explain why, often names the boolean to flip
`sudo journalctl -t setroubleshoot` | Plain-English alerts (needs `setroubleshoot-server`)
`sudo sealert -a /var/log/audit/audit.log` | Analyse the audit log
`sudo grep denied /var/log/audit/audit.log` | Raw denials

### Build a Local Policy Module (audit2allow)
Only after you have ruled out a wrong label, a boolean or a port label, and have read what you are allowing.
```bash
sudo ausearch -m AVC -ts recent | audit2allow -M myapp
cat myapp.te                      # review it
sudo semodule -i myapp.pp
```
COMMAND | DESCRIPTION
---|---
`sudo semodule -l` | Installed modules
`sudo semodule -r myapp` | Remove a module
`sudo semanage permissive -a httpd_t` | Make one domain permissive, the rest stay enforcing
`sudo semanage permissive -d httpd_t` | Undo

### Containers and Volumes
Bind mounts for Docker and Podman need a label or the container is denied:
```bash
docker run -v /srv/app:/data:Z <IMAGE>    # private label for this container
docker run -v /srv/shared:/data:z <IMAGE> # shared label for several containers
```
Do not use `:Z` on system directories such as `/home` or `/etc`. See [Docker](../docker/docker.md).

---
## AppArmor

### Status
COMMAND | DESCRIPTION
---|---
`sudo aa-status` | Loaded profiles, modes and confined processes
`sudo apparmor_status` | Same
`systemctl status apparmor` | Service state
`ps auxZ \| grep -v unconfined` | Confined processes
`ls /etc/apparmor.d/` | Profiles
`cat /sys/module/apparmor/parameters/enabled` | `Y` if the kernel has it on

### Modes
MODE | EFFECT
---|---
`enforce` | Violations are blocked and logged
`complain` | Violations are logged only (like SELinux permissive)
`unconfined` | No profile

COMMAND | DESCRIPTION
---|---
`sudo aa-complain /etc/apparmor.d/<PROFILE>` | Put a profile in complain mode
`sudo aa-enforce /etc/apparmor.d/<PROFILE>` | Back to enforce
`sudo aa-disable /etc/apparmor.d/<PROFILE>` | Disable a profile (links it into `disable/`)
`sudo apparmor_parser -r /etc/apparmor.d/<PROFILE>` | Reload after editing
`sudo apparmor_parser -R /etc/apparmor.d/<PROFILE>` | Unload
`sudo aa-complain /etc/apparmor.d/*` | All profiles to complain (debugging only)

### Read Denials
COMMAND | DESCRIPTION
---|---
`sudo journalctl -k \| grep -i apparmor` | Kernel log lines with `apparmor="DENIED"`
`sudo dmesg \| grep -i 'apparmor="DENIED"'` | Same from dmesg
`sudo aa-logprof` | Walk through logged events and update profiles interactively
`sudo aa-genprof <PROGRAM>` | Create a new profile by running the program
`sudo aa-notify -s 1 -v` | Summary of denials (desktop)

Install the tools: `sudo apt install apparmor-utils apparmor-profiles`.

### Local Overrides
Do not edit packaged profiles. Add rules to the local include file named in the profile, for example `/etc/apparmor.d/local/usr.sbin.mysqld`:
```
/srv/mysql/ r,
/srv/mysql/** rwk,
```
Then reload: `sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.mysqld`. This is the usual fix when moving a database data directory ([MySQL](../databases/mysql.md), [PostgreSQL Cheat-Sheet](../databases/postgres.md)).

### Docker
Docker applies the `docker-default` AppArmor profile to containers when AppArmor is on.

COMMAND | DESCRIPTION
---|---
`docker run --security-opt apparmor=<PROFILE> <IMAGE>` | Use a custom profile
`docker run --security-opt apparmor=unconfined <IMAGE>` | No AppArmor profile (debugging only)
`docker inspect -f '{{.AppArmorProfile}}' <CONTAINER>` | Profile in use

## Quick Comparison
| | SELinux | AppArmor |
|---|---|---|
| Model | Labels on files and processes | Paths in profiles |
| Default on | RHEL family | Ubuntu, Debian, SUSE |
| Debug mode | Permissive | Complain |
| Denial log | `audit.log` (`ausearch`) | Kernel log / `journalctl -k` |
| Fix helper | `audit2allow`, booleans, `semanage` | `aa-logprof`, local include files |
