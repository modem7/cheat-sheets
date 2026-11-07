# Ubuntu
Ubuntu is a glibc and apt based distribution. The `ubuntu` image is a minimal root filesystem with fewer packages than a normal install.

Documentation: [Ubuntu Server docs](https://documentation.ubuntu.com/server/)
Project: [Ubuntu](https://ubuntu.com/) · [Docker Hub](https://hub.docker.com/_/ubuntu)

See also [Container Distros](distros.md), [Debian](debian.md) and [Dockerfile](../docker/docker-file.md).

## apt in Dockerfiles
COMMAND | DESCRIPTION
---|---
`apt-get update` | Refresh indexes; always in the same `RUN` as the install
`apt-get install -y --no-install-recommends PACKAGE` | Install without recommended extras
`rm -rf /var/lib/apt/lists/*` | Remove the indexes at the end of the layer
`apt-get purge -y --auto-remove PACKAGE` | Remove a package and its unused dependencies
`apt-cache policy PACKAGE` | Installed and candidate versions
`apt-get install -y PACKAGE=VERSION` | Pin a version
`dpkg -L PACKAGE` | List a package's files
`dpkg -S /PATH/TO/FILE` | Which package owns a file

```dockerfile
FROM ubuntu:24.04
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      ca-certificates curl tzdata \
 && rm -rf /var/lib/apt/lists/*
```

Use `apt-get` rather than `apt` in scripts: `apt` is meant for interactive use. Setting `DEBIAN_FRONTEND` on the `RUN` line keeps it out of the final image environment.

## Image Tags
TAG | MEANING
---|---
`ubuntu:24.04` | LTS release by number (preferred)
`ubuntu:noble` | The same release by codename
`ubuntu:latest` | Latest LTS; avoid in builds
`ubuntu:rolling` | Latest release including non-LTS (unverified)

## Users
COMMAND | DESCRIPTION
---|---
`useradd -r -u 10001 -m APP` | Create a system user with a fixed UID and a home directory
`groupadd -r GROUP` | Create a system group
`id ubuntu` | The 24.04 image already contains an `ubuntu` user (UID 1000), so `USER ubuntu` works

## CA Certificates and Timezone
COMMAND | DESCRIPTION
---|---
`apt-get install -y --no-install-recommends ca-certificates` | Needed for HTTPS from a minimal image
`update-ca-certificates` | Rebuild after adding `.crt` files to `/usr/local/share/ca-certificates/`
`apt-get install -y --no-install-recommends tzdata` | Install zone data
`ln -fs /usr/share/zoneinfo/Europe/London /etc/localtime && dpkg-reconfigure -f noninteractive tzdata` | Set the timezone without a prompt
`-e TZ=Europe/London` | Alternative at `docker run` (needs `tzdata`; unverified)

## Gotchas
SYMPTOM | FIX
---|---
Build hangs on a `tzdata` or keyboard prompt | Set `DEBIAN_FRONTEND=noninteractive` for that `RUN`
`E: Unable to locate package` | Run `apt-get update` in the same `RUN` (the image ships without indexes)
`curl: (60) SSL certificate problem` | Install `ca-certificates`
Image grows after installs | Remove `/var/lib/apt/lists/*` in the same layer
No `sudo`, `ps`, `ping` and similar | Minimal image; install the package that provides it
Sources are in `/etc/apt/sources.list.d/ubuntu.sources` | 24.04 uses the deb822 format, not `sources.list`
