# Restore-Test a Backup
Prove that a restic backup of a Docker host can be restored from a clean machine: list it, restore a file, restore a database dump into a scratch Postgres, bring a stack up from the restored files, time it and check the alerts.

Documentation: [restic: restoring](https://restic.readthedocs.io/en/stable/050_restore.html) · [PostgreSQL: pg_restore](https://www.postgresql.org/docs/current/app-pgrestore.html)

> **Verification:** the restic steps (`snapshots`, `restore --verify`, `dump` piped into `pg_restore`, `check --read-data-subset`) and the scratch-Postgres row count were run with restic 0.19.1 and `postgres:16` in containers against a local repository. Restoring from B2 or a Storage Box, and the whole-stack step, were **not** run *(unverified)*.

## Goal
You have evidence, with a date and a timing, that the newest backup restores to working data using only the documented credentials. Failures you found are fixed in the runbook, not discovered during an outage.

## Prerequisites
- A restic repository from [Off-Site Docker Host Backup with restic](offsite-docker-host-backup.md) (the same steps apply to other restic repositories)
- A **clean machine** (a spare VM, a laptop, a throwaway cloud server) with restic and Docker installed and none of the original host's files
- The repository URL, the repository password and the storage credentials, taken from your password manager and not from the original host
- Enough free disk for the restore; on B2 a full restore counts against egress ([Backblaze B2](../cloud/provider/backblaze-b2.md))

## Steps
### 1. Reach the repository from the clean machine
```bash
export RESTIC_REPOSITORY=<REPOSITORY>
export AWS_ACCESS_KEY_ID=<B2_KEY_ID>
export AWS_SECRET_ACCESS_KEY=<B2_APPLICATION_KEY>
install -m 600 /dev/null ~/restic-password        # paste the password into it
export RESTIC_PASSWORD_FILE=~/restic-password
restic cat config
restic snapshots --group-by host,tags
```
If this fails, your documented credentials are incomplete: that is the first finding. Write down what was missing. Use `unset` or close the shell afterwards, since the keys sit in its environment.

### 2. Check the newest snapshot is recent
Look at the time column of `restic snapshots`. A newest snapshot older than your schedule allows means the timer or the ping alert is not doing its job ([Backup Strategy](../backup/backup.md), monitoring).

### 3. Restore one file and compare
```bash
SCRATCH="$(mktemp -d)"
restic restore latest --tag files --host <HOSTNAME> --target "$SCRATCH" --include /opt/stacks/app/compose.yaml --verify
ls -l "$SCRATCH/opt/stacks/app/"
```
`--verify` re-reads the restored files and compares them with the snapshot. Compare against the live copy where one exists: `diff "$SCRATCH/opt/stacks/app/compose.yaml" /opt/stacks/app/compose.yaml`. Paths are restored below the target, keeping their full path.

### 4. Restore a database dump into a scratch Postgres
```bash
docker run -d --name pg-scratch -e POSTGRES_PASSWORD=<SCRATCH_PASSWORD> postgres:16
sleep 8
docker exec pg-scratch createdb -U postgres restored
restic dump latest <DATABASE>.dump --tag db --host <HOSTNAME> \
  | docker exec -i pg-scratch pg_restore -U postgres -d restored --no-owner --exit-on-error
docker exec pg-scratch psql -U postgres -d restored -c '\dt'
docker exec pg-scratch psql -U postgres -d restored -tc 'SELECT count(*) FROM <TABLE>'
```
Compare the count with the live database. Use the same Postgres major version as the source, or a newer one. Other engines and SQLite integrity checks are in [Database Dumps](../backup/database-dumps.md).

### 5. Bring a whole application up from the restore
```bash
restic restore latest --tag files --host <HOSTNAME> --target /srv/restore-test --include /opt/stacks/app
cd /srv/restore-test/opt/stacks/app
sed -i 's/^APP_HOST=.*/APP_HOST=restore-test.example.com/' .env
docker compose config >/dev/null
docker compose -p restore-test up -d
docker compose -p restore-test ps
```
Use a different project name (`-p restore-test`) so nothing collides with a live stack. Remove or change published ports and Traefik labels first so the copy does not take over real traffic. Restore the database dump into the stack's database as in step 4, then open the app and check recent data is present. Anything that needed a manual fix goes into the runbook.

### 6. Check the repository itself
```bash
restic check --read-data-subset=5%
```
Run it from the clean machine too, with a different subset each time (`--read-data-subset=1/5`, then `2/5`, ...) to cover the whole repository over a few weeks ([restic](../backup/restic.md)).

### 7. Time it and compare with your RTO
Record the wall-clock time from step 1 to a working app, and the restore size. A 2 TB restore over a 100 Mbit/s link takes about 44 hours ([Backup Strategy](../backup/backup.md), RPO and RTO). If that is too slow, add a local copy as well as the off-site one.

### 8. Confirm the alerts fire
Break one night on purpose: stop the timer, or point the ping at a wrong URL, and check you are told after the grace period. Then fix it.
```bash
sudo systemctl stop restic-docker-backup.timer
# wait for the Healthchecks grace time to pass and confirm the alert arrives
sudo systemctl start restic-docker-backup.timer
```

### 9. Write it down
Add the date, the snapshot ID, the timings, what failed and what you changed to your runbook ([Backup Strategy](../backup/backup.md), disaster recovery runbook). Repeat at least quarterly and after every major change to the backup set-up.

## Verify
- `restic restore ... --verify` ended with `finished verifying`.
- The scratch database has the expected tables and row counts.
- The restored stack reached `healthy` and showed recent data.
- The timing is recorded and meets your RTO, or you have a ticket to fix it.
- The missed-backup alert reached you.

## Troubleshooting
SYMPTOM | FIX
---|---
`wrong password or no key found` | The password in the password manager differs from the one used at `init`; find the right one, and correct the runbook
`repository is already locked` | Another restic run is active; check `pgrep restic` before `restic unlock`
`restic dump` prints nothing or `not found in snapshot` | The filter matched another snapshot; add `--tag` and `--host`, and check the name with `restic ls latest --tag db`
`pg_restore: error: ... role does not exist` | Add `--no-owner`, or create the role first
`pg_restore` ends with a version error | Restore into the same or a newer Postgres major version
Restore very slow | Check the link speed and the egress limits of the provider; restore only what you need with `--include`
Restored files owned by the wrong user | Run restic as root when restoring, and check numeric IDs on the new machine
Compose stack starts but is empty | The volume data was not in the snapshot; fix the include list in the backup script

## Rollback / Cleanup
```bash
docker compose -p restore-test down -v        # destructive: removes the scratch volumes
docker rm -f pg-scratch                        # destructive: removes the scratch database
rm -rf "$SCRATCH" /srv/restore-test            # destructive: deletes the restored data
unset RESTIC_REPOSITORY AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY RESTIC_PASSWORD_FILE
shred -u ~/restic-password
```
Restored data may contain secrets, so delete it when you are done. Destroy a throwaway server completely.

## Related Sheets
- [restic](../backup/restic.md) · [Backup Strategy](../backup/backup.md) · [Database Dumps](../backup/database-dumps.md) · [Docker Volume Backup](../backup/docker-volume-backup.md)
- [PostgreSQL Cheat-Sheet](../databases/postgres.md) · [Docker-Compose](../docker/docker-compose.md) · [Backblaze B2](../cloud/provider/backblaze-b2.md)
- [Off-Site Docker Host Backup with restic](offsite-docker-host-backup.md) · [Migrate a Docker Service Between Hosts](migrate-docker-service-between-hosts.md) · [Docker Service Deploy](docker-service-deploy.md)
