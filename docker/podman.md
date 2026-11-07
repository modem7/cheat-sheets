# Podman
Podman is a daemonless, rootless-capable container engine with a Docker-compatible CLI. Use it where you want containers without a root daemon, managed as systemd services through Quadlet. Podman 6 is the current major version.

Documentation: [Podman docs](https://docs.podman.io/) · [Quadlet (podman-systemd.unit)](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html)
Project: [containers/podman](https://github.com/containers/podman)

> **Verification:** commands were checked against the Podman man pages in the upstream repository and docs.podman.io (November 2026, Podman 6.1). Nothing was run. Items marked *(unverified)* were not confirmed. For Docker equivalents see [Docker](docker.md).

## Everyday Commands
Most Docker commands work unchanged. Podman also takes `docker`-style flags.

COMMAND | DESCRIPTION
---|---
`podman run -d --name <NAME> -p 8080:80 <IMAGE>` | Run a container
`podman ps -a` | List containers
`podman images` | List images
`podman exec -it <NAME> sh` | Shell into a container
`podman logs -f <NAME>` | Follow logs
`podman rm <NAME>` / `podman rmi <IMAGE>` | Remove a container or image
`podman build -f <FILE> -t <TAG> .` | Build an image (see [Dockerfile](docker-file.md))
`podman login <REGISTRY>` / `podman push <IMAGE>` / `podman pull <IMAGE>` | Registry operations (see [Docker Registry](docker-registry.md))
`podman info` | Show host and runtime details
`podman system df` | Show disk use
`podman system prune` | Remove unused data (destructive)
`podman system reset` | Remove all pods, containers, images, networks, volumes and machines (destructive)
`podman volume create <NAME>` / `podman volume prune` | Create volumes, remove unused ones (destructive)
`podman secret create <NAME> <FILE>` | Store a secret (`-` reads stdin)

The `podman-docker` package and `alias docker=podman` are *not verified* against the docs; release notes say `DOCKER_HOST` is set by default for rootless users when `podman-docker` is installed.

## Registries and Short Names
Podman reads `registries.conf` in order: `$XDG_CONFIG_HOME/containers/registries.conf` (or `~/.config/containers/registries.conf`), then `/etc/containers/registries.conf`, then `/usr/share/containers/registries.conf`. Files in `registries.conf.d` override.

KEY | PURPOSE
---|---
`unqualified-search-registries` | Registries tried for names without a registry, such as `nginx`
`short-name-mode` | `enforcing`, `permissive` or `disabled`

```toml
unqualified-search-registries = ["docker.io"]
```

Prefer fully qualified names such as `docker.io/library/nginx:1.27` to avoid prompts and spoofing.

## Rootless
Rootless containers run as your user with user namespaces.

COMMAND / SETTING | DESCRIPTION
---|---
`/etc/subuid` and `/etc/subgid` | Must list a range for your user
`podman system migrate` | Apply changed `subuid` or `subgid` ranges to existing containers
`podman unshare <COMMAND>` | Run a command inside the user namespace (fix volume ownership)
`--userns=keep-id` | Map your UID into the container
`-v <HOST_PATH>:<PATH>:Z` / `:z` | Relabel a bind mount for SELinux (`Z` private, `z` shared); see [SELinux and AppArmor](../linux/selinux-apparmor.md)
`sysctl net.ipv4.ip_unprivileged_port_start=443` | Let rootless containers bind ports below 1024 (example from the docs)
`loginctl enable-linger $USER` | Keep your user services running after logout

## Networking
Netavark is the network backend and aardvark-dns provides container name resolution. Podman 6 removed `slirp4netns`; rootless networking uses **pasta** (the default since 5.0). Rootless bridge port forwarding still defaults to `rootlessport`; forwarding with pasta is experimental via `rootless_port_forwarder="pasta"` in `containers.conf`.

COMMAND | DESCRIPTION
---|---
`podman network create <NAME>` | Create a network
`podman network ls` | List networks

## Pods and Kubernetes YAML
COMMAND | DESCRIPTION
---|---
`podman pod create --name <POD>` | Create a pod *(synopsis unverified)*
`podman run --pod <POD> <IMAGE>` | Run a container in a pod *(unverified)*
`podman pod ps` / `podman pod rm <POD>` | List or remove pods *(unverified)*
`podman kube generate <NAME>` | Generate Kubernetes YAML from a container or pod (`generate kube` is an alias)
`podman kube play <FILE>.yml` | Run Kubernetes YAML (`play kube` is an alias)

## Quadlet (systemd Services)
Quadlet turns unit files into systemd services. `podman generate systemd` is deprecated in favour of Quadlet.

Rootless unit files go in `~/.config/containers/systemd/` (also `$XDG_RUNTIME_DIR/containers/systemd/` and `/etc/containers/systemd/users/`). `~/.config/containers/systemd/web.container`:

```ini
[Unit]
Description=Web server

[Container]
Image=docker.io/library/nginx:1.27
PublishPort=8080:80
Volume=web-data.volume:/usr/share/nginx/html

[Service]
Restart=always

[Install]
WantedBy=default.target
```

COMMAND | DESCRIPTION
---|---
`systemctl --user daemon-reload` | Regenerate services from Quadlet files
`systemctl --user start web.service` | Start (the service name is the file name with `.service`)
`systemctl --user status web.service` | Check status
`/usr/lib/systemd/system-generators/podman-system-generator --user --dryrun` | Dry run the generator (path from the docs; it may differ by distribution)

Keep `[Install]` sections to `WantedBy=default.target` for user services. See [systemd](../linux/systemd.md) for unit basics.

## Auto-Update
Label a container `io.containers.autoupdate=registry` (or `AutoUpdate=registry` in a Quadlet `[Container]` section, *unverified*), then:

COMMAND | DESCRIPTION
---|---
`podman auto-update` | Pull newer images and restart labelled units
`systemctl --user enable --now podman-auto-update.timer` | Run it on a schedule (timer name documented; the combined `enable --now` form is standard systemd)

## Docker Compose and the Socket
COMMAND | DESCRIPTION
---|---
`podman compose up -d` | Wrapper that calls `docker-compose` or `podman-compose` (`PODMAN_COMPOSE_PROVIDER` picks one); see [Docker-Compose](docker-compose.md)
`systemctl --user start podman.socket` | Start the Docker-compatible API socket
`systemctl --user enable podman.socket` | Enable it at login
`export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/podman/podman.sock` | Point Docker tools at Podman

## Podman Machine
COMMAND | DESCRIPTION
---|---
`podman machine init [NAME]` | Create a Linux VM (required on macOS and Windows, optional on Linux)
`podman machine start` | Start it *(synopsis unverified)*
`podman machine ssh [NAME] [COMMAND]` | SSH into the VM

## Troubleshooting
SYMPTOM | FIX
---|---
Cannot bind port below 1024 | Raise `net.ipv4.ip_unprivileged_port_start` or publish a higher port
Permission denied on a bind mount | Add `:Z`, or use `podman unshare chown` or `--userns=keep-id`
Rootless containers stop at logout | `loginctl enable-linger $USER`
Image name prompts for a registry | Use a fully qualified image name or set `unqualified-search-registries`
`newuidmap` errors | Check `/etc/subuid` and `/etc/subgid`, then `podman system migrate`

## See Also
- [Docker](docker.md)
- [Docker-Compose](docker-compose.md)
- [Docker Registry](docker-registry.md)
- [OCI Images](oci-images.md)
- [SELinux and AppArmor](../linux/selinux-apparmor.md)
- [Container Scanning](../security/container-scanning.md)
