# Ports and Protocols
A reference of well-known TCP/UDP ports, the services and homelab/DevOps tools that use them, IP protocol numbers, private and special address ranges, and the commands for checking what is listening or reachable. Background: [TCP vs UDP](tcp-vs-udp.md), scanning with [NMap](../tools/nmap.md), secure transports in [TLS (Transport Layer Security)](tls.md), [VPN (Virtual Private Network)](vpn.md) and [DNS over TLS (DoT)](dns-over-tls.md).

Authoritative list: [IANA Service Name and Transport Protocol Port Number Registry](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml). Many ports below (especially above 1024) are application defaults, not registered standards, and are usually configurable.

## Port Ranges
RANGE | NAME | NOTES
---|---|---
`0-1023` | System / well-known | Binding needs root (or `CAP_NET_BIND_SERVICE`) on Linux
`1024-49151` | Registered | Applications and databases
`49152-65535` | Dynamic / ephemeral (IANA) | Linux uses `32768-60999` by default (`sysctl net.ipv4.ip_local_port_range`)

## Remote Access and Management
PORT | PROTO | SERVICE | NOTES
---|---|---|---
`22` | TCP | SSH, SFTP, SCP | Also Git over SSH. See [OpenSSH Cheat-Sheet](../tools/openssh.md)
`23` | TCP | Telnet | Cleartext, avoid
`3389` | TCP, UDP | RDP | Windows Remote Desktop. Do not expose to the internet
`5900` | TCP | VNC | Display `:1` is `5901` and so on
`5985` / `5986` | TCP | WinRM HTTP / HTTPS | PowerShell remoting, see [PowerShell Remote Access](../windows/powershell-remote.md)
`161` / `162` | UDP | SNMP / SNMP traps | SNMPv3 can add encryption
`623` | UDP | IPMI / BMC | Keep on a management VLAN

## Name, Address and Time Services
PORT | PROTO | SERVICE | NOTES
---|---|---|---
`53` | UDP, TCP | DNS | TCP for large replies and zone transfers (AXFR)
`853` | TCP | DNS over TLS | UDP `853` is DNS over QUIC. See [DNS over TLS (DoT)](dns-over-tls.md)
`443` | TCP | DNS over HTTPS | Same port as HTTPS. See [DNS over HTTPS (DoH)](dns-over-https.md)
`67` / `68` | UDP | DHCP server / client | DHCPv6 uses `547` / `546`
`69` | UDP | TFTP | PXE boot
`123` | UDP | NTP | Chrony and ntpd
`5353` | UDP | mDNS | Bonjour, Avahi (multicast `224.0.0.251`)
`5355` | UDP, TCP | LLMNR | Windows link-local name resolution
`1900` | UDP | SSDP / UPnP | Discovery, often disabled on routers
`137` / `138` / `139` | UDP / UDP / TCP | NetBIOS | Legacy SMB name and session services
`9` | UDP | Wake-on-LAN | Magic packet, `7` is also used

## Web and Proxies
PORT | PROTO | SERVICE | NOTES
---|---|---|---
`80` | TCP | HTTP | |
`443` | TCP, UDP | HTTPS | UDP `443` is HTTP/3 (QUIC)
`8080` | TCP | Alternate HTTP | Proxies, dashboards (Traefik API in insecure mode)
`8443` | TCP | Alternate HTTPS | UniFi, Tomcat
`3128` | TCP | Squid | Proxmox SPICE proxy also uses `3128`
`1080` | TCP | SOCKS proxy | |
`81` | TCP | Nginx Proxy Manager admin UI | Public traffic uses `80` / `443`

## Email
PORT | PROTO | SERVICE | ENCRYPTED VARIANT
---|---|---|---
`25` | TCP | SMTP (server to server) | STARTTLS
`587` | TCP | SMTP submission (clients) | STARTTLS, the usual client choice
`465` | TCP | SMTP submission | Implicit TLS ("SMTPS"), see [SMTP](smtp.md)
`110` | TCP | POP3 | `995` implicit TLS
`143` | TCP | IMAP | `993` implicit TLS

