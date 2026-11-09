# HAProxy
HAProxy is a load balancer and reverse proxy for TCP and HTTP. Use it in front of several backends, for TLS termination, health checks and drain-and-maintain workflows. These notes follow the 3.0 documentation.

Documentation: [HAProxy 3.0 configuration](https://docs.haproxy.org/3.0/configuration.html) · [Management guide](https://docs.haproxy.org/3.0/management.html)

## Minimal Config
```text
defaults
    mode http
    timeout connect 5s
    timeout client  30s
    timeout server  30s

frontend web
    bind :80
    default_backend app

backend app
    balance roundrobin
    option httpchk GET /health
    server app1 192.0.2.10:8080 check
    server app2 192.0.2.11:8080 check
```

The `option httpchk [<method>] <uri> [<version>]` form is from the manual. The `check` keyword on `server` lines enables health checks, but its `inter` tuning was not verified.

## Validate and Reload
COMMAND | DESCRIPTION
---|---
`haproxy -c -f /etc/haproxy/haproxy.cfg` | Check the config (exit status non-zero on error)
`haproxy -c -V -f /etc/haproxy/haproxy.cfg` | Also print "Configuration file is valid"
`sudo systemctl reload haproxy` | Reload without dropping connections

In master-worker mode a reload re-executes on `SIGUSR2`, and the service script runs the check first. Always validate before reloading.

## Modes and Balancing
OPTION | MEANING
---|---
`mode tcp` | Layer 4, no HTTP parsing (databases, SSH, TLS passthrough)
`mode http` | Layer 7, enables headers, redirects and routing
`balance roundrobin` | Rotate through servers
`balance leastconn` | Fewest connections, recommended for long sessions such as SQL
`balance static-rr` | Round robin with fixed weights
`balance first` | Fill the first server before using the next
`balance source` | Hash of the client IP, so a client sticks to a server

## HTTP Options
OPTION | MEANING
---|---
`option forwardfor [except <NET>] [header <NAME>] [if-none]` | Add `X-Forwarded-For` with the client IP
`redirect scheme https if !{ ssl_fc }` | Redirect to HTTPS (the manual's example form)
`bind :8443 ssl crt <PEM_FILE>` | Terminate TLS with a certificate bundle
`send-proxy`, `send-proxy-v2` | Server options that pass client addresses using the PROXY protocol

The backend must be configured to accept the PROXY protocol before you enable `send-proxy`, or connections fail.

## Stats
```text
listen stats
    bind 127.0.0.1:8404
    mode http
    stats enable
    stats uri /stats
```

Bind it to a trusted address only. `stats enable` and `stats uri <PREFIX>` are from the manual.

## Runtime Socket
In the `global` section:

```text
stats socket /var/run/haproxy.sock mode 600 level admin
```

COMMAND | DESCRIPTION
---|---
`echo "show stat" \| socat stdio /var/run/haproxy.sock` | Server and backend statistics
`echo "show servers state" \| socat stdio /var/run/haproxy.sock` | Server states (optionally add a backend name)
`echo "set server <BACKEND>/<SERVER> state drain" \| socat stdio /var/run/haproxy.sock` | Stop new sessions, let existing ones finish
`echo "set server <BACKEND>/<SERVER> state maint" \| socat stdio /var/run/haproxy.sock` | Take it out of service
`echo "set server <BACKEND>/<SERVER> state ready" \| socat stdio /var/run/haproxy.sock` | Return it to service

Use `drain` first, then `maint` once connections have gone, for a clean upgrade.

## Not Verified
ACL and `use_backend` routing examples, the `check inter` text, logging directives, and certificate renewal hooks.

## See Also
- [Squid](squid.md)
- [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md)
- [Nginx](nginx.md)
