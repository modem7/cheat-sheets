# borgmatic
borgmatic wraps [BorgBackup](borg.md) with a YAML config file: one command runs create, prune, compact and check, takes care of database dumps, runs hooks and pings monitoring services. This sheet is for **borgmatic 2.x** (flat config, `commands:` hooks, `repo-create`/`repo-list`) on top of **Borg 1.4**. That is what the `modem7/borgmatic-docker` image ships (borgmatic 2.2.0, Borg 1.4.5 at the time of writing).

Documentation: [borgmatic docs](https://torsion.org/borgmatic/) · [Configuration reference](https://torsion.org/borgmatic/reference/configuration/) · [Command-line actions](https://torsion.org/borgmatic/reference/command-line/actions/) · [Docker image](https://github.com/modem7/docker-borgmatic)

> **Verification:** Action names, the `*_databases` keys, `name: all`, `restore --archive latest --database` and the Healthchecks/Apprise options were checked against the borgmatic docs or the docker-borgmatic repository's own example configs. `check --repair` and the exact 1.x to 2.x migration details were **not** verified. No command was executed. Always run `borgmatic config validate` and a dry run first.

See also: [Backup Strategy](backup.md) · [BorgBackup](borg.md) · [restic](restic.md) · [Database Dumps](database-dumps.md) · [Docker Volume Backup](docker-volume-backup.md) · [Docker](../docker/docker.md) · [Docker-Compose](../docker/docker-compose.md)

---
## Commands
COMMAND | DESCRIPTION
---|---
`borgmatic` | Run the default actions: create, prune, compact, check (only the ones configured)
`borgmatic --verbosity 1 --stats` | Run with progress and statistics (`-v 1`)
`borgmatic --dry-run -v 2` | Show what would happen without changing anything
`borgmatic --config <FILE>` | Use a specific config file (default `/etc/borgmatic/config.yaml`, `/etc/borgmatic.d/*.yaml`, `~/.config/borgmatic/config.yaml`)
`borgmatic config generate --destination <FILE>` | Write a fully commented example config
`borgmatic config validate` | Check the config files
`borgmatic repo-create --encryption repokey-blake2` | Create the repository (borgmatic 2.x name for `init`)
`borgmatic create --stats --list` | Back up only
`borgmatic prune` | Apply the `keep_*` policy
`borgmatic compact` | Free space after prune
`borgmatic check` | Run configured consistency checks
`borgmatic repo-list` | List archives
`borgmatic list --archive latest` | List files in an archive
`borgmatic info` | Repository and archive information
`borgmatic extract --archive latest --path <PATH> --destination <DIR>` | Restore files (no FUSE needed)
`borgmatic mount --archive latest --mount-point <DIR>` | Browse with FUSE
`borgmatic umount --mount-point <DIR>` | Unmount
`borgmatic restore --archive latest --database <NAME>` | Restore a database dump from an archive
`borgmatic key export` | Export the repository key
`borgmatic borg <BORG_ARGS>` | Pass arbitrary arguments to Borg using the config's repository and credentials

`extract` restores files only. Database dumps made by borgmatic are restored with `borgmatic restore`.

---
## Minimal config
`/etc/borgmatic.d/config.yaml` (borgmatic 2.x, flat, no `location:`/`storage:`/`retention:` sections):
```yaml
source_directories:
    - /srv
    - /etc

repositories:
    - path: ssh://<USER>@<HOST>/./borg-repo
      label: offsite
    - path: /mnt/backup/borg-repo
      label: local

exclude_caches: true
one_file_system: true
compression: auto,zstd

# Passphrase: prefer a command or the BORG_PASSPHRASE_FILE/PASSCOMMAND mechanisms, not plain text.
encryption_passcommand: cat /etc/borgmatic.d/passphrase
ssh_command: ssh -i /root/.ssh/id_ed25519

# Explicit name so archives survive a hostname change (see Docker gotcha below).
archive_name_format: '<HOST>-{now:%Y-%m-%dT%H:%M:%S}'

keep_daily: 7
keep_weekly: 4
keep_monthly: 12
keep_yearly: 1

checks:
    - name: repository
      frequency: 2 weeks
    - name: archives
      frequency: 4 weeks
```

Environment variables are expanded in the config: `${VAR}` or `${VAR:-default}`. Use `\${VAR}` for a literal. Example: `path: ${BORG_REPO}`.

Create the repository once, back up, and verify:
```bash
borgmatic config validate
borgmatic repo-create --encryption repokey-blake2
borgmatic --stats -v 1 --list
borgmatic repo-list
borgmatic extract --archive latest --path srv/<APP> --destination /tmp/restore
```
Export and store the key: `borgmatic key export`.

---
## Hooks (`commands:`)
borgmatic 2.x replaces the old `before_backup`, `after_backup`, `on_error` and similar hook lists with a single `commands:` list.

```yaml
commands:
    # Runs once before everything
    - before: everything
      run:
          - echo "starting"
    # Before/after a single action
    - before: action
      when: [create]
      run:
          - /etc/borgmatic.d/dump-stuff.sh
    # After a successful run
    - after: everything
      states: [finish]
      run:
          - /etc/borgmatic.d/after-backup
    # On failure
    - after: everything
      states: [fail]
      run:
          - /etc/borgmatic.d/failed-backup
    # Always restart containers, success or failure
    - after: everything
      states: [finish, fail]
      run:
          - docker compose --project-directory /opt/stacks/app start
```

KEY | MEANING
---|---
`before:` / `after:` | `everything`, `configuration`, `repository`, `action` (and `dump_data_sources` and `error` forms exist, see the reference)
`when:` | For `action`: list of actions such as `create`, `prune`, `check`
`states:` | For `after`: `finish`, `fail`
`run:` | List of shell commands

Soft failure for removable or intermittent targets: a `before` command that exits with status **75** skips the run without raising an error.
```yaml
commands:
    - before: action
      when: [create]
      run:
          - findmnt /mnt/backup-drive > /dev/null || exit 75
```

Old (1.x) to new (2.x) at a glance:
1.x | 2.x
---|---
`location:` / `storage:` / `retention:` / `consistency:` sections | All options at the top level
`before_backup:`, `after_backup:`, `on_error:` hook lists | `commands:` with `before`/`after`, `when`, `states`
`borgmatic init` | `borgmatic repo-create`
`borgmatic list` for archives | `borgmatic repo-list` (and `list` for files)

---
## Native database backups
borgmatic can stream database dumps into the archive, so there is no temp file and no separate cron job. Restore with `borgmatic restore`. See [Database Dumps](database-dumps.md) for standalone dumps.

```yaml
postgresql_databases:
    - name: appdb
      hostname: db
      username: app
      password: ${POSTGRES_PASSWORD}
      format: custom
    - name: all            # every database (pg_dumpall)
      hostname: db
      username: postgres
      password: ${POSTGRES_PASSWORD}

mariadb_databases:
    - name: wpdb
      hostname: mariadb
      username: wp
      password: ${MARIADB_PASSWORD}

sqlite_databases:
    - name: app
      path: /mnt/source/app/app.db
```
Other keys: `mysql_databases`, `mongodb_databases`. `name: all` is not special for SQLite.

```bash
borgmatic restore --archive latest --database appdb          # target database must exist
borgmatic restore --archive latest --database appdb --hostname db
```

---
## Monitoring
Healthchecks.io (pings on start, success and failure):
```yaml
healthchecks:
    ping_url: ${BORG_HEALTHCHECK_URL}
```

Apprise (included in the docker image), borgmatic 1.8.4+:
```yaml
apprise:
    services:
        - url: <APPRISE_URL>
          label: notify
    states: [fail]
    fail:
        title: Backup failed
```
Other supported services include ntfy, Uptime Kuma, Pushover and Cronitor. See the [monitoring reference](https://torsion.org/borgmatic/how-to/monitor-your-backups/).

---
## Docker
Image: [`modem7/borgmatic-docker`](https://github.com/modem7/docker-borgmatic) (S6 Overlay, amd64 and arm64, includes Borg, borgmatic and Apprise).

```yaml
services:
  borgmatic:
    image: modem7/borgmatic-docker:latest
    container_name: borgmatic
    hostname: borgmatic
    restart: unless-stopped
    stop_grace_period: 10m
    volumes:
      - /home:/mnt/source:ro
      - ./data/repository:/mnt/borg-repository
      - ./data/borgmatic.d:/etc/borgmatic.d/
      - ./data/.config/borg:/root/.config/borg
      - ./data/.ssh:/root/.ssh
      - ./data/.cache/borg:/root/.cache/borg
      - ./data/.state/borgmatic:/root/.local/state/borgmatic
    environment:
      - TZ=Europe/London
      - CRON=0 2 * * *
      - BORG_PASSPHRASE_FILE=/run/secrets/borg_passphrase
    secrets:
      - borg_passphrase

secrets:
  borg_passphrase:
    file: ./secrets/borg_passphrase
```

Image behaviour worth knowing:
- Scheduling: `CRON` env var, else `/etc/borgmatic.d/crontab.txt`, else daily at 01:00. `CRON=false` disables it. Use `borgmatic-start` (not `borgmatic`) in a crontab so SIGTERM reaches borgmatic and the repo lock is released.
- `BORG_PASSPHRASE_FILE` (and any `BORG_*_FILE`) is read into the base variable at startup.
- `DOCKERCLI=true` plus `/var/run/docker.sock` lets hooks stop and start labelled containers.
- Mount your sources **read-only** under `/mnt/source`. Archive paths are then `mnt/source/...` without a leading slash.
- `/root/.config/borg` holds keys: back it up.

First run and restore:
```bash
docker exec -it borgmatic borgmatic repo-create --encryption repokey-blake2
docker exec -it borgmatic borgmatic --stats -v 1 --list
docker exec borgmatic borgmatic repo-list
docker exec borgmatic borgmatic config generate -d /etc/borgmatic.d/config.yaml
docker exec borgmatic borgmatic extract --archive latest --path mnt/source/<PATH> --destination /tmp/restore
```
One-shot run without cron:
```bash
docker run --rm -it --hostname borgmatic -e CRON=false -e BORG_PASSPHRASE_FILE=/run/secrets/borg_passphrase \
  -v ./data/borgmatic.d:/etc/borgmatic.d/ -v ./data/repository:/mnt/borg-repository \
  -v ./secrets/borg_passphrase:/run/secrets/borg_passphrase:ro \
  modem7/borgmatic-docker borgmatic repo-list
```

**Hostname gotcha:** the default archive name includes `{hostname}`, and a container's hostname changes on rebuild unless you set `hostname:`. Archives then no longer match `latest`, prune and compact. Pin it with `hostname:` in compose, `archive_name_format: 'myhost-{now:%Y-%m-%dT%H:%M:%S}'`, or `archive_hostname:` (Borg 1.4.5 or newer).

Stopping containers for a consistent copy (label services with `backup`):
```yaml
commands:
    - before: everything
      run:
          - docker ps -q -f "label=backup" | xargs --no-run-if-empty docker container stop -t 60
    - after: everything
      states: [finish, fail]
      run:
          - docker compose --project-directory /opt/stacks/app start
```
Browsing an archive with FUSE needs `SYS_ADMIN` and `/dev/fuse`, which the image's restore compose file sets up. Stale lock: `borg break-lock /mnt/borg-repository`.
