# Dozzle
Dozzle is a lightweight web viewer for Docker container logs: live tail, search and multi-host, with no database. Use it for quick "what is this container doing" checks. For stored, queryable logs use [Loki and Grafana Alloy](loki-alloy.md).

Documentation: [Dozzle](https://dozzle.dev/)

## Install
```yaml
services:
  dozzle:
    image: amir20/dozzle:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - dozzle_data:/data
    ports:
      - "8080:8080"
volumes:
  dozzle_data:
```

Mounting `docker.sock` gives root-equivalent access to the host, and `:ro` does not restrict the Docker API. Keep Dozzle behind authentication and off the public internet.

## Options
ENVIRONMENT VARIABLE | DESCRIPTION
---|---
`DOZZLE_ENABLE_ACTIONS=true` | Allow start, stop and restart from the UI
`DOZZLE_ENABLE_SHELL=true` | Allow a shell inside containers from the UI
`DOZZLE_AUTH_PROVIDER=simple` | Built-in login, users in `/data/users.yml`
`DOZZLE_AUTH_TTL=48h` | Session lifetime (units `s`, `m`, `h`; default is a browser session)
`DOZZLE_FILTER=label=<KEY>=<VALUE>` | Only show matching containers
`DOZZLE_HOSTNAME=<NAME>` | Name shown for this host
`DOZZLE_REMOTE_AGENT=<HOST>:7007` | Add agents (comma-separated)

## Simple Authentication
Generate the users file, then mount `/data`:

```bash
docker run -it --rm amir20/dozzle generate admin --password PASSWORD --email admin@example.com --name "Admin" > users.yml
```

Drop `--password` to be prompted (needs `-it`). Place `users.yml` in the `/data` volume.

## Multiple Hosts (Agents)
Run an agent on each remote Docker host:

```yaml
services:
  dozzle-agent:
    image: amir20/dozzle:latest
    command: agent
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - "7007:7007"
```

On the main instance set `DOZZLE_REMOTE_AGENT=agent-host:7007`. Anyone who can reach port 7007 can read every log on that host and run commands in its containers, so keep it on a private network or a Docker network. The agent ignores `DOZZLE_ENABLE_SHELL` and `DOZZLE_ENABLE_ACTIONS`.

## See Also
- [Loki and Grafana Alloy](loki-alloy.md)
- [Docker](../docker/docker.md)
- [Docker Troubleshooting](../docker/docker-troubleshooting.md)
- [Portainer](portainer.md)
