# Container Distros
Overview of the Linux distributions most often used as Docker base images, with the container-specific commands and gotchas for each. Pair with [Dockerfile](../docker/docker-file.md) and [Docker](../docker/docker.md).

SHEET | DESCRIPTION
---|---
[Alpine Linux](alpine.md) | `apk`, musl vs glibc, tiny images, BusyBox `sh`, `adduser`
[Ubuntu](ubuntu.md) | `apt-get` in Dockerfiles, `tzdata`, LTS tags, the `ubuntu` user
[Debian](debian.md) | `apt-get`, `-slim` tags, `ca-certificates`, codename tags
[Amazon Linux](amazon-linux.md) | AL2023 `dnf`, `curl-minimal`, `shadow-utils`, no microdnf
[Fedora](fedora.md) | `dnf5`, short-lived releases, `update-ca-trust`, `useradd`

## How These Were Chosen
Ranked by Docker Hub pull count of the official images (checked on 2026-11-07, rounded). BusyBox (a tool set, not a full distribution) and CentOS (end of life) were skipped.

IMAGE | PULLS
---|---
`busybox` | 13.0 billion (skipped)
`alpine` | 12.5 billion
`ubuntu` | 10.2 billion
`debian` | 1.8 billion
`centos` | 1.2 billion (skipped, end of life)
`amazonlinux` | 0.99 billion
`fedora` | 0.14 billion
`rockylinux` | 0.047 billion
`almalinux` | 0.019 billion

## Choosing a Base
SITUATION | USE
---|---
Smallest image, software known to work on musl | Alpine
Broad glibc compatibility, large package archive | Debian `-slim` or Ubuntu
Prebuilt binaries built for glibc | Debian or Ubuntu, not Alpine
Matching an AWS host OS | Amazon Linux 2023
Newest toolchains, RPM ecosystem | Fedora (short support window)
Long-lived RHEL-compatible base | Rocky Linux or AlmaLinux (not covered here)

## Common Checks
COMMAND | DESCRIPTION
---|---
`docker run --rm IMAGE cat /etc/os-release` | Show the distribution and version
`docker run --rm IMAGE id` | Show the default user (root in all five)
`docker image ls IMAGE` | Compare image sizes
`docker run --rm -it IMAGE sh` | Interactive shell for trying commands (Alpine has no `bash`)

See [Container Scanning](../security/container-scanning.md) for checking image CVEs.
