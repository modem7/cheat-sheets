# SQLite Cheat-Sheet

SQLite is a relational database contained in a C library. In contrast to many other databases, SQLite is not a client-server database engine. Rather, it's embedded into an end program.

SQLite generally follows the PostgreSQL ([[postgres]]) syntax but does not enforce type checking (columns use type affinity; `STRICT` tables are available since 3.37).

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

## Notes
- `sqlite_master` lists all schema objects: `SELECT name, type FROM sqlite_master;`
- Do not copy a live database file with `cp` while it is being written. Use `.backup`.
- Browse with [DB Browser for SQLite](https://sqlitebrowser.org/).
