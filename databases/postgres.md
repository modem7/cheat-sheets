# PostgreSQL Cheat-Sheet
PostgreSQL, also known as Postgres, is a free and open-source relational database management system. PostgreSQL features transactions with Atomicity, Consistency, Isolation, Durability (ACID) properties, automatically updatable views, materialized views, triggers, foreign keys, and stored procedures. It is designed to handle a range of workloads, from single machines to data warehouses or web services with many concurrent users.

Documentation: [PostgreSQL Docs](https://www.postgresql.org/docs/current/)

See also: [PostgreSQL Backup and Replication](postgres-backup-replication.md) · [Redis](redis.md) · [MongoDB](mongodb.md) · [MySQL](mysql.md) · [SQLite Cheat-Sheet](sqlite.md) · [SQL](sql.md)

## Installation
### Install PostgreSQL on Ubuntu / Debian
```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib postgresql-client
sudo systemctl status postgresql.service
```
This installs the version shipped with your release (16 on Ubuntu 24.04, 12 on 20.04). For a newer version use the official PGDG apt repository. In paths below replace `16` with your major version (`ls /etc/postgresql`).

### Run in Docker
```bash
docker run -d --name postgres --restart unless-stopped \
  -e POSTGRES_PASSWORD=Supersecret \
  -e POSTGRES_USER=myuser -e POSTGRES_DB=dbname \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16
docker exec -it postgres psql -U myuser -d dbname
```
See [Docker](../docker/docker.md) and [Docker-Compose](../docker/docker-compose.md). For major versions 18 and later the image changed its data directory layout, so check the image documentation for the mount path before upgrading.

### Install / deploy Postgres on Kubernetes with Zalando Postgres Operator

Postgres is probably the most common database on cloud platforms and also runs on [Kubernetes](../kubernetes/kubernetes.md). Several "Kubernetes Operators" handle the deployment of Postgres clusters for you. One of them is the [Postgres Operator by Zalando](https://github.com/zalando/postgres-operator).

Tutorials for deploying the operator and working with it:

- [Deploy Zalando Postgres Operator on your Kubernetes cluster](https://thedatabaseme.de/2022/03/13/keep-the-elefants-in-line-deploy-zalando-operator-on-your-kubernetes-cluster/)
- [Configure Zalando Postgres Operator Backup with WAL-G](https://thedatabaseme.de/2022/03/26/backup-to-s3-configure-zalando-postgres-operator-backup-with-wal-g/)
- [Configure Zalando Postgres Operator Restore with WAL-G](https://thedatabaseme.de/2022/05/03/restore-and-clone-from-s3-configure-zalando-postgres-operator-restore-with-wal-g/)

## Initial database connection

A local connection (from the database server) can be made with:

```bash
sudo -u postgres psql
```
```
psql (16.4 (Ubuntu 16.4-0ubuntu0.24.04.1))
Type "help" for help.

postgres=#
```

## Set password for postgres database user

Set the password for the `postgres` database user with the `\password` meta-command or with `ALTER USER postgres PASSWORD 'Supersecret';`. By default `pg_hba.conf` only lets the OS user `postgres` connect locally (`peer`), so a password login is not possible until you change it.

### Update pg_hba.conf to allow password connections

To allow the `postgres` database user to log in without OS user authentication, edit `pg_hba.conf` (`/etc/postgresql/<VERSION>/main/pg_hba.conf`). Ask Postgres where it is with `sudo -u postgres psql -c 'SHOW hba_file;'`.

```
local   all             postgres                                peer
```

Change the method at the end of that line to `scram-sha-256` (the current default password method since PostgreSQL 14; `md5` still works but is older).

```
local   all             postgres                                scram-sha-256
```

Passwords set while `password_encryption` was `md5` keep working under `md5` only. Re-set them (`\password`) after switching to `scram-sha-256`.

To accept remote connections two more things are needed:

1. In `postgresql.conf` set `listen_addresses = '*'` (or a specific IP).
2. Add a `host` line to `pg_hba.conf` for the allowed network:

```
host    all             all             192.168.1.0/24          scram-sha-256
```

Apply with a restart (a reload is enough for `pg_hba.conf` alone):

```bash
sudo systemctl restart postgresql
```

Connect from another host, for example:

```bash
psql -U postgres -d postgres -h databasehostname
```
Open TCP port 5432 in the firewall only for trusted networks (see [UFW (uncomplicated firewall)](../linux/ufw.md)).

## Creation of additional database users

```sql
CREATE USER myuser WITH ENCRYPTED PASSWORD 'Supersecret';
```
```
CREATE ROLE

postgres=# \du
                                   List of roles
 Role name |                         Attributes                         | Member of
-----------+------------------------------------------------------------+-----------
 myuser    |                                                            | {}
 postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS | {}
```

## Creation of additional databases

You can create new databases within an instance. Log in with `psql` (see above).

```sql
CREATE DATABASE dbname OWNER myuser;
```
```
CREATE DATABASE

postgres=# \l
                                  List of databases
   Name    |  Owner   | Encoding |   Collate   |    Ctype    |   Access privileges
-----------+----------+----------+-------------+-------------+-----------------------
 dbname    | myuser   | UTF8     | en_US.UTF-8 | en_US.UTF-8 |
 postgres  | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 |
 template0 | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/postgres          +
           |          |          |             |             | postgres=CTc/postgres
 template1 | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/postgres          +
           |          |          |             |             | postgres=CTc/postgres
```

If you leave out `OWNER`, the current user becomes the owner of the new database.

To change the owner of an existing database later:

```sql
ALTER DATABASE dbname OWNER TO myuser;
```

Grant a user rights on a database:

```sql
GRANT ALL PRIVILEGES ON DATABASE dbname TO myuser;
```
On PostgreSQL 15 and later, ordinary users can no longer create objects in the `public` schema by default. Make the user the database owner (as above) or run `GRANT ALL ON SCHEMA public TO myuser;` while connected to that database.

## psql Meta-Commands
COMMAND | DESCRIPTION
---|---
`\l` | List databases
`\c dbname` | Connect to a database
`\dt` | List tables (`\dt *.*` for all schemas)
`\d tablename` | Describe a table
`\dn` | List schemas
`\du` | List roles
`\dx` | List installed extensions
`\df` | List functions
`\x` | Toggle expanded output (good for wide rows)
`\timing` | Toggle query timing
`\i file.sql` | Run a SQL file
`\copy tbl TO 'f.csv' CSV HEADER` | Export a table to CSV on the client
`\password user` | Change a password safely
`\conninfo` | Show the current connection
`\q` | Quit

## Backup and Restore
COMMAND | DESCRIPTION
---|---
`pg_dump -U myuser -h HOST dbname > dbname.sql` | Plain SQL dump of one database
`pg_dump -U myuser -Fc dbname > dbname.dump` | Compressed custom-format dump
`pg_dumpall -U postgres > all.sql` | Dump every database plus roles
`psql -U myuser -d dbname < dbname.sql` | Restore a plain dump
`pg_restore -U myuser -d dbname --clean --if-exists dbname.dump` | Restore a custom-format dump
`createdb -U postgres -O myuser dbname` | Create the target database first if needed

## Maintenance and Inspection
```sql
SELECT version();
SELECT pg_size_pretty(pg_database_size('dbname'));
SELECT pid, usename, state, query FROM pg_stat_activity;
SELECT pg_terminate_backend(<PID>);
VACUUM (ANALYZE, VERBOSE) tablename;
```

## Drop Users and Databases
```sql
DROP DATABASE dbname;
DROP USER myuser;
```
A user that owns objects cannot be dropped. Use `REASSIGN OWNED BY myuser TO postgres; DROP OWNED BY myuser;` first.

## Roles and Privileges
In Postgres users and groups are both **roles**. `CREATE USER` is `CREATE ROLE ... LOGIN`.

SQL | DESCRIPTION
---|---
`CREATE ROLE readonly NOLOGIN;` | Group role with no login
`GRANT CONNECT ON DATABASE dbname TO readonly;` | Allow connecting
`GRANT USAGE ON SCHEMA public TO readonly;` | Allow seeing the schema
`GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;` | Read existing tables
`ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly;` | Read future tables (for objects created by the current role)
`GRANT readonly TO alice;` | Add a user to the group
`CREATE ROLE app LOGIN PASSWORD '<PASSWORD>' CONNECTION LIMIT 20;` | App user with a connection cap
`ALTER ROLE app SET search_path = app, public;` | Per-role setting
`ALTER ROLE app VALID UNTIL '2027-01-01';` | Password expiry
`REVOKE ALL ON DATABASE dbname FROM PUBLIC;` | Stop other roles connecting by default
`REVOKE CREATE ON SCHEMA public FROM PUBLIC;` | Harden the `public` schema
`\du+` / `\dp` / `\ddp` | psql: roles, table privileges, default privileges
`SELECT rolname, rolsuper, rolcanlogin FROM pg_roles;` | List roles

Give each application its own role and database. Do not use the `postgres` superuser in applications.

## Indexes
SQL | DESCRIPTION
---|---
`CREATE INDEX idx_users_email ON users (email);` | B-tree index (default)
`CREATE INDEX CONCURRENTLY idx_orders_user ON orders (user_id);` | Build without blocking writes (cannot run in a transaction)
`CREATE UNIQUE INDEX ON users (lower(email));` | Unique, on an expression
`CREATE INDEX ON orders (created_at) WHERE status = 'open';` | Partial index
`CREATE INDEX ON orders (user_id, created_at DESC);` | Multi-column (order matters)
`CREATE INDEX ON docs USING gin (tags);` | GIN: arrays, `jsonb`, full text
`CREATE INDEX ON events USING brin (created_at);` | BRIN: tiny index for huge, naturally ordered tables
`DROP INDEX CONCURRENTLY idx_users_email;` | Drop without a long lock
`REINDEX INDEX CONCURRENTLY idx_users_email;` | Rebuild a bloated index
`\di+` | psql: indexes and sizes

Find unused and missing indexes:
```sql
SELECT relname, indexrelname, idx_scan FROM pg_stat_user_indexes ORDER BY idx_scan ASC LIMIT 20;
SELECT relname, seq_scan, idx_scan FROM pg_stat_user_tables ORDER BY seq_scan DESC LIMIT 20;
```
Primary keys and unique constraints create their own indexes. Foreign key columns are **not** indexed automatically.

## EXPLAIN
SQL | DESCRIPTION
---|---
`EXPLAIN SELECT ...;` | Estimated plan, runs nothing
`EXPLAIN ANALYZE SELECT ...;` | Runs the query and shows real times and row counts
`EXPLAIN (ANALYZE, BUFFERS) SELECT ...;` | Adds buffer (cache and disk) use
`EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) ...` | Machine-readable output

`EXPLAIN ANALYZE` really executes the statement. Wrap `INSERT`, `UPDATE` and `DELETE` in `BEGIN; ... ROLLBACK;`.

What to look for: `Seq Scan` on a big table with a selective filter (missing index), estimated rows far from actual rows (run `ANALYZE`), `Sort` spilling to disk (`work_mem`), nested loops with large row counts, `Rows Removed by Filter` very high.

Find slow queries with the `pg_stat_statements` extension:
```sql
CREATE EXTENSION pg_stat_statements;      -- also needs shared_preload_libraries = 'pg_stat_statements' and a restart
SELECT calls, round(total_exec_time) AS ms, round(mean_exec_time) AS mean_ms, left(query, 80) AS query
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;
```
Log slow statements: `log_min_duration_statement = 500` (milliseconds) in `postgresql.conf`.

## Vacuum and Autovacuum
Updates and deletes leave dead rows. Autovacuum removes them and updates statistics. It is on by default and should stay on.

SQL | DESCRIPTION
---|---
`VACUUM (ANALYZE, VERBOSE) tablename;` | Reclaim space for reuse and refresh statistics
`VACUUM FULL tablename;` | Rewrite the table, returns disk to the OS, **locks the table**
`ANALYZE;` | Update planner statistics for the database (run after big loads or restores)
`SELECT relname, n_dead_tup, last_autovacuum, last_autoanalyze FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 10;` | Tables with dead rows
`SELECT pg_size_pretty(pg_total_relation_size('tablename'));` | Table plus index size
`ALTER TABLE tablename SET (autovacuum_vacuum_scale_factor = 0.02);` | Vacuum a busy table more often
`SELECT pid, now() - xact_start AS age, state, query FROM pg_stat_activity WHERE xact_start IS NOT NULL ORDER BY age DESC;` | Long transactions (they stop vacuum from cleaning up)

Command line: `vacuumdb --all --analyze-in-stages` (after a `pg_upgrade`), `reindexdb`. For bloat without downtime use the `pg_repack` extension.

## Extensions
SQL | DESCRIPTION
---|---
`SELECT * FROM pg_available_extensions ORDER BY name;` | What can be installed
`CREATE EXTENSION IF NOT EXISTS pg_trgm;` | Install into the current database (needs the right privileges, `postgresql-contrib` package on Debian/Ubuntu)
`\dx` | Installed extensions
`ALTER EXTENSION name UPDATE;` | Update after a package upgrade
`DROP EXTENSION name;` | Remove

EXTENSION | USE
---|---
`pg_stat_statements` | Query statistics
`pg_trgm` | Fuzzy and `LIKE '%x%'` search with a GIN or GiST index
`uuid-ossp` / `pgcrypto` | UUID and crypto functions (`gen_random_uuid()` is built in since 13)
`citext` | Case-insensitive text type
`hstore` | Key/value column (`jsonb` is usually better)
`postgis` | Geospatial data
`pgvector` | Vector similarity search (separate package, extension name `vector`)
`timescaledb` | Time-series (separate package)
`pg_repack` | Online table and index rebuild
`postgres_fdw` | Query other Postgres servers as tables

In Docker, use an image that ships the extension (for example `postgis/postgis`, `pgvector/pgvector`, `timescale/timescaledb`) because extension binaries must be on the server host.

## Tuning Basics
Settings in `postgresql.conf` (or `ALTER SYSTEM SET ...;` then `SELECT pg_reload_conf();`). Defaults are conservative. Check with `SHOW <SETTING>;` and see what needs a restart: `SELECT name, setting, pending_restart FROM pg_settings WHERE pending_restart;`

SETTING | STARTING POINT | NOTES
---|---|---
`shared_buffers` | 25% of RAM | Restart needed
`effective_cache_size` | 50-75% of RAM | Planner hint only, no memory is reserved
`work_mem` | 4-64 MB | Per sort or hash **per query node**, many connections multiply it
`maintenance_work_mem` | 256 MB - 1 GB | Vacuum, index builds
`max_connections` | 100 | Use PgBouncer instead of thousands of connections
`wal_buffers` | 16 MB | Default usually fine
`checkpoint_timeout` / `max_wal_size` | `15min` / `4GB` | Fewer, smoother checkpoints on write-heavy loads
`random_page_cost` | `1.1` on SSD | Default `4` suits spinning disks
`effective_io_concurrency` | `200` on SSD / NVMe | |
`log_min_duration_statement` | `500` | Log slow queries (ms)
`idle_in_transaction_session_timeout` | `5min` | Kill forgotten transactions

Use [PGTune](https://pgtune.leopard.in.ua/) for a first draft and measure afterwards. Docker: pass settings as `postgres -c shared_buffers=1GB -c max_connections=200` after the image name. Also see [Linux Performance Troubleshooting](../linux/performance-troubleshooting.md) and [PostgreSQL Backup and Replication](postgres-backup-replication.md).

## Useful Queries
```sql
-- Database and table sizes
SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database ORDER BY pg_database_size(datname) DESC;
SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 10;

-- Active queries and blockers
SELECT pid, usename, state, wait_event_type, now() - query_start AS runtime, left(query, 60)
FROM pg_stat_activity WHERE state <> 'idle' ORDER BY runtime DESC;
SELECT pg_blocking_pids(pid), pid, query FROM pg_stat_activity WHERE cardinality(pg_blocking_pids(pid)) > 0;

-- Cancel (polite) or terminate (hard)
SELECT pg_cancel_backend(<PID>);
SELECT pg_terminate_backend(<PID>);

-- Cache hit ratio (aim for >99% on OLTP)
SELECT sum(blks_hit) * 100.0 / nullif(sum(blks_hit) + sum(blks_read), 0) AS hit_pct FROM pg_stat_database;
```
