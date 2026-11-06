# PostgreSQL Cheat-Sheet
PostgreSQL, also known as Postgres, is a free and open-source relational database management system. PostgreSQL features transactions with Atomicity, Consistency, Isolation, Durability (ACID) properties, automatically updatable views, materialized views, triggers, foreign keys, and stored procedures. It is designed to handle a range of workloads, from single machines to data warehouses or web services with many concurrent users.

Documentation: [PostgreSQL Docs](https://www.postgresql.org/docs/current/)

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
See [[docker]] and [[docker-compose]]. For major versions 18 and later the image changed its data directory layout, so check the image documentation for the mount path before upgrading.

### Install / deploy Postgres on Kubernetes with Zalando Postgres Operator

Postgres is probably the most common database on cloud platforms and also runs on Kubernetes ([[kubernetes]]). Several "Kubernetes Operators" handle the deployment of Postgres clusters for you. One of them is the [Postgres Operator by Zalando](https://github.com/zalando/postgres-operator).

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
Open TCP port 5432 in the firewall only for trusted networks (see [[ufw]]).

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
