# smartctl
`smartctl` (from smartmontools) reads and tests a disk's SMART data, and `smartd` watches it in the background and emails or notifies you. Use it to catch a failing drive before it dies. SMART is a hint, not a guarantee, so keep [backups](../backup/backup.md) regardless. For the hardware overview see [Hardware Inspection](hardware-inspection.md).

Documentation: [smartmontools](https://www.smartmontools.org/), [smartctl man page](https://linux.die.net/man/8/smartctl) (this mirror is smartmontools 5.43 from 2012, so NVMe and newer options are not covered here)

## Install
```bash
sudo apt install smartmontools
```

## Read Health
COMMAND | DESCRIPTION
---|---
`sudo smartctl --scan` | List devices smartctl can see
`sudo smartctl -i /dev/sdX` | Model, serial, firmware, capacity, SMART enabled
`sudo smartctl -H /dev/sdX` | Overall health verdict (PASSED or FAILED)
`sudo smartctl -A /dev/sdX` | Attribute table (ATA drives)
`sudo smartctl -a /dev/sdX` | Everything ATA: health, info, capabilities, attributes, error and self-test logs
`sudo smartctl -x /dev/sdX` | Extended output, including more logs
`sudo smartctl -c /dev/sdX` | Capabilities and self-test durations
`sudo smartctl -l error /dev/sdX` | The most recent errors
`sudo smartctl -l selftest /dev/sdX` | Self-test history

A failing `-H` means the drive has failed or predicts failure within 24 hours. A passing `-H` does not mean the drive is healthy, so read the attributes and logs too. An attribute marked "Pre-fail" does not mean the disk is about to fail. The normalised value is compared with the threshold, and at or below it the attribute has failed.

## Self-tests
COMMAND | DESCRIPTION
---|---
`sudo smartctl -t short /dev/sdX` | Short test, a few minutes
`sudo smartctl -t long /dev/sdX` | Full surface scan, can take hours
`sudo smartctl -t conveyance /dev/sdX` | Check for shipping damage
`sudo smartctl -c /dev/sdX` | Shows how long each test takes

Run a test, wait for the stated duration, then read the result with `-l selftest`. Tests run on the drive while it stays usable.

## Attributes Worth Watching
ID | NAME | WHY IT MATTERS
---|---|---
5 | Reallocated sectors | Bad sectors the drive has remapped. A rising count is a warning
187 | Reported uncorrectable errors | Read errors the drive could not correct
188 | Command timeout | Operations that timed out, often cabling or power
197 | Current pending sectors | Sectors waiting to be remapped. Non-zero is a warning
198 | Offline uncorrectable | Sectors that failed during offline scans
199 | UDMA CRC error count | Usually a bad SATA cable or connector

The IDs and meanings are widely used, but were not confirmed from the man page in this pass. Vendors differ, so watch for change over time rather than one reading.

## Device Types
SITUATION | OPTION
---|---
Plain SATA or SAS on Linux | Usually automatic
USB enclosure | `-d sat` (some bridges need `-d sat` or `-d usbjmicron`, `-d usbcypress`, `-d usbsunplus`)
Behind a MegaRAID controller | `-d megaraid,N` where N is 0 to 127, e.g. `smartctl -a -d megaraid,2 /dev/sda`
NVMe | `smartctl -a /dev/nvme0` or `nvme smart-log /dev/nvme0` (nvme-cli). Not checked in this pass

Use `-n standby` to skip a sleeping disk, and give `-d` as well or the disk may spin up.

## smartd
`smartd` polls every 30 minutes by default. Generate a starting config from a scan:

```bash
sudo smartctl --scan-open -- -a -W 4,45,50 -m admin@example.com | sudo tee /etc/smartd.conf
```

A typical hand-written line (check `smartd.conf(5)` for the exact syntax on your version):

```text
DEVICESCAN -a -o on -S on -s (S/../.././02|L/../../6/03) -m admin@example.com
```

That monitors all disks, runs a short test daily at 02:00 and a long test on Saturdays at 03:00, and emails on problems.

COMMAND | DESCRIPTION
---|---
`sudo smartd -q onecheck` | Check once and exit, to test the config
`sudo smartd -q showtests` | Show the self-test schedule
`sudo systemctl restart smartd` | Reload after editing (service name is `smartd` or `smartmontools` by distro)

The service name and the schedule syntax are from experience, not the man page read here. Monitoring tools such as [Beszel](../apps/beszel.md) can also read SMART data.

## See Also
- [Hardware Inspection](hardware-inspection.md)
- [ZFS](zfs.md)
- [RAID with mdadm](raid-mdadm.md)
- [Beszel](../apps/beszel.md)
