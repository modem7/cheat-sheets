# SQLite Cheat-Sheet

General SQL and engine differences: [SQL](sql.md).

SQLite is a relational database contained in a C library. In contrast to many other databases, SQLite is not a client-server database engine. Rather, it's embedded into an end program.

SQLite generally follows the PostgreSQL ([PostgreSQL Cheat-Sheet](postgres.md)) syntax but does not enforce type checking (columns use type affinity; `STRICT` tables are available since 3.37).

You can open a SQLite Database with `sqlite3 <filename>` directly.

## Shell Commands (dot-commands)
COMMAND | DESCRIPTION
---|---
`.help` | Show all commands
`.databases` | Show all attached databases
`.tables` | Show all tables
`.schema [<TABLE>]` | Show CREATE statements
`.indexes <TABLE>` | Show indexes
`.headers on` | Show column headers
`.mode column` | Aligned columns (also `csv`, `json`, `markdown`, `table`, `line`)
`.timer on` | Show query time
`.read <FILE>.sql` | Run SQL from a file
`.import <FILE>.csv <TABLE>` | Import CSV (use `.mode csv` first)
`.output <FILE>` | Send results to a file (`.output` alone resets)
`.dump` | Whole database as SQL
`.backup <FILE>` | Backup the current database
`.restore <FILE>` | Restore from a backup
`.once <FILE>` | Write only the next query's result to a file
`.quit` | Exit

## Command Line
COMMAND | DESCRIPTION
---|---
`sqlite3 app.db "SELECT * FROM users LIMIT 5;"` | Run one statement
`sqlite3 -header -column app.db "SELECT * FROM users;"` | Formatted output
`sqlite3 -csv -header app.db "SELECT * FROM users;" > users.csv` | Export CSV
`sqlite3 app.db .dump > backup.sql` | SQL dump
`sqlite3 new.db < backup.sql` | Restore from a dump
`sqlite3 app.db ".backup 'backup.db'"` | Online consistent backup
`sqlite3 app.db "VACUUM;"` | Rebuild and shrink the file
`sqlite3 app.db "PRAGMA integrity_check;"` | Check for corruption

## Useful PRAGMAs
PRAGMA | DESCRIPTION
---|---
`PRAGMA journal_mode=WAL;` | Write-ahead log: better concurrency
`PRAGMA foreign_keys=ON;` | Enforce foreign keys (off by default, per connection)
`PRAGMA table_info(users);` | Column details
`PRAGMA index_list(users);` | Indexes on a table
`PRAGMA user_version;` | Schema version number you can use for migrations
`PRAGMA busy_timeout=5000;` | Wait up to 5 s for locks

