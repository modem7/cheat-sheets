# Jellyfin
Jellyfin is a free, self-hosted media server for movies, TV, music and photos. It pairs with the [arr stack](arr-stack.md) for acquiring and organising media.

Documentation: [Jellyfin docs](https://jellyfin.org/docs/)

## Install (Docker)
Official images are `jellyfin/jellyfin` and `ghcr.io/jellyfin/jellyfin`. The `linuxserver/jellyfin` image is also popular.

```yaml
services:
  jellyfin:
    image: jellyfin/jellyfin
    container_name: jellyfin
    restart: unless-stopped
    ports:
      - "8096:8096/tcp"
      - "7359:7359/udp"
    volumes:
      - ./config:/config
      - ./cache:/cache
      - /srv/media:/media:ro
```

PORT | USE
---|---
`8096/tcp` | HTTP web UI and API
`8920/tcp` | HTTPS (if you terminate TLS in Jellyfin)
`7359/udp` | Client discovery. Needs host networking or a LAN-reachable mapping to work

Mount media read-only if Jellyfin does not need to delete files. The first-run wizard asks for an admin user and libraries. Add each library with a content type and display name.

## Hardware Transcoding
Supported: Intel QSV, NVIDIA NVENC, AMD AMF, VAAPI, VideoToolbox and RKMPP. `jellyfin-ffmpeg` is recommended. Docker on non-Linux hosts is not supported for this.

COMMAND | DESCRIPTION
---|---
`lspci -nn \| grep -Ei "3d\|display\|vga"` | Identify the GPU
`ls -l /dev/dri` | Check render devices exist on the host

Pass `/dev/dri` into the container (the docs show `--device /dev/dri/:/dev/dri/`, the compose form is `devices: - /dev/dri:/dev/dri`, which is not verbatim from the docs). Then enable the method under Dashboard, Playback, Transcoding.

## Reverse Proxy
Add your proxy's address under Dashboard, Networking, **Known Proxies**. Jellyfin then respects `X-Forwarded-For`, `X-Forwarded-Proto` and `X-Forwarded-Host`. WebSockets must be proxied. Caddy is the documented recommendation. See [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md) and [Cloudflare Tunnel](cloudflared.md).

## Backup and Restore
- **Built in (10.11 and later):** Dashboard, Backups. In Docker the archives land in `config/data/backups` under your config volume.
- **Manual:** stop the container (`docker stop jellyfin`), then copy the config and data directories.
- **Restore from an archive:** start Jellyfin with `--restore-archive PATH_TO_BACKUP_ZIP`.
- There is no documented way to downgrade.

## See Also
- [arr stack](arr-stack.md)
- [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md)
- [mergerfs](../linux/mergerfs.md)
- [Hardware Inspection](../linux/hardware-inspection.md)
