# MySQL
MySQL is an open source relational database. MariaDB is a compatible fork, see [MariaDB Cheat-Sheet](mariadb.md). Most commands below work on both.

Documentation: [MySQL Reference Manual](https://dev.mysql.com/doc/refman/en/)

See also: [MySQL and MariaDB Replication](mysql-replication.md) · [MariaDB Cheat-Sheet](mariadb.md) · [PostgreSQL Cheat-Sheet](postgres.md)

## Connect
COMMAND | DESCRIPTION
---|---
`mysql -u <USER> -p` | Local login, prompts for password
`mysql -u <USER> -p -h <HOST> -P 3306 <DATABASE>` | Remote login to a database
`sudo mysql` | Root login via unix socket
`mysql -u <USER> -p -e "SHOW DATABASES;"` | Run one statement and exit
`mysql -u <USER> -p <DATABASE> < file.sql` | Run a SQL file

## Databases and Tables
SQL | DESCRIPTION
---|---
`SHOW DATABASES;` | List databases
`CREATE DATABASE app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;` | Create a database
`USE app;` | Select a database
`SHOW TABLES;` | List tables
`DESCRIBE users;` | Show columns
`SHOW CREATE TABLE users\G` | Show the CREATE statement
`SHOW INDEX FROM users;` | Show indexes
`DROP DATABASE app;` | Delete a database

## Users and Privileges
SQL | DESCRIPTION
---|---
`CREATE USER 'app'@'%' IDENTIFIED BY '<PASSWORD>';` | Create a user (any host)
`CREATE USER 'app'@'localhost' IDENTIFIED BY '<PASSWORD>';` | Create a local-only user
`GRANT ALL PRIVILEGES ON app.* TO 'app'@'%';` | Grant full access to one database
`GRANT SELECT ON app.* TO 'ro'@'%';` | Read-only access
`SHOW GRANTS FOR 'app'@'%';` | Show privileges
`REVOKE ALL PRIVILEGES ON app.* FROM 'app'@'%';` | Revoke
`ALTER USER 'app'@'%' IDENTIFIED BY '<NEWPASS>';` | Change a password
`DROP USER 'app'@'%';` | Delete a user
`FLUSH PRIVILEGES;` | Reload grants (not needed after GRANT or CREATE USER)
`SELECT user, host FROM mysql.user;` | List users

## Backup and Restore
COMMAND | DESCRIPTION
---|---
`mysqldump -u <USER> -p <DATABASE> > backup.sql` | Dump one database
`mysqldump -u <USER> -p --single-transaction --routines --triggers <DATABASE> > backup.sql` | Consistent InnoDB dump with routines
`mysqldump -u <USER> -p --all-databases --single-transaction > all.sql` | Dump everything
`mysqldump -u <USER> -p <DATABASE> \| gzip > backup.sql.gz` | Compressed dump
`mysql -u <USER> -p <DATABASE> < backup.sql` | Restore
`gunzip < backup.sql.gz \| mysql -u <USER> -p <DATABASE>` | Restore compressed
`docker exec -i <CONTAINER> mysql -u root -p<PASSWORD> <DATABASE> < backup.sql` | Restore into a container

## Inspection and Performance
SQL | DESCRIPTION
---|---
`SHOW PROCESSLIST;` | Running queries
`KILL <ID>;` | Kill a query
`SHOW STATUS LIKE 'Threads_connected';` | Connection count
`SHOW VARIABLES LIKE 'max_connections';` | Check a setting
`EXPLAIN SELECT ...;` | Query plan
`SELECT table_schema, ROUND(SUM(data_length+index_length)/1024/1024,1) AS mb FROM information_schema.tables GROUP BY table_schema;` | Database sizes in MB
`SHOW ENGINE INNODB STATUS\G` | InnoDB internals and last deadlock

## Indexes
SQL | DESCRIPTION
---|---
`CREATE INDEX idx_users_email ON users (email);` | Add an index
`CREATE UNIQUE INDEX uq_users_email ON users (email);` | Unique index
`CREATE INDEX idx_orders ON orders (user_id, created_at);` | Composite (leftmost column first)
`ALTER TABLE users ADD INDEX idx_name (name);` | Same via `ALTER`
`ALTER TABLE users ADD FULLTEXT INDEX ft_bio (bio);` | Full-text index (`MATCH(bio) AGAINST('word')`)
`DROP INDEX idx_name ON users;` | Remove
`SHOW INDEX FROM users;` | List
`ANALYZE TABLE users;` | Refresh index statistics
`OPTIMIZE TABLE users;` | Rebuild and reclaim space (InnoDB recreates the table)
`SELECT * FROM sys.schema_unused_indexes;` | Indexes never used since start (MySQL `sys` schema)
`SELECT * FROM sys.schema_redundant_indexes;` | Overlapping indexes

Index the columns you filter, join and sort on. Every index slows writes and uses disk. Keep the primary key short in InnoDB: all secondary indexes carry it.

## EXPLAIN
SQL | DESCRIPTION
---|---
`EXPLAIN SELECT * FROM orders WHERE user_id = 5;` | Plan
`EXPLAIN FORMAT=TREE SELECT ...;` | Readable tree (MySQL 8)
`EXPLAIN ANALYZE SELECT ...;` | Runs the query, shows actual times (MySQL 8.0.18+; `ANALYZE SELECT` on MariaDB)
`EXPLAIN FORMAT=JSON SELECT ...;` | Detailed JSON

Read the `type` column: `const`, `eq_ref`, `ref`, `range` are good, `index` scans the whole index, `ALL` is a full table scan. Check `key` (the index used, `NULL` is none), `rows` (estimate), and `Extra` (`Using filesort`, `Using temporary` are slow on big sets, `Using index` means a covering index).

Slow query log:
```sql
SET GLOBAL slow_query_log = 1;
SET GLOBAL long_query_time = 1;
SET GLOBAL log_queries_not_using_indexes = 0;
SHOW VARIABLES LIKE 'slow_query_log_file';
```
Summarise it with `mysqldumpslow -s t /var/log/mysql/mysql-slow.log | head` or `pt-query-digest` (Percona Toolkit). Make settings permanent in the config file.

## Maintenance
COMMAND | DESCRIPTION
---|---
`mysqlcheck -u root -p --all-databases` | Check tables
`mysqlcheck -u root -p --optimize --all-databases` | Optimise tables
`mysqlcheck -u root -p --analyze --all-databases` | Update statistics
`mysql_upgrade` | After a major upgrade on older servers (8.0.16+ upgrades automatically at start)
`SHOW TABLE STATUS FROM app\G` | Rows, size, engine per table
`SELECT table_name, ROUND((data_length+index_length)/1024/1024,1) AS mb FROM information_schema.tables WHERE table_schema='app' ORDER BY mb DESC;` | Biggest tables
`SELECT * FROM sys.statement_analysis LIMIT 10;` | Slowest statement digests (`sys` schema, MySQL 5.7+)
`SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read%';` | Buffer pool misses (`reads` vs `read_requests`)

## Tuning Basics
In `/etc/mysql/mysql.conf.d/mysqld.cnf` under `[mysqld]`, then restart. Check with `SHOW VARIABLES LIKE '...';`.

SETTING | STARTING POINT
---|---
`innodb_buffer_pool_size` | 50-70% of RAM on a dedicated database host. The most important setting
`innodb_log_file_size` | Larger for write-heavy loads (MySQL 8.0.30+ uses `innodb_redo_log_capacity`, for example `2G`)
`innodb_flush_log_at_trx_commit` | `1` safe (default). `2` is faster and can lose about 1 s on an OS crash
`innodb_flush_method` | `O_DIRECT` on Linux
`max_connections` | 150-300. Each connection uses memory
`tmp_table_size` / `max_heap_table_size` | 64 MB - 256 MB
`slow_query_log` / `long_query_time` | On, `1`
`character-set-server` / `collation-server` | `utf8mb4` / `utf8mb4_0900_ai_ci` (MySQL 8) or `utf8mb4_unicode_ci`

MySQL 8.0 removed the query cache (MariaDB still has one, off by default). Use [MySQLTuner](https://github.com/major/MySQLTuner-perl) for advice from a running server. Replication is in [MySQL and MariaDB Replication](mysql-replication.md).

## Users: Good Practice
- One user per application, limited to its own database and the hosts it connects from (`'app'@'192.168.1.%'`).
- Use `caching_sha2_password` (default in MySQL 8) and make sure client libraries support it.
- `CREATE ROLE reader; GRANT SELECT ON app.* TO reader; GRANT reader TO 'alice'@'%'; SET DEFAULT ROLE reader TO 'alice'@'%';` uses roles (MySQL 8 and MariaDB 10.0.5+).
- `ALTER USER 'app'@'%' PASSWORD EXPIRE INTERVAL 180 DAY;` password expiry.
- `ALTER USER 'app'@'%' WITH MAX_USER_CONNECTIONS 20;` per-user connection cap.
- `SHOW GRANTS;` for the current user. `SELECT user, host, plugin FROM mysql.user;` lists authentication plugins.

## Run with Docker
```bash
docker run -d --name mysql -e MYSQL_ROOT_PASSWORD=<PASSWORD> -e MYSQL_DATABASE=app \
  -v mysql-data:/var/lib/mysql -p 127.0.0.1:3306:3306 mysql:8.4
```

## Config
PATH | DESCRIPTION
---|---
`/etc/mysql/my.cnf` | Main config, includes `conf.d/` and `mysql.conf.d/`
`/var/lib/mysql/` | Data directory
`/var/log/mysql/error.log` | Error log

## Reset a Lost Root Password
```bash
sudo systemctl stop mysql
sudo mysqld_safe --skip-grant-tables --skip-networking &
mysql -u root
```
```sql
FLUSH PRIVILEGES;
ALTER USER 'root'@'localhost' IDENTIFIED BY '<NEWPASS>';
```
Then stop `mysqld_safe` and start the service normally.
