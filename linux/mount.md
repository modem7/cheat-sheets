# Mount
In **Linux ([[linux]])**, `mount` attaches a filesystem on a device to a directory. Before a user can access a file on a Unix-like machine, the filesystem on the device which contains the file needs to be mounted. It is used for disks, SD cards, USB storage, ISO images and network shares ([[nfs]]).

---
## List mount-points
```
findmnt (optional)<device/directory>
```

## Unmount
```
umount <device/directory>
```

## Find Devices
COMMAND | DESCRIPTION
---|---
`lsblk -f` | Devices, filesystems, UUIDs and mount points
`sudo blkid` | UUID and type of each device
`df -hT` | Mounted filesystems with usage
`findmnt --real` | Real (non-virtual) mounts as a tree

## Mount
COMMAND | DESCRIPTION
---|---
`sudo mount /dev/sdb1 /mnt/data` | Mount a partition
`sudo mount -o ro /dev/sdb1 /mnt/data` | Mount read-only
`sudo mount -o remount,rw /mnt/data` | Change options of a live mount
`sudo mount -o loop image.iso /mnt/iso` | Mount an ISO image
`sudo mount --bind /src /dst` | Bind-mount a directory elsewhere
`sudo mount -t nfs <SERVER>:/export /mnt/nfs` | NFS share
`sudo mount -t cifs //<SERVER>/share /mnt/smb -o username=<USER>,uid=1000` | SMB/CIFS share
`sudo umount -l /mnt/data` | Lazy unmount a busy mount
`sudo umount -f /mnt/nfs` | Force unmount an unreachable NFS share
`lsof +f -- /mnt/data` / `fuser -vm /mnt/data` | What is keeping a mount busy

## Make It Permanent (`/etc/fstab`)
Use UUIDs, not `/dev/sdX` names, which can change.
```
UUID=1234-ABCD  /mnt/data  ext4  defaults,nofail  0  2
<SERVER>:/export  /mnt/nfs  nfs  defaults,_netdev,nofail  0  0
//<SERVER>/share  /mnt/smb  cifs  credentials=/root/.smbcreds,uid=1000,_netdev,nofail  0  0
```
FIELD | MEANING
---|---
1 | Device, `UUID=`, or remote path
2 | Mount point
3 | Filesystem type
4 | Options (`nofail` avoids a boot hang if absent, `_netdev` waits for the network)
5 | dump flag (0)
6 | fsck order (1 for root, 2 for others, 0 to skip)

Test before rebooting: `sudo mount -a` and `findmnt --verify`. After editing, `sudo systemctl daemon-reload`.

## Format a New Disk
```bash
sudo parted /dev/sdb --script mklabel gpt mkpart primary ext4 0% 100%
sudo mkfs.ext4 /dev/sdb1
```
