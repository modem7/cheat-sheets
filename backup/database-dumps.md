# Database Dumps
Copying a live database's data directory gives an inconsistent backup. Take a **logical dump** (or a snapshot made by the database itself) first, then let your file backup tool ([[restic]], [[borgmatic]], [[rsync]]) pick up the dump. This sheet covers consistent dumps, scheduling, rotation, running dumps in Docker, and restore tests. Day-to-day SQL and client usage live in [[postgres]], [[mysql]], [[mariadb]] and [[sqlite]].

Documentation: [PostgreSQL: backup and restore](https://www.postgresql.org/docs/current/backup.html) · [MariaDB: mariadb-dump](https://mariadb.com/kb/en/mariadb-dump/) · [MySQL: mysqldump](https://dev.mysql.com/doc/refman/8.4/en/mysqldump.html) · [SQLite: backup API and `.backup`](https://www.sqlite.org/backup.html) · [Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)

> **Verification:** `sqlite3_rsync` existence and the 3.50.0 change (WAL and page-size requirement removed) were checked against the SQLite docs. Everything else here is standard database tooling written from knowledge and was **not** re-checked against the documentation this session, including `VACUUM INTO`, the Redis multi-part AOF layout, `mariadb-backup` and the MySQL `--source-data` rename. No command was executed. Restore every dump into a scratch instance at least once.

See also: [[backup]] · [[docker-volume-backup]] · [[postgres]] · [[mysql]] · [[mariadb]] · [[sqlite]] · [[docker]] · [[docker-compose]] · [[linux]]

---
## Principles
- A dump must be **consistent**: use `--single-transaction` for InnoDB, `pg_dump` (which is snapshot based), `sqlite3 .backup`, or `BGSAVE` for Redis.
- Dump to a **temp name then rename**, so a half-written file is never mistaken for a good one.
- Dump with a **least-privilege** account. Keep credentials in `~/.pgpass` or option files, never on the command line (`ps` shows arguments).
- Compress (`gzip`, `zstd`), keep several generations, and ship them off the host.
- A dump that was never restored is untested. Check the restore, see the end of this sheet.

---
## PostgreSQL
COMMAND | DESCRIPTION
---|---
`pg_dump -Fc -f <DB>.dump <DB>` | Custom-format dump (compressed, flexible restore)
`pg_dump -Fd -j 4 -f <DB>.dir <DB>` | Directory format, parallel (4 jobs)
`pg_dump <DB> \| zstd > <DB>.sql.zst` | Plain SQL, compressed
`pg_dump -Fc --no-owner --no-acl <DB> > <DB>.dump` | Portable between roles
`pg_dumpall --globals-only > globals.sql` | Roles and tablespaces (`-g`), which `pg_dump` does not include
`pg_dumpall > all.sql` | Every database plus roles
`pg_restore --list <DB>.dump` | List contents, also a quick "is this readable" test
`pg_restore -d <DB> --clean --if-exists <DB>.dump` | Restore into an existing database
`pg_restore -C -d postgres <DB>.dump` | Create the database from the dump, then restore into it
`pg_restore -j 4 -d <DB> <DB>.dump` | Parallel restore (custom or directory format)

Credentials: `~/.pgpass` (mode `0600`), one line per server:
```
<HOST>:5432:<DB>:<USER>:<PASSWORD>
```
Or set `PGPASSFILE=/etc/backup/pgpass`.

Back up the globals alongside each database dump, or the roles are missing after a rebuild:
```bash
pg_dumpall --globals-only > globals.sql
```

---
## MariaDB and MySQL
COMMAND | DESCRIPTION
---|---
`mariadb-dump --single-transaction --routines --triggers --events <DB> > <DB>.sql` | Consistent InnoDB dump with stored code
`mariadb-dump --single-transaction --routines --triggers --events --all-databases > all.sql` | Every database
`mysqldump --single-transaction --routines --triggers --events <DB> > <DB>.sql` | The same on MySQL
`mariadb-dump ... \| gzip > <DB>.sql.gz` | Compressed
`gunzip < <DB>.sql.gz \| mariadb <DB>` | Restore (`mysql` on MySQL)
`mariadb-dump --defaults-extra-file=/etc/backup/my.cnf ...` | Credentials from a file

Notes:
- `mariadb-dump` is the MariaDB name, `mysqldump` the older one. Newer MariaDB versions ship `mysqldump` only as a link.
- `--single-transaction` gives a consistent snapshot for InnoDB only. MyISAM tables need `--lock-all-tables` or a quiet period.
- For a replica seed, `--source-data` (MySQL 8.2+) replaced `--master-data`, MariaDB still uses `--master-data`.
- For very large datasets, a physical backup (`mariadb-backup --backup --target-dir=<DIR>`, then `--prepare`, then `--copy-back` on an empty datadir) is faster to restore than replaying SQL.

Credentials file `/etc/backup/my.cnf` (mode `0600`):
```ini
[client]
user=<USER>
password=<PASSWORD>
host=<HOST>
```

---
## SQLite
COMMAND | DESCRIPTION
---|---
`sqlite3 <DB> ".backup '<DEST>.db'"` | Online, consistent copy using the backup API. Safe while the app is running
`sqlite3 <DB> "VACUUM INTO '<DEST>.db'"` | Writes a compacted, consistent copy (fails if the file exists)
`sqlite3 <DB> .dump \| gzip > <DB>.sql.gz` | SQL text dump
`sqlite3 <DEST>.db "PRAGMA integrity_check;"` | Verify a backup, expect `ok`
`sqlite3_rsync <SRC>.db <HOST>:<DEST>.db` | Efficient online replication of a live database over SSH (check your SQLite version has it)

- **Never** `cp` a live SQLite file: in WAL mode the data is also in `-wal` and `-shm` files, and a copy taken mid-write is torn.
- `sqlite3_rsync` before SQLite 3.50.0 needed both databases in WAL mode with the same page size, 3.50.0 removed that limit.
- Run `.backup` from a process that can open the database. For a container, `docker exec`, see below.

---
## Redis
COMMAND | DESCRIPTION
---|---
`redis-cli BGSAVE` | Fork and write an RDB snapshot in the background
`redis-cli LASTSAVE` | Unix time of the last successful save, poll it to see `BGSAVE` finish
`redis-cli INFO persistence` | Check `rdb_bgsave_in_progress` and `rdb_last_bgsave_status:ok`
`redis-cli CONFIG GET dir` | Where `dump.rdb` and the AOF live
`redis-cli --rdb <FILE>.rdb` | Pull an RDB dump over the network from a running server
`redis-check-rdb <FILE>.rdb` | Verify an RDB file
`redis-check-aof <FILE>` | Verify (and with `--fix` repair) an AOF file
`redis-cli BGREWRITEAOF` | Compact the AOF in the background

Wait for a `BGSAVE` to finish, then copy:
```bash
before=$(redis-cli LASTSAVE)
redis-cli BGSAVE
until [ "$(redis-cli LASTSAVE)" != "$before" ]; do sleep 1; done
cp /var/lib/redis/dump.rdb /backup/redis-$(date +%F).rdb
```
`SAVE` does the same synchronously and blocks the server, avoid it in production.

Restore: stop Redis, put `dump.rdb` into the `dir`, start Redis. **If `appendonly yes` is set Redis loads the AOF in preference to the RDB**, so either restore the AOF too or start with `appendonly no`, then re-enable it. Redis 7 and later keep the AOF as a multi-part set under an `appenddirname` directory (default `appendonlydir`), back that directory up as a whole.

---
## Dumping from Docker Containers
```bash
# PostgreSQL
docker exec <CONTAINER> pg_dump -U <USER> -Fc <DB> > <DB>-$(date +%F).dump

# MariaDB, password from the container's environment rather than the host's process list
docker exec <CONTAINER> sh -c 'exec mariadb-dump --single-transaction --routines -uroot -p"$MARIADB_ROOT_PASSWORD" <DB>' | gzip > <DB>-$(date +%F).sql.gz

# SQLite inside a container that has the sqlite3 client
docker exec <CONTAINER> sqlite3 /data/app.db ".backup '/data/backup.db'"

# Redis
docker exec <CONTAINER> redis-cli BGSAVE
```
- Use `docker exec` **without** `-t` when redirecting binary output (a TTY mangles it) for `-Fc` dumps. Use `-i` only when piping input.
- Restore into a container: `docker exec -i <CONTAINER> pg_restore -U <USER> -d <DB> --clean --if-exists < <DB>.dump`.
- [[borgmatic]] can dump PostgreSQL, MariaDB, MySQL, MongoDB and SQLite natively into the archive, see its sheet.
- With the `offen/docker-volume-backup` sidecar, an `archive-pre` label can run the dump first, see [[docker-volume-backup]].

---
## Dump Script (bash)
```bash
#!/usr/bin/env bash
# /usr/local/bin/db-dump.sh : dump, verify, rotate. Credentials come from ~/.pgpass and /etc/backup/my.cnf.
set -euo pipefail
DEST=/srv/backups/db
KEEP_DAYS=14
STAMP=$(date +%F_%H%M)
mkdir -p "$DEST"

pg_dump -Fc -h <HOST> -U <USER> <DB> > "$DEST/<DB>-$STAMP.dump.tmp"
pg_restore --list "$DEST/<DB>-$STAMP.dump.tmp" > /dev/null          # readable?
mv "$DEST/<DB>-$STAMP.dump.tmp" "$DEST/<DB>-$STAMP.dump"

mariadb-dump --defaults-extra-file=/etc/backup/my.cnf --single-transaction --routines --triggers --events <DB2> \
  | gzip > "$DEST/<DB2>-$STAMP.sql.gz.tmp"
gzip -t "$DEST/<DB2>-$STAMP.sql.gz.tmp"
mv "$DEST/<DB2>-$STAMP.sql.gz.tmp" "$DEST/<DB2>-$STAMP.sql.gz"

find "$DEST" -type f -mtime +"$KEEP_DAYS" -delete
```

---
## Scheduling
### systemd timer
`/etc/systemd/system/db-dump.service`:
```ini
[Unit]
Description=Database dumps

[Service]
Type=oneshot
User=backup
ExecStart=/usr/local/bin/db-dump.sh
```
`/etc/systemd/system/db-dump.timer`:
```ini
[Unit]
Description=Nightly database dumps

[Timer]
OnCalendar=*-*-* 01:30:00
RandomizedDelaySec=10m
Persistent=true

[Install]
WantedBy=timers.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now db-dump.timer
systemctl list-timers db-dump.timer
journalctl -u db-dump.service -n 30
```
Schedule the dump **before** the file backup, for example dumps at 01:30 and [[restic]] at 02:30.

### cron
```bash
30 1 * * * /usr/local/bin/db-dump.sh >> /var/log/db-dump.log 2>&1 && curl -fsS -m 10 --retry 5 https://hc-ping.com/<UUID> > /dev/null
```
The `&&` means the ping only fires on success, so a missed ping raises the alert.

---
## Restore Test
Restore into a scratch instance, never over production, and check the data.

```bash
# PostgreSQL
docker run -d --name pg-restore-test -e POSTGRES_PASSWORD=<PASSWORD> postgres:17
sleep 10
docker exec pg-restore-test createdb -U postgres restoretest
docker exec -i pg-restore-test pg_restore -U postgres -d restoretest < <DB>-<DATE>.dump
docker exec pg-restore-test psql -U postgres -d restoretest -c '\dt'
docker rm -f pg-restore-test

# SQLite
sqlite3 <DEST>.db "PRAGMA integrity_check;"
```
Compare a row count or a recent record with production and note the restore time against your RTO, see [[backup]].
