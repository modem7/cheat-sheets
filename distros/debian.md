# Debian
Debian is a glibc and apt based distribution and the base under many language images such as `python` and `node`. The `-slim` variants drop docs and extras.

Documentation: [Debian Reference](https://www.debian.org/doc/manuals/debian-reference/)
Project: [Debian](https://www.debian.org/) · [Docker Hub](https://hub.docker.com/_/debian)

See also [Container Distros](distros.md), [Ubuntu](ubuntu.md) and [Dockerfile](../docker/docker-file.md).

## apt in Dockerfiles
COMMAND | DESCRIPTION
---|---
`apt-get update` | Refresh indexes; always in the same `RUN` as the install
`apt-get install -y --no-install-recommends PACKAGE` | Install without recommended extras
`rm -rf /var/lib/apt/lists/*` | Remove the indexes at the end of the layer
`apt-get purge -y --auto-remove PACKAGE` | Remove a package and its unused dependencies
`apt-cache policy PACKAGE` | Installed and candidate versions
`dpkg -L PACKAGE` | List a package's files
`dpkg -S /PATH/TO/FILE` | Which package owns a file
`cat /etc/debian_version` | Exact point release (`12.15` in the image checked)

```dockerfile
FROM debian:12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*
```

## Image Tags
TAG | MEANING
---|---
`debian:12` | Major release by number (preferred)
`debian:bookworm` | The same release by codename
`debian:12-slim` / `debian:bookworm-slim` | Smaller variant
`debian:stable` / `debian:stable-slim` | Follows the current stable release, so the major version changes over time
`debian:testing` / `debian:sid` | Moving development releases; not for production
`debian:bookworm-YYYYMMDD` | Dated tag for reproducibility (check the tag list on Docker Hub; unverified)

## Users
COMMAND | DESCRIPTION
---|---
`useradd -r -u 10001 APP` | Create a system user; a UID above 999 prints a `SYS_UID_MAX` warning but works
`useradd -u 10001 -m APP` | Create a regular user with a home directory
`groupadd -r GROUP` | Create a system group

## CA Certificates and Timezone
COMMAND | DESCRIPTION
---|---
`apt-get install -y --no-install-recommends ca-certificates` | Needed for HTTPS; not in the base image
`update-ca-certificates` | Rebuild after adding `.crt` files to `/usr/local/share/ca-certificates/`
`ln -fs /usr/share/zoneinfo/Europe/London /etc/localtime` | Set the timezone (`/usr/share/zoneinfo` is present in `debian:12`)
`-e TZ=Europe/London` | Alternative at `docker run` (unverified)

## Gotchas
SYMPTOM | FIX
---|---
`E: Unable to locate package` | Run `apt-get update` in the same `RUN`
`curl: (60) SSL certificate problem` | Install `ca-certificates`
Missing `ps`, `ping` | Install `procps`, `iputils-ping`
`stable` tag jumped to a new release | Pin the number or codename
Sources are in `/etc/apt/sources.list.d/debian.sources` | 12 uses the deb822 format, not `sources.list`
