# UniFi Backups and Migration
How to back up UniFi consoles and self-hosted controllers, restore them, and move to new hardware. There are two kinds: System Config Backups on UniFi OS, and Network-only `.unf` files on self-hosted servers.

Documentation: [Backups and Migration](https://help.ui.com/hc/en-us/articles/360008976393) · [Auto backup locations](https://help.ui.com/hc/en-us/articles/205202580)

## System Config Backups (UniFi OS)
Go to Settings, Control Plane, Backups.

TASK | HOW
---|---
Cloud backup | Tick "System Backups". Runs weekly and before each major update, saved to your UI account at account.ui.com/backups. Only the owner manages them
Offline backup | Download a file from the same page
Restore | Choose Restore, then pick a cloud backup or upload a file
Partial restore | Untick "Restore All Applications and Settings"

- Moving to a different console model needs UniFi OS 3.1 or newer.
- **Protect recordings do not migrate.** Back them up separately if you need them.
- Keep one offline copy somewhere that is not the console.

## Network `.unf` Backups
Used on self-hosted Network Servers and older installs. You can back up settings only or include log history.

PLATFORM | AUTOBACKUP PATH
---|---
Software install | `{data.dir}/backup/autobackup`
Cloud Key | `/data/autobackup`
Docker (`jacobalberty`) | `~/unifi/data/backup` (inferred from its volume layout)

Override the location with `autobackup.dir=` in `system.properties`. On the Debian package `data.dir` is probably `/usr/lib/unifi/data` (inferred from the log path, so confirm it).

## Migrate Between Hosts
For example from a legacy Network Server to UniFi OS Server or a Cloud Gateway:

1. Update the new Network application first.
2. Download the `.unf` file from the old one and copy the device SSH credentials.
3. Restore it on the new host.
4. Wait for devices to show online.
5. Shut down the old host, or Forget the devices on it.
6. For devices adopted over layer 3, turn on "Override Inform Host" on the old controller and enter the new IP. If that fails, factory reset and re-adopt, see [UniFi Device CLI and Adoption](unifi-device-cli.md).

On Linux, automatic migration to UniFi OS Server is not available, so use Site Export (Settings, System, Site Management, Export Site) and then Import Site on the new host.

## Before You Upgrade
- Take a fresh backup and download it.
- Check the release notes for the Network version you are moving to.
- Avoid Early Access builds on production.
- Do not downgrade without a backup from the older version. Downgrade behaviour was **not verified**.

## Off-box Copies
Autobackups on a self-hosted host sit in the data directory, so include it in your [restic](../backup/restic.md) or [Borgmatic](../backup/borgmatic.md) job. Stop or snapshot the service first if the database is active.

## Not Verified
Downgrade and rollback behaviour, and exact Debian and Docker data paths.

## See Also
- [UniFi](unifi.md)
- [UniFi Hosting](unifi-hosting.md)
- [UniFi Protect](unifi-protect.md)
- [restic](../backup/restic.md)
