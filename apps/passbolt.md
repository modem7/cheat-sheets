# Passbolt
Passbolt is a self-hosted, open-source password manager for teams, built on OpenPGP. This sheet covers the Community Edition (CE) in Docker Compose, the `cake passbolt` admin commands, and backup and restore.

Documentation: [Passbolt hosting docs](https://www.passbolt.com/docs/hosting/) · [Install on Docker](https://www.passbolt.com/docs/hosting/install/ce/docker/) · [Useful cake commands](https://www.passbolt.com/docs/hosting/useful-commands/) · [Backup from Docker](https://www.passbolt.com/docs/hosting/maintenance/backup/from-docker/)
Project: [passbolt](https://www.passbolt.com/)

> **Verification:** the install steps, the official compose file (`docker-compose-ce.yaml`, downloaded and read), the `register_user`, `healthcheck`, `version`, `recover_user`, `cleanup`, `send_test_email`, `users_index` and user-promotion commands, and the backup and restore commands were checked against the Passbolt docs. **Not run**, and not verified: nothing was executed against a live Passbolt. `sql_export` syntax, `keyring_init` syntax, the `cake passbolt` command list beyond those named here, and the upgrade path are **unverified**. Restores can overwrite data and the docs say to restore only into an empty database.

See also: [Docker-Compose](../docker/docker-compose.md) · [Traefik](traefik.md) · [Bitwarden Cheat-Sheet](../tools/bitwarden.md) · [GPG](../security/gpg.md) · [Database Dumps](../backup/database-dumps.md) · [borgmatic](../backup/borgmatic.md) · [Security](../security/security.md)

---
## Requirements
- A working SMTP server (invites, recovery and notifications are sent by email)
- A working NTP service on the host, or GPG authentication fails on clock drift
- A real hostname with TLS in front, since the browser extension needs HTTPS ([Traefik](traefik.md), [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md))

## Install with Docker Compose
COMMAND | DESCRIPTION
---|---
`curl -LO https://download.passbolt.com/ce/docker/docker-compose-ce.yaml` | Download the official compose file
`curl -LO https://github.com/passbolt/passbolt_docker/releases/latest/download/docker-compose-ce-SHA512SUM.txt` | Download its checksum
`sha512sum -c docker-compose-ce-SHA512SUM.txt` | Verify the file (must print `OK`)
`docker compose -f docker-compose-ce.yaml up -d` | Start MariaDB and Passbolt
`docker compose -f docker-compose-ce.yaml logs -f passbolt` | Follow the application log
`docker compose -f docker-compose-ce.yaml ps` | Container state

Before the first start, edit the file: change the image tag from `latest-ce` to a pinned version, set `APP_FULL_BASE_URL`, replace the sample database password, and add the SMTP variables. The official file ships a sample database password, so never run it as is.

```yaml
services:
  db:
    image: mariadb:10.11
    restart: unless-stopped
    environment:
      MYSQL_RANDOM_ROOT_PASSWORD: "true"
      MYSQL_DATABASE: passbolt
      MYSQL_USER: passbolt
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - database_volume:/var/lib/mysql

  passbolt:
    image: passbolt/passbolt:PINNED_TAG-ce
    restart: unless-stopped
    depends_on:
      - db
    environment:
      APP_FULL_BASE_URL: https://passbolt.example.com
      DATASOURCES_DEFAULT_HOST: db
      DATASOURCES_DEFAULT_USERNAME: passbolt
      DATASOURCES_DEFAULT_PASSWORD: ${DB_PASSWORD}
      DATASOURCES_DEFAULT_DATABASE: passbolt
      EMAIL_DEFAULT_FROM_NAME: Passbolt
      EMAIL_DEFAULT_FROM: passbolt@example.com
      EMAIL_TRANSPORT_DEFAULT_HOST: smtp.example.com
      EMAIL_TRANSPORT_DEFAULT_PORT: 587
      EMAIL_TRANSPORT_DEFAULT_USERNAME: ${SMTP_USER}
      EMAIL_TRANSPORT_DEFAULT_PASSWORD: ${SMTP_PASSWORD}
      EMAIL_TRANSPORT_DEFAULT_TLS: "true"
    volumes:
      - gpg_volume:/etc/passbolt/gpg
      - jwt_volume:/etc/passbolt/jwt
    command: ["/usr/bin/wait-for.sh", "-t", "0", "db:3306", "--", "/docker-entrypoint.sh"]
    ports:
      - 80:80
      - 443:443

volumes:
  database_volume:
  gpg_volume:
  jwt_volume:
```

The structure and volume names match the official file. `${...}` values come from a `.env` file next to the compose file (mode `600`, not in git). The official file has a commented rootless alternative (`latest-ce-non-root`, ports `80:8080` and `443:4433`).

VARIABLE | MEANING
---|---
`APP_FULL_BASE_URL` | Public URL (default `https://passbolt.local`, self-signed)
`DATASOURCES_DEFAULT_HOST` / `_USERNAME` / `_PASSWORD` / `_DATABASE` | Database connection
`EMAIL_DEFAULT_FROM_NAME` / `EMAIL_DEFAULT_FROM` | Sender
`EMAIL_TRANSPORT_DEFAULT_HOST` / `_PORT` / `_USERNAME` / `_PASSWORD` / `_TLS` | SMTP server
`PASSBOLT_GPG_SERVER_KEY_FINGERPRINT` | Required if you mount your own `passbolt.php`, otherwise the instance stops working

### Create the First Admin
```bash
docker compose -f docker-compose-ce.yaml exec passbolt su -m -c "/usr/share/php/passbolt/bin/cake passbolt register_user -u ADMIN_EMAIL -f FIRST_NAME -l LAST_NAME -r admin" -s /bin/sh www-data
```
It prints a setup link. Open it in a browser with the Passbolt extension installed to finish registration. The link is a one-time secret.

## cake passbolt Commands
Run these as the web user. From the host:

```bash
docker compose exec passbolt su -s /bin/bash -c "source /etc/environment && ./bin/cake passbolt COMMAND" www-data
```

For the rootless image use `docker compose exec passbolt ./bin/cake passbolt COMMAND`.

COMMAND | DESCRIPTION
---|---
`passbolt healthcheck` | Check the install; filter with `--database`, `--gpg`, `--application`, `--ssl`, `--environment`, `--configFiles`, `--core`, `--smtpSettings`, `--jwt`, `--metadata`
`passbolt healthcheck --posix` | Exit code reflects errors and warnings (for monitoring)
`passbolt version` | Show the installed version
`passbolt register_user -u EMAIL -f FIRST -l LAST -r admin` | Create a user
`passbolt recover_user -u EMAIL -c` | Create a new recovery token and print the URL (use when email is broken)
`passbolt recover_user -u EMAIL` | Print the URL of an existing, still valid token
`passbolt users_index` | List users
`passbolt user_promote_to_administrator -u EMAIL -a ADMIN_EMAIL` | Promote a user to admin (check the options with `--help`)
`passbolt mfa_user_settings_disable -u EMAIL` | Disable a user's MFA settings
`passbolt send_test_email -r EMAIL` | Send a test email to check SMTP (the docs show a positional address in places)
`passbolt cleanup --dry-run` | Preview database integrity fixes
`passbolt cleanup` | Apply them (modifies the database, aborts if there are no admin users)
`passbolt sql_export` | Database export used by the backup tooling (syntax unverified)

Use `./bin/cake passbolt COMMAND --help` in the container for the options on your version.

## Backup and Restore
Back up all of these together: the database, the GPG server keys, the compose and environment files, `passbolt.php` if mounted, and TLS certificates. Without the server key the database cannot be used, and without the database the key is useless.

```bash
# Database
docker compose -f docker-compose-ce.yaml exec db bash -c \
  'mariadb-dump -u${MYSQL_USER} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE}' > backup.sql

# GPG server keys
docker compose -f docker-compose-ce.yaml cp passbolt:/etc/passbolt/gpg/serverkey_private.asc ./serverkey_private.asc
docker compose -f docker-compose-ce.yaml cp passbolt:/etc/passbolt/gpg/serverkey.asc ./serverkey.asc
```

The `mariadb-dump` command uses the `MYSQL_*` variables of the `db` container; the official file sets them for you. Treat `serverkey_private.asc` and `backup.sql` as secrets and encrypt them before they leave the host.

Restore into an empty database. The command does not drop anything, a failure can leave the database half imported, and large dumps can exceed the PHP `memory_limit`.

```bash
docker compose -f docker-compose-ce.yaml cp backup.sql passbolt:/tmp/backup.sql
docker compose -f docker-compose-ce.yaml exec passbolt \
  su -s /bin/bash -c "source /etc/environment && ./bin/cake passbolt mysql_import --dir /tmp --file backup.sql" www-data
```

Always pass `--file`. After restoring keys, import them into the web server user's keyring with `passbolt keyring_init` (exact syntax unverified, see the Passbolt key restore docs) and run `passbolt healthcheck --gpg`. Rehearse a restore ([Restore-Test a Backup](../recipes/restore-test-a-backup.md)) and see [Database Dumps](../backup/database-dumps.md) for scheduling.

## Troubleshooting
SYMPTOM | FIX
---|---
Login or GPG authentication fails | Check host time (NTP) and run `passbolt healthcheck --gpg`
No invite or recovery email | Run `send_test_email`; check the `EMAIL_*` variables; use `recover_user -u EMAIL -c` for the link
Container loops waiting for the database | Check the `db` logs and that the `DATASOURCES_*` password matches `MYSQL_PASSWORD`
Instance breaks after mounting `passbolt.php` | Set `PASSBOLT_GPG_SERVER_KEY_FINGERPRINT` explicitly
Browser extension refuses the site | `APP_FULL_BASE_URL` must match the public HTTPS URL and certificate
Lost admin access | `recover_user -u EMAIL -c` for a new link; the user's private key and passphrase are not recoverable by the server

## See Also
- [Docker-Compose](../docker/docker-compose.md)
- [Traefik](traefik.md)
- [Bitwarden Cheat-Sheet](../tools/bitwarden.md)
- [GPG](../security/gpg.md)
- [Database Dumps](../backup/database-dumps.md)
- [borgmatic](../backup/borgmatic.md)
- [Security](../security/security.md)
