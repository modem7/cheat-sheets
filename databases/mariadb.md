# MariaDB Cheat-Sheet
MariaDB is a community fork of MySQL. Day-to-day SQL, backup and user commands are the same, see [MySQL](mysql.md). General SQL: [SQL](sql.md).

## Install MariaDB on Ubuntu
```bash
sudo apt update
sudo apt install mariadb-server
sudo mysql_secure_installation
```
Check it runs: `sudo systemctl status mariadb` and `sudo mariadb`.

## Access Database from outside
Open `/etc/mysql/mariadb.conf.d/50-server.cnf` and change the `bind-address` to:
```
bind-address = 0.0.0.0
```
Restart with `sudo systemctl restart mariadb`, then open the firewall only to trusted hosts (`sudo ufw allow from <CIDR> to any port 3306`, see [UFW (uncomplicated firewall)](../linux/ufw.md)). Prefer a specific interface address over `0.0.0.0`.

## Create Administrative User
1. Create a new user `newuser` for the host `localhost` with a new `password`:
```mysql
CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password';
```

2. Grant all permissions to the new user
```mysql
GRANT ALL PRIVILEGES ON * . * TO 'newuser'@'localhost';
```
Use `ON <db>.*` instead of `*.*` for an application user, and add `WITH GRANT OPTION` only for real admins.

3. Update permissions
```mysql
FLUSH PRIVILEGES;
```

## Maintenance
COMMAND | DESCRIPTION
---|---
`sudo mariadb` | Root login through the unix socket
`mariadb-admin status` | Uptime and thread count
`mariadb-admin processlist` | Running queries
`mariadb-dump --single-transaction --all-databases > all.sql` | Full logical backup
`mariadb-check --all-databases --auto-repair` | Check and repair tables
`mariadb-upgrade` | Run after a major version upgrade
`SELECT VERSION();` | Server version
`SHOW GLOBAL STATUS LIKE 'Threads_connected';` | Connections now
`SET GLOBAL slow_query_log=1; SET GLOBAL long_query_time=1;` | Log queries slower than 1 s

## Run with Docker
```bash
docker run -d --name mariadb -e MARIADB_ROOT_PASSWORD=<PASSWORD> \
  -v mariadb-data:/var/lib/mysql -p 127.0.0.1:3306:3306 mariadb:11
```
## Users and Authentication
SQL | DESCRIPTION
---|---
`CREATE USER 'app'@'192.168.1.%' IDENTIFIED BY '<PASSWORD>';` | App user limited to the LAN
`GRANT SELECT, INSERT, UPDATE, DELETE ON app.* TO 'app'@'192.168.1.%';` | Least privilege
`CREATE USER 'admin'@'localhost' IDENTIFIED VIA unix_socket;` | Log in as the matching OS user, no password
`ALTER USER 'root'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('<PASSWORD>');` | Give root a password (default on Debian/Ubuntu is socket authentication)
`CREATE ROLE reader; GRANT SELECT ON app.* TO reader; GRANT reader TO 'alice'@'%'; SET DEFAULT ROLE reader FOR 'alice'@'%';` | Roles
`SHOW GRANTS FOR 'app'@'192.168.1.%';` | Privileges
`SELECT user, host, plugin FROM mysql.user;` | List users (a view over `mysql.global_priv` in 10.4+)
`SET PASSWORD FOR 'app'@'%' = PASSWORD('<NEWPASS>');` | Change a password
`DROP USER 'app'@'%';` | Remove

On Debian/Ubuntu `sudo mariadb` works for root through the unix socket, a password is not needed and a remote root login is not possible. Create a separate admin user for remote use, see [MySQL](mysql.md).

## Indexes, EXPLAIN and Slow Queries
Index and query tuning follow [MySQL](mysql.md). MariaDB specifics:

SQL | DESCRIPTION
---|---
`EXPLAIN SELECT ...;` | Plan (`EXPLAIN EXTENDED` and `FORMAT=JSON` also work)
`ANALYZE SELECT ...;` | Runs the query and shows estimated and actual rows. MariaDB's counterpart to `EXPLAIN ANALYZE`
`ANALYZE FORMAT=JSON SELECT ...;` | Detailed timing
`SHOW INDEX FROM users;` | List indexes
`SELECT * FROM information_schema.INDEX_STATISTICS;` | Index use (needs `userstat=1`)
`SET GLOBAL userstat=1;` | Enable table, index and user statistics
`SET GLOBAL slow_query_log=1; SET GLOBAL long_query_time=1;` | Slow query log
`SET GLOBAL log_slow_verbosity='query_plan,explain';` | Add plans to the slow log
`ANALYZE TABLE t PERSISTENT FOR ALL;` | Engine-independent statistics

Summarise the slow log: `mariadb-dumpslow -s t /var/log/mysql/mariadb-slow.log | head`.

## Tuning Basics
In `/etc/mysql/mariadb.conf.d/50-server.cnf` under `[mysqld]`, then `sudo systemctl restart mariadb`.

SETTING | STARTING POINT
---|---
`innodb_buffer_pool_size` | 50-70% of RAM on a dedicated host
`innodb_log_file_size` | `512M` - `2G` for write-heavy workloads
`innodb_flush_log_at_trx_commit` | `1` safe, `2` faster with small risk
`innodb_flush_method` | `O_DIRECT`
`max_connections` | 150 - 300
`character-set-server` / `collation-server` | `utf8mb4` / `utf8mb4_unicode_ci`
`thread_handling` | `pool-of-threads` for many short connections
`query_cache_type` | `0`. The query cache is mostly a bottleneck on busy servers

Use [MySQLTuner](https://github.com/major/MySQLTuner-perl) for suggestions. Check with `SHOW GLOBAL VARIABLES LIKE '...';` and `SHOW GLOBAL STATUS;`.

## Backup and Replication
COMMAND | DESCRIPTION
---|---
`mariadb-dump --single-transaction --routines --triggers --events --all-databases > all.sql` | Logical backup
`mariadb-dump --single-transaction <DB> \| gzip > db.sql.gz` | One database, compressed
`mariadb-backup --backup --target-dir=/backup/full --user=root --password=<PASSWORD>` | Physical hot backup (package `mariadb-backup`)
`mariadb-backup --prepare --target-dir=/backup/full` | Prepare it for restore
`mariadb-backup --copy-back --target-dir=/backup/full` | Restore into an empty data dir (stop the server first, then `chown -R mysql:mysql`)

GTID replication, monitoring lag and failover are in [MySQL and MariaDB Replication](mysql-replication.md). Galera Cluster gives multi-primary replication: see the MariaDB docs.

Used as the external datastore for K3s HA in [Install K3S in High Availability Mode](../kubernetes/k3s-install-ha-externaldb.md). MariaDB 10.5+ also ships `mariadb*` command names, with `mysql*` kept as links.