## Directory, Authentication and File Sharing
PORT | PROTO | SERVICE | NOTES
---|---|---|---
`389` | TCP, UDP | LDAP | STARTTLS available
`636` | TCP | LDAPS | Implicit TLS
`3268` / `3269` | TCP | Active Directory Global Catalog / over TLS | |
`88` | TCP, UDP | Kerberos | |
`464` | TCP, UDP | Kerberos password change | |
`135` | TCP | MS RPC endpoint mapper | Plus a high dynamic range
`445` | TCP | SMB / CIFS | Never expose to the internet
`2049` | TCP, UDP | NFS | NFSv4 needs only `2049`. See [NFS](../linux/nfs.md)
`111` | TCP, UDP | rpcbind / portmapper | NFSv3 only
`21` | TCP | FTP control | Data on `20` (active) or a passive range. Use SFTP instead
`873` | TCP | rsync daemon | `rsync -e ssh` uses `22`
`3260` | TCP | iSCSI target | |
`22000` | TCP, UDP | Syncthing sync | `21027` UDP discovery, `8384` web UI

## Databases and Message Brokers
PORT | PROTO | SERVICE | NOTES
---|---|---|---
`3306` | TCP | MySQL / MariaDB | See [MySQL](../databases/mysql.md), [MariaDB Cheat-Sheet](../databases/mariadb.md)
`5432` | TCP | PostgreSQL | See [PostgreSQL Cheat-Sheet](../databases/postgres.md)
`1433` | TCP | Microsoft SQL Server | |
`1521` | TCP | Oracle | |
`27017` | TCP | MongoDB | |
`6379` | TCP | Redis | `6380` often used for TLS
`11211` | TCP, UDP | Memcached | Disable UDP to avoid amplification abuse
`9200` / `9300` | TCP | Elasticsearch HTTP / transport | Kibana is `5601`
`8086` | TCP | InfluxDB | |
`5672` / `15672` | TCP | RabbitMQ AMQP / management UI | `5671` AMQP over TLS
`9092` | TCP | Kafka | |
`4222` | TCP | NATS | |
`1883` / `8883` | TCP | MQTT / MQTT over TLS | Mosquitto

## VPN and Tunnels
PORT | PROTO | SERVICE | NOTES
---|---|---|---
`51820` | UDP | WireGuard | Default, configurable. See [WireGuard](../apps/wireguard.md)
`41641` | UDP | Tailscale (WireGuard) | Falls back to relays. See [Tailscale](../apps/tailscale.md)
`1194` | UDP, TCP | OpenVPN | UDP preferred
`500` / `4500` | UDP | IPsec IKE / NAT-T | Plus ESP (protocol 50), see below
`1701` | UDP | L2TP | Normally inside IPsec
`1723` | TCP | PPTP | Insecure, avoid. Needs GRE (protocol 47)
`3478` | UDP, TCP | STUN / TURN | WebRTC and Tailscale NAT traversal
`5349` | TCP, UDP | STUN / TURN over TLS | |

## Monitoring and Observability
PORT | PROTO | SERVICE | NOTES
---|---|---|---
`9090` | TCP | Prometheus | See [Prometheus](../apps/prometheus.md)
`9093` | TCP | Alertmanager | |
`9091` | TCP | Pushgateway | |
`9100` | TCP | node_exporter | |
`9115` | TCP | blackbox_exporter | |
`9153` | TCP | CoreDNS metrics | |
`3000` | TCP | Grafana | See [Grafana](../apps/grafana.md). Gitea and AdGuard Home setup also default to `3000`
`3100` | TCP | Loki | |
`3200` | TCP | Tempo | |
`12345` | TCP | Grafana Alloy UI | |
`8080` | TCP | cAdvisor | |
`10050` / `10051` | TCP | Zabbix agent / server | |
`5666` | TCP | Nagios NRPE | |
`514` | UDP | Syslog | `601` TCP, `6514` TCP over TLS
`3001` | TCP | Uptime Kuma | Default Docker mapping
`9000` | TCP | Portainer (legacy HTTP), MinIO API, SonarQube | See [Portainer](../apps/portainer.md). `9443` is Portainer HTTPS, `8000` the edge tunnel

## Docker
PORT | PROTO | SERVICE | NOTES
---|---|---|---
`2375` | TCP | Docker daemon API, **unencrypted** | Never expose, equals root on the host
`2376` | TCP | Docker daemon API with TLS | |
`2377` | TCP | Swarm cluster management | |
`7946` | TCP, UDP | Swarm node discovery | |
`4789` | UDP | Swarm overlay network (VXLAN) | |
`5000` | TCP | Docker registry | `registry:2` image default
`50000` | TCP | Jenkins agent (JNLP) | Web UI on `8080`

