# SQL
Standard **SQL** basics and common queries, with the points where PostgreSQL, MySQL/MariaDB and SQLite differ. Engine-specific administration is in [PostgreSQL Cheat-Sheet](postgres.md), [MySQL](mysql.md), [MariaDB Cheat-Sheet](mariadb.md) and [SQLite Cheat-Sheet](sqlite.md).

Documentation: [PostgreSQL SQL reference](https://www.postgresql.org/docs/current/sql.html) · [MariaDB SQL statements](https://mariadb.com/kb/en/sql-statements/) · [SQLite SQL syntax](https://www.sqlite.org/lang.html)

> **Verification:** the example queries below were run unchanged on SQLite, PostgreSQL 17 and MariaDB (Alpine packages) in a throwaway container, using the tables in the first section. Engine-specific rows were run on the engine they name. Behaviour can differ by version.

See also: [PostgreSQL Cheat-Sheet](postgres.md) · [MySQL](mysql.md) · [MariaDB Cheat-Sheet](mariadb.md) · [SQLite Cheat-Sheet](sqlite.md) · [Redis](redis.md)

---
## Example Tables
The queries on this sheet use these two tables.

```sql
CREATE TABLE dept (id INT PRIMARY KEY, name VARCHAR(20) NOT NULL);
CREATE TABLE emp (id INT PRIMARY KEY, name VARCHAR(20),
                  dept_id INT REFERENCES dept(id), salary INT);
INSERT INTO dept VALUES (1,'ops'),(2,'dev'),(3,'empty');
INSERT INTO emp VALUES (1,'ann',1,100),(2,'bob',2,200),(3,'cy',2,300),(4,'di',NULL,50);
```

---
## Querying
COMMAND | DESCRIPTION
---|---
`SELECT * FROM emp;` | All rows and columns
`SELECT name, salary FROM emp WHERE salary > 100 ORDER BY salary DESC;` | Filter and sort
`SELECT name FROM emp WHERE dept_id IS NULL;` | Test for NULL (`= NULL` never matches)
`SELECT DISTINCT dept_id FROM emp;` | Unique values
`SELECT * FROM emp ORDER BY id LIMIT 2 OFFSET 1;` | Paging (all three engines)
`SELECT name FROM emp WHERE name LIKE 'a%';` | Pattern match (`%` any text, `_` one character)
`SELECT name FROM emp WHERE salary BETWEEN 100 AND 200;` | Inclusive range
`SELECT name FROM emp WHERE id IN (1, 3);` | Match a list
`SELECT COALESCE(dept_id, 0) FROM emp;` | First non-NULL value
`SELECT CASE WHEN salary >= 200 THEN 'high' ELSE 'low' END FROM emp;` | Conditional expression

---
## Joins and Aggregates
COMMAND | DESCRIPTION
---|---
`SELECT e.name, d.name FROM emp e INNER JOIN dept d ON d.id = e.dept_id;` | Only matching rows
`SELECT d.name, e.name FROM dept d LEFT JOIN emp e ON e.dept_id = d.id;` | Keep every dept, NULL where no employee
`SELECT d.name, COUNT(e.id) AS n, SUM(e.salary) AS total FROM dept d LEFT JOIN emp e ON e.dept_id = d.id GROUP BY d.name HAVING COUNT(e.id) >= 0;` | Group, then filter groups with `HAVING`
`SELECT COUNT(*), MIN(salary), MAX(salary), AVG(salary) FROM emp;` | Common aggregates
`SELECT name, salary, RANK() OVER (ORDER BY salary DESC) AS r FROM emp;` | Window function
`WITH big AS (SELECT * FROM emp WHERE salary > 100) SELECT name FROM big;` | Common table expression (CTE)
`SELECT name FROM emp WHERE dept_id IN (SELECT id FROM dept WHERE name = 'dev');` | Subquery

`COUNT(*)` counts rows; `COUNT(column)` skips NULLs. Window functions need MySQL 8, MariaDB 10.2 or SQLite 3.25 or later (versions unverified; the query ran on current packages).

---
## Changing Data
COMMAND | DESCRIPTION
---|---
`INSERT INTO emp (id, name, salary) VALUES (5, 'ed', 120);` | Insert a row
`UPDATE emp SET salary = salary + 10 WHERE dept_id = 2;` | Update matching rows (always use `WHERE`)
`DELETE FROM emp WHERE id = 4;` | Delete matching rows (always use `WHERE`)
`BEGIN;` ... `COMMIT;` / `ROLLBACK;` | Transaction (MySQL and MariaDB also accept `START TRANSACTION;`)
`CREATE INDEX idx_emp_dept ON emp (dept_id);` | Add an index
`ALTER TABLE emp ADD COLUMN email VARCHAR(50);` | Add a column
`DROP TABLE t;` | Remove a table and its data (destructive)

---
## Engine Differences
TASK | POSTGRESQL | MYSQL / MARIADB | SQLITE
---|---|---|---
Interactive client | `psql` | `mysql` or `mariadb` | `sqlite3`
List tables | `\dt` | `SHOW TABLES;` | `.tables`
Describe a table | `\d emp` | `DESCRIBE emp;` | `.schema emp`
Auto-increment key | `id serial PRIMARY KEY` or `GENERATED ... AS IDENTITY` | `id INT AUTO_INCREMENT PRIMARY KEY` | `id INTEGER PRIMARY KEY AUTOINCREMENT`
Upsert | `INSERT ... ON CONFLICT (k) DO UPDATE SET v = EXCLUDED.v` | `INSERT ... ON DUPLICATE KEY UPDATE v = VALUES(v)` | `INSERT ... ON CONFLICT(k) DO UPDATE SET v = excluded.v`
String concatenation | `'a' \|\| 'b'` | `CONCAT('a','b')` (`\|\|` is logical OR by default) | `'a' \|\| 'b'`
Case-insensitive match | `ILIKE` | `LIKE` (depends on collation) | `LIKE` (ASCII only by default)
Current time | `now()` | `NOW()` | `datetime('now')`
Return affected rows | `INSERT ... RETURNING *` | MariaDB 10.5+ only (unverified); not in MySQL | `RETURNING` since 3.35 (unverified)
Quote identifiers | `"name"` | `` `name` `` | `"name"` or `` `name` ``

Always write `WHERE` in `UPDATE` and `DELETE`, and use a transaction when the result matters.

---
## Troubleshooting
SYMPTOM | FIX
---|---
`= NULL` returns nothing | Use `IS NULL` or `IS NOT NULL`
`'a' \|\| 'b'` returns `0` in MariaDB | `\|\|` is OR there; use `CONCAT()` or enable `PIPES_AS_CONCAT` in `sql_mode` (unverified)
`GROUP BY` error about non-aggregated columns | Add the column to `GROUP BY` or aggregate it
Counts too high after a join | A join multiplies rows; use `COUNT(DISTINCT ...)` or aggregate first
Type surprises in SQLite | Columns use type affinity and are not strictly typed unless the table is `STRICT`

---
## See Also
- [PostgreSQL Cheat-Sheet](postgres.md)
- [MySQL](mysql.md)
- [MariaDB Cheat-Sheet](mariadb.md)
- [SQLite Cheat-Sheet](sqlite.md)
