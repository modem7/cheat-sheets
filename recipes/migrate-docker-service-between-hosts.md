# Migrate a Docker Service Between Hosts
Move a Compose stack, its volumes and its database from one Docker host to another with a short, planned outage, a DNS cut-over and a way back.

Documentation: [Compose file reference](https://docs.docker.com/reference/compose-file/) · [Docker: volumes](https://docs.docker.com/engine/storage/volumes/)

> **Verification:** the volume copy pipe (`tar` from a read-only volume into `tar xpf` in another volume, keeping numeric owner and mode) was run between two Docker volumes on one machine. The Postgres dump and restore pattern was run with `postgres:16` in containers. Copying over SSH between two real hosts, the DNS cut-over and the Traefik certificate behaviour were **not** run *(unverified)*.

## Goal
`app.example.com` is served from the new host with the same data, the old host keeps a stopped, intact copy for a week, and you can switch back by changing DNS.

## Prerequisites
- A new host set up as in [New Server Checklist](new-server-checklist.md), with the same Docker major version and the same proxy and network layout as the old one ([Docker Service Deploy](docker-service-deploy.md))
- SSH from the old host to the new host with a key (see [OpenSSH Cheat-Sheet](../tools/openssh.md))
- A recent, **tested** backup of the stack ([Off-Site Docker Host Backup with restic](offsite-docker-host-backup.md), [Restore-Test a Backup](restore-test-a-backup.md)). A migration is a restore plus a deletion risk.
- Control of the DNS record, and a maintenance window

## Steps
### 1. Inventory what the stack owns
On the old host, from the stack directory:
```bash
cd /opt/stacks/<STACK>
docker compose config --volumes
docker compose config | grep -E 'image:|source:|external|name:'
docker compose ps --format '{{ .Service }} {{ .Image }}'
ls -la
```
Write down: the images and tags, named volumes, bind-mount paths, external networks, `.env` and secret files, published ports, and anything that points at the old host (hostnames in config files, webhook URLs, IP allow-lists, backup jobs, monitoring targets).

### 2. Lower the DNS TTL
A day ahead, set the TTL of `app.example.com` to 60 or 300 seconds so the cut-over takes effect quickly ([DNS Record Types](../networking/dns-record-types.md), [DNS Troubleshooting](dns-troubleshooting.md)).

### 3. Prepare the new host and rehearse
Recreate the shared pieces first (`docker network create proxy`, Traefik with a valid `acme.json`, see [Docker Service Deploy](docker-service-deploy.md)). Copy the stack directory, including `.env` and `secrets/`, while preserving permissions and hidden files:
```bash
rsync -aHAX --numeric-ids --info=progress2 /opt/stacks/<STACK>/ <USER>@<NEW_HOST>:/opt/stacks/<STACK>/
```
On the new host, pull the images now so the outage is short:
```bash
cd /opt/stacks/<STACK> && docker compose pull
```
Do not start it yet. Two copies of an app writing to separate databases, or two instances sending the same emails, cause trouble.

### 4. Stop the stack on the old host
```bash
cd /opt/stacks/<STACK>
docker compose stop            # keeps containers and volumes; the outage starts here
```
If the database must be dumped by the database itself, stop only the app, take the dump, then stop everything:
```bash
docker compose stop app
docker compose exec -T db pg_dump -U postgres -Fc <DATABASE> > /tmp/<DATABASE>.dump
docker compose stop
```
Other engines are in [Database Dumps](../backup/database-dumps.md). A dump is portable across hosts and across minor versions; a copied data directory is not portable across major versions.

### 5. Copy the data
**Named volume**, streamed over SSH, with owners and modes kept (the volume names include the Compose project prefix, check `docker volume ls`):
```bash
ssh <USER>@<NEW_HOST> docker volume create <PROJECT>_<VOLUME>
docker run --rm -v <PROJECT>_<VOLUME>:/data:ro alpine tar cf - -C /data . \
  | ssh <USER>@<NEW_HOST> 'docker run --rm -i -v <PROJECT>_<VOLUME>:/data alpine tar xpf - -C /data'
```
**Bind mount** data:
```bash
sudo rsync -aHAX --numeric-ids --info=progress2 /srv/<STACK>/ <USER>@<NEW_HOST>:/srv/<STACK>/
```
(the remote side needs root, or use `--rsync-path="sudo rsync"`). Do not copy a live database's data volume: either skip it and restore the dump, or copy it only while the database container is stopped and the same major version will read it. For the database dump:
```bash
scp /tmp/<DATABASE>.dump <USER>@<NEW_HOST>:/tmp/
```
Files that held credentials (the dump, `.env`) should be deleted from `/tmp` afterwards.

### 6. Start the database on the new host and restore
```bash
cd /opt/stacks/<STACK>
docker compose up -d db
docker compose exec -T db pg_restore -U postgres -d <DATABASE> --clean --if-exists --no-owner < /tmp/<DATABASE>.dump
```
If the database does not exist yet, create it first: `docker compose exec db createdb -U postgres <DATABASE>`. Restore the dump into a fresh volume, not on top of old data.

### 7. Start the stack and test before the cut-over
```bash
docker compose up -d
docker compose ps
```
Test through the new host without touching DNS by overriding the resolution on your workstation:
```bash
curl -sI --resolve app.example.com:443:<NEW_HOST_IP> https://app.example.com | head -n 1
```
Traefik with HTTP-01 cannot get a certificate for `app.example.com` until DNS points at the new host, so the first requests show its default certificate. Either copy the old `acme.json` (mode `600`) to the new host in step 3, or use a DNS-01 resolver, which does not depend on where the name points ([Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md)). Check the app in a browser using a hosts-file entry, and verify recent data is there.

### 8. Cut over
Change the DNS record to the new host's address (`203.0.113.20`, an example documentation address). Wait for the TTL, then watch the new host's logs:
```bash
dig +short app.example.com
docker compose logs -f --tail 50 app
```
Update everything from step 1 that pointed at the old host: webhooks, monitoring targets ([Monitor a Homelab with Prometheus and Grafana](monitor-homelab-prometheus-grafana.md)), backup jobs, firewall rules, and the cron or timer that backs the new host up.

### 9. Keep the old host as the rollback, then retire it
Leave the stack stopped on the old host for about a week. Do not run `docker compose down -v` there until the new host has produced at least one good backup and one tested restore. Then remove the stack and the old volumes ([Docker Cleanup](../docker/docker-cleanup.md)), and restore the DNS TTL to its normal value.

## Verify
```bash
dig +short app.example.com                                  # the new address
curl -sI https://app.example.com | head -n 1
docker compose ps                                           # healthy on the new host
docker compose exec -T db psql -U postgres -d <DATABASE> -tc 'SELECT count(*) FROM <TABLE>'
```
Row counts and file counts match what you wrote down before the move, new data is written on the new host, and the next backup includes the stack.

## Troubleshooting
SYMPTOM | FIX
---|---
App starts but is empty | The volume name differs (project prefix); compare `docker volume ls` on both hosts and copy into the name the Compose file uses
`permission denied` on data | Owners were not kept: copy again with `tar xpf` or `rsync -aHAX --numeric-ids`, as root
`pg_restore` errors about roles or owners | Add `--no-owner`, or create the roles first
Database fails to start: "database files are incompatible with server" | A data directory was copied between major versions; restore from the dump instead
Certificate is the default Traefik one | DNS does not point at the new host yet, `acme.json` has the wrong mode, or the challenge cannot reach port 80 ([TLS Troubleshooting](tls-troubleshooting.md))
Old host still receives traffic | A resolver, router or browser cached the old record; wait for the old TTL, check with `dig @<RESOLVER>`
Two instances running | Stop the old stack; check scheduled jobs and webhooks that call the old address
Image is not found for the new CPU architecture | The hosts differ (amd64 against arm64); use multi-arch images ([OCI Images](../docker/oci-images.md))

## Rollback / Cleanup
- **Back out:** stop the stack on the new host (`docker compose stop`), start it on the old host (`docker compose start`), and point DNS back. New data written on the new host stays there, so export it first if you need it.
- **Clean up the new host after a failed attempt:** `docker compose down -v` removes its containers **and volumes** (destructive), then repeat from step 3.
- **Finish:** delete `/tmp/<DATABASE>.dump` on both hosts, and remove the old stack only after the retention period in step 9.

## Related Sheets
- [Docker](../docker/docker.md) · [Docker-Compose](../docker/docker-compose.md) · [Docker Networking](../docker/docker-networking.md) · [Docker Cleanup](../docker/docker-cleanup.md) · [OCI Images](../docker/oci-images.md)
- [Docker Volume Backup](../backup/docker-volume-backup.md) · [Database Dumps](../backup/database-dumps.md) · [rsync](../backup/rsync.md) · [PostgreSQL Cheat-Sheet](../databases/postgres.md) · [OpenSSH Cheat-Sheet](../tools/openssh.md)
- [Traefik](../apps/traefik.md) · [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md) · [DNS Record Types](../networking/dns-record-types.md)
- [Docker Service Deploy](docker-service-deploy.md) · [New Server Checklist](new-server-checklist.md) · [Off-Site Docker Host Backup with restic](offsite-docker-host-backup.md) · [Restore-Test a Backup](restore-test-a-backup.md) · [Monitor a Homelab with Prometheus and Grafana](monitor-homelab-prometheus-grafana.md) · [TLS Troubleshooting](tls-troubleshooting.md) · [DNS Troubleshooting](dns-troubleshooting.md)
