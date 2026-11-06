# Docker Cleanup
How to see what Docker is using and remove it safely: containers, images, networks, volumes and build cache, plus log rotation so the disk does not fill again. The order matters. Volumes hold data, so they get their own warnings.

Documentation: [docker system prune](https://docs.docker.com/reference/cli/docker/system/prune/) · [Prune unused objects](https://docs.docker.com/engine/manage-resources/pruning/) · [JSON File logging driver](https://docs.docker.com/engine/logging/drivers/json-file/)

> **Verification:** the `container prune --filter until=`, `builder prune` (`--keep-storage`, `--filter until=`, `-a`) options and the `daemon.json` log options were checked against the Docker docs. The rest is from the CLI reference. No command was executed. Review what a prune would delete before you run it, and never run `--volumes` on a host whose data lives in anonymous volumes you still need.

See also: [[docker]] · [[docker-troubleshooting]] · [[docker-registry]] · [[docker-compose]] · [[storage-and-filesystems]]

---
## See What Takes Space
COMMAND | DESCRIPTION
---|---
`docker system df` | Summary: images, containers, volumes, build cache, with "reclaimable" amounts
`docker system df -v` | Per-image, container and volume sizes
`docker ps -as` | Containers with the size of their writable layer
`docker images --format 'table {{.Repository}}:{{.Tag}}\t{{.Size}}' \| sort -k2 -h` | Images by size
`docker volume ls -f dangling=true` | Volumes no container uses
`docker builder du` | Build cache usage
`sudo du -xh --max-depth=1 /var/lib/docker \| sort -h` | Raw directories (`overlay2`, `volumes`, `containers`)
`sudo du -sh /var/lib/docker/containers/*/*-json.log \| sort -h \| tail` | Biggest container logs

---
## Safe Order
Work from least to most risky. Run the matching `ls` first.

STEP | COMMAND | REMOVES
---|---|---
1 | `docker container prune` | Stopped containers
2 | `docker image prune` | Dangling images (untagged `<none>`)
3 | `docker network prune` | Networks with no containers
4 | `docker builder prune` | Dangling build cache
5 | `docker image prune -a` | Every image not used by a container (re-pull needed later)
6 | `docker volume prune` | **Data.** Volumes not used by any container (see below)

`docker system prune` runs steps 1 to 4 together (containers, networks, dangling images, dangling cache). It asks for confirmation; `-f` skips that.

---
## Prune With Filters
COMMAND | DESCRIPTION
---|---
`docker container prune --filter "until=24h"` | Stopped containers older than a day
`docker image prune -a --filter "until=720h"` | Unused images created more than 30 days ago
`docker image prune -a --filter "label!=keep"` | Skip images labelled `keep`
`docker system prune --filter "until=168h"` | System prune of objects older than a week
`docker builder prune --filter "until=72h"` | Build cache not used for 3 days
`docker builder prune --keep-storage 5GB` | Trim the cache to 5 GB
`docker builder prune -a` | All build cache, including used
`docker buildx prune --filter "until=72h"` | Same for buildx builders
`docker network prune --filter "until=24h"` | Old unused networks

`until` takes a duration (`24h`), a timestamp or a Unix time. Add `-f` to skip the prompt in scripts.

---
## Containers
COMMAND | DESCRIPTION
---|---
`docker ps -a --filter status=exited` | List stopped containers
`docker rm CONTAINER` | Remove one (`-f` for a running one, `-v` also removes its anonymous volumes)
`docker rm $(docker ps -aq --filter status=exited)` | Remove all exited
`docker run --rm ...` | Never leave a throwaway container behind

## Images
COMMAND | DESCRIPTION
---|---
`docker images -f dangling=true` | Untagged leftovers from rebuilds
`docker image prune` | Remove those
`docker rmi IMAGE:TAG` | Remove one
`docker images --filter "reference=REPO/*"` | Everything from one repo
`docker rmi $(docker images -q REPO/NAME \| tail -n +4)` | Keep the 3 newest of one repository (check the list first)
`docker image ls --digests` | Show digests, to spot duplicates

An image used by a stopped container is not removed by `image prune -a` until that container is removed.

## Volumes (Careful)
Volumes hold databases and app data. Deleting them cannot be undone.

COMMAND | DESCRIPTION
---|---
`docker volume ls` | All volumes
`docker volume ls -f dangling=true` | Volumes with no container attached
`docker volume inspect VOLUME` | Mountpoint, labels, driver
`docker ps -a --filter volume=VOLUME` | Which containers use a volume (including stopped)
`docker volume rm VOLUME` | Remove one
`docker volume prune` | Remove **anonymous** unused volumes only (since Docker 23)
`docker volume prune -a` | Remove **all** unused volumes, named ones too
`docker volume prune --filter "label!=keep"` | Keep labelled volumes
`docker system prune --volumes` | System prune plus anonymous unused volumes
`docker compose down -v` | Removes the project's volumes too

Rules of thumb:
- A volume counts as "unused" if no **container** (running or stopped) references it. Stopped containers protect their volumes. If you removed the stack with `compose down`, its volumes become prunable.
- Back up first: `docker run --rm -v VOLUME:/data -v "$PWD":/backup busybox tar czf /backup/VOLUME.tgz -C /data .` (see [[docker]]).
- Name important volumes and label them (`labels: keep: "true"` in Compose) so filters can protect them.

## Build Cache
COMMAND | DESCRIPTION
---|---
`docker builder du` | Show cache entries
`docker builder prune` | Remove dangling cache
`docker builder prune --filter until=24h` | Only older entries
`docker builder prune --keep-storage 10GB` | Keep a 10 GB budget
`docker buildx du` / `docker buildx prune` | Same for the buildx builder you use

In CI, run `docker builder prune --filter until=168h -f` weekly instead of wiping the cache every run.

---
## Log Rotation
The default `json-file` driver keeps logs forever. One chatty container can fill the disk.

Global default, in `/etc/docker/daemon.json` (merge with existing keys, then `sudo systemctl restart docker`). It only applies to **new** containers, so recreate existing ones:
```json
{
  "log-driver": "local",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```
`local` stores compact, compressed logs (defaults 20 MB x 5). `json-file` with the same `log-opts` also works, and keeps `docker logs` plus plain JSON on disk.

Per container or per Compose service:
```bash
docker run -d --log-opt max-size=10m --log-opt max-file=3 IMAGE
```
```yaml
services:
  app:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```
COMMAND | DESCRIPTION
---|---
`docker inspect -f '{{.HostConfig.LogConfig}}' CONTAINER` | Log config in use
`docker inspect -f '{{.LogPath}}' CONTAINER` | Log file path
`sudo truncate -s 0 $(docker inspect -f '{{.LogPath}}' CONTAINER)` | Empty a runaway log now without restarting
`sudo journalctl --vacuum-size=500M` | If you use the `journald` driver, trim the journal ([[systemd]])

Do not `rm` the log file of a running container: the daemon keeps it open and the space stays used. Truncate it instead.

---
## Automate It
A weekly systemd timer ([[systemd]]) running a conservative prune:

`/etc/systemd/system/docker-prune.service`:
```ini
[Unit]
Description=Prune unused Docker objects

[Service]
Type=oneshot
ExecStart=/usr/bin/docker system prune -f --filter "until=168h"
ExecStart=/usr/bin/docker builder prune -f --filter "until=168h"
```
`/etc/systemd/system/docker-prune.timer`:
```ini
[Unit]
Description=Weekly Docker prune

[Timer]
OnCalendar=weekly
Persistent=true

[Install]
WantedBy=timers.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now docker-prune.timer
```
This leaves volumes and in-use images alone. Pair it with image update tools such as Watchtower or Renovate, which leave old image versions behind.

## Moving Docker's Data Directory
If `/var/lib/docker` sits on a small disk, move it:
```bash
sudo systemctl stop docker docker.socket
sudo rsync -aHAX /var/lib/docker/ /mnt/bigdisk/docker/
# in /etc/docker/daemon.json: {"data-root": "/mnt/bigdisk/docker"}
sudo systemctl start docker
docker info | grep 'Docker Root Dir'
```
Keep the old directory until you have checked that containers and volumes work, then delete it.
