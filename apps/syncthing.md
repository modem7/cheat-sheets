# Syncthing
Syncthing is continuous, peer-to-peer file synchronisation with end-to-end encryption and no central server. Use it to keep folders in sync across machines. It is not a backup tool, because a deletion syncs too. See [Restic](../backup/restic.md) for backups.

Documentation: [Syncthing docs](https://docs.syncthing.net/)

## Ports
PORT | USE
---|---
`22000/tcp` | Sync connections
`22000/udp` | Sync over QUIC
`21027/udp` | Local discovery
`8384/tcp` | Web GUI (listens on `127.0.0.1` by default)

Open the sync ports on the firewall (`sudo ufw allow syncthing`, or `sudo firewall-cmd --zone=public --add-service=syncthing --permanent`). To reach the GUI remotely set the GUI address to `0.0.0.0:8384`, and **set a GUI user and password first**.

## Docker
The official image is `syncthing/syncthing` (the compose layout and image details were not checked against the docs here, so confirm them in the Docker section of the README).

## Commands
COMMAND | DESCRIPTION
---|---
`syncthing` / `syncthing serve` | Run Syncthing
`syncthing serve --no-browser` | Run without opening a browser
`syncthing serve --gui-address=0.0.0.0:8384` | Change the GUI listen address
`syncthing generate --gui-user=<USER> --gui-password=<PASSWORD>` | Create config and set GUI credentials
`syncthing device-id` | Show this device's ID
`syncthing paths` | Show config, data and log paths
`syncthing upgrade --check-only` | Check for a new version
`syncthing cli <COMMAND>` | Talk to the running instance (`config`, `show`, `operations`, `errors`, `debug`)

The default config directory is `$XDG_STATE_HOME/syncthing`, or `~/.local/state/syncthing` on Unix and `%LOCALAPPDATA%\Syncthing` on Windows.

## Folder Types
TYPE | BEHAVIOUR
---|---
Send & Receive | Default, two-way sync
Send Only | Incoming changes are ignored. **Override Changes** pushes this copy over the others
Receive Only | Local changes are not sent. **Revert Local Changes** discards them
Receive Encrypted | For an untrusted host (details not checked here)

## Ignore Patterns (.stignore)
Put `.stignore` in the folder root. The first matching pattern wins.

```text
(?d).DS_Store
(?d)Thumbs.db
/node_modules
*.tmp
!important.tmp
```

- `*`, `**`, `?`, `[]` and `{}` are wildcards. A leading `/` anchors to the folder root and `!` negates.
- `(?d)` lets Syncthing delete an ignored file if it blocks removing a directory. `(?i)` is case-insensitive.
- `//` starts a comment, and `#include <FILE>` pulls in another file.

## Versioning
TYPE | KEEPS
---|---
`trashcan` | Deleted and replaced files in `.stversions`
`simple` | The last N versions
`staggered` | Versions thinned by age (30s, 1h, 1d, 30d, then until `maxAge`)
`external` | Runs your command

Parameters include `cleanoutDays`, `keep`, `maxAge` and `command`. Versions are the safety net for accidental deletions, so enable one on important folders.

## Relays
Relaying is on by default and only used when a direct connection fails, retrying direct periodically. Traffic stays end-to-end encrypted, but the relay operator can see the volume. To use your own relay set `relay://HOST[:PORT]/?id=RELAY_DEVICE_ID`.

## See Also
- [Nextcloud](nextcloud.md)
- [Immich](immich.md)
- [Restic](../backup/restic.md)
- [Obsidian](../tools/obsidian.md)
