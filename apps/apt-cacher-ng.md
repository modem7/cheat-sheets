# APT Cacher NG
APT Cacher NG is a caching proxy for Debian and Ubuntu package downloads. Run one in the lab so many VMs and containers fetch each package from the internet once, which speeds up installs and templates such as [Proxmox cloud-init](../proxmox/proxmox-cloud-init.md).

Documentation: [APT Cacher NG manual](https://www.unix-ag.uni-kl.de/~bloch/acng/html/)

## Server
Install it on a host that stays on, such as an LXC. The `apt install` command and package name were not on the pages read, so check your distribution (the package is commonly `apt-cacher-ng`). It listens on port 3142 by default in the manual's examples. The main file is `acng.conf`.

SETTING | MEANING
---|---
`BindAddress` | Space-separated list of IPs to listen on. The default is all interfaces, IPv4 and IPv6
`PassThroughPattern: .*` | Tunnel HTTPS through the proxy **without caching** it
`Remap-<NAME>: <MERGING_URLS> ; <TARGET_URLS> ; <FLAGS>` | Map several mirrors onto one cache path

Restrict `BindAddress` to a management network. There is no user authentication in the examples read, so firewall port 3142 to your own VLANs.

## Clients
Point apt at the cache in `/etc/apt/apt.conf.d/02proxy` (the file name is your choice):

```text
Acquire::http::proxy "http://<CACHE_HOST>:3142";
```

Or rewrite a source line to go through the cache:

```text
deb http://<CACHE_HOST>:3142/ftp.uni-kl.de/debian etch main
```

The proxy setting is simpler for many hosts, and works from cloud-init or a template.

## HTTPS Repositories
Third-party repositories on HTTPS are a common snag:

METHOD | RESULT
---|---
`deb http://HTTPS///get.docker.com/ubuntu docker main` | Cached. The `HTTPS///` prefix tells the server to fetch over HTTPS. The author's preferred route
`http://<CACHE_HOST>:3142/HTTPS///<HOST>/<PATH>` | The same idea as a URL rewrite
`PassThroughPattern: .*` | Tunnelled, **not cached**
Add the HTTPS URL to a `Remap-` list | Alternative

With `PassThroughPattern`, HTTPS traffic bypasses caching, so the cache only helps for plain HTTP mirrors.

## Maintenance
A daily maintenance cron job exists, and cache clean-up is triggered from the report page in the manual (section 7.1). The report page URL, the cache directory default, `acngtool`, and Docker image details were not verified.

## Not Verified
The `apt install` command, the report page URL, `CacheDir` defaults, `acngtool`, Docker images, and running it in a Proxmox LXC.

## See Also
- [Squid](squid.md)
- [Aptly](../tools/aptly.md)
- [Proxmox Cloud-Init](../proxmox/proxmox-cloud-init.md)
- [New Server Checklist](../recipes/new-server-checklist.md)
