# Docker-Compose
Compose defines and runs multi-container applications from a single YAML file (`compose.yaml`). It ships with Docker as the `docker compose` plugin (the old standalone `docker-compose` is end-of-life). See [Docker](docker.md), [Dockerfile](docker-file.md) and [Docker Networking](docker-networking.md).

Documentation: [Compose file reference](https://docs.docker.com/reference/compose-file/)

## CLI
COMMAND | DESCRIPTION
---|---
`docker compose up -d` | Create and start in the background
`docker compose up -d --build` | Rebuild images first
`docker compose up -d --force-recreate` | Recreate containers even if unchanged
`docker compose down` | Stop and remove containers and networks
`docker compose down -v` | Also remove named volumes (deletes data)
`docker compose ps` | List services
`docker compose logs -f <SERVICE>` | Follow logs
`docker compose exec <SERVICE> sh` | Shell into a running service
`docker compose run --rm <SERVICE> <CMD>` | One-off container
`docker compose pull` | Pull newer images
`docker compose restart <SERVICE>` | Restart a service
`docker compose stop` / `start` | Stop / start without removing
`docker compose config` | Validate and print the resolved file
`docker compose config --services` | List service names
`docker compose top` | Processes in each service
`docker compose -f a.yaml -f b.yaml up -d` | Merge multiple files
`docker compose --profile <NAME> up -d` | Enable a profile
`docker compose -p <NAME> up -d` | Set the project name

Update a stack to the latest images:
```bash
docker compose pull && docker compose up -d && docker image prune -f
```

## Full Example
```yaml
services:
  app:
    image: ghcr.io/example/app:1.2.3
    restart: unless-stopped
    environment:
      DATABASE_URL: postgres://app:${DB_PASSWORD}@db:5432/app
    env_file: .env
    ports:
      - "127.0.0.1:8080:8080"
    volumes:
      - app-data:/data
      - ./config.yml:/etc/app/config.yml:ro
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:8080/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    networks: [frontend, backend]
    deploy:
      resources:
        limits:
          memory: 512M

  db:
    image: postgres:17
    restart: unless-stopped
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: app
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 10s
      retries: 5
    networks: [backend]

volumes:
  app-data:
  db-data:

networks:
  frontend:
  backend:
    internal: true
```

## Networking
By default Compose creates one network per project, and services reach each other by service name. You can change the behaviour by defining custom networks in your compose file.

### Create and assign custom network
```yaml
networks:
  custom-network:

services:
  app:
    networks:
      - custom-network
```

### Use existing networks
If you want to use an existing Docker network for your compose files, you can add the `external: true` parameter in your compose file.
```yaml
networks:
  existing-network:
    external: true
```

## Volumes
Volumes allow containers to use persistent storage.
```yaml
volumes:
  my-volume:

services:
  app:
    volumes:
      - my-volume:/path-in-container        # named volume
      - ./host-dir:/path-in-container:ro    # bind mount, read-only
```
Named volumes are stored in `/var/lib/docker/volumes`.

## Variables and Secrets
- `${VAR}` is substituted from the shell or from a `.env` file next to the compose file.
- `${VAR:-default}` supplies a default, `${VAR:?error}` fails when unset.
- Keep `.env` out of Git. For real secrets use the top-level `secrets:` block instead of environment variables.
```yaml
services:
  app:
    secrets: [db_password]
secrets:
  db_password:
    file: ./db_password.txt
```

## Profiles, Extends and Overrides
- `compose.override.yaml` is merged automatically with `compose.yaml`. Use it for local development changes.
- `profiles: [debug]` on a service keeps it off unless `--profile debug` is given.
- `include:` (Compose 2.20+) pulls in other compose files.

## Tips
- Pin image tags, avoid `latest`.
- Bind published ports to `127.0.0.1` unless they must be public.
- Use `depends_on` with `condition: service_healthy` for start-up order.
- Run `docker compose config` before committing to catch mistakes.
- Drop the obsolete top-level `version:` key.
