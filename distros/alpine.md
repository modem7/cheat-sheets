# Alpine Linux
Alpine is a small musl libc and BusyBox based distribution; the `alpine` image is about 13 MB. Use it for small images where the software is known to work on musl.

Documentation: [Alpine Linux Wiki](https://wiki.alpinelinux.org/)
Project: [Alpine Linux](https://alpinelinux.org/) · [Docker Hub](https://hub.docker.com/_/alpine)

See also [Container Distros](distros.md) and [Dockerfile](../docker/docker-file.md).

## apk Package Manager
COMMAND | DESCRIPTION
---|---
`apk add --no-cache PACKAGE` | Install without keeping an index cache (use this in Dockerfiles)
`apk add --no-cache --virtual .build-deps build-base` | Install build tools as a named group
`apk del .build-deps` | Remove that group after building
`apk update` | Refresh the package index (not needed with `--no-cache`)
`apk upgrade --no-cache` | Upgrade installed packages
`apk search -q PATTERN` | Search packages by name
`apk info -W /PATH/TO/FILE` | Which package owns a file
`apk info -v` | List installed packages with versions
`apk list -I` | List installed packages
`apk add --no-cache PACKAGE=VERSION` | Pin a version (must exist in the repository)

## Image Tags
TAG | MEANING
---|---
`alpine:3.22` | A specific release (preferred for reproducible builds)
`alpine:3` | Latest 3.x release
`alpine:latest` | Newest stable release; avoid in builds
`alpine:edge` | Rolling development branch

Pin the release: old package versions are removed from the repositories, so an unpinned `apk add` can break later.

## Users and Groups
COMMAND | DESCRIPTION
---|---
`adduser -D -u 10001 APP` | Create user `APP` with no password and a fixed UID (also creates a same-named group)
`addgroup -S GROUP && adduser -S -G GROUP USER` | Create a system group and a system user in it
`USER APP` | Dockerfile instruction to drop root

```dockerfile
FROM alpine:3.22
RUN adduser -D -u 10001 app
USER app
```

## CA Certificates and Timezone
COMMAND | DESCRIPTION
---|---
`apk add --no-cache ca-certificates` | CA bundle at `/etc/ssl/certs/ca-certificates.crt`
`update-ca-certificates` | Rebuild the bundle after adding `.crt` files to `/usr/local/share/ca-certificates/`
`apk add --no-cache tzdata` | Install zone data (not in the base image)
`ln -sf /usr/share/zoneinfo/Europe/London /etc/localtime` | Set the timezone (after installing `tzdata`)
`-e TZ=Europe/London` | Alternative at `docker run` (needs `tzdata`; unverified)

## Gotchas
SYMPTOM | CAUSE AND FIX
---|---
`bash: not found` | No bash by default. Use `sh`, or `apk add --no-cache bash`
`./binary: not found` though the file exists | Usually a glibc binary missing its loader. Alpine uses musl: use a musl build, compile on Alpine, or switch to Debian or Ubuntu
`ldd --version` prints `musl libc` | Confirms musl
`/bin/sh` is BusyBox `ash` | No bashisms (`[[ ]]`, arrays); lint with `shellcheck -s sh`
`apk` warns `opening from cache ... No such file` | Harmless when using `--no-cache` without an earlier `apk update` (seen on 3.22)
Python or Node packages compile from source | Prebuilt `manylinux` wheels target glibc, so musl may need build tools (`--virtual .build-deps`) (unverified per package)
DNS behaves differently from glibc | musl has its own resolver; check the musl docs if lookups differ (unverified in detail)
