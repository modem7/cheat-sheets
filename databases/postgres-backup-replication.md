# PostgreSQL Backup and Replication
Logical dumps with `pg_dump`, physical base backups, WAL archiving with point-in-time recovery (PITR), streaming replication and logical replication. Basic setup, users and psql are in [PostgreSQL Cheat-Sheet](postgres.md).

Documentation: [Backup and Restore](https://www.postgresql.org/docs/current/backup.html) · [Continuous archiving and PITR](https://www.postgresql.org/docs/current/continuous-archiving.html) · [High availability and replication](https://www.postgresql.org/docs/current/high-availability.html) · [Logical replication](https://www.postgresql.org/docs/current/logical-replication.html) · [pg_basebackup](https://www.postgresql.org/docs/current/app-pgbasebackup.html) · [pgBackRest](https://pgbackrest.org/)

> **Verification:** the `pg_basebackup` flags (`-D`, `-F p`, `-X s`, `-P`, `-R`) were checked against the PostgreSQL docs (current is 18). **Not verified against the docs:** `archive_command`, recovery settings, replication slots, publication and subscription syntax, `pg_dump`/`pg_restore` parallel flags, and `pg_promote()` (they follow the documentation as known). No command was executed. Test every restore on a spare machine: a backup you have not restored is not a backup. Replace the `16` in paths with your major version.

See also: [PostgreSQL Cheat-Sheet](postgres.md) · [Docker](../docker/docker.md) · [MySQL and MariaDB Replication](mysql-replication.md) · [systemd](../linux/systemd.md) · [UFW (uncomplicated firewall)](../linux/ufw.md) · [Linux](../linux/linux.md)

---
## Choosing a Method
METHOD | TOOL | GOOD FOR | LIMITS
---|---|---|---
Logical dump | `pg_dump`, `pg_dumpall` | One database or table, version upgrades, small and mid databases | Restore time grows with size, no PITR
Base backup | `pg_basebackup` | Whole cluster, fast restore, starting a replica | Same major version and architecture only
WAL archiving + base backup | `archive_command` or pgBackRest/WAL-G | PITR: restore to any moment | More moving parts
Streaming replication | physical standby | Failover, read scaling | Replicates mistakes too: not a backup
Logical replication | publication/subscription | Selected tables, upgrades between major versions, migrations | No DDL replication, sequences are not synced

Use more than one: a regular dump or base backup plus WAL archiving, and a copy offsite.

---
## pg_dump and pg_restore
COMMAND | DESCRIPTION
---|---
`pg_dump -U <USER> -h <HOST> <DB> > db.sql` | Plain SQL dump
`pg_dump -Fc -f db.dump <DB>` | Custom format (compressed, restore selectively)
`pg_dump -Fd -j 4 -f db_dir <DB>` | Directory format, 4 parallel jobs (fastest dump of large databases)
`pg_dump -Fc --schema-only <DB> > schema.dump` | Schema only
`pg_dump -Fc --data-only <DB> > data.dump` | Data only
`pg_dump -Fc -t <TABLE> <DB> > table.dump` | One table (`-T` excludes)
`pg_dumpall --globals-only > globals.sql` | Roles and tablespaces (not included in `pg_dump`)
`pg_dumpall > all.sql` | Every database plus globals
`pg_restore -l db.dump` | List the contents of an archive
`pg_restore -d <DB> --clean --if-exists db.dump` | Restore into an existing database
`pg_restore -d <DB> -j 4 db.dump` | Parallel restore (custom and directory formats)
`pg_restore -d <DB> -t <TABLE> db.dump` | Restore one table
`pg_restore --no-owner --no-privileges -d <DB> db.dump` | Ignore ownership from another server
`psql -d <DB> -f db.sql` | Restore a plain dump (add `-v ON_ERROR_STOP=1` to stop on first error)
`pg_dump <DB> \| gzip > db.sql.gz` / `gunzip -c db.sql.gz \| psql <DB>` | Compressed plain dump

Restore into a new database:
```bash
createdb -U postgres -O <OWNER> <DB>
pg_restore -U postgres -d <DB> -j 4 --no-owner db.dump
psql -U postgres -d <DB> -c 'ANALYZE;'
```
Restore the roles first (`psql -f globals.sql postgres`), or restores fail on missing owners. Run `ANALYZE` after a restore.

In Docker:
```bash
docker exec postgres pg_dump -U <USER> -Fc <DB> > db.dump
docker exec -i postgres pg_restore -U <USER> -d <DB> --clean --if-exists < db.dump
```
Do not add `-t` (a TTY) when redirecting binary output, it corrupts the dump. Restores need `-i` to read stdin.

Use `~/.pgpass` (`HOST:PORT:DB:USER:PASSWORD`, mode `0600`) or `PGPASSFILE` for scripts, never passwords on the command line. A scheduled backup belongs in a [systemd](../linux/systemd.md) timer or cron.

---
## Base Backup (pg_basebackup)
A copy of the whole data directory taken while the server runs. Needs a role with `REPLICATION` and a `replication` line in `pg_hba.conf`.

```sql
CREATE ROLE replicator WITH REPLICATION LOGIN ENCRYPTED PASSWORD '<PASSWORD>';
```
`pg_hba.conf` (reload after):
```
host  replication  replicator  192.168.1.0/24  scram-sha-256
```
```bash
pg_basebackup -h <PRIMARY> -U replicator -D /backups/base-$(date +%F) -Fp -Xs -P
pg_basebackup -h <PRIMARY> -U replicator -D /backups/base -Ft -z -Xs -P       # compressed tar
```
FLAG | MEANING
---|---
`-D <DIR>` | Target directory (required, must be empty)
`-F p` / `-F t` | Plain files (default) or tar
`-X s` | Stream WAL during the backup (default) so the backup is self-consistent
`-P` | Progress
`-R` | Write `standby.signal` and `primary_conninfo` for a new replica
`-z` | Gzip the tar output
`-C -S <SLOT>` | Create a replication slot and use it
`--checkpoint=fast` | Do not wait for the next checkpoint

Restore a plain base backup: stop PostgreSQL, move the old data directory aside, copy the backup into place (owner `postgres`, mode `0700`), start. With `-Xs` it recovers to the end of the backup.

Incremental base backups exist from PostgreSQL 17 (`pg_basebackup --incremental`, `pg_combinebackup`).

---
## WAL Archiving and Point-in-Time Recovery
Continuously copy WAL segments away, then replay them on a base backup up to any chosen time.

`postgresql.conf` on the primary:
```
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /mnt/wal_archive/%f && cp %p /mnt/wal_archive/%f'
archive_timeout = 300
```
`archive_mode` needs a restart; `archive_command` a reload. The command must return 0 only when the file is safely stored and must not overwrite existing files. `/mnt/wal_archive` should be on another disk or host ([NFS](../linux/nfs.md)). Check it works: `SELECT * FROM pg_stat_archiver;` and `SELECT pg_switch_wal();`.

Restore to a point in time:
1. Stop PostgreSQL and move the damaged data directory away.
2. Restore the latest base backup into the data directory.
3. Configure recovery in `postgresql.conf` (or `postgresql.auto.conf`):
```
restore_command = 'cp /mnt/wal_archive/%f %p'
recovery_target_time = '2026-11-05 14:30:00+00'
recovery_target_action = 'promote'
```
4. Create the signal file and start:
```bash
sudo -u postgres touch /var/lib/postgresql/16/main/recovery.signal
sudo systemctl start postgresql
```
5. Watch the log (`journalctl -u postgresql`, or `/var/log/postgresql/`). When recovery ends and `recovery_target_action=promote` is set, the server opens read-write. Check the data, then remove the recovery settings.

Other targets: `recovery_target_name` (from `pg_create_restore_point('name')`), `recovery_target_lsn`, `recovery_target_xid`, `recovery_target = 'immediate'` (end of backup only).

### pgBackRest
Production-grade tool for backups, WAL archiving, retention, parallel and incremental backups, and restores. It replaces hand-written `archive_command` scripts.
```bash
sudo apt install pgbackrest
```
`/etc/pgbackrest/pgbackrest.conf`:
```ini
[global]
repo1-path=/var/lib/pgbackrest
repo1-retention-full=2
start-fast=y

[main]
pg1-path=/var/lib/postgresql/16/main
```
`postgresql.conf`: `archive_mode = on`, `archive_command = 'pgbackrest --stanza=main archive-push %p'`, `wal_level = replica`.
COMMAND | DESCRIPTION
---|---
`sudo -u postgres pgbackrest --stanza=main stanza-create` | Initialise
`sudo -u postgres pgbackrest --stanza=main check` | Verify config and archiving
`sudo -u postgres pgbackrest --stanza=main backup --type=full` | Full backup (`diff` and `incr` also)
`sudo -u postgres pgbackrest info` | Backups and WAL range
`sudo -u postgres pgbackrest --stanza=main restore --type=time --target="2026-11-05 14:30:00+00" --target-action=promote` | PITR
`sudo -u postgres pgbackrest --stanza=main --delta restore` | Restore reusing existing files

It can store the repository on S3-compatible storage, SFTP or a remote host. See the [user guide](https://pgbackrest.org/user-guide.html). WAL-G is an alternative that targets object storage.

---
## Streaming Replication (Physical)
A standby that replays the primary's WAL and can serve read-only queries. Same major version required.

**Primary** `postgresql.conf`:
```
listen_addresses = '*'
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
hot_standby = on
```
Create the `replicator` role and `pg_hba.conf` line as in the base backup section, then restart. Create a slot so the primary keeps WAL the standby still needs:
```sql
SELECT pg_create_physical_replication_slot('standby1');
```
**Standby**, with an empty data directory and PostgreSQL stopped:
```bash
sudo systemctl stop postgresql
sudo -u postgres rm -rf /var/lib/postgresql/16/main/*
sudo -u postgres pg_basebackup -h <PRIMARY> -U replicator \
  -D /var/lib/postgresql/16/main -Fp -Xs -P -R -S standby1
sudo systemctl start postgresql
```
`-R` creates `standby.signal` and writes `primary_conninfo` and `primary_slot_name` into `postgresql.auto.conf`.

COMMAND | DESCRIPTION
---|---
`SELECT * FROM pg_stat_replication;` | On the primary: connected standbys, state, `replay_lag`
`SELECT pg_is_in_recovery();` | `t` on a standby
`SELECT * FROM pg_stat_wal_receiver;` | On the standby: connection state
`SELECT now() - pg_last_xact_replay_timestamp() AS lag;` | Replay delay on a standby
`SELECT slot_name, active, restart_lsn FROM pg_replication_slots;` | Slots (an inactive slot keeps WAL forever and can fill the disk)
`SELECT pg_drop_replication_slot('standby1');` | Remove a slot you no longer use

Synchronous replication (no data loss on failover, writes wait for the standby): set `synchronous_standby_names = 'FIRST 1 (standby1)'` on the primary and give the standby an `application_name` in `primary_conninfo`.

### Failover and Switchover
Promote a standby to primary:
```bash
sudo -u postgres pg_ctlcluster 16 main promote      # Debian/Ubuntu
# or from SQL
sudo -u postgres psql -c 'SELECT pg_promote();'
```
After promotion the old primary cannot just rejoin. Rebuild it as a standby with `pg_basebackup` (or `pg_rewind` if `wal_log_hints` or data checksums were on). For automatic failover use **Patroni** or **repmgr**, and a proxy such as HAProxy or PgBouncer in front. Streaming replication is not a backup: a `DROP TABLE` replicates instantly.

---
## Logical Replication
Replicate chosen tables (not the whole cluster) between databases, including across major versions and platforms.

**Publisher** `postgresql.conf`: `wal_level = logical` (restart). Role with `REPLICATION` or `pg_hba.conf` access for the subscriber.
```sql
-- on the publisher
CREATE PUBLICATION app_pub FOR TABLE users, orders;
-- or: CREATE PUBLICATION all_pub FOR ALL TABLES;

-- on the subscriber (tables must already exist with the same schema)
CREATE SUBSCRIPTION app_sub
  CONNECTION 'host=<PUBLISHER> port=5432 dbname=<DB> user=replicator password=<PASSWORD>'
  PUBLICATION app_pub;
```
Copy the schema first: `pg_dump --schema-only <DB> | psql -h <SUBSCRIBER> <DB>`.

COMMAND | DESCRIPTION
---|---
`\dRp+` / `\dRs+` | psql: list publications / subscriptions
`SELECT * FROM pg_stat_subscription;` | Subscriber progress
`SELECT * FROM pg_stat_replication;` | Publisher side
`ALTER SUBSCRIPTION app_sub DISABLE;` / `ENABLE` | Pause and resume
`ALTER SUBSCRIPTION app_sub REFRESH PUBLICATION;` | Pick up tables added to the publication
`DROP SUBSCRIPTION app_sub;` | Remove (also drops the slot on the publisher)

Limits: DDL, sequence values and large objects are not replicated. Tables need a primary key (or `REPLICA IDENTITY FULL`) for `UPDATE` and `DELETE`. The subscriber can be written to, so avoid conflicts.

Use for: zero-downtime major upgrades (publish from the old version, subscribe from the new, switch, then fix sequences with `setval`), moving a few tables, feeding a reporting database.

---
## Checklist
- [ ] Backups run on a schedule and alert on failure.
- [ ] A copy is stored off the host, and encrypted.
- [ ] A restore was tested, with timing, in the last quarter.
- [ ] `pg_dumpall --globals-only` is part of the routine (roles are not in `pg_dump`).
- [ ] WAL archive disk and replication slot lag are monitored.
- [ ] Config files (`postgresql.conf`, `pg_hba.conf`) are kept in version control.