See [Docker](../docker/docker.md) and [Docker Networking](../docker/docker-networking.md).

## Kubernetes
PORT | PROTO | COMPONENT | NOTES
---|---|---|---
`6443` | TCP | kube-apiserver | Also the k3s supervisor / API. See [Kubernetes](../kubernetes/kubernetes.md), [K3S](../kubernetes/k3s.md)
`2379` / `2380` | TCP | etcd client / peer | Control plane only
`10250` | TCP | kubelet API | Used by the API server for logs and exec
`10257` | TCP | kube-controller-manager (HTTPS) | |
`10259` | TCP | kube-scheduler (HTTPS) | |
`10256` | TCP | kube-proxy health | |
`30000-32767` | TCP, UDP | NodePort Services | Default range
`8472` | UDP | Flannel VXLAN | k3s default CNI. `51820` for flannel WireGuard backend
`4240` | TCP | Cilium health checks | `4244` Hubble
`9345` | TCP | RKE2 supervisor | Node registration
`443` / `80` | TCP | Ingress controllers | See [Traefik](../apps/traefik.md), [Nginx](../apps/nginx.md)
`53` | UDP, TCP | CoreDNS | See [Kubernetes DNS](../kubernetes/kubernetes-dns.md)
`22` | TCP | Node SSH | |

## Homelab and Self-Hosted
PORT | PROTO | SERVICE | NOTES
---|---|---|---
`8006` | TCP | Proxmox VE web UI and API | HTTPS. See [Proxmox VE Overview and Install](../proxmox/proxmox-overview.md)
`8007` | TCP | Proxmox Backup Server | See [Proxmox Backup and Restore](../proxmox/proxmox-backup.md)
`5405-5412` | UDP | Corosync cluster traffic | See [Proxmox Clustering and HA](../proxmox/proxmox-cluster-ha.md)
`5900-5999` / `3128` | TCP | Proxmox VNC and SPICE consoles | |
`60000-60050` | TCP | Proxmox live migration | Default range
`53` / `80` / `443` | UDP+TCP / TCP / TCP | Pi-hole | DNS plus web UI. Pi-hole can also serve DHCP on `67`
`3000` / `80` | TCP | AdGuard Home | `853` DoT, `784` DoQ
`8123` | TCP | Home Assistant | |
`32400` | TCP | Plex Media Server | |
`8096` / `8920` | TCP | Jellyfin HTTP / HTTPS | |
`8989` / `7878` / `9696` | TCP | Sonarr / Radarr / Prowlarr | |
`8200` | TCP | HashiCorp Vault | |
`8500` | TCP | Consul | |
`4646` | TCP | Nomad | |
`8000` | TCP | Woodpecker CI server | gRPC agent traffic on `9000`
`8080` | TCP | UniFi inform | UI on `8443`, STUN on UDP `3478`, discovery UDP `10001`
`1880` | TCP | Node-RED | |
`8384` | TCP | Syncthing web UI | |

## Encrypted Variants
PLAIN | ENCRYPTED | HOW
---|---|---
HTTP `80` | HTTPS `443` | Implicit TLS
SMTP `25` / `587` | SMTPS `465` | STARTTLS upgrade vs implicit TLS
IMAP `143` | IMAPS `993` | Implicit TLS
POP3 `110` | POP3S `995` | Implicit TLS
LDAP `389` | LDAPS `636` | Implicit TLS (or STARTTLS on `389`)
FTP `21` | FTPS `990` (implicit) | Or SFTP over SSH on `22`
DNS `53` | DoT `853`, DoH `443` | See [DNS over TLS (DoT)](dns-over-tls.md), [DNS over HTTPS (DoH)](dns-over-https.md)
MQTT `1883` | `8883` | TLS
Syslog `514` | `6514` | TLS
Docker API `2375` | `2376` | TLS client certificates
Telnet `23` | SSH `22` | Replace outright

**STARTTLS** begins in cleartext on the plain port and upgrades; **implicit TLS** is encrypted from the first byte on its own port. Details in [TLS (Transport Layer Security)](tls.md) and [TLS Handshake](tls-handshake.md).

## IP Protocol Numbers
These are the values of the IP header "protocol" field. Firewalls match them with `-p` (iptables / [UFW (uncomplicated firewall)](../linux/ufw.md) / [IPTables](../linux/iptables.md)), and ports exist only for TCP, UDP, SCTP and similar.

