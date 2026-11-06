# NFS
Network File System (NFS) is a distributed file system protocol originally developed by Sun Microsystems (Sun), available in **[Linux](linux.md)**, allowing a user on a client computer to access files over a computer network much like local storage is accessed. NFS, like many other protocols, builds on the Open Network Computing Remote Procedure Call (ONC RPC) system. NFS is an open IETF standard defined in a Request for Comments (RFC), allowing anyone to implement the protocol.

NFSv4 uses a single TCP port (2049). NFSv3 also needs rpcbind (111) and extra ports. See also [Mount](mount.md).

---
## Install NFS
Install NFS Client on Ubuntu
```
sudo apt -y update
sudo apt -y install nfs-common
```
Install NFS Server on Ubuntu
```
sudo apt -y install nfs-kernel-server
```

## Client Configuration
COMMAND | DESCRIPTION
---|---
`showmount -e <SERVER>` | List exports offered by a server
`sudo mount -t nfs4 <SERVER>:/srv/nfs /mnt/nfs` | Mount an export
`sudo mount -t nfs4 -o ro,nolock,soft,timeo=50 <SERVER>:/srv/nfs /mnt/nfs` | Mount with options
`sudo umount /mnt/nfs` | Unmount
`nfsstat -m` | Show active mounts and their options

Permanent mount in `/etc/fstab`:
```
<SERVER>:/srv/nfs  /mnt/nfs  nfs4  defaults,_netdev,nofail  0  0
```
Test with `sudo mount -a`.

## Server Configuration
### Configuration
Exports are defined in `/etc/exports`:
```
/srv/nfs 192.168.1.0/24(rw,sync,no_subtree_check)
/srv/nfs 192.168.1.2(rw,sync,no_root_squash,subtree_check)
```
OPTION | MEANING
---|---
`rw` / `ro` | Read-write / read-only
`sync` | Reply after data is written (safe, default)
`async` | Reply before write (faster, risk of loss)
`root_squash` | Map remote root to `nobody` (default)
`no_root_squash` | Keep remote root privileges (use only where trusted)
`all_squash,anonuid=1000,anongid=1000` | Map everyone to one local user
`no_subtree_check` | Recommended for most exports
`fsid=0` | Pseudo-root for NFSv4

Create the directory and apply:
```bash
sudo mkdir -p /srv/nfs && sudo chown nobody:nogroup /srv/nfs
sudo exportfs -ra
sudo systemctl enable --now nfs-kernel-server
```

### root rw permissions
Note the **root_squash** mount option. This option is set by default and must be disabled if not wanted.
*Fix:* enable `no_root_squash` in the `/etc/exports` file and reload the permissions with `sudo exportfs -ra`

## Server Commands
COMMAND | DESCRIPTION
---|---
`sudo exportfs -v` | Show active exports and options
`sudo exportfs -ra` | Re-read `/etc/exports`
`sudo exportfs -u <CLIENT>:<PATH>` | Unexport
`sudo ss -tlnp \| grep 2049` | Check NFS is listening
`sudo ufw allow from 192.168.1.0/24 to any port nfs` | Open the firewall to the LAN only ([UFW (uncomplicated firewall)](ufw.md))
`nfsstat -s` | Server statistics

## Troubleshooting
- `access denied by server`: client IP not in `/etc/exports`, or you forgot `exportfs -ra`.
- `Stale file handle`: the export was recreated. Unmount (`umount -f` / `-l`) and mount again.
- Permission denied on write: UID/GID mismatch or `root_squash`. Use matching IDs or `all_squash` with `anonuid`.
- Hangs on boot: add `_netdev,nofail` and consider `soft` only for non-critical data.
- Kubernetes: use the NFS CSI driver or `nfs` volumes ([Kubernetes](../kubernetes/kubernetes.md)).
