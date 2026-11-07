# Arr Stack
The *arr stack automates a media library: Prowlarr manages indexers, Sonarr (TV) and Radarr (films) search and import, and qBittorrent downloads. This sheet uses the linuxserver.io images in one Docker Compose file, with a single shared `/data` tree so imports are hardlinks and instant moves.

Documentation: [Servarr Wiki](https://wiki.servarr.com/) · [Servarr Docker Guide](https://wiki.servarr.com/docker-guide) · [linuxserver.io images](https://docs.linuxserver.io/images/docker-sonarr/) · [TRaSH Guides: Hardlinks](https://trash-guides.info/hardlinks/)
Project: [Sonarr](https://sonarr.tv/) · [Radarr](https://radarr.video/) · [Prowlarr](https://prowlarr.com/) · [qBittorrent](https://www.qbittorrent.org/)

> **Verification:** the image names, ports, `PUID`, `PGID`, `TZ`, `WEBUI_PORT` and `TORRENTING_PORT` variables and the initial qBittorrent password behaviour were checked against docs.linuxserver.io. The `/data` layout, hardlink behaviour, Prowlarr sync levels and settings names were checked against the Servarr Wiki. The `X-Api-Key` header and endpoint paths were confirmed from the apps' OpenAPI files on GitHub. **Not run:** no stack was started, so the combined Compose file, the settings click path and the example `curl` calls are **unverified**. Menu names change between versions, so treat the paths as a guide. This repository has no Plex or Jellyfin sheet, so the media server is not linked.

See also: [Docker](../docker/docker.md) · [Docker-Compose](../docker/docker-compose.md) · [mergerfs](../linux/mergerfs.md) · [Traefik](traefik.md) · [Tailscale](tailscale.md) · [curl](../tools/curl.md) · [jq](../tools/jq.md) · [Automate Container Updates Safely](../recipes/automate-container-updates.md)

---
## Parts and Ports
APP | IMAGE | WEB PORT | JOB
---|---|---|---
Prowlarr | `lscr.io/linuxserver/prowlarr` | 9696 | Indexer manager; syncs indexers into Sonarr and Radarr
Sonarr | `lscr.io/linuxserver/sonarr` | 8989 | TV series: search, grab, import, rename
Radarr | `lscr.io/linuxserver/radarr` | 7878 | Films: search, grab, import, rename
qBittorrent | `lscr.io/linuxserver/qbittorrent` | 8080 | Download client; peer port 6881 TCP and UDP

## Folder Layout
Give every container that touches files the same `/data` mount. Two separate mounts such as `/tv` and `/downloads` look like different file systems, so hardlinks fail and an import becomes a slow copy and delete.

```text
/srv/data                    (host)  ->  /data  (every container)
├── torrents
│   ├── movies
│   └── tv
└── media
    ├── movies
    └── tv
```

CONTAINER | MOUNT
---|---
Sonarr, Radarr | `/srv/data:/data` (whole tree)
qBittorrent | `/srv/data/torrents:/data/torrents`
Media server | `/srv/data/media:/data/media`
Prowlarr | Config only, no media

```bash
sudo mkdir -p /srv/data/torrents/{movies,tv} /srv/data/media/{movies,tv}
sudo chown -R 1000:1000 /srv/data
sudo chmod -R 775 /srv/data
```

`1000:1000` matches `PUID` and `PGID` below. The `/srv/data` tree must be one file system on the host (one disk, one mount, or a [mergerfs](../linux/mergerfs.md) pool). The Servarr Docker Guide suggests a per-app user with a shared group and `UMASK=002`.

## Docker Compose
`compose.yaml` in `/opt/stacks/arr`, with the config of each app kept under `/opt/stacks/arr/config`:

```yaml
services:
  prowlarr:
    image: lscr.io/linuxserver/prowlarr:latest
    container_name: prowlarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/London
    volumes:
      - ./config/prowlarr:/config
    ports:
      - 9696:9696
    restart: unless-stopped

  sonarr:
    image: lscr.io/linuxserver/sonarr:latest
    container_name: sonarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/London
    volumes:
      - ./config/sonarr:/config
      - /srv/data:/data
    ports:
      - 8989:8989
    restart: unless-stopped

  radarr:
    image: lscr.io/linuxserver/radarr:latest
    container_name: radarr
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/London
    volumes:
      - ./config/radarr:/config
      - /srv/data:/data
    ports:
      - 7878:7878
    restart: unless-stopped

  qbittorrent:
    image: lscr.io/linuxserver/qbittorrent:latest
    container_name: qbittorrent
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/London
      - WEBUI_PORT=8080
      - TORRENTING_PORT=6881
    volumes:
      - ./config/qbittorrent:/config
      - /srv/data/torrents:/data/torrents
    ports:
      - 8080:8080
      - 6881:6881
      - 6881:6881/udp
    restart: unless-stopped
```

Each service block follows its linuxserver.io page, with the optional `/tv`, `/movies` and `/downloads` mounts replaced by the shared `/data`. Services on the default Compose network reach each other by service name (`http://sonarr:8989`). Pin image tags and bind ports to `127.0.0.1` or put a reverse proxy in front ([Traefik](traefik.md)). Never expose these UIs directly to the internet.

VARIABLE | MEANING
---|---
`PUID` / `PGID` | User and group ID the app runs as; find yours with `id`
`TZ` | Time zone, for example `Europe/London`
`WEBUI_PORT` | qBittorrent web UI port; change both sides of the port mapping and the variable together
`TORRENTING_PORT` | qBittorrent peer port, map it as TCP and UDP
`UMASK` | Many images accept it (for example `002`); not in the linuxserver examples above, so check each image page

```bash
docker compose up -d
docker compose logs -f qbittorrent
docker compose pull && docker compose up -d
```

## First-Run Setup
STEP | WHERE | SETTING
---|---|---
1 | qBittorrent | Log in as `admin` with the temporary password printed in `docker compose logs qbittorrent`, then set your own under Tools, Options, Web UI. If you do not, a new password is generated at each start
2 | qBittorrent | Default save path `/data/torrents`; one category per app (for example `tv` and `movies`), saved under `/data/torrents/<CATEGORY>`
3 | Sonarr, Radarr | Settings, General: set authentication and note the API key
4 | Sonarr | Settings, Media Management, Add Root Folder `/data/media/tv`
5 | Radarr | Settings, Media Management, Add Root Folder `/data/media/movies`
6 | Sonarr, Radarr | Settings, Media Management, Importing: keep "Use Hard links instead of Copy" on
7 | Sonarr, Radarr | Settings, Download Clients, add qBittorrent: host `qbittorrent`, port `8080`, your credentials, and a category
8 | Prowlarr | Settings, Apps (the wiki section is called Applications): add Sonarr and Radarr with Prowlarr server `http://prowlarr:9696`, app server `http://sonarr:8989` or `http://radarr:7878`, and the app's API key
9 | Prowlarr | Add indexers; they sync to the apps. Sync level "Add and Remove Only" or "Full Sync" (full overwrites changes made in the app)
10 | Sonarr, Radarr | Add a series or film and check Activity, then confirm the imported file is a hardlink (below)

Notes from the Servarr Wiki:
- Set a category in the download client; without one, unrelated downloads show in Activity.
- Hardlinks and atomic moves need the download folder and library on the same file system and mount.
- Torrents keep seeding from `/data/torrents`, so removing them there is not safe until the import is done.
- With a reverse proxy, include the URL base in the Prowlarr app server URL or synced indexers break.
- A remote path mapping is rarely needed when everything is a container sharing `/data`.

Check hardlinks: matching inode numbers and a link count of 2 or more mean the file is not duplicated.

```bash
ls -li /srv/data/torrents/tv/FILE.mkv /srv/data/media/tv/SHOW/Season\ 01/FILE.mkv
stat -c '%h %i %n' /srv/data/torrents/tv/FILE.mkv
```

## API Key Usage
Each app has an API key under Settings, General (Prowlarr: Settings, General, Security). Send it in the `X-Api-Key` header; an `apikey` query parameter is also accepted but ends up in logs and history. Sonarr and Radarr use API v3, Prowlarr uses v1.

COMMAND | DESCRIPTION
---|---
`curl -H "X-Api-Key: $SONARR_KEY" http://localhost:8989/api/v3/system/status` | Version and status of Sonarr
`curl -H "X-Api-Key: $SONARR_KEY" http://localhost:8989/api/v3/series \| jq '.[].title'` | List series titles
`curl -H "X-Api-Key: $SONARR_KEY" http://localhost:8989/api/v3/queue` | Download queue
`curl -H "X-Api-Key: $RADARR_KEY" http://localhost:7878/api/v3/movie \| jq '.[].title'` | List films
`curl -H "X-Api-Key: $RADARR_KEY" http://localhost:7878/api/v3/queue` | Download queue
`curl -H "X-Api-Key: $PROWLARR_KEY" http://localhost:9696/api/v1/system/status` | Prowlarr status
`curl -H "X-Api-Key: $PROWLARR_KEY" http://localhost:9696/api/v1/indexer` | Configured indexers
`curl -H "X-Api-Key: $PROWLARR_KEY" "http://localhost:9696/api/v1/search?query=TERM&type=search"` | Search all indexers
`curl http://localhost:8989/ping` | Liveness endpoint `/ping` (listed in Sonarr's OpenAPI file; unverified whether it needs a key)

`POST /api/v3/command` runs actions such as a search or refresh; the command names and bodies are not listed here (unverified, see each app's API docs). Keep keys in an environment variable or file, never in a script in git. Regenerate a key if it leaks, then update the apps that use it.

## Backups and Updates
- Back up each `./config/*` folder with the containers stopped, or use each app's built-in backup (menu location unverified). The media tree needs its own backup ([borgmatic](../backup/borgmatic.md)).
- To reset a forgotten login, stop the app, delete the `AuthenticationMethod` line in `config.xml` in its config folder, and start it again to set a new one.
- Update with `docker compose pull && docker compose up -d`, or automate it ([Automate Container Updates Safely](../recipes/automate-container-updates.md)).

## Troubleshooting
SYMPTOM | FIX
---|---
Import copies instead of hardlinking | Different mounts or file systems; use one `/data` mount in Sonarr, Radarr and the client, and keep "Use Hardlinks" on
Import is slow | It is copy and delete, same cause
"No files found" or path error after download | The client reports a path the app cannot see; use identical `/data/torrents` paths in client and apps (or a remote path mapping)
Permission denied on import | `PUID` and `PGID` differ between containers, or `/data` is not group-writable; fix ownership and use a shared group
Prowlarr test fails for an app | Wrong URL or API key; use service names and the app's own port, include the URL base behind a proxy
Indexers vanish or change in an app | Prowlarr is set to Full Sync and overrides local edits
qBittorrent login rejected | Use the temporary password from the logs, or set a permanent one
Downloads do not start from outside | Forward or allow the peer port (`TORRENTING_PORT`) on TCP and UDP
Clock errors or wrong air dates | Set `TZ` on every container

## See Also
- [Docker](../docker/docker.md)
- [Docker-Compose](../docker/docker-compose.md)
- [mergerfs](../linux/mergerfs.md)
- [Traefik](traefik.md)
- [Tailscale](tailscale.md)
- [curl](../tools/curl.md)
- [jq](../tools/jq.md)
- [Automate Container Updates Safely](../recipes/automate-container-updates.md)
