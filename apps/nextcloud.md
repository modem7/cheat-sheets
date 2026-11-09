# Nextcloud
Nextcloud is a self-hosted file sync, calendar, contacts and collaboration server. The quickest supported install is the All-in-One (AIO) container. Day-to-day admin uses the `occ` command.

Documentation: [Admin manual](https://docs.nextcloud.com/server/latest/admin_manual/), [All-in-One](https://github.com/nextcloud/all-in-one)

## All-in-One (Docker)
```yaml
services:
  nextcloud-aio-mastercontainer:
    image: ghcr.io/nextcloud-releases/all-in-one:latest
    container_name: nextcloud-aio-mastercontainer
    restart: always
    init: true
    ports:
      - "80:80"
      - "8080:8080"
      - "8443:8443"
    volumes:
      - nextcloud_aio_mastercontainer:/mnt/docker-aio-config
      - /var/run/docker.sock:/var/run/docker.sock:ro
volumes:
  nextcloud_aio_mastercontainer:
```

The mastercontainer starts and manages the other containers from its own interface on port 8080. It mounts `docker.sock`, which is root-equivalent on the host. Optional variables: `NEXTCLOUD_DATADIR`, `APACHE_PORT` (when you use your own reverse proxy) and `AIO_DISABLE_BACKUP_SECTION`. Open `443/tcp`, `443/udp`, `3478/tcp` and `3478/udp` on the firewall. AIO backups use Borg, configured in the AIO interface, and updates are done by stopping and then starting and updating containers from that interface (both from a summary of the README).

## occ
Run as the web server user. In AIO use `sudo docker exec --user www-data -it nextcloud-aio-nextcloud php occ <COMMAND>`.

COMMAND | DESCRIPTION
---|---
`sudo -E -u www-data php occ status` | Version and install state
`php occ maintenance:mode --on` / `--off` | Maintenance mode (turn on before backups)
`php occ files:scan --all -vv` | Rescan the file system after changing files outside Nextcloud
`php occ db:add-missing-indices` | Add database indices the admin page asks for (`--dry-run` available)
`php occ db:add-missing-columns` | Add missing columns
`php occ app:list` | Installed apps
`php occ app:update --all` | Update all apps
`php occ app:enable <APP>` / `app:disable <APP>` | Turn an app on or off
`php occ config:system:get <KEY>` | Read a `config.php` value
`php occ config:system:set trusted_domains 2 --value=cloud.example.com` | Add a trusted domain
`php occ user:list` | List users
`php occ user:resetpassword <USER>` | Reset a password

## Behind a Reverse Proxy
Add to `config/config.php`:

```php
'trusted_proxies' => ['PROXY_IP'],
'overwriteprotocol' => 'https',
'overwrite.cli.url' => 'https://cloud.example.com',
```

`overwritehost` is usually not needed. `forwarded_for_headers` defaults to `X-Forwarded-For`. Wrong `trusted_domains` and `overwrite*` values are the usual cause of "access through untrusted domain" errors and redirect loops. See [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md).

## Background Jobs
Use cron, which is the recommended mode:

```bash
sudo crontab -u www-data -e
```

```text
*/5 * * * * php -f /var/www/nextcloud/cron.php
```

Then select Cron in Administration settings, Basic settings, or run `php occ background:cron`. A systemd timer works too.

## Backup
Back up the config, custom apps, theme, data directory and database. Turn maintenance mode on first, dump the database (`mariadb-dump`, `mysqldump`, `pg_dump` or `sqlite3 .dump`), then copy the files. See [Database Dumps](../backup/database-dumps.md) and [Restic](../backup/restic.md).

## See Also
- [Immich](immich.md)
- [Syncthing](syncthing.md)
- [Samba](samba.md)
- [Database Dumps](../backup/database-dumps.md)
