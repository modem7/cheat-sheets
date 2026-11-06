# MySQL and MariaDB Replication
Asynchronous source/replica replication using GTIDs (global transaction IDs), how to watch lag, and how to fail over. MySQL 8.4 and MariaDB use different GTID implementations and slightly different commands, so each has its own section. Basics are in [[mysql]] and [[mariadb]].

Documentation: [MySQL 8.4 Replication](https://dev.mysql.com/doc/refman/8.4/en/replication.html) · [CHANGE REPLICATION SOURCE TO](https://dev.mysql.com/doc/refman/8.4/en/change-replication-source-to.html) · [MariaDB Replication](https://mariadb.com/kb/en/replication/) · [MariaDB CHANGE MASTER TO](https://mariadb.com/kb/en/change-master-to/) · [MariaDB GTID](https://mariadb.com/kb/en/gtid/)

> **Verification:** `CHANGE REPLICATION SOURCE TO ... SOURCE_AUTO_POSITION=1` and `GET_SOURCE_PUBLIC_KEY` (MySQL 8.4), MariaDB `MASTER_USE_GTID=slave_pos` and that `SHOW SLAVE STATUS` and `SHOW REPLICA STATUS` are interchangeable in MariaDB were checked against the official docs. **Not verified against the docs:** the status field names, the MariaDB version that added the REPLICA aliases, the config examples and the failover procedures (they follow the documentation as known). No command was executed. Terminology changed: MySQL 8.4 uses SOURCE/REPLICA (the old `CHANGE MASTER TO` and `START SLAVE` were removed in 8.4), MariaDB still accepts MASTER/SLAVE.

See also: [[mysql]] · [[mariadb]] · [[postgres-backup-replication]] · [[docker]] · [[ufw]] · [[linux]]

---
## Concepts
TERM | MEANING
---|---
Source (primary/master) | Accepts writes, records them in the binary log
Replica (slave) | Fetches the binary log (I/O thread) and applies it (SQL/applier thread)
GTID | Global transaction ID. Lets a replica find its position by itself, no log file and offset needed
Binary log | `log_bin`. Required on the source (and on a replica that is a failover candidate)
`server_id` | Unique number per server. Required

Replication is **asynchronous**: the source does not wait for the replica, so a failover can lose the last transactions. Semi-synchronous plugins and Galera (MariaDB) or Group Replication / InnoDB Cluster (MySQL) exist for stronger guarantees. Replication is not a backup: a `DROP TABLE` replicates. See also the [[mysql]] backup commands.

---
# MySQL 8.4 (GTID)

## 1. Configure the Source
`/etc/mysql/mysql.conf.d/replication.cnf` (or `my.cnf`):
```ini
[mysqld]
server-id                = 1
log_bin                  = mysql-bin
binlog_format            = ROW
gtid_mode                = ON
enforce_gtid_consistency = ON
binlog_expire_logs_seconds = 604800
bind-address             = 0.0.0.0
```
Restart, then create a replication user:
```sql
CREATE USER 'repl'@'192.168.1.%' IDENTIFIED BY '<PASSWORD>';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'192.168.1.%';
```
(`REPLICATION SLAVE` is still the privilege name.) Open port 3306 only to the replica ([[ufw]]).

## 2. Configure the Replica
```ini
[mysqld]
server-id                = 2
log_bin                  = mysql-bin
gtid_mode                = ON
enforce_gtid_consistency = ON
read_only                = ON
super_read_only          = ON
relay_log                = relay-bin
log_replica_updates      = ON
```
Restart.

## 3. Seed the Replica With Data
For an empty source, skip this. Otherwise take a consistent dump with GTIDs from the source and load it on the replica:
```bash
# on the source
mysqldump -u root -p --all-databases --single-transaction --routines --triggers \
  --source-data=2 --set-gtid-purged=ON > seed.sql
# on the replica
mysql -u root -p < seed.sql
```
`--set-gtid-purged=ON` writes `SET @@GLOBAL.GTID_PURGED=...` into the dump so the replica starts from the right place. Clone plugin (`CLONE INSTANCE FROM`) or Percona XtraBackup are faster for large databases. On the replica run `RESET BINARY LOGS AND GTIDS;` first if it is not new.

## 4. Point the Replica at the Source
```sql
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST = '<SOURCE-HOST>',
  SOURCE_PORT = 3306,
  SOURCE_USER = 'repl',
  SOURCE_PASSWORD = '<PASSWORD>',
  SOURCE_AUTO_POSITION = 1,
  GET_SOURCE_PUBLIC_KEY = 1;
START REPLICA;
```
`GET_SOURCE_PUBLIC_KEY=1` lets the `caching_sha2_password` login work without TLS. Prefer `SOURCE_SSL=1` on untrusted networks. The replica threads must be stopped (`STOP REPLICA;`) when you run `CHANGE REPLICATION SOURCE TO`.

## 5. Check Status
```sql
SHOW REPLICA STATUS\G
```
FIELD | GOOD VALUE
---|---
`Replica_IO_Running` | `Yes`
`Replica_SQL_Running` | `Yes`
`Seconds_Behind_Source` | Small number. `NULL` means a thread is not running
`Last_IO_Error` / `Last_SQL_Error` | Empty
`Retrieved_Gtid_Set` / `Executed_Gtid_Set` | Executed catches up with retrieved
`Source_Log_File`, `Read_Source_Log_Pos` | Position (informational with GTIDs)

---
# MariaDB (GTID)
MariaDB GTIDs look like `domain-server_id-sequence` (for example `0-1-1234`) and are tracked per domain. They work differently from MySQL GTIDs, so `SOURCE_AUTO_POSITION` does not exist: you use `MASTER_USE_GTID`.

## 1. Source
`/etc/mysql/mariadb.conf.d/60-replication.cnf`:
```ini
[mysqld]
server_id         = 1
log_bin           = /var/log/mysql/mariadb-bin
binlog_format     = ROW
log_slave_updates = ON
expire_logs_days  = 7
bind-address      = 0.0.0.0
```
```sql
CREATE USER 'repl'@'192.168.1.%' IDENTIFIED BY '<PASSWORD>';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'192.168.1.%';
```
(On MariaDB 10.5.1+ the privilege is also named `REPLICATION REPLICA`, and `REPLICATION SLAVE` still works.)

## 2. Replica
```ini
[mysqld]
server_id         = 2
log_bin           = /var/log/mysql/mariadb-bin
read_only         = ON
relay_log         = relay-bin
log_slave_updates = ON
```

## 3. Seed
```bash
# on the source
mariadb-dump --all-databases --single-transaction --routines --triggers --master-data=2 --gtid > seed.sql
# on the replica
mariadb < seed.sql
```
The dump comment holds the GTID, or on the replica `SELECT @@gtid_slave_pos;`. Set it before starting: `SET GLOBAL gtid_slave_pos = '0-1-1234';`.

## 4. Connect
```sql
CHANGE MASTER TO
  MASTER_HOST='<SOURCE-HOST>',
  MASTER_USER='repl',
  MASTER_PASSWORD='<PASSWORD>',
  MASTER_USE_GTID=slave_pos;
START SLAVE;
```
`MASTER_USE_GTID` values: `slave_pos` (the replica's own position, normal), `current_pos` (use after promotion, so the replica's own writes are accounted for), `no` (classic file and position).

## 5. Check Status
```sql
SHOW REPLICA STATUS\G      -- same output as SHOW SLAVE STATUS
```
FIELD | GOOD VALUE
---|---
`Slave_IO_Running` / `Slave_SQL_Running` | `Yes` / `Yes`
`Seconds_Behind_Master` | Small number
`Last_IO_Error` / `Last_SQL_Error` | Empty
`Gtid_IO_Pos` | Position the I/O thread has fetched
`Using_Gtid` | `Slave_Pos` or `Current_Pos`

Also: `SELECT @@gtid_current_pos, @@gtid_slave_pos, @@gtid_binlog_pos;`. `SHOW ALL SLAVES STATUS` lists multi-source setups.

---
## Monitoring Lag
CHECK | DETAIL
---|---
`Seconds_Behind_Source` / `Seconds_Behind_Master` | Estimate only. Can read 0 while the I/O thread is stalled, or `NULL` when stopped
Heartbeat table (`pt-heartbeat` from Percona Toolkit) | Accurate lag, source writes a timestamp each second, replica compares
MySQL: `performance_schema.replication_applier_status_by_worker` and `replication_connection_status` | Per-worker errors and lag
GTID gap: compare `@@gtid_executed` (MySQL) or `@@gtid_current_pos` (MariaDB) on source and replica | Transactions not applied yet. MySQL: `SELECT GTID_SUBTRACT('<SOURCE-SET>', @@gtid_executed);`
Alert on | Threads not `Yes`, lag above threshold for N minutes, `Last_SQL_Error` not empty, binlog disk usage

Typical causes of growing lag: single-threaded apply of heavy transactions (MySQL: `replica_parallel_workers`, MariaDB: `slave_parallel_threads` and `slave_parallel_mode`), long-running `ALTER` or batch jobs, slow disk on the replica, tables without primary keys (row events scan the whole table), network.

## Common Errors
ERROR | FIX
---|---
`Duplicate entry` / `Could not execute Write_rows` | The replica has data the source does not. Find the cause (a write on the replica). Resync from a fresh dump rather than skipping if you can
`Could not find first log file name in binary log index file` | Source purged logs the replica needs. Re-seed the replica
`Got fatal error 1236 from source` (GTID purged) | Same: replica is too far behind. Re-seed
`Access denied` / SSL errors | Check the user and host pattern, `GET_SOURCE_PUBLIC_KEY`, certificates
Replica stopped after a crash | `STOP REPLICA; START REPLICA;` and check `relay_log_recovery=ON`
Skip one MySQL GTID transaction (last resort, understand the data drift first) | `STOP REPLICA; SET GTID_NEXT='<UUID>:<N>'; BEGIN; COMMIT; SET GTID_NEXT='AUTOMATIC'; START REPLICA;`
Skip on MariaDB (last resort) | `STOP SLAVE; SET GLOBAL gtid_slave_pos='<NEXT-GTID>'; START SLAVE;` (or `SET GLOBAL sql_slave_skip_counter=1` for non-GTID)

---
## Failover and Switchover
**Planned switchover** (no data loss):
1. Stop writes on the source: `SET GLOBAL read_only=ON; SET GLOBAL super_read_only=ON;` (MySQL). `FLUSH TABLES WITH READ LOCK;` also works. Stop application writes first.
2. Wait until the replica has caught up: lag 0, and the GTID sets match.
3. On the replica: `STOP REPLICA;` (`STOP SLAVE`), then `RESET REPLICA ALL;` (`RESET SLAVE ALL`), and turn read-only off: `SET GLOBAL super_read_only=OFF; SET GLOBAL read_only=OFF;`.
4. Repoint applications to the new source (DNS, proxy, config).
5. Turn the old source into a replica: `CHANGE REPLICATION SOURCE TO ...` pointing at the new source (MySQL `SOURCE_AUTO_POSITION=1`; MariaDB `MASTER_USE_GTID=current_pos`), `START REPLICA`.

**Unplanned failover** (source is dead):
1. Choose the most up-to-date replica (compare `Retrieved_Gtid_Set` / `Executed_Gtid_Set`, or MariaDB `Gtid_IO_Pos`).
2. Let it apply its relay log: wait until `Replica_SQL_Running_State` says it has read all relay log.
3. Promote as above and repoint the other replicas and the application.
4. When the old source returns, **do not** put it back as is. It may hold transactions the new source lacks. Compare GTIDs and re-seed it as a replica.

Expect to lose recent transactions with asynchronous replication.

Automation: **Orchestrator** (MySQL and MariaDB topology manager), **MaxScale** (MariaDB proxy with automatic failover), **ProxySQL** (query routing), **MySQL Router and InnoDB Cluster**, **Galera Cluster** (MariaDB, multi-primary, synchronous-style certification). For a homelab, a documented manual switchover plus backups is often enough.

---
## Docker Example
```yaml
services:
  mysql-source:
    image: mysql:8.4
    command: >
      --server-id=1 --log-bin=mysql-bin --gtid-mode=ON --enforce-gtid-consistency=ON
    environment:
      MYSQL_ROOT_PASSWORD: <PASSWORD>
    volumes: [source-data:/var/lib/mysql]
  mysql-replica:
    image: mysql:8.4
    command: >
      --server-id=2 --log-bin=mysql-bin --gtid-mode=ON --enforce-gtid-consistency=ON
      --read-only=ON --super-read-only=ON --log-replica-updates=ON
    environment:
      MYSQL_ROOT_PASSWORD: <PASSWORD>
    volumes: [replica-data:/var/lib/mysql]
volumes:
  source-data:
  replica-data:
```
Then run the `CREATE USER` on the source and the `CHANGE REPLICATION SOURCE TO` on the replica with `SOURCE_HOST='mysql-source'`. See [[docker-compose]] and [[docker]].

## Useful Commands
COMMAND | DESCRIPTION
---|---
`SHOW BINARY LOG STATUS;` | MySQL 8.4: current binlog file and position (replaces `SHOW MASTER STATUS`)
`SHOW BINARY LOGS;` | Binlog files and sizes
`SHOW MASTER STATUS;` | MariaDB: same information
`PURGE BINARY LOGS BEFORE NOW() - INTERVAL 7 DAY;` | Free disk space (never delete binlog files by hand)
`SHOW REPLICAS;` | MySQL: replicas registered with the source (`SHOW SLAVE HOSTS` on MariaDB)
`STOP REPLICA; START REPLICA;` | Restart both threads (`STOP SLAVE; START SLAVE;` on MariaDB)
`RESET REPLICA ALL;` | Remove replication config (`RESET SLAVE ALL;` on MariaDB)
`SET GLOBAL replica_parallel_workers=4;` | MySQL parallel apply (stop the replica first)
`SET GLOBAL slave_parallel_threads=4;` | MariaDB parallel apply (stop the slave first)