## Examples
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO users (name) VALUES ('alice'), ('bob');
SELECT name, datetime(created_at, 'localtime') FROM users;
ALTER TABLE users ADD COLUMN email TEXT;
CREATE INDEX idx_users_name ON users(name);
EXPLAIN QUERY PLAN SELECT * FROM users WHERE name = 'alice';
```

## Users and Access
SQLite has **no users, roles or passwords**. Access is controlled by file permissions on the database file and its directory (SQLite also creates `-wal`, `-shm` or `-journal` files next to it, so the directory must be writable by the same user):
```bash
chmod 600 app.db
chown appuser:appuser app.db
```
Open read-only with `sqlite3 -readonly app.db` or `file:app.db?mode=ro` URIs. For encryption use SQLCipher or an encrypted file system.

## Indexes
SQL | DESCRIPTION
---|---
`CREATE INDEX idx_users_name ON users(name);` | Index
`CREATE UNIQUE INDEX uq_users_email ON users(email);` | Unique
`CREATE INDEX idx_open ON orders(created_at) WHERE status = 'open';` | Partial index
`CREATE INDEX idx_lower ON users(lower(email));` | Expression index
`DROP INDEX idx_users_name;` | Remove
`.indexes users` | List (shell)
`PRAGMA index_info(idx_users_name);` | Columns of an index
`REINDEX;` | Rebuild
`ANALYZE;` | Gather statistics for the planner
`PRAGMA optimize;` | Run `ANALYZE` where useful. Run before closing a long-lived connection

## EXPLAIN QUERY PLAN
```sql
EXPLAIN QUERY PLAN SELECT * FROM users WHERE name = 'alice';
```
OUTPUT | MEANING
---|---
`SEARCH users USING INDEX idx_users_name (name=?)` | Index lookup (good)
`SEARCH users USING INTEGER PRIMARY KEY (rowid=?)` | Primary key lookup
`SCAN users` | Full table scan. Fine for small tables, a problem on big ones
`USE TEMP B-TREE FOR ORDER BY` | Sort without an index
`COVERING INDEX` | Answered from the index alone

In the shell, `.eqp on` shows the plan for each query, and `.scanstats on` adds scan statistics.

## Vacuum and Maintenance
COMMAND | DESCRIPTION
---|---
`VACUUM;` | Rebuild the file to reclaim free pages (needs free disk of about the database size, takes a write lock)
`VACUUM INTO 'copy.db';` | Write a compacted copy (also a safe backup)
`PRAGMA auto_vacuum = INCREMENTAL;` | Set **before** creating tables (or follow with `VACUUM`), then `PRAGMA incremental_vacuum;`
`PRAGMA wal_checkpoint(TRUNCATE);` | Fold the WAL file back into the database
`PRAGMA integrity_check;` / `PRAGMA quick_check;` | Verify the file (`ok` is good)
`PRAGMA foreign_key_check;` | Find foreign key violations
`PRAGMA page_count; PRAGMA freelist_count;` | Pages in the file and free pages (a high ratio means `VACUUM` would help)
`PRAGMA page_size;` | Page size (set before creating the database)
`.dbinfo` | Summary of database properties (shell)

## Performance Settings
Set per connection when opening the database (WAL persists in the file, the rest do not):
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;      -- safe with WAL, much faster than FULL
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;
PRAGMA cache_size = -64000;       -- negative = KiB, here 64 MB
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 268435456;
```
Group many writes in one transaction (`BEGIN; ... COMMIT;`), it is the largest single speed-up. One writer at a time: use WAL and a busy timeout for concurrent readers. Do not put SQLite database files on NFS or other network file systems ([NFS](../linux/nfs.md)), file locking is unreliable.

## Extensions and Features
FEATURE | USE
---|---
`FTS5` | Full-text search virtual tables: `CREATE VIRTUAL TABLE docs USING fts5(title, body);` then `SELECT * FROM docs WHERE docs MATCH 'word';`
`JSON1` | `json_extract(col, '$.key')`, `col ->> '$.key'`, `json_each()` (built in from 3.38)
`R*Tree` | Spatial indexes
`STRICT` tables | `CREATE TABLE t (...) STRICT;` enforces column types (3.37+)
`generated columns` | `full_name TEXT GENERATED ALWAYS AS (first \|\| ' ' \|\| last) VIRTUAL`
`.load ./ext` | Load a loadable extension (for example `sqlite-vec`, `spellfix1`)
`UPSERT` | `INSERT ... ON CONFLICT(id) DO UPDATE SET name = excluded.name;`
`RETURNING` | `INSERT ... RETURNING id;` (3.35+)

## Backup
- `sqlite3 app.db ".backup 'backup.db'"` or `VACUUM INTO` are consistent while the app is running.
- `.dump` gives portable SQL, slower to restore.
- Copying the file is only safe when no process writes. With WAL copy the `-wal` and `-shm` files too, or checkpoint first.
- [Litestream](https://litestream.io/) streams WAL changes to S3-compatible storage for continuous backup.

## Notes
- `sqlite_master` lists all schema objects: `SELECT name, type FROM sqlite_master;`
- Do not copy a live database file with `cp` while it is being written. Use `.backup`.
- Browse with [DB Browser for SQLite](https://sqlitebrowser.org/).