NUMBER | PROTOCOL | NOTES
---|---|---
`1` | ICMP | Ping, unreachable. Do not block it wholesale (breaks path MTU discovery)
`2` | IGMP | Multicast group membership
`4` | IP-in-IP | Encapsulation
`6` | TCP | |
`17` | UDP | |
`41` | IPv6 encapsulation | 6in4 tunnels
`47` | GRE | PPTP, tunnels
`50` | ESP | IPsec payload, no ports
`51` | AH | IPsec authentication header
`58` | ICMPv6 | Required for IPv6 neighbour discovery
`89` | OSPF | |
`112` | VRRP | keepalived, router failover (multicast `224.0.0.18`)
`115` | L2TP | |
`132` | SCTP | |

## Private and Special Address Ranges
RANGE | PURPOSE
---|---
`10.0.0.0/8` | Private (RFC 1918)
`172.16.0.0/12` | Private (`172.16.0.0` to `172.31.255.255`). Docker uses `172.17.0.0/16` by default
`192.168.0.0/16` | Private
`100.64.0.0/10` | Carrier-grade NAT (RFC 6598). Tailscale assigns addresses from here
`127.0.0.0/8` | Loopback
`169.254.0.0/16` | Link-local (APIPA), also cloud metadata `169.254.169.254`
`224.0.0.0/4` | Multicast
`240.0.0.0/4` | Reserved. `255.255.255.255` is limited broadcast
`0.0.0.0/8` | "This network". `0.0.0.0` means all interfaces when binding
`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` | Documentation (TEST-NET)
`198.18.0.0/15` | Benchmarking
`::1/128` | IPv6 loopback
`fe80::/10` | IPv6 link-local
`fc00::/7` | IPv6 unique local (in practice `fd00::/8`)
`ff00::/8` | IPv6 multicast
`2001:db8::/32` | IPv6 documentation

## Checking Ports
Listening on this machine:

COMMAND | DESCRIPTION
---|---
`ss -tulpn` | All listening TCP and UDP sockets with owning process (`sudo` to see other users' processes)
`ss -tln` | Listening TCP only, numeric
`ss -tn state established '( sport = :22 )'` | Established SSH connections
`ss -tn dst <IP>` | Connections to one host
`sudo lsof -i :443` | Process using a port
`sudo fuser 8080/tcp` | PID on a port
`netstat -tulpn` | Older equivalent (net-tools)
`netstat -ano \| findstr :443` | Windows, last column is the PID
`Get-NetTCPConnection -State Listen` | PowerShell listening ports
`Get-Process -Id <PID>` | PowerShell process for a PID

Reaching a remote port:

COMMAND | DESCRIPTION
---|---
`nc -zv <HOST> 443` | TCP connect test (`-w 3` for a timeout)
`nc -zv <HOST> 20-25` | Test a port range
`nc -zvu <HOST> 51820` | UDP "test" (no reply is not proof of a closed port)
`nc -l 8080` | Listen on a port for testing
`timeout 3 bash -c '</dev/tcp/<HOST>/443' && echo open` | Bash-only, no extra tools
`curl -v telnet://<HOST>:443` | Connect with curl, see [curl](../tools/curl.md)
`nmap -p 22,80,443 <HOST>` | Specific ports (`-p-` for all 65535)
`nmap -sU -p 53,123,161 <HOST>` | UDP scan (slow, needs root)
`nmap -sV -p 443 <HOST>` | Identify the service and version
`Test-NetConnection -ComputerName <HOST> -Port 443` | PowerShell TCP test, shows `TcpTestSucceeded`
`Test-NetConnection <HOST> -Port 443 -InformationLevel Quiet` | Returns `True` or `False`

Tips:
- A port can be open on the host but blocked by [UFW (uncomplicated firewall)](../linux/ufw.md), [IPTables](../linux/iptables.md), a cloud security group or the [Proxmox firewall](../proxmox/proxmox-firewall.md). Check from both sides.
- `127.0.0.1:PORT` in `ss` means loopback only, `0.0.0.0:PORT` or `*:PORT` means all IPv4 interfaces, `[::]:PORT` all IPv6.
- Docker published ports (`-p 8080:80`) are inserted into iptables ahead of `ufw` rules, so `ufw deny` does not hide them. Bind to loopback with `-p 127.0.0.1:8080:80`.
- Scan only hosts you own or are authorised to test. See [NMap](../tools/nmap.md). To test a port by hand, see [socat and netcat](socat-and-netcat.md).
