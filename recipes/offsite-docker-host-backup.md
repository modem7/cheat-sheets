# Off-Site Docker Host Backup with restic
Back up the volumes, Compose files and databases of a Docker host to an encrypted restic repository on Backblaze B2 (or a Hetzner Storage Box), on a nightly systemd timer with a dead-man's-switch ping.

Documentation: [restic: preparing a repository](https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html) · [restic: scripting](https://restic.readthedocs.io/en/stable/075_scripting.html) · [Healthchecks.io docs](https://healthchecks.io/docs/)

> **Verification:** the restic commands (`init`, `backup`, `--stdin`, `snapshots`, `check --read-data-subset`, `restore --verify`, `dump`, `forget --dry-run`) were run against a local repository with restic 0.19.1 in a container. The B2 S3 endpoint form, the Storage Box SSH setup and the systemd units were **not** run against real accounts and are marked *(unverified)* where they rely on provider behaviour.

## Goal
Every night the host pushes a deduplicated, encrypted snapshot of `/opt/stacks`, `/etc` and fresh database dumps to a bucket you do not control from the host's own credentials alone. Old snapshots are thinned, the repository is checked, and you are alerted when a night is missed.

## Prerequisites
- A Docker host laid out as in [Docker Service Deploy](docker-service-deploy.md) (stacks in `/opt/stacks/<NAME>`)
- restic installed (`sudo apt install restic`) on the host
- **Either** a Backblaze B2 account **or** a Hetzner Storage Box ([Backblaze B2](../cloud/provider/backblaze-b2.md), [Hetzner Cloud](../cloud/provider/hetzner-cloud.md))
- A free Healthchecks.io check (or a self-hosted one) for the ping URL
- A place off the host for the restic password (a password manager, see [Backup Strategy](../backup/backup.md))

> **The restic password is the key.** Lose it and every snapshot is unreadable. Store it somewhere other than this host before you run `restic init`.

## Steps
### 1. Decide what goes in
Back up the data you cannot rebuild: bind-mounted data directories, named volumes, Compose files, `.env` files and secrets, and logical database dumps. Skip image layers and caches ([Docker Volume Backup](../backup/docker-volume-backup.md)).

```bash
docker volume ls
docker inspect --format '{{ range .Mounts }}{{ .Type }} {{ .Source }}{{ "\n" }}{{ end }}' <CONTAINER>
```
Named volumes live under `/var/lib/docker/volumes`. Backing up a live database directory gives an inconsistent copy, so dump databases first (step 5).

### 2. Create the bucket and a restricted key (Backblaze B2)
Create a **private** bucket and a **bucket-restricted** application key with read and write access ([Backblaze B2](../cloud/provider/backblaze-b2.md)). Do not use the master key. The restic documentation recommends B2's **S3-compatible API** over the native `b2:` backend because of error-handling issues in the B2 library, and asks for the key to be created with at least read and write access to the bucket. The S3 backend only hides files it no longer needs, so also add the B2 lifecycle rule "Keep only the last version of the file".

For the Storage Box instead, enable SSH support in the Storage Box settings and install your public key on it (see the [Hetzner Storage Box docs](https://docs.hetzner.com/storage/storage-box/access/access-ssh-rsync-borg)) *(unverified)*. SSH, SFTP and Borg use port 23 on a Storage Box ([Hetzner Cloud](../cloud/provider/hetzner-cloud.md)).

### 3. Store the credentials
```bash
sudo install -d -m 700 /etc/restic
sudo install -m 600 /dev/null /etc/restic/password       # then paste the repository password into it
sudo install -m 600 /dev/null /etc/restic/env.conf
```
`/etc/restic/env.conf` for B2 over the S3 API. This is a systemd `EnvironmentFile`, so no `export` and no quotes. The endpoint is shown in the B2 bucket details *(the `s3.<REGION>.backblazeb2.com` form is from the [Backblaze B2](../cloud/provider/backblaze-b2.md) sheet, unverified)*:
```ini
RESTIC_REPOSITORY=s3:https://s3.<REGION>.backblazeb2.com/<BUCKET>/<HOSTNAME>
RESTIC_PASSWORD_FILE=/etc/restic/password
AWS_ACCESS_KEY_ID=<B2_KEY_ID>
AWS_SECRET_ACCESS_KEY=<B2_APPLICATION_KEY>
```
For a Storage Box over SFTP, add a host alias to `/root/.ssh/config` (restic uses the normal SSH config, so the alias carries the port and key):
```text
Host storagebox
    HostName <USER>.your-storagebox.de
    User <USER>
    Port 23
    IdentityFile /root/.ssh/id_ed25519_restic
    ServerAliveInterval 60
    ServerAliveCountMax 240
```
```ini
RESTIC_REPOSITORY=sftp:storagebox:restic/<HOSTNAME>
RESTIC_PASSWORD_FILE=/etc/restic/password
```
A path without a leading slash is relative to the remote user's home directory. The `<USER>.your-storagebox.de` host name form is *unverified*; copy the host name from your Storage Box page.

### 4. Initialise the repository
```bash
sudo bash -c 'set -a; . /etc/restic/env.conf; set +a; restic init'
```
Load the file the same way before any manual restic command, so you act on the same repository as the timer. Keep `restic cat config` as the "can I reach and open it" test ([restic](../backup/restic.md)).

### 5. Dump the databases before each run
A small script writes each database straight into restic, with no temporary file. `/usr/local/bin/restic-docker-backup.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail

STACKS=/opt/stacks

# One snapshot per database dump, streamed from the container (-T: no TTY).
docker compose -f "$STACKS/app/compose.yaml" exec -T db \
  pg_dump -U postgres -Fc <DATABASE> \
  | restic backup --stdin --stdin-filename <DATABASE>.dump --tag db --host <HOSTNAME>

# Files: Compose files, env files, secrets and bind-mounted data.
restic backup --tag files --host <HOSTNAME> --one-file-system \
  --exclude-caches --exclude-file /etc/restic/excludes \
  "$STACKS" /etc

# Retention, then a rolling integrity check of 5 percent of the data.
restic forget --group-by host,tags --keep-daily 7 --keep-weekly 4 --keep-monthly 12 --prune
restic check --read-data-subset=5%
```
```bash
sudo chmod 750 /usr/local/bin/restic-docker-backup.sh
printf '*.log\n*.tmp\n' | sudo tee /etc/restic/excludes
```
Notes:
- `--host` pins the recorded name so snapshots stay grouped if the host is renamed.
- Group `forget` by `host,tags` so the `db` and `files` snapshots are thinned independently. With the default `host,paths` grouping each stdin dump is its own group.
- MariaDB, SQLite and Redis dump commands are in [Database Dumps](../backup/database-dumps.md).
- If a stack uses SQLite or file-backed state, stop the stack or use the app's own backup command first.
- `restic check --read-data-subset` downloads data, so on B2 it counts against egress ([Backblaze B2](../cloud/provider/backblaze-b2.md)).

### 6. Schedule it with systemd
`/etc/systemd/system/restic-docker-backup.service`:
```ini
[Unit]
Description=restic backup of the Docker host
Wants=network-online.target
After=network-online.target docker.service

[Service]
Type=oneshot
EnvironmentFile=/etc/restic/env.conf
ExecStart=/usr/local/bin/restic-docker-backup.sh
ExecStartPost=/usr/bin/curl -fsS -m 10 --retry 5 -o /dev/null https://hc-ping.com/<UUID>
```
`ExecStartPost` only runs when `ExecStart` succeeded, so a failed night sends no ping and Healthchecks alerts you. `/etc/systemd/system/restic-docker-backup.timer`:
```ini
[Unit]
Description=Nightly restic backup of the Docker host

[Timer]
OnCalendar=*-*-* 02:30:00
RandomizedDelaySec=15m
Persistent=true

[Install]
WantedBy=timers.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now restic-docker-backup.timer
sudo systemctl start restic-docker-backup.service      # first run by hand
journalctl -u restic-docker-backup.service -n 50 --no-pager
```
Set the Healthchecks period to one day with a grace time of a few hours.

### 7. Protect the repository from the host
Ransomware on the host can use the repository credentials to delete backups. For a stronger set-up, use a bucket with Object Lock, or run `forget --prune` from a separate trusted machine and give the host a key that cannot delete ([restic](../backup/restic.md), gotchas).

## Verify
```bash
sudo bash -c 'set -a; . /etc/restic/env.conf; set +a; restic snapshots'
sudo bash -c 'set -a; . /etc/restic/env.conf; set +a; restic stats --mode raw-data'
systemctl list-timers restic-docker-backup.timer
```
You should see recent `db` and `files` snapshots for `<HOSTNAME>`. Then prove you can get data back with [Restore-Test a Backup](restore-test-a-backup.md). A backup you have never restored is a hope, not a backup.

## Troubleshooting
SYMPTOM | FIX
---|---
`Fatal: repository does not exist` | Wrong `RESTIC_REPOSITORY`, wrong bucket or prefix, or you did not load `env.conf`; test with `restic cat config`
`wrong password or no key found` | The password file differs from the one used at `init`; do not re-init, find the right password
S3 `403` or `AccessDenied` | The key is restricted to another bucket, or lacks read or write; recreate it for this bucket
SFTP asks for a password or hangs | The key is not installed on the Storage Box, the port is not 23, or the alias is missing from the SSH config of the **user running restic** (root for the timer)
`unable to create lock in backend: repository is already locked` | Another run is active; check `pgrep restic` before `restic unlock`
`docker compose exec` fails with "the input device is not a TTY" | Add `-T`
Backup size suddenly drops | A path or volume went missing; compare with `restic diff <ID1> <ID2>`
Bucket grows without bound on B2 | Add the lifecycle rule in step 2; run `forget --prune`
No Healthchecks alert after a failed night | The ping must only fire on success (`ExecStartPost`); check the check's period and grace time

## Rollback / Cleanup
- Stop the schedule: `sudo systemctl disable --now restic-docker-backup.timer`.
- Remove old data: `restic forget --keep-last 3 --prune` (destructive, run with `--dry-run` first).
- Delete the repository: empty and delete the bucket in the provider console (destructive).
- Revoke the application key in the provider console if it may have leaked.

## Related Sheets
- [restic](../backup/restic.md) · [BorgBackup](../backup/borg.md) · [borgmatic](../backup/borgmatic.md) · [rclone](../backup/rclone.md) · [Backup Strategy](../backup/backup.md)
- [Docker Volume Backup](../backup/docker-volume-backup.md) · [Database Dumps](../backup/database-dumps.md) · [Docker-Compose](../docker/docker-compose.md)
- [Backblaze B2](../cloud/provider/backblaze-b2.md) · [Hetzner Cloud](../cloud/provider/hetzner-cloud.md) · [OpenSSH Cheat-Sheet](../tools/openssh.md) · [systemd](../linux/systemd.md)
- [Restore-Test a Backup](restore-test-a-backup.md) · [Docker Service Deploy](docker-service-deploy.md) · [Migrate a Docker Service Between Hosts](migrate-docker-service-between-hosts.md)
