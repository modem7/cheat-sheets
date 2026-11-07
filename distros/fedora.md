# Fedora
Fedora is a glibc and RPM based distribution with fast-moving packages and a short support window (a release lasts roughly 13 months). Use it for new toolchains, not long-lived production bases.

Documentation: [Fedora Docs](https://docs.fedoraproject.org/) · [DNF5 docs](https://dnf5.readthedocs.io/)
Project: [Fedora](https://fedoraproject.org/) · [Docker Hub](https://hub.docker.com/_/fedora)

See also [Container Distros](distros.md), [Amazon Linux](amazon-linux.md), [SELinux and AppArmor](../linux/selinux-apparmor.md) and [Dockerfile](../docker/docker-file.md).

## dnf in Dockerfiles
`fedora:42` uses dnf5 (`dnf --version` reports `dnf5 5.2.x`). `microdnf` is a symlink to `dnf5` there, so both behave the same.

COMMAND | DESCRIPTION
---|---
`dnf -y install --setopt=install_weak_deps=False PACKAGE` | Install without weak (recommended) dependencies
`dnf clean all` | Remove cached metadata and packages (run in the same layer)
`dnf -y upgrade` | Upgrade installed packages
`dnf search TERM` | Search packages
`dnf provides /PATH/TO/FILE` | Which package provides a file
`dnf repoquery --installed` | List installed packages
`rpm -qf /PATH/TO/FILE` | Which installed package owns a file
`rpm -ql PACKAGE` | List a package's files

```dockerfile
FROM fedora:42
RUN dnf -y install --setopt=install_weak_deps=False jq \
 && dnf clean all
```

## Image Tags
TAG | MEANING
---|---
`fedora:42` | A specific release (preferred)
`fedora:latest` | Newest release; avoid in builds
`fedora:rawhide` | Development branch (unverified)

Check the end-of-life date of the release you pin on the Fedora Docs site.

## Users
COMMAND | DESCRIPTION
---|---
`useradd -r -u 10001 APP` | Create a system user; a UID above 999 prints a `SYS_UID_MAX` warning but works
`useradd -u 10001 -m APP` | Create a regular user with a home directory

## CA Certificates and Timezone
COMMAND | DESCRIPTION
---|---
`update-ca-trust` | Rebuild the trust store after adding certificates to `/etc/pki/ca-trust/source/anchors/`
`ln -sf /usr/share/zoneinfo/Europe/London /etc/localtime` | Set the timezone (`/usr/share/zoneinfo` is present in `fedora:42`)

The CA bundle and `curl`, `bash` and `sudo` are already in the image.

## Gotchas
SYMPTOM | FIX
---|---
Command syntax or output differs from older docs | `dnf` is dnf5 since Fedora 41; older posts describe dnf4
Image is large for a base (about 250 MB) | Fedora ships more than Debian or Alpine; run `dnf clean all` and avoid weak deps
Releases stop receiving updates | Move to the next release regularly
SELinux denials on bind mounts | Add `:z` or `:Z` to the volume, see [SELinux and AppArmor](../linux/selinux-apparmor.md)
