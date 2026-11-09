# NetBox
NetBox is a source of truth for network and infrastructure: sites, racks, devices, cables, IP addresses, prefixes and VLANs, with a REST API. Use it to stop tracking IP plans and rack layouts in spreadsheets. For VLAN design see [VLANs](../homelab/vlans.md).

Documentation: [NetBox docs](https://netboxlabs.com/docs/netbox/), [netbox-docker](https://github.com/netbox-community/netbox-docker)

## Install (netbox-docker)
Requires Docker 20.10.10 or later and Compose 1.28.0 or later.

```bash
git clone -b release https://github.com/netbox-community/netbox-docker.git
cd netbox-docker
cp docker-compose.override.yml.example docker-compose.override.yml
docker compose pull
docker compose up
```

The UI is at `http://HOST:8000/`. Create the admin user:

```bash
docker compose exec netbox /opt/netbox/netbox/manage.py createsuperuser
```

Or set `SUPERUSER_*` variables in the override file. Images are `netboxcommunity/netbox` on Docker Hub, Quay and GHCR. Pin a tag that matches the netbox-docker release (`vX.Y.Z-a.b.c`) instead of `latest`. Put HTTPS in front of it, see [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md).

## What to Model
OBJECT | USE
---|---
Regions, sites, locations, racks | Where things are
Devices, device types, interfaces, cables | What you own and how it is wired
Prefixes, IP addresses, VRFs | IP address management
VLANs | VLAN IDs and names per site
Virtual machines, clusters | Hypervisor guests (for example [Proxmox](../proxmox/proxmox-overview.md))
Circuits, ASNs, tenancy | ISP links, routing and ownership

A homelab can start with one site, a few prefixes (one per [VLAN](../homelab/vlans.md)) and a device list, then grow.

## REST API
Base URL `https://HOST/api/`, detail URLs need a trailing slash, and Swagger UI is at `/api/schema/swagger-ui/`.

```bash
curl -H "Authorization: Bearer ${NETBOX_TOKEN}" -H "Accept: application/json" \
  "https://netbox.example.com/api/dcim/devices/?limit=50"
```

ENDPOINT | OBJECTS
---|---
`/api/dcim/sites/` | Sites
`/api/dcim/racks/` | Racks
`/api/dcim/devices/` | Devices
`/api/ipam/prefixes/` | Prefixes
`/api/ipam/ip-addresses/` | IP addresses

- **v2 tokens** (4.5 and later): `Authorization: Bearer nbt_<key>.<token>`. Stored hashed, shown once.
- **v1 tokens**: `Authorization: Token <token>`. Deprecated in 4.6 and removed in 5.0.
- Paging uses `limit` and `offset`. The default page size is 50 and the maximum 1000. Filter with query parameters such as `?device_id=123`.
- NetBox 4.7.0 and 4.7.1 leaked token plaintext through background bulk-write jobs, so treat tokens from those versions as exposed.

Client libraries such as `pynetbox` and the Ansible inventory plugin exist (see [Ansible](../tools/ansible.md)), but their syntax is not verified here.

## See Also
- [VLANs](../homelab/vlans.md)
- [Homelab](../homelab/homelab.md)
- [Ansible](../tools/ansible.md)
- [Terraform](../tools/terraform.md)
