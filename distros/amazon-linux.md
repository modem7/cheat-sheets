# Amazon Linux
Amazon Linux 2023 (AL2023) is AWS's RPM based distribution, derived from Fedora packages. Use the `amazonlinux` image to match an AWS host, for example for Lambda custom runtimes or EC2.

Documentation: [AL2023 User Guide](https://docs.aws.amazon.com/linux/al2023/ug/)
Project: [Amazon Linux](https://aws.amazon.com/linux/amazon-linux-2023/) · [Docker Hub](https://hub.docker.com/_/amazonlinux)

See also [Container Distros](distros.md), [Fedora](fedora.md) and [Dockerfile](../docker/docker-file.md).

## dnf in Dockerfiles
AL2023 uses dnf 4 (`4.14.0` in the image checked). There is no `microdnf` in `amazonlinux:2023`; use `dnf`. `yum` is also present.

COMMAND | DESCRIPTION
---|---
`dnf -y install --setopt=install_weak_deps=False PACKAGE` | Install without weak dependencies
`dnf clean all` | Remove cached metadata (run in the same layer)
`dnf -y upgrade` | Upgrade installed packages
`dnf search TERM` | Search packages
`dnf provides /PATH/TO/FILE` | Which package provides a file
`dnf repolist` | Show enabled repositories (`amazonlinux` by default)
`rpm -qf /PATH/TO/FILE` | Which installed package owns a file
`rpm -q PACKAGE` | Check a package and its version

```dockerfile
FROM amazonlinux:2023
RUN dnf -y install --setopt=install_weak_deps=False tar gzip \
 && dnf clean all
```

## Image Tags
TAG | MEANING
---|---
`amazonlinux:2023` | AL2023, release stream (preferred)
`amazonlinux:2` | Amazon Linux 2, the older generation; check AWS for its end-of-support date
`amazonlinux:latest` | Avoid in builds

Dated tags such as `2023.12.20261102` exist (the image checked reports that in `/etc/system-release`).

## Users
COMMAND | DESCRIPTION
---|---
`dnf -y install shadow-utils` | `useradd` is not in the base image; install this first
`useradd -r -u 10001 APP` | Create a system user; a UID above 999 can print a `SYS_UID_MAX` warning (unverified on AL2023)

## CA Certificates and Timezone
COMMAND | DESCRIPTION
---|---
`update-ca-trust` | Rebuild the trust store after adding certificates to `/etc/pki/ca-trust/source/anchors/`
`ln -sf /usr/share/zoneinfo/Europe/London /etc/localtime` | Set the timezone (`/usr/share/zoneinfo` is present)

The CA bundle, `curl` and `bash` are already in the image.

## Gotchas
SYMPTOM | FIX
---|---
`curl` conflicts when installing the full package | The image ships `curl-minimal`; use `dnf install --allowerasing curl` to swap it
`useradd: command not found` | Install `shadow-utils`
`which`, `tar`, `gzip` missing | Minimal image; install them
`microdnf: not found` | Not shipped; use `dnf`
Guides for Amazon Linux 2 do not apply | AL2 used `yum`, `amazon-linux-extras` and a different release model; AL2023 uses `dnf`
