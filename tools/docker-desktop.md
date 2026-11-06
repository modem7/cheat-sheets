# Docker Desktop
Docker Desktop is Docker's desktop app for Windows, macOS and Linux. It bundles the Docker Engine, the `docker` CLI, Docker Compose, a built-in Kubernetes cluster and a GUI inside a lightweight VM. For the engine and commands see [Docker](../docker/docker.md) and [Docker-Compose](../docker/docker-compose.md); on Linux servers you normally install Docker Engine directly instead.

Documentation: [Docker Desktop Docs](https://docs.docker.com/desktop/)

> Licence: Docker Desktop is free for personal use, education, open source and small businesses, but larger organisations need a paid subscription. Check the current terms on the Docker site.

---
## Install
PLATFORM | COMMAND
---|---
Windows | `winget install Docker.DockerDesktop` or `choco install docker-desktop` ([Chocolatey](../windows/chocolatey.md))
macOS | `brew install --cask docker` ([Homebrew](../macos/homebrew.md))
Linux | the `.deb` or `.rpm` package from the Docker docs

Windows uses the WSL 2 backend by default (see [WSL Cheat-Sheet](wsl.md)). On Apple Silicon see [Docker on macOS Silicon](../macos/docker-on-macos-silicon.md) for architecture notes.

## Windows: WSL 2 Integration
Settings > Resources > WSL integration enables Docker inside chosen distros. In the distro, `docker version` should then show both client and server. If `docker` is not found, restart the distro (`wsl --shutdown` from PowerShell) and check that integration is on for that distro.

## Built-in Kubernetes
Settings > Kubernetes > Enable Kubernetes creates a single-node cluster and a `docker-desktop` context for [Kubectl](../kubernetes/kubectl.md):
```bash
kubectl config use-context docker-desktop
kubectl get nodes
```
For multi-node local clusters see [Kind](../kubernetes/kind.md), and for a lightweight real distribution see [K3S](../kubernetes/k3s.md).

## Resources and Cleanup
- Settings > Resources sets CPUs, memory, swap and the disk image size. Raise memory if builds or databases get OOM-killed.
- Disk grows with images and volumes. Clean up with:

COMMAND | DESCRIPTION
---|---
`docker system df` | Show disk use
`docker system prune` | Remove stopped containers, unused networks and dangling images
`docker system prune -a --volumes` | Aggressive: also unused images and volumes (check first, volumes hold data)
`docker builder prune` | Clear the build cache

## Useful Features
- **Dev Environments, Extensions and Docker Scout** (image vulnerability scanning) are available in the GUI.
- `docker context ls` shows `desktop-linux` (or `default`) and any remote contexts.
- `docker compose` (plugin, with a space) is the current command; `docker-compose` (hyphen) is the old standalone tool.
- Host networking and `host.docker.internal` differ from native Linux. Use `host.docker.internal` to reach services on the host from a container.

## Troubleshooting
- **Engine will not start**: restart Docker Desktop, check virtualisation is enabled in BIOS and, on Windows, that WSL 2 is installed and updated (`wsl --update`).
- **Slow bind mounts on macOS or WSL**: keep project files inside the Linux filesystem (WSL) or use named volumes.
- **Port already in use**: `docker ps` to find the owner, or change the host port in `-p HOST:CONTAINER`.

## Not Verified
Written from knowledge and not run here. Menu names and licence terms change between releases.
