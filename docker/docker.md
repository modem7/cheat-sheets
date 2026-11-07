# Docker
**Docker** is a set of platform as a service (PaaS) products that use OS-level virtualization to deliver software in packages called _containers_. The service has both free and premium tiers. The software that hosts the containers is called **Docker Engine**.

Project Homepage: [Home - Docker](https://www.docker.com/)
Documentation: [Docker Documentation | Docker Documentation](https://docs.docker.com/)

---
## Installation

One click installation script:
```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

Run docker as non root user:
```
sudo groupadd docker
sudo usermod -aG docker $USER
```

Install Docker Engine : [Docker Engine](https://docs.docker.com/engine/install/)

---
## Build Images
See [Dockerfile](docker-file.md) for instructions, multi-stage builds and best practices.

COMMAND | DESCRIPTION
---|---
`docker build -t NAME:TAG .` | Build an image from the current directory
`docker buildx build --platform linux/amd64,linux/arm64 -t NAME --push .` | Multi-arch build and push


---
## Docker CLI

**Run Containers**

COMMAND | DESCRIPTION
---|---
`docker run IMAGE` | Start a new container
`docker run --name CONTAINER IMAGE` | Start a new container and set a name
`docker run -p HOSTPORT:CONTAINERPORT IMAGE` | Start a new container with mapped ports
`docker run -P IMAGE` | Start a new container and map all ports

**Container Management:**

COMMAND | DESCRIPTION
---|---
`docker create IMAGE` | Create a new container
`docker start CONTAINER` | Start a container
`docker stop CONTAINER` | Graceful stop a container
`docker kill CONTAINER` | Kill (SIGKILL) a container
`docker restart CONTAINER` | Graceful stop and restart a container
`docker pause CONTAINER` | Suspend a container
`docker unpause CONTAINER` | Resume a container
`docker rm CONTAINER` | Destroy a container

**Container Bulk Management**

COMMAND | DESCRIPTION
---|---
`docker stop $(docker ps -q)` | To stop all the running containers
`docker stop $(docker ps -a -q)` | To stop all the stopped and running containers
`docker kill $(docker ps -q)` | To kill all the running containers
`docker kill $(docker ps -a -q)` | To kill all the stopped and running containers
`docker restart $(docker ps  -q)` | To restart all  running containers
`docker restart $(docker ps -a -q)` | To restart all the stopped and running containers
`docker rm $(docker ps  -q)` | To destroy all running containers
`docker rm $(docker ps -a -q)` | To destroy all the stopped and running containers
`docker pause $(docker ps  -q)` | To pause all  running containers
`docker pause $(docker ps -a -q)` | To pause all the stopped and running containers
`docker start $(docker ps  -q)` | To start all  running containers
`docker start $(docker ps -a -q)` | To start all the stopped and running containers
`docker rm -vf $(docker ps -a -q)` | To delete all containers including its volumes use
`docker rmi -f $(docker images -a -q)` | To delete all the images
`docker system prune` | Delete stopped containers, unused networks, dangling images and dangling build cache (not volumes)
`docker system prune -a` | Also delete all images not used by a container
`docker system prune --volumes` | Also delete anonymous volumes not used by any container (see [Docker Cleanup](docker-cleanup.md))

**Inspect Containers:**

COMMAND | DESCRIPTION
---|---
`docker ps` | List running containers
`docker ps -a` | List all containers, including stopped
`docker logs CONTAINER` | Show a container output
`docker logs -f CONTAINER` | Follow a container output
`docker top CONTAINER` | List the processes running in a container
`docker diff` | Show the differences with the image (modified files)
`docker inspect` | Show information of a container (json formatted)

**Run Commands:**

COMMAND | DESCRIPTION
---|---
`docker attach CONTAINER` | Attach to a container
`docker cp CONTAINER:PATH HOSTPATH` | Copy files from the container
`docker cp HOSTPATH CONTAINER:PATH` | Copy files into the container
`docker export CONTAINER` | Export the content of the container (tar archive)
`docker exec CONTAINER` | Run a command inside a container
`docker exec -it CONTAINER /bin/bash` | Open an interactive shell inside a container (there is no bash in some images, use /bin/sh)
`docker wait CONTAINER` | Wait until the container terminates and return the exit code

**Images:**

COMMAND | DESCRIPTION
---|---
`docker images` | List all local images
`docker history IMAGE` | Show the image history
`docker inspect IMAGE` | Show information (json formatted)
`docker tag IMAGE TAG` | Tag an image
`docker commit CONTAINER IMAGE` | Create an image (from a container)
`docker import URL` | Create an image (from a tarball)
`docker rmi IMAGE` | Delete images
`docker pull REPO:[TAG]` | pull an image/repo from a registry
`docker push REPO:[TAG]` | push and image/repo to a registry
`docker search TEXT` | Search an image on the official registry
`docker login` | Login to a registry
`docker logout` | Logout from a registry
`docker save REPO:[TAG]` | Export an image/repo as a tarball
`docker load` | Load images from a tarball

**Volumes:**

COMMAND | DESCRIPTION
---|---
`docker volume ls` | List all volumes
`docker volume create VOLUME` | Create a volume
`docker volume inspect VOLUME` | Show information (json formatted)
`docker volume rm VOLUME` | Destroy a volume
`docker volume ls --filter="dangling=true"` | List all dangling volumes (not referenced by any container)
`docker volume prune` | Delete all volumes (not referenced by any container)

### Backup a container
Backup docker data from inside container volumes and package it in a tarball archive.
`docker run --rm --volumes-from CONTAINER -v $(pwd):/backup busybox tar cvfz /backup/backup.tar CONTAINERPATH`

An automated backup can be done also by this [Ansible playbook](https://github.com/thedatabaseme/docker_backup).
The output is also a (compressed) tar. The playbook can also manage the backup retention.
So older backups will get deleted automatically.

To also create and backup the container configuration itself, you can use `docker-replay`for that. If you lose
the entire container, you can recreate it with the export from `docker-replay`.
A more detailed tutorial on how to use docker-replay can be found [here](https://thedatabaseme.de/2022/03/18/shorty-generate-docker-run-commands-using-docker-replay/).

### Restore container from backup
Restore the volume with a tarball archive.
`docker run --rm --volumes-from CONTAINER -v $(pwd):/backup busybox sh -c "cd CONTAINERPATH && tar xvf /backup/backup.tar --strip 1"`

## Networks
See [Docker Networking](docker-networking.md) for drivers, port publishing and debugging.

COMMAND | DESCRIPTION
---|---
`docker network ls` | List networks
`docker network create NAME` | Create a user-defined bridge
`docker network connect NETWORK CONTAINER` | Attach a container
`docker network inspect NAME` | Show details

## Useful `docker run` Options
OPTION | DESCRIPTION
---|---
`-d` | Run in the background
`--rm` | Remove the container when it exits
`-it` | Interactive with a terminal
`-e KEY=value` / `--env-file FILE` | Set environment variables
`-v HOSTPATH:CONTAINERPATH[:ro]` | Bind mount (add `:ro` for read-only)
`-v VOLUME:CONTAINERPATH` | Named volume
`--mount type=bind,src=HOSTPATH,dst=CONTAINERPATH` | Explicit mount syntax (errors if the host path is missing)
`--network NAME` | Join a network
`-p 127.0.0.1:8080:80` | Publish on localhost only
`--user 1000:1000` | Run as a UID and GID
`--read-only --tmpfs /tmp` | Read-only root file system with a writable `/tmp`
`--cap-drop ALL --cap-add NET_BIND_SERVICE` | Reduce capabilities
`--security-opt no-new-privileges` | Block privilege escalation
`--init` | Add a tiny init as PID 1 (reaps zombies, forwards signals)
`--add-host name:IP` | Add a hosts entry (`host.docker.internal:host-gateway` reaches the host on Linux)
`--hostname NAME` | Set the hostname
`--entrypoint CMD` | Override the image entrypoint
`--health-cmd ... --health-interval 30s` | Add a health check from the command line
`--pull always` | Pull before run

## Resource Limits
OPTION | DESCRIPTION
---|---
`--memory 512m` | Hard memory limit. The kernel OOM-kills the container above it
`--memory-swap 1g` | Memory plus swap. Equal to `--memory` disables swap
`--memory-reservation 256m` | Soft limit
`--cpus 1.5` | Limit to 1.5 CPUs
`--cpu-shares 512` | Relative weight under contention (default 1024)
`--cpuset-cpus 0,1` | Pin to specific CPUs
`--pids-limit 200` | Cap the number of processes
`--ulimit nofile=65536:65536` | Set an ulimit
`--shm-size 256m` | Size of `/dev/shm` (default 64 MB)
`--device-read-bps /dev/sda:50mb` | Throttle disk reads

Change limits on a running container: `docker update --memory 1g --memory-swap 1g --cpus 2 CONTAINER`. Check use with `docker stats`. See [Docker Troubleshooting](docker-troubleshooting.md) for OOM kills. In Compose use `deploy.resources.limits` or `mem_limit`, see [Docker-Compose](docker-compose.md).

## Restart Policies
POLICY | BEHAVIOUR
---|---
`no` | Never restart (default)
`on-failure[:MAX]` | Restart on non-zero exit, optionally up to MAX times
`always` | Always restart, including after the daemon starts. A manually stopped container restarts when the daemon restarts
`unless-stopped` | Like `always`, but stays stopped if you stopped it

```bash
docker run -d --restart unless-stopped --name web nginx
docker update --restart unless-stopped web          # change an existing one
docker inspect -f '{{.HostConfig.RestartPolicy.Name}} {{.RestartCount}}' web
```
Containers only come back after a reboot if the Docker service is enabled: `sudo systemctl enable docker containerd`. `--restart` and `--rm` cannot be combined.

## Output Formatting and Filters
`--format` takes a Go template. Use `json` to dump a field as JSON and `table` for headings.

COMMAND | DESCRIPTION
---|---
`docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'` | Custom table of running containers
`docker ps -a --format '{{.Names}}: {{.Status}}'` | One line per container
`docker ps --filter status=exited --filter "name=web"` | Filter by state and name
`docker ps --filter health=unhealthy` | Unhealthy containers
`docker images --format '{{.Repository}}:{{.Tag}} {{.Size}}'` | Images and sizes
`docker images --filter dangling=true` | Untagged images
`docker inspect -f '{{.State.Status}}' CONTAINER` | One field
`docker inspect -f '{{.State.ExitCode}} {{.State.OOMKilled}}' CONTAINER` | Exit code and OOM flag
`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}' CONTAINER` | Container IP addresses
`docker inspect -f '{{json .Mounts}}' CONTAINER \| jq` | Mounts as JSON (see [jq](../tools/jq.md))
`docker inspect -f '{{.HostConfig.LogConfig.Type}}' CONTAINER` | Logging driver in use
`docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'` | One snapshot of resource use
`docker network inspect -f '{{range .Containers}}{{.Name}} {{end}}' NAME` | Containers on a network

Persist a default in `~/.docker/config.json`: `{"psFormat": "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"}`.

## System and Disk Usage
COMMAND | DESCRIPTION
---|---
`docker info` | Daemon info: storage driver, cgroup version, root dir, registries
`docker version` | Client and server versions
`docker system df` | Disk use of images, containers, volumes and build cache
`docker system df -v` | Per-item breakdown
`docker system events` | Live event stream (also `docker events`)
`docker stats` | Live CPU, memory, network and block I/O
`du -sh /var/lib/docker/*` | Raw size on disk of the Docker root

Cleaning up is covered in [Docker Cleanup](docker-cleanup.md).

## Logging
`docker logs` works for the `json-file`, `local` and `journald` drivers.

COMMAND | DESCRIPTION
---|---
`docker logs --tail 100 -f CONTAINER` | Last 100 lines and follow
`docker logs --since 10m CONTAINER` | Last 10 minutes
`docker logs -t CONTAINER` | Show timestamps
`docker inspect -f '{{.LogPath}}' CONTAINER` | Where the json-file log lives

Default driver is `json-file` with **no rotation**. Set limits globally in `/etc/docker/daemon.json` (applies to containers created after a daemon restart):
```json
{
  "log-driver": "local",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
```
Or per container: `docker run --log-driver json-file --log-opt max-size=10m --log-opt max-file=3 IMAGE`. The `local` driver compresses and defaults to 20 MB x 5 files. Other drivers: `journald`, `syslog`, `gelf`, `fluentd`, `awslogs`, `none`. In Compose set `logging:` per service, see [Docker-Compose](docker-compose.md).

## Contexts (remote Docker hosts)
COMMAND | DESCRIPTION
---|---
`docker context ls` | List contexts (`*` marks the active one)
`docker context create remote --docker "host=ssh://USER@HOST"` | Add a remote host over SSH
`docker context use remote` | Switch the default
`docker --context remote ps` | One command against another host
`docker context inspect remote` | Show settings
`docker context rm remote` | Remove
`DOCKER_HOST=ssh://USER@HOST docker ps` | Same without a context

SSH access needs key-based login and the user in the `docker` group on the remote host. See [OpenSSH Cheat-Sheet](../tools/openssh.md).

## Buildx and Multi-Platform Builds
COMMAND | DESCRIPTION
---|---
`docker buildx ls` | Builders and platforms
`docker buildx create --name multi --driver docker-container --use` | Create a builder that can do multi-platform and cache export
`docker buildx inspect --bootstrap` | Start the builder and list platforms
`docker buildx build --platform linux/amd64,linux/arm64 -t REPO:TAG --push .` | Multi-arch build and push
`docker buildx build --load -t NAME .` | Build for the local platform into the local image store
`docker buildx build --cache-to type=registry,ref=REPO:buildcache,mode=max --cache-from type=registry,ref=REPO:buildcache .` | Remote build cache (useful in CI)
`docker buildx build --secret id=npmrc,src=$HOME/.npmrc .` | Pass a build secret (use `RUN --mount=type=secret,id=npmrc` in the Dockerfile)
`docker buildx imagetools inspect REPO:TAG` | Show the manifest list and platforms
`docker buildx prune` | Clear the builder cache
`docker run --privileged --rm tonistiigi/binfmt --install all` | Install QEMU emulators to build non-native platforms

`--load` only works for one platform at a time. See [Dockerfile](docker-file.md) for Dockerfile practices.

## Rootless Mode
Run the daemon and containers without root. Limits: no ports below 1024 by default, some network and storage drivers differ.
```bash
sudo apt install -y uidmap dbus-user-session
grep "$USER" /etc/subuid /etc/subgid        # needs at least 65536 IDs each
dockerd-rootless-setuptool.sh install
systemctl --user enable --now docker
sudo loginctl enable-linger "$USER"          # keep it running after logout
export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/docker.sock
```
Allow low ports if needed: `echo 'net.ipv4.ip_unprivileged_port_start=80' | sudo tee /etc/sysctl.d/99-rootless.conf && sudo sysctl --system`. Docs: [Rootless mode](https://docs.docker.com/engine/security/rootless/).

## Docker Init and Scout
COMMAND | DESCRIPTION
---|---
`docker init` | Interactive: generates `Dockerfile`, `compose.yaml`, `.dockerignore` and `README.Docker.md` for a project
`docker scout quickview IMAGE` | Vulnerability summary for an image
`docker scout cves IMAGE` | List CVEs (`--only-severity critical,high`)
`docker scout recommendations IMAGE` | Suggested base image updates
`docker scout compare --to IMAGE:old IMAGE:new` | Diff two images

Scout needs a Docker login and some features need a Docker subscription. Free alternatives: Trivy (`trivy image IMAGE`) and Grype.

## Debugging
`docker debug CONTAINER` opens a shell with extra tools inside a container, even a distroless one (needs Docker Desktop or a recent Docker CLI and a Docker login; check your plan). Other recipes, such as netshoot, `docker events` and exit codes, are in [Docker Troubleshooting](docker-troubleshooting.md).

`docker run --name netshoot --rm -it nicolaka/netshoot /bin/bash`

## See Also
[Docker-Compose](docker-compose.md) · [Dockerfile](docker-file.md) · [Docker Networking](docker-networking.md) · [Docker Troubleshooting](docker-troubleshooting.md) · [Docker Cleanup](docker-cleanup.md) · [Docker Registry](docker-registry.md) · [Podman](podman.md) · [OCI Images](oci-images.md) · [Docker Desktop](../tools/docker-desktop.md) · [UFW (uncomplicated firewall)](../linux/ufw.md)

