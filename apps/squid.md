# Squid
Squid is a caching and filtering HTTP proxy. In a homelab it is used to cache downloads, restrict which sites a VLAN can reach, or give isolated hosts a controlled way out. These notes follow the Squid 7 configuration manual.

Documentation: [Squid 7 configuration reference](https://www.squid-cache.org/Versions/v7/cfgman/) · [Squid wiki](https://wiki.squid-cache.org/)

## Core Directives
DIRECTIVE | MEANING
---|---
`http_port 3128` | Listening port. There is no default, and the examples use 3128
`http_access allow\|deny [!]ACL ...` | Access rules, first match wins
`cache_mem 256 MB` | RAM cache size (default 256 MB)
`cache_dir ufs <DIR> <MBYTES> <L1> <L2>` | Disk cache. Defaults are 100 MB, 16 and 256
`maximum_object_size 4 MB` | Largest object cached (default 4 MB)
`visible_hostname <NAME>` | Name used in errors and headers (defaults to the host name)
`refresh_pattern [-i] REGEX MIN PERCENT MAX` | Freshness rules. Min and max are minutes, first match wins

Default `refresh_pattern` lines:

```text
refresh_pattern ^ftp:           1440    20%     10080
refresh_pattern -i (/cgi-bin/|\?) 0     0%      0
refresh_pattern .               0       20%     4320
```

## Access Rules
Rules are checked in order and the first match wins. If nothing matches, Squid does the opposite of the last rule, so always end with a deny:

```text
acl localnet src 192.0.2.0/24
http_access allow localnet
http_access deny all
```

Only allow your own networks. An open proxy is abused quickly. A `dstdomain` ACL such as `acl allowed dstdomain .example.com` appears in the FAQ, but the file-based form was not verified.

## Operating
COMMAND | DESCRIPTION
---|---
`squid -z` | Create the cache directories in a new `cache_dir`
`squid -k reconfigure` | Reload the configuration
`squid -k shutdown` | Stop cleanly

The cache directory must exist and be writable by the Squid user. Install and `squid -k parse` for a syntax check, log paths and the service name were not verified here, so check your distribution's package.

## Transparent (Intercept) Mode
`intercept` accepts connections that a firewall has redirected, so clients need no proxy setting:

```text
http_port 3129 intercept
```

```bash
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 3129
```

Limits from the Squid wiki: HTTP only, authentication is disabled on that port, and SSL-Bump is usually incompatible. Keep a normal `http_port 3128` for explicit clients. For HTTPS, clients should use the proxy explicitly.

## SSL Bump
Squid can decrypt HTTPS (SSL-Bump) with its own certificate authority. The wiki calls it a man-in-the-middle attack and warns it may be illegal without consent. Certificate caches can use several GB of RAM, and peek-and-splice (3.5 and later) replaced the older bump modes. For a homelab, prefer allow-listing domains with CONNECT and do not decrypt.

## Not Verified
`squid -k parse`, log paths, the `apt install` command, basic authentication, file-based `dstdomain` lists, `squidclient`, and cache refresh tuning.

## See Also
- [HAProxy](haproxy.md)
- [APT Cacher NG](apt-cacher-ng.md)
- [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md)
