# BIND 9
BIND 9 (`named`) is the reference authoritative and recursive DNS server. In a homelab it usually serves your own zone (`home.example.com`) with a primary and optional secondary, while a resolver such as [Unbound](unbound.md) or [Pi-hole](pihole.md) handles recursion for clients.

Documentation: [BIND 9 Administrator Reference Manual](https://bind9.readthedocs.io/en/latest/) · [rndc](https://bind9.readthedocs.io/en/latest/manpages.html#rndc-name-server-control-utility)
Project: [BIND 9 at ISC](https://www.isc.org/bind/)

> **Verification:** `rndc`, `named-checkconf` and `named-checkzone` options were checked against the man pages in Ubuntu 24.04 (`bind9`, `bind9-utils`), and the example config and zone were validated with those two checkers. File locations are Debian and Ubuntu (`/etc/bind/`); other distributions differ. The configuration was not served to real clients.

## Install and Service
COMMAND | DESCRIPTION
---|---
`sudo apt install bind9 bind9-utils bind9-dnsutils` | Server, checkers and `dig`
`sudo systemctl enable --now named` | Start now and at boot (the unit is also available as `bind9`)
`sudo systemctl status named` | Service state
`sudo journalctl -u named -f` | Follow logs

## Check Before Reloading
COMMAND | DESCRIPTION
---|---
`named-checkconf` | Check `named.conf` and included files (no output means OK)
`named-checkconf -z` | Also test-load every primary zone
`named-checkconf -p` | Print the configuration in canonical form
`named-checkconf -px` | Same, hiding shared secrets
`named-checkzone example.com /etc/bind/zones/db.example.com` | Check one zone file
`named-checkzone -i full example.com /etc/bind/zones/db.example.com` | Stricter integrity checks

## rndc
`rndc` controls the running server over a local control channel; the Debian package sets up its key.

COMMAND | DESCRIPTION
---|---
`sudo rndc status` | Server version, zone count, query log state
`sudo rndc reload` | Reload configuration and changed zones
`sudo rndc reload example.com` | Reload one zone
`sudo rndc reconfig` | Pick up new or removed zones only
`sudo rndc flush` | Flush the resolver cache
`sudo rndc flushname <NAME>` | Remove one name from the cache
`sudo rndc zonestatus example.com` | Serial, type and refresh times
`sudo rndc retransfer example.com` | Secondary: force a fresh transfer
`sudo rndc notify example.com` | Primary: tell secondaries the zone changed
`sudo rndc querylog on` / `off` | Log every query (noisy)
`sudo rndc freeze example.com` / `thaw example.com` | Pause dynamic updates to edit a zone file by hand, then resume

## Primary Zone
`/etc/bind/named.conf.local`:

```text
zone "example.com" {
    type primary;
    file "/etc/bind/zones/db.example.com";
    allow-transfer { 192.0.2.54; };
    notify yes;
};

zone "2.0.192.in-addr.arpa" {
    type primary;
    file "/etc/bind/zones/db.192.0.2";
};
```

`/etc/bind/zones/db.example.com`:

```text
$TTL 1h
@   IN SOA ns1.example.com. hostmaster.example.com. (
        2026110701 ; serial (YYYYMMDDnn)
        1h         ; refresh
        15m        ; retry
        1w         ; expire
        1h )       ; negative cache TTL
    IN NS  ns1.example.com.
    IN NS  ns2.example.com.
ns1 IN A   192.0.2.53
ns2 IN A   192.0.2.54
nas IN A   192.0.2.20
www IN CNAME nas
```

`/etc/bind/zones/db.192.0.2`:

```text
$TTL 1h
@   IN SOA ns1.example.com. hostmaster.example.com. (
        2026110701 ; serial
        1h 15m 1w 1h )
    IN NS  ns1.example.com.
53  IN PTR ns1.example.com.
20  IN PTR nas.example.com.
```

Increase the serial on every change, otherwise secondaries do not transfer. Names ending in a dot are absolute.

## Options
`/etc/bind/named.conf.options`:

```text
options {
    directory "/var/cache/bind";
    listen-on { 192.0.2.53; 127.0.0.1; };
    allow-query { 192.0.2.0/24; localhost; };
    recursion no;
    dnssec-validation auto;
};
```

OPTION | PURPOSE
---|---
`recursion no` | Authoritative only; never open to the internet as a recursive resolver
`allow-query` | Who may ask
`allow-transfer` | Who may fetch the whole zone (restrict to secondaries)
`listen-on` | Addresses to bind
`forwarders { ... };` | Send recursive queries to an upstream (only if recursion is on)
`dnssec-validation auto` | Validate with the built-in trust anchor

## Test
```bash
dig @192.0.2.53 www.example.com +short
dig @192.0.2.53 -x 192.0.2.20 +short
dig @192.0.2.53 example.com SOA +short
dig @192.0.2.53 example.com AXFR
```

See [dig](../networking/dig.md) for more options.

## Troubleshooting
SYMPTOM | FIX
---|---
Zone not loaded | `sudo journalctl -u named`, then `named-checkzone`
Changes not visible | Serial not increased, or you forgot `rndc reload`
`REFUSED` | `allow-query` or `recursion no` blocks the client
Secondary out of date | `rndc zonestatus` on both; `rndc retransfer` on the secondary; check `allow-transfer` and the firewall (TCP 53)
Permission denied reading a zone file | AppArmor on Ubuntu confines `named` to `/etc/bind` and `/var/cache/bind`; put zone files there
Dynamic update fails | The directory must be writable by `named` (`/var/cache/bind` or `/var/lib/bind`)

## See Also
- [dig](../networking/dig.md)
- [Unbound](unbound.md)
- [Pi-hole](pihole.md)
- [DNS Troubleshooting](../recipes/dns-troubleshooting.md)
- [DNS Record Types](../networking/dns-record-types.md)
- [Ports and Protocols](../networking/ports-and-protocols.md)
