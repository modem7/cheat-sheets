# Portainer
Easily deploy, configure and secure containers in minutes on **[Docker](../docker/docker.md)**, **[Kubernetes](../kubernetes/kubernetes.md)**, Swarm and Nomad in any cloud, datacenter or device.

Project Homepage: [Portainer](https://www.portainer.io)
Documentation: [Portainer Docs](https://docs.portainer.io)

---
## Install (Docker, Community Edition)
```bash
docker volume create portainer_data
docker run -d --name portainer --restart=always \
  -p 9443:9443 -p 8000:8000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:lts
```
Open `https://<HOST>:9443` and create the admin user straight away. The setup window closes after about 5 minutes and Portainer must be restarted if you miss it.

> Mounting `docker.sock` gives Portainer root-equivalent control of the host. Do not expose it to the internet without TLS and strong authentication.

## Agent (Manage Another Host)
```bash
docker run -d --name portainer_agent --restart=always \
  -p 9001:9001 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /var/lib/docker/volumes:/var/lib/docker/volumes \
  portainer/agent:lts
```
Then add an **Environment** of type *Docker Standalone > Agent* pointing at `<HOST>:9001`.

## Operations
COMMAND | DESCRIPTION
---|---
`docker logs portainer` | Check start-up and errors
`docker pull portainer/portainer-ce:lts && docker rm -f portainer` then re-run the install command | Upgrade (data lives in `portainer_data`)
`docker run --rm -v portainer_data:/data portainer/helper-reset-password` | Reset the admin password
`docker run --rm -v portainer_data:/data -v $(pwd):/backup busybox tar czf /backup/portainer.tgz /data` | Back up the data volume

## Features Worth Knowing
- **Stacks**: deploy Compose files (see [Docker-Compose](../docker/docker-compose.md)) from the UI or straight from a Git repository with auto-update.
- **Templates**: one-click app deployments.
- **Users and teams**: role-based access to environments.
- **Kubernetes**: manage namespaces, deployments and apply manifests.

## Portainer vs Dockhand
- **Portainer**: manages Docker, Swarm, Kubernetes and Nomad; mature, with Community and paid Business editions and RBAC in Business.
- **[Dockhand](dockhand.md)**: Docker only, newer and lighter; Git stacks with webhooks, built-in Grype/Trivy scanning, Hawser agents; BSL 1.1 licence (free for personal and non-production use).
- Choose Portainer for Kubernetes/Swarm or a long-established tool, Dockhand for a simple Docker-only UI. Full table in [Dockhand](dockhand.md).
