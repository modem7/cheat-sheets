# Docker Volume Backup
Docker named volumes and bind mounts hold the state of your containers. This sheet covers three approaches: a one-off `tar` through a throwaway container, the `offen/docker-volume-backup` sidecar for scheduled archives to local or S3 storage, and feeding bind mounts to [restic](restic.md) or [borgmatic](borgmatic.md). For general Docker commands see [Docker](../docker/docker.md) and [Docker-Compose](../docker/docker-compose.md).

Documentation: [offen/docker-volume-backup](https://offen.github.io/docker-volume-backup/) · [Configuration reference](https://offen.github.io/docker-volume-backup/reference/) · [Docker: back up, restore or migrate volumes](https://docs.docker.com/engine/storage/volumes/#back-up-restore-or-migrate-data-volumes)

> **Verification:** The `offen/docker-volume-backup` variable and label names (`BACKUP_CRON_EXPRESSION`, `BACKUP_FILENAME`, `BACKUP_RETENTION_DAYS`, `BACKUP_PRUNING_PREFIX`, `AWS_S3_BUCKET_NAME`, `AWS_ENDPOINT`, `GPG_PASSPHRASE`, `BACKUP_STOP_DURING_BACKUP_LABEL`, the `stop-during-backup`, `archive-pre` and `exec-label` labels) were checked against its reference. The deprecated names noted below come from the same page. The plain `tar` recipes are standard but were not executed or re-checked. The latest major version of the image was **not** verified, pin a tag you have tested. No command was executed.

See also: [Backup Strategy](backup.md) · [Database Dumps](database-dumps.md) · [borgmatic](borgmatic.md) · [restic](restic.md) · [rclone](rclone.md) · [Linux](../linux/linux.md)

---
## Find What to Back Up
COMMAND | DESCRIPTION
---|---
`docker volume ls` | List named volumes
`docker volume inspect <VOLUME>` | Show the mountpoint (usually `/var/lib/docker/volumes/<VOLUME>/_data`)
`docker inspect -f '{{ json .Mounts }}' <CONTAINER>` | Volumes and bind mounts used by a container
`docker compose config --volumes` | Volumes declared in a Compose project
`docker system df -v` | Volume sizes

Bind mounts are ordinary host directories and can be backed up by any file backup tool. Named volumes live under `/var/lib/docker/volumes` and can be backed up from the host as root, or through a container as below.

---
## Quick Tar Backup and Restore
Back up a volume to a tarball in the current directory (the volume is mounted read-only):
```bash
docker run --rm \
  -v <VOLUME>:/data:ro \
  -v "$PWD":/backup \
  alpine tar czf /backup/<VOLUME>-$(date +%F).tar.gz -C /data .
```

Restore into a (new, empty) volume:
```bash
docker volume create <VOLUME>
docker run --rm \
  -v <VOLUME>:/data \
  -v "$PWD":/backup:ro \
  alpine tar xzf /backup/<VOLUME>-<DATE>.tar.gz -C /data
```

Check the archive and its contents without restoring:
```bash
tar tzf <VOLUME>-<DATE>.tar.gz | head
docker run --rm -v <VOLUME>:/data:ro alpine sh -c 'cd /data && find . -type f | wc -l'
```

Notes:
- Run as a container that can preserve ownership (the default root user does). Add `--numeric-ids` for tar if the IDs must survive across hosts: `tar --numeric-owner`.
- Use `tar --xattrs --acls` flags only if the image's tar supports them (busybox tar in Alpine may not, use `apk add tar` or a Debian image if you need them).
- A tar of a volume while the app is running is **crash-consistent only**. Stop the container first, or use the dump approach for databases, see [Database Dumps](database-dumps.md).

Stop, back up, start:
```bash
docker compose stop <SERVICE>
docker run --rm -v <VOLUME>:/data:ro -v "$PWD":/backup alpine tar czf /backup/<VOLUME>.tar.gz -C /data .
docker compose start <SERVICE>
```

---
## offen/docker-volume-backup
A small sidecar container that mounts the volumes read-only at `/backup/<NAME>`, optionally stops labelled containers, writes a `.tar.gz`, and uploads or prunes it on a cron schedule.

```yaml
services:
  app:
    image: ghcr.io/example/app:1.2.3
    volumes:
      - app_data:/var/lib/app
    labels:
      # Stop this container while the archive is written (consistent copy)
      - docker-volume-backup.stop-during-backup=true

  backup:
    image: offen/docker-volume-backup:<TAG>
    restart: always
    environment:
      BACKUP_CRON_EXPRESSION: "0 2 * * *"
      BACKUP_FILENAME: "app-backup-%Y-%m-%dT%H-%M-%S.tar.gz"
      BACKUP_PRUNING_PREFIX: "app-backup-"
      BACKUP_RETENTION_DAYS: "14"
    volumes:
      - app_data:/backup/app_data:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./backups:/archive              # local copy of the archives

volumes:
  app_data:
```

Upload to S3-compatible storage by adding:
```yaml
    environment:
      AWS_S3_BUCKET_NAME: <BUCKET>
      AWS_ENDPOINT: <ENDPOINT>           # omit for AWS itself
      AWS_ACCESS_KEY_ID: <ACCESS_KEY_ID>
      AWS_SECRET_ACCESS_KEY: <SECRET_ACCESS_KEY>
```
Put secrets in an `.env` file or Docker secrets (`*_FILE` variants exist for many settings, see the reference) rather than the Compose file.

KEY | DESCRIPTION
---|---
`BACKUP_CRON_EXPRESSION` | Schedule, standard cron syntax
`BACKUP_FILENAME` | Archive name template using Go-style `%Y-%m-%d` placeholders
`BACKUP_RETENTION_DAYS` | Delete archives older than this
`BACKUP_PRUNING_PREFIX` | Only prune files starting with this prefix (set it, so pruning cannot touch other files)
`GPG_PASSPHRASE` | Encrypt the archive symmetrically with GPG
`BACKUP_STOP_DURING_BACKUP_LABEL` | Change the label value used to find containers to stop
`docker-volume-backup.stop-during-backup=true` | Label: stop this container during the backup, restart after
`docker-volume-backup.archive-pre` / `.archive-post` | Label: run a command in that container before and after the archive (for example a database dump)
`docker-volume-backup.exec-label` | Label: only run the exec commands for containers sharing this value

Deprecated names (still seen in older guides): `BACKUP_STOP_CONTAINER_LABEL` (use `BACKUP_STOP_DURING_BACKUP_LABEL`), the `exec-pre` and `exec-post` labels (use `archive-pre` and `archive-post`), and the `EMAIL_*` settings (use `NOTIFICATION_URLS`).

Dump a database into the volume before archiving:
```yaml
  db:
    image: postgres:17
    labels:
      - docker-volume-backup.archive-pre=/bin/sh -c 'pg_dump -U postgres -Fc app > /tmp/backup/app.dump'
    volumes:
      - db_dump:/tmp/backup
  backup:
    volumes:
      - db_dump:/backup/db_dump:ro
```

Run one backup now and check the result:
```bash
docker exec <BACKUP_CONTAINER> backup
ls -lh ./backups
tar tzf ./backups/<ARCHIVE>.tar.gz | head
```

Restore (stop the app first, then extract over the volume):
```bash
docker compose stop app
docker run --rm -v app_data:/data -v "$PWD/backups":/archive:ro alpine \
  sh -c 'cd /data && tar xzf /archive/<ARCHIVE>.tar.gz --strip-components=2 -C /data'
docker compose start app
```
`--strip-components` depends on the archive layout: the archive stores paths under `backup/<NAME>/...`, so list it first (`tar tzf`) and adjust.

---
## Using restic or borgmatic Instead
Prefer deduplicated, encrypted repositories over many full tarballs once the data is large.

- Mount named volumes or bind mounts **read-only** into the backup container and back up that path. See the compose example in [borgmatic](borgmatic.md).
- With a named volume on the host, back up `/var/lib/docker/volumes/<VOLUME>/_data` directly with [restic](restic.md). Stop the container first or accept crash-consistency.
- Hooks in borgmatic can stop labelled containers before the backup and always restart them afterwards (`states: [finish, fail]`).

---
## Compose Files and Config
Back up the project directory (`compose.yaml`, `.env`, config files) too, because volumes alone do not rebuild the stack. Keep non-secret parts in git. Keep `.env` in the encrypted backup. A full rebuild needs: compose files, `.env`, volume data, and database dumps.

---
## Gotchas
- `docker compose down -v` deletes named volumes. Take a backup before running it.
- A restore into a volume that already has data merges and overwrites. Restore into a **new** volume, test, then switch.
- File ownership matters: restore as root and keep numeric IDs so the app's UID can still read the data.
- Do not back up `/var/lib/docker` wholesale while the daemon runs. Back up volumes and Compose files, not the engine state.
