# Docker Service Deploy
Deploy a Docker Compose application behind Traefik with automatic Let's Encrypt TLS, with secrets kept out of the Compose file, healthchecks, and a routine for updates and logs.

Documentation: [Traefik Docker provider](https://doc.traefik.io/traefik/providers/docker/) · [Compose file reference](https://docs.docker.com/reference/compose-file/)

## Goal
`https://app.example.com` serves your application over TLS through Traefik, the stack restarts on failure, secrets are not in git, and you know how to update, inspect and roll it back.

## Prerequisites
- A host with Docker and the Compose plugin ([New Server Checklist](new-server-checklist.md))
- A DNS `A` record for `app.example.com` pointing at the host (`203.0.113.10`), and ports 80 and 443 reachable from the internet (needed for the HTTP-01 challenge)
- A directory per stack, for example `/opt/stacks/app`

## Steps
### 1. Create the shared proxy network and layout
```bash
docker network create proxy
mkdir -p /opt/stacks/traefik /opt/stacks/app
touch /opt/stacks/traefik/acme.json && chmod 600 /opt/stacks/traefik/acme.json
```
Traefik refuses to use an `acme.json` that is group or world readable.

### 2. Traefik static configuration
`/opt/stacks/traefik/traefik.yml` ([Traefik](../apps/traefik.md)):
```yaml
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"
providers:
  docker:
    exposedByDefault: false
    network: proxy
certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@example.com
      storage: /acme.json
      httpChallenge:
        entryPoint: web
```
While testing, add `caServer: https://acme-staging-v02.api.letsencrypt.org/directory` under `acme:` to avoid production rate limits, then remove it and delete `acme.json` contents.

### 3. Run Traefik
`/opt/stacks/traefik/compose.yaml`:
```yaml
services:
  traefik:
    image: traefik:v3
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik.yml:/etc/traefik/traefik.yml:ro
      - ./acme.json:/acme.json
    networks: [proxy]
networks:
  proxy:
    external: true
```
```bash
cd /opt/stacks/traefik && docker compose up -d
```
Pin `traefik:v3` to a full version tag for repeatable deploys. The Docker socket gives Traefik full control of Docker; consider a socket proxy for exposed hosts.

### 4. Keep secrets out of the Compose file
Create `/opt/stacks/app/.env` (mode `600`, listed in `.gitignore`) for plain settings, and use file-based secrets for passwords:
```bash
cd /opt/stacks/app
mkdir -p secrets && chmod 700 secrets
openssl rand -base64 32 > secrets/db_password && chmod 600 secrets/db_password
printf 'APP_HOST=app.example.com\nTZ=Europe/London\n' > .env
```
Commit a `.env.example` with the same keys and no values. Variables in `.env` are used for `${VAR}` substitution in the Compose file; use `env_file:` to pass a file into a container.

### 5. The application stack
`/opt/stacks/app/compose.yaml` ([Docker-Compose](../docker/docker-compose.md)):
```yaml
services:
  app:
    image: ghcr.io/example/app:1.2.3
    restart: unless-stopped
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1:8080/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s
    networks: [proxy, internal]
    labels:
      - traefik.enable=true
      - traefik.docker.network=proxy
      - traefik.http.routers.app.rule=Host(`${APP_HOST}`)
      - traefik.http.routers.app.entrypoints=websecure
      - traefik.http.routers.app.tls.certresolver=letsencrypt
      - traefik.http.services.app.loadbalancer.server.port=8080

  db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets: [db_password]
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks: [internal]

secrets:
  db_password:
    file: ./secrets/db_password

volumes:
  db-data:

networks:
  proxy:
    external: true
  internal:
```
Only images that support the `_FILE` convention (the official `postgres`, `mysql` and `mariadb` images do) can read a secret from a file; for others, check the image documentation. Replace the `healthcheck` command with something that exists in your image. The database sits only on the `internal` network, so it is not reachable from Traefik or the host.

### 6. Validate and start
```bash
docker compose config           # renders the file, fails on errors
docker compose up -d
docker compose ps               # STATUS should reach "healthy"
```

### 7. Logs
```bash
docker compose logs -f --tail 100 app
docker logs -f traefik
```
Set the Traefik `log.level: INFO` (and optionally `accessLog: {}`) in `traefik.yml` for more detail.

### 8. Update
```bash
cd /opt/stacks/app
docker compose pull
docker compose up -d
docker image prune -f
```
Back up volumes first (for a database use a dump, for example `docker compose exec db pg_dump -U postgres > backup.sql`). To change versions, edit the image tag and run the same two commands.

## Verify
```bash
curl -sI https://app.example.com | head -n 1           # HTTP/2 200
curl -sI http://app.example.com | grep -i '^location'  # redirects to https
echo | openssl s_client -connect app.example.com:443 -servername app.example.com 2>/dev/null \
  | openssl x509 -noout -issuer -dates
docker compose ps
```
If the certificate is the self-signed "TRAEFIK DEFAULT CERT", the challenge has not completed: read `docker logs traefik`, and see [TLS Troubleshooting](tls-troubleshooting.md) and [DNS Troubleshooting](dns-troubleshooting.md).

## Rollback / Cleanup
- Roll back an update: set the previous image tag in `compose.yaml`, then `docker compose up -d`. Restore the database from the dump if a migration ran.
- Stop and remove the stack but keep data: `docker compose down`. Add `-v` only to delete the volumes as well.
- Remove the shared network once nothing uses it: `docker network rm proxy`.

## Related Sheets
- [Docker](../docker/docker.md) · [Docker-Compose](../docker/docker-compose.md) · [Docker Networking](../docker/docker-networking.md) · [Dockerfile](../docker/docker-file.md)
- [Traefik](../apps/traefik.md) · [Nginx](../apps/nginx.md) · [Portainer](../apps/portainer.md) · [Dockhand](../apps/dockhand.md)
- [PostgreSQL Cheat-Sheet](../databases/postgres.md) · [curl](../tools/curl.md) · [OpenSSL](../tools/openssl.md)
- [New Server Checklist](new-server-checklist.md) · [TLS Troubleshooting](tls-troubleshooting.md)
- [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md) · [Container Scanning](../security/container-scanning.md) · [SOPS and age](../security/sops-age.md) · [Docker Volume Backup](../backup/docker-volume-backup.md) · [CI Docker Builds](../cicd/ci-docker-builds.md) · [Renovate](../cicd/renovate.md)
