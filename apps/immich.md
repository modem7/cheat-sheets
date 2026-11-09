# Immich
Immich is a self-hosted photo and video library with mobile backup, face recognition and search. It is a Docker Compose stack of a server, a machine-learning service, Redis-compatible cache and PostgreSQL.

Documentation: [Immich docs](https://docs.immich.app/)

## Install
```bash
wget -O docker-compose.yml https://github.com/immich-app/immich/releases/latest/download/docker-compose.yml
wget -O .env https://github.com/immich-app/immich/releases/latest/download/example.env
docker compose up -d
```

Edit `.env` before the first start:

VARIABLE | DESCRIPTION
---|---
`UPLOAD_LOCATION` | Where photos and videos live (default `./library`). Put it on large, backed-up storage
`DB_DATA_LOCATION` | PostgreSQL data (default `./postgres`). Use a local disk, not a network share
`IMMICH_VERSION` | Image tag. The example uses the major tag `v3`, so pin a release for control
`DB_PASSWORD` | Change from the default `postgres`
`TZ` | Time zone

The web UI is on port 2283 (`IMMICH_PORT`). Put it behind a [reverse proxy](../homelab/reverse-proxy-patterns.md) for HTTPS. The first user to register becomes the admin. Always check the release notes before upgrading, as major versions can have breaking changes.

## Upgrade
```bash
docker compose pull && docker compose up -d
docker image prune
```

Do not downgrade. Pin a tag such as `v3` if you want control over when updates arrive.

## Backup
- Immich creates database dumps daily at 02:00 into `UPLOAD_LOCATION/backups` and keeps 14. A manual dump is under Administration, Job Queues, Create Database Dump.
- Back up `UPLOAD_LOCATION` (the critical folders are `library`, `upload` and `profile`, plus `thumbs` and `encoded-video`, which can be regenerated).
- Dump the database first, then copy the files.

```bash
docker exec -t immich_postgres pg_dump --clean --if-exists --dbname=DB_NAME --username=DB_USER | gzip > /path/to/backup/dump.sql.gz
```

Use [Restic](../backup/restic.md) or [Borg](../backup/borg.md) for the file copy. The restore steps were not checked here, so follow the Immich backup page and run a [restore test](../recipes/restore-test-a-backup.md).

## Hardware Acceleration
FEATURE | HOW
---|---
Video transcoding | Download `hwaccel.transcoding.yml` from the release, uncomment `extends` under `immich-server`. NVENC, QSV (`/dev/dri:/dev/dri`), RKMPP and VAAPI are supported. Linux and WSL2 only. Then enable it under Administration, Video Transcoding
Machine learning | Download `hwaccel.ml.yml`, add `-armnn`, `-cuda`, `-rocm`, `-openvino` or `-rknn` to the machine-learning image tag, and uncomment `extends`. Use `MACHINE_LEARNING_DEVICE_IDS` for several GPUs

## immich-cli
Needs Node.js 22 or later.

COMMAND | DESCRIPTION
---|---
`npm i -g @immich/cli` | Install (or use the `ghcr.io/immich-app/immich-cli` image)
`immich login <URL> <API_KEY>` | Authenticate (create the key in your account settings)
`immich upload --recursive <DIR>` | Upload a folder
`immich upload --recursive --album-name "<NAME>" <DIR>` | Upload into an album
`immich upload --dry-run --recursive <DIR>` | Show what would be uploaded

Other flags: `--album`, `--skip-hash`, `--ignore`, `--delete`, `--include-hidden`, `--concurrency`.

## See Also
- [Nextcloud](nextcloud.md)
- [Syncthing](syncthing.md)
- [Restic](../backup/restic.md)
- [Docker Compose](../docker/docker-compose.md)
