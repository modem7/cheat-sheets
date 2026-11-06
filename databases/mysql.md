# MySQL
MySQL is an open source relational database. MariaDB is a compatible fork, see [[mariadb]]. Most commands below work on both.

Documentation: [MySQL Reference Manual](https://dev.mysql.com/doc/refman/en/)

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
