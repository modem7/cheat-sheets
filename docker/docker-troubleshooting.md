# Docker Troubleshooting
A checklist for the usual Docker problems: containers that exit or restart, OOM kills, networking and DNS, volume permissions, full disks and failing healthchecks. Work from the quick triage first, then the matching section.

Documentation: [Docker troubleshooting](https://docs.docker.com/engine/daemon/troubleshoot/) · [docker debug](https://docs.docker.com/reference/cli/docker/debug/) · [netshoot](https://github.com/nicolaka/netshoot)

> **Verification:** `docker debug` syntax and the Docker Hub pull-limit headers were checked against the Docker docs. Everything else comes from the CLI reference and common practice. No command was executed. `docker debug` pricing and availability was not confirmed in the official docs; check your plan.

See also: [[docker]] · [[docker-compose]] · [[docker-networking]] · [[docker-cleanup]] · [[docker-registry]] · [[performance-troubleshooting]] · [[systemd]]

---
## Quick Triage
COMMAND | DESCRIPTION
---|---
`docker ps -a` | State of every container (`Exited (137)`, `Restarting`, `unhealthy`)
`docker logs --tail 100 CONTAINER` | Why it stopped
`docker inspect -f '{{.State.ExitCode}} {{.State.OOMKilled}} {{.State.Error}}' CONTAINER` | Exit code, OOM flag, runtime error
`docker events --since 30m` | What the daemon did recently
`docker stats --no-stream` | CPU and memory right now
`docker system df` | Disk use
`docker compose ps` / `docker compose logs --tail 100 SERVICE` | Same for a Compose project
`journalctl -u docker -b --no-pager \| tail -50` | Daemon logs ([[systemd]])
`docker info \| grep -i -e warning -e 'storage driver' -e cgroup` | Daemon warnings

---
## Container Exits Immediately
CAUSE | CHECK
---|---
Main process finished | A container lives as long as PID 1. A shell or `echo` command exits at once
Crash on start | `docker logs CONTAINER`. Config error, missing env var, bad credentials
Wrong command or entrypoint | `docker inspect -f '{{.Config.Entrypoint}} {{.Config.Cmd}}' CONTAINER`
Exec format error | Image built for another CPU (`arm64` vs `amd64`). `docker image inspect -f '{{.Architecture}}' IMAGE`
Binary not found | `no such file or directory` can mean a missing loader (an Alpine/musl vs glibc binary) or a script with Windows CRLF line endings
Permission denied | Executable bit missing or `noexec` mount, or running as a user with no access
Port already in use | `bind: address already in use`. `sudo ss -tulpn \| grep :PORT`

Start it with a shell instead to look around:
```bash
docker run --rm -it --entrypoint sh IMAGE
docker run --rm -it --entrypoint sh --user 0 IMAGE            # as root
docker create --name tmp IMAGE && docker cp tmp:/etc/app.conf . && docker rm tmp
```
Keep a crashing container alive for inspection: `docker run -d --entrypoint sleep IMAGE infinity`, then `docker exec -it ...`.

### Exit Codes
CODE | MEANING
---|---
`0` | Clean exit
`1` | Application error
`125` | `docker run` itself failed (bad flag, daemon error)
`126` | Command found but not executable
`127` | Command not found
`137` | SIGKILL (128+9): OOM killer or `docker kill`/stop timeout
`139` | SIGSEGV (128+11): crash
`143` | SIGTERM (128+15): normal `docker stop`

Restart loop: `docker ps` shows `Restarting (1) ...`. Read the logs, and consider `--restart on-failure:5` while debugging so it stops trying.

---
## OOMKilled
Exit code 137 with `OOMKilled=true` means the container hit its memory limit, or the host ran out of memory.
```bash
docker inspect -f '{{.State.OOMKilled}}' CONTAINER
docker inspect -f '{{.HostConfig.Memory}}' CONTAINER         # 0 = no limit
sudo dmesg -T | grep -i -e 'out of memory' -e 'killed process'
docker stats --no-stream
```
- Raise the limit (`docker update --memory 2g --memory-swap 2g CONTAINER`, or `mem_limit` / `deploy.resources.limits.memory` in Compose) or fix the leak.
- Set runtime heap sizes below the container limit: Java `-XX:MaxRAMPercentage=75`, Node `--max-old-space-size`.
- If `OOMKilled=false` and exit 137, something sent SIGKILL: a stop that exceeded the timeout (`docker stop -t 30`), a host OOM kill, or a manual `kill`.
- `WARNING: No swap limit support` in `docker info` means swap accounting is off. Enable `cgroup_enable=memory swapaccount=1` on the kernel command line on distributions that need it.

---
## Networking and DNS
### Can't reach a published port
COMMAND | DESCRIPTION
---|---
`docker port CONTAINER` | Published ports
`sudo ss -tulpn \| grep :PORT` | Is the host listening (`docker-proxy` or `dockerd`)
`curl -v http://127.0.0.1:PORT` | Test from the host
`docker exec CONTAINER ss -tulpn` | Is the app listening **inside**, and on `0.0.0.0`, not `127.0.0.1`
`docker network inspect NAME` | Is the container on the network you think
`sudo iptables -t nat -L DOCKER -n` | Docker's port-forward rules ([[iptables]])

An app bound to `127.0.0.1` inside the container is unreachable through a published port. Bind to `0.0.0.0`. A port published as `127.0.0.1:8080:80` is only reachable on the host itself. UFW does not block published ports ([[ufw]]).

### Containers can't reach each other
- On the **default** bridge there is no name resolution. Use a user-defined network (`docker network create app`) or Compose ([[docker-networking]]).
- Use the **service/container name** and the **container port**, not the published port.
- Containers must share a network: `docker network inspect NAME -f '{{range .Containers}}{{.Name}} {{end}}'`.
- `localhost` inside a container is the container itself. To reach the host: `--add-host host.docker.internal:host-gateway` and use `host.docker.internal`.

### DNS fails inside a container
```bash
docker run --rm busybox nslookup example.com
docker run --rm --dns 1.1.1.1 busybox nslookup example.com     # works? it's the host resolver
docker exec CONTAINER cat /etc/resolv.conf
```
- Host uses `127.0.0.53` (systemd-resolved): Docker substitutes the real upstream resolvers. If the host's DNS is only reachable locally, set `"dns": ["192.168.1.1"]` in `/etc/docker/daemon.json` and restart Docker.
- VPN, corporate DNS or split DNS: set `dns` and `dns-search` explicitly.
- Bridge subnet clashes with your LAN or VPN (default `172.17.0.0/16`, networks created later use `172.18+`): set `"default-address-pools": [{"base": "10.200.0.0/16", "size": 24}]` in `daemon.json`, or give a network a `--subnet`.
- No internet from containers but the host works: check `net.ipv4.ip_forward=1`, and that no firewall change (firewalld, a flushed iptables, `nft flush ruleset`) removed Docker's rules. Restart Docker to rebuild them ([[nftables]]).
- `docker compose` containers resolve each other through the embedded DNS at `127.0.0.11`.

### Netshoot
A container full of network tools, attached to the network or namespace you want to debug.
```bash
docker run --rm -it nicolaka/netshoot                                       # default bridge
docker run --rm -it --network NETWORK nicolaka/netshoot                     # join an app network
docker run --rm -it --network container:CONTAINER nicolaka/netshoot         # share a container's network namespace
docker run --rm -it --net host nicolaka/netshoot                            # host network
```
Inside: `dig`, `nslookup`, `curl`, `ss`, `ip a`, `tcpdump -ni eth0`, `nmap`, `mtr`, `iperf3`, `traceroute`.

---
## docker debug and Other Ways In
COMMAND | DESCRIPTION
---|---
`docker debug CONTAINER` | Shell with debugging tools in a running container, including slim and distroless images. Your changes stay in the debug layer
`docker debug IMAGE` | Same for an image without running it
`docker exec -it CONTAINER sh` | Plain shell (needs a shell in the image)
`docker run --rm -it --pid container:CONTAINER --network container:CONTAINER nicolaka/netshoot` | Debug sidecar sharing PID and network namespaces
`docker cp CONTAINER:PATH .` | Pull a file out for inspection
`docker diff CONTAINER` | Files changed since start
`docker top CONTAINER` | Processes in the container
`sudo nsenter -t $(docker inspect -f '{{.State.Pid}}' CONTAINER) -n ss -tulpn` | Run a host tool in the container's network namespace

---
## Permission Problems on Volumes
Files in a bind mount keep the **host** UID and GID. A container process running as another UID gets `Permission denied`.

COMMAND | DESCRIPTION
---|---
`docker exec CONTAINER id` | UID and GID the app runs as
`ls -ln /host/path` | Numeric owner on the host
`docker run --user "$(id -u):$(id -g)" ...` | Run as your host user
`sudo chown -R 1000:1000 /host/path` | Give the container's UID ownership
`sudo setfacl -R -m u:1000:rwX /host/path` | ACL for a second user without changing the owner
`docker run -e PUID=1000 -e PGID=1000 ...` | LinuxServer.io images: set the user with these
`docker volume inspect VOLUME -f '{{.Mountpoint}}'` | Named volume location on the host (`/var/lib/docker/volumes/`)

- Named volumes are initialised from the image's directory content and ownership the first time. Bind mounts are not.
- **SELinux** hosts: add `:z` or `:Z` to the mount (`-v /srv/app:/data:Z`), see [[selinux-apparmor]].
- Read-only root (`--read-only`) or `:ro` mounts give `Read-only file system`. Add a `--tmpfs` or a writable volume.
- **NFS/CIFS** bind mounts: root squash and server-side ownership decide. Check export options in [[nfs]].
- **Rootless Docker or user namespaces** (`userns-remap`): container UID 0 maps to a high host UID, so the host path must be owned by the mapped UID (see `/etc/subuid`), not by 0 or 1000.
- Windows/WSL: keep project files inside the Linux file system, not `/mnt/c`.

---
## Disk Full
```bash
df -h /var/lib/docker
docker system df
sudo du -xh --max-depth=1 /var/lib/docker | sort -h
sudo du -sh /var/lib/docker/containers/*/*-json.log | sort -h | tail
```
Typical culprits: unrotated `json-file` logs, build cache, unused images, dangling volumes, a container writing into its own layer (`docker diff`, `docker ps -s`). Fixes, safe prune order and log rotation are in [[docker-cleanup]]. `no space left on device` while `df -h` shows space can be inodes (`df -i`).

---
## Healthcheck Issues
COMMAND | DESCRIPTION
---|---
`docker ps --filter health=unhealthy` | Unhealthy containers
`docker inspect -f '{{json .State.Health}}' CONTAINER \| jq` | Status, failing streak and the last 5 probe outputs ([[jq]])
`docker inspect -f '{{.Config.Healthcheck}}' CONTAINER` | The configured check
`docker exec CONTAINER sh -c 'curl -fsS http://localhost:8080/health; echo $?'` | Run the check by hand

Common causes:
- The command's tool is not in the image (`curl` or `wget` missing in a slim image). Use what is installed, or a small binary of your own.
- Checking `localhost` while the app listens only on another interface, or using the published port instead of the container port.
- `start_period` too short for a slow app: failures during it do not count if you set it (`--health-start-period 60s`).
- A shell form check exits with the wrong code. Exit `0` is healthy, `1` unhealthy.
- In Compose, `depends_on: condition: service_healthy` waits forever on a check that never passes.
```yaml
healthcheck:
  test: ["CMD", "curl", "-fsS", "http://localhost:8080/health"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 60s
```
Healthchecks only mark a container unhealthy. Plain Docker does not restart it; use an orchestrator or an `autoheal` sidecar if you want that.

---
## Daemon Problems
COMMAND | DESCRIPTION
---|---
`sudo systemctl status docker` | Is the daemon running
`journalctl -u docker -b` | Daemon log
`sudo dockerd --debug` | Run in the foreground with debug output (stop the service first)
`docker info` | `Cannot connect to the Docker daemon` means the daemon is down or `DOCKER_HOST` or your group membership is wrong
`ls -l /var/run/docker.sock` | Socket owner and group (`docker`)
`groups` | Are you in the `docker` group (log out and in after adding)
`sudo systemctl restart docker` | Restart. Containers without `--live-restore` stop and then follow their restart policy
`cat /etc/docker/daemon.json \| jq .` | A JSON syntax error here prevents the daemon from starting

Set `"live-restore": true` in `daemon.json` to keep containers running while the daemon restarts.

## Pull Problems
ERROR | LIKELY CAUSE
---|---
`toomanyrequests` | Docker Hub rate limit, log in or use a mirror ([[docker-registry]])
`unauthorized` / `denied` | Wrong or missing login, wrong image name, private repo
`manifest unknown` | Tag does not exist or no manifest for your platform
`no matching manifest for linux/arm64` | Image lacks your architecture. Use `--platform linux/amd64` (emulated)
`x509: certificate signed by unknown authority` | Proxy or private registry CA not trusted. Add it to `/etc/docker/certs.d/HOST/ca.crt`
`net/http: TLS handshake timeout` | Network, DNS or proxy. Test `curl -I https://registry-1.docker.io/v2/`
