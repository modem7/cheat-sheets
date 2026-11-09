# Komodo
Komodo is a self-hosted tool to build and deploy software across many servers: Docker Compose stacks, containers, image builds, repos, procedures and alerts, managed from one web UI or from TOML files in Git. It sits in the same space as [Portainer](portainer.md) and [Dockhand](dockhand.md). This sheet covers Komodo v2.

Project: [Komodo](https://github.com/moghtech/komodo)
Documentation: [komo.do](https://komo.do/docs/intro)

## Architecture
- **Core** is the web server with the API and UI (port 9120).
- **Periphery** is a small stateless agent on each server that runs the Docker commands.
- Core needs a database: MongoDB (recommended in the docs) or FerretDB on PostgreSQL.

## Install Core and Periphery (MongoDB)
Download `compose/mongo.compose.yaml` and `compose/compose.env` from the Komodo repository into `./komodo/`, edit `compose.env`, then:

```bash
docker compose -p komodo -f komodo/mongo.compose.yaml --env-file komodo/compose.env up -d
```

For FerretDB use `compose/ferretdb.compose.yaml` instead. Pin the FerretDB image, as its updates can break. MongoDB does not run on some CPUs, which is the reason to pick FerretDB. Images are `ghcr.io/moghtech/komodo-core` and `ghcr.io/moghtech/komodo-periphery`, tagged `2` by default (`COMPOSE_KOMODO_IMAGE_TAG`).

Change these defaults in `compose.env` before first start:

VARIABLE | DEFAULT | NOTE
---|---|---
`KOMODO_DATABASE_USERNAME` / `KOMODO_DATABASE_PASSWORD` | `admin` / `admin` | Change both
`KOMODO_INIT_ADMIN_USERNAME` / `KOMODO_INIT_ADMIN_PASSWORD` | `admin` / `changeme` | Initial login
`KOMODO_HOST` | | Public URL of Core
`KOMODO_JWT_SECRET`, `KOMODO_WEBHOOK_SECRET` | | Set random values
`KOMODO_LOCAL_AUTH` | `true` | Username and password login
`KOMODO_OIDC_*` | | OIDC login, see [Pocket ID](pocket-id.md)

Secrets accept a `_FILE` suffix. Core and Periphery trust each other through public keys (`KOMODO_PERIPHERY_PUBLIC_KEY`, `PERIPHERY_CORE_PUBLIC_KEYS`) and no passkey variable is documented. In the shipped compose, Periphery connects out to Core (`PERIPHERY_CORE_ADDRESS=ws://core:9120`). Periphery mounts `/var/run/docker.sock`, which is root-equivalent on the host. Its root directory (`/etc/komodo` by default) must be mounted at the same path inside and outside the container.

## Add More Servers (Periphery)
On each extra host run the setup script as root, using the address of Core and an onboarding key created in the UI:

```bash
curl -sSL https://raw.githubusercontent.com/moghtech/komodo/main/scripts/setup-periphery.py | python3 - --core-address CORE_ADDRESS --onboarding-key ONBOARDING_KEY
```

Read the script first. It installs `/usr/local/bin/periphery`, a systemd unit and `/etc/komodo/periphery.config.toml`. Add `--user` for a user-mode install (the user must be in the `docker` group). Re-running updates it, and `--version v2.0.0` pins a version.

## Resources
RESOURCE | USE
---|---
Server | A machine running Periphery
Stack | A Compose project, from the UI, files on the host, or a Git repo with a webhook
Deployment | A single container
Build / Builder | Build images, and the machine that builds
Repo | A cloned Git repo
Procedure / Action | Scheduled or manual sequences, and scripts
Resource Sync | Define resources in TOML files in Git
Alerter | Send alerts for events

## km CLI
Install with the script below or `brew tap moghtech/komodo && brew install km`. The Core image also ships it: `docker exec -it komodo-core km ...`.

```bash
curl -sSL https://raw.githubusercontent.com/moghtech/komodo/main/scripts/install-cli.py | python3
```

COMMAND | DESCRIPTION
---|---
`km --help` | Help
`km deploy stack <STACK>` | Deploy a stack
`km run action <ACTION> -y` | Run an action without a prompt
`km set var <NAME> <VALUE> -y` | Set a variable
`km database backup` / `km database restore -y` | Back up or restore the Core database
`km ssh <SERVER>` / `km exec <CONTAINER> bash` | Shell on a server or in a container
`km config` | Show the merged CLI config

## Backup
New installs get a daily "Backup Core Database" procedure. Mount a host path at `/backups` (`COMPOSE_KOMODO_BACKUPS_PATH`). It writes gzip dumps into dated folders and keeps 14. There is no built-in encryption. `km database restore` does **not** empty the target database first.

## Gotchas
- A v1 to v2 upgrade on FerretDB needs a migration, so read the upgrade notes first.
- Port 8120 for Periphery is not in the shipped compose (unverified for inbound mode).
- A comparison with Portainer is not documented by the project, so judge it yourself.

## See Also
- [Portainer](portainer.md)
- [Dockhand](dockhand.md)
- [Docker Compose](../docker/docker-compose.md)
- [Automate Container Updates](../recipes/automate-container-updates.md)
