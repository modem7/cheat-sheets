# Docker on macOS Silicon
Docker on Apple Silicon (M-series, `arm64`) runs Linux containers in a lightweight VM. See [[docker]].

## Installation
Docker Desktop: `brew install --cask docker`

Lighter alternatives: [OrbStack](https://orbstack.dev), [Colima](https://github.com/abiosoft/colima) (`brew install colima docker && colima start`), Rancher Desktop.

## Platform
Most images have `arm64` variants. For amd64-only images, emulation (slower) can be selected explicitly:
```
docker run --platform linux/arm/v7

docker run --platform linux/amd64
```
COMMAND | DESCRIPTION
---|---
`docker run --platform linux/amd64 <IMAGE>` | Run an Intel image under emulation
`docker build --platform linux/amd64 -t <NAME> .` | Build an Intel image
`docker buildx build --platform linux/amd64,linux/arm64 -t <NAME> --push .` | Multi-arch image
`docker image inspect <IMAGE> --format '{{.Architecture}}'` | Architecture of an image
`docker manifest inspect <IMAGE>` | Platforms an image supports
`export DOCKER_DEFAULT_PLATFORM=linux/amd64` | Make amd64 the default for the shell

In Compose, set `platform: linux/amd64` on a service ([[docker-compose]]).

## Shared volumes
Shared volumes can be configured in the Docker Desktop Settings `Docker -> Preferences... -> Resources -> File Sharing`

## Performance Tips
- Use VirtioFS file sharing (Settings > General) and "Use Rosetta for x86_64/amd64 emulation" (Settings > General).
- Bind mounts are slower than named volumes. Keep `node_modules` and databases in volumes.
- Give the VM enough memory and CPUs under Settings > Resources, but not all of your Mac.
- `docker system df` and `docker system prune` reclaim the disk image space.

## Troubleshooting
- `exec format error`: image architecture does not match, use `--platform`.
- Slow amd64 containers: look for an `arm64` tag or build natively.
- Ports unreachable from the LAN: publish with `-p 0.0.0.0:<PORT>:<PORT>`. Check the macOS firewall.
