# Docker Networking
How containers talk to each other, the host and the outside world. See also [[docker]] and [[docker-compose]].

## Network Drivers
DRIVER | DESCRIPTION
---|---
`bridge` | Default. Containers get private IPs on a virtual bridge and reach the outside via NAT
`host` | Container shares the host's network stack. No port mapping, no isolation
`none` | No networking
`overlay` | Multi-host networking for Docker Swarm
`macvlan` | Container gets its own MAC and IP on the physical LAN
`ipvlan` | Like macvlan but shares the host MAC

> On the **default** `bridge` network containers can only reach each other by IP. On **user-defined** bridges they can also resolve each other by container name. Use user-defined networks.

## Managing Networks
COMMAND | DESCRIPTION
---|---
`docker network ls` | List networks
`docker network create <NAME>` | Create a user-defined bridge
`docker network create --subnet 172.30.0.0/24 --gateway 172.30.0.1 <NAME>` | Create with a fixed subnet
`docker network inspect <NAME>` | Show config and attached containers
`docker network connect <NETWORK> <CONTAINER>` | Attach a running container
`docker network disconnect <NETWORK> <CONTAINER>` | Detach a container
`docker network rm <NAME>` | Remove a network
`docker network prune` | Remove all unused networks

## Containers and Ports
COMMAND | DESCRIPTION
---|---
`docker run -d --network <NAME> --name <C> <IMAGE>` | Start a container on a network
`docker run -d -p 8080:80 <IMAGE>` | Publish host 8080 to container 80
`docker run -d -p 127.0.0.1:8080:80 <IMAGE>` | Publish on localhost only
`docker run -d -P <IMAGE>` | Publish all EXPOSEd ports to random host ports
`docker run --network host <IMAGE>` | Use the host network
`docker run --add-host host.docker.internal:host-gateway <IMAGE>` | Reach the host from a container on Linux
`docker run --dns 1.1.1.1 <IMAGE>` | Custom DNS server
`docker port <CONTAINER>` | Show port mappings

> Published ports bypass UFW rules because Docker writes its own iptables rules. Bind to `127.0.0.1` for anything that must not be public. See [[ufw]] and [[iptables]].

## Debugging
COMMAND | DESCRIPTION
---|---
`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}' <CONTAINER>` | Container IP addresses
`docker exec <CONTAINER> getent hosts <OTHER>` | Test name resolution between containers
`docker exec <CONTAINER> cat /etc/resolv.conf` | Check DNS settings (embedded DNS is 127.0.0.11)
`docker run --rm --network container:<CONTAINER> nicolaka/netshoot` | Debug with a toolbox sharing the container's network namespace
`sudo iptables -t nat -L -n` | See NAT rules Docker created
`ip -br a show docker0` | Show the default bridge

## Compose Example
```yaml
services:
  web:
    image: nginx
    ports:
      - "127.0.0.1:8080:80"
    networks: [frontend, backend]
  db:
    image: postgres:17
    networks: [backend]

networks:
  frontend:
  backend:
    internal: true   # no outbound internet access
```
