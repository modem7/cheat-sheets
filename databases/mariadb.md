# MariaDB Cheat-Sheet
MariaDB is a community fork of MySQL. Day-to-day SQL, backup and user commands are the same, see [[mysql]].

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
Restart with `sudo systemctl restart mariadb`, then open the firewall only to trusted hosts (`sudo ufw allow from <CIDR> to any port 3306`, see [[ufw]]). Prefer a specific interface address over `0.0.0.0`.

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
Used as the external datastore for K3s HA in [[k3s-install-ha-externaldb]]. MariaDB 10.5+ also ships `mariadb*` command names, with `mysql*` kept as links.
