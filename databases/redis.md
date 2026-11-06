# Redis
Redis is an in-memory data store used as a cache, session store, queue and simple database. It keeps data in RAM and can persist it to disk with snapshots (RDB) and an append-only file (AOF). Valkey is a compatible fork that uses the same commands and `redis-cli`-style tools.

Documentation: [Redis docs](https://redis.io/docs/latest/) · [Commands](https://redis.io/docs/latest/commands/) · [redis-cli](https://redis.io/docs/latest/develop/tools/cli/) · [Persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)

> **Verification:** the `redis-cli` options (`--bigkeys`, `--memkeys`, `--keystats`, `--scan`, `--latency`) and the Docker image tags were checked against the Redis docs and Docker Hub. **Not verified against the docs:** ACL, replication and persistence settings below (they come from the Redis documentation as known, not re-read). No command was executed. Commands like `FLUSHALL` and `KEYS *` are dangerous on a real instance.

See also: [Docker](../docker/docker.md) · [Docker-Compose](../docker/docker-compose.md) · [PostgreSQL Cheat-Sheet](postgres.md) · [Linux](../linux/linux.md) · [Linux Performance Troubleshooting](../linux/performance-troubleshooting.md)

---
## Run in Docker
```bash
docker run -d --name redis --restart unless-stopped \
  -p 127.0.0.1:6379:6379 \
  -v redis-data:/data \
  redis:8 \
  redis-server --appendonly yes --requirepass <PASSWORD>

docker exec -it redis redis-cli -a '<PASSWORD>' ping
```
Compose:
```yaml
services:
  redis:
    image: redis:8
    restart: unless-stopped
    command: ["redis-server", "--appendonly", "yes", "--maxmemory", "256mb", "--maxmemory-policy", "allkeys-lru"]
    volumes:
      - redis-data:/data
    ports:
      - "127.0.0.1:6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
volumes:
  redis-data:
```
Mount `/data` or the data is lost with the container. Do not expose port 6379 to the internet. See [Docker](../docker/docker.md) and [Docker-Compose](../docker/docker-compose.md). Prefer `--requirepass` or an ACL file over a password on the command line in production (it shows in `ps`). Pin a major version tag (`redis:7`, `redis:8`).

## Install on Ubuntu / Debian
```bash
sudo apt update && sudo apt install -y redis-server
sudo systemctl enable --now redis-server
redis-cli ping
```
Config: `/etc/redis/redis.conf`. For a current version use the official packages repository.

---
## redis-cli
COMMAND | DESCRIPTION
---|---
`redis-cli` | Connect to `127.0.0.1:6379`
`redis-cli -h <HOST> -p 6379 -a <PASSWORD>` | Remote with password (warns that it is insecure; prefer `REDISCLI_AUTH`)
`REDISCLI_AUTH=<PASSWORD> redis-cli` | Password from the environment
`redis-cli --user <USER> --pass <PASSWORD>` | ACL user
`redis-cli -n 2` | Select database 2
`redis-cli --tls -h <HOST>` | TLS connection
`redis-cli ping` | Returns `PONG`
`redis-cli INFO` | Full server info (`INFO memory`, `INFO stats`, `INFO replication`)
`redis-cli -r 5 -i 1 INFO clients` | Repeat every second, 5 times
`redis-cli MONITOR` | Stream every command (heavy, debugging only)
`redis-cli --scan --pattern 'user:*'` | Iterate keys safely (use instead of `KEYS`)
`redis-cli --scan --pattern 'sess:*' \| xargs -L 100 redis-cli DEL` | Delete keys matching a pattern, in batches
`redis-cli --bigkeys` | Sample the keyspace and report the largest key of each type
`redis-cli --memkeys` | Same, by memory use
`redis-cli --keystats` | Combined key size and memory distribution (recent versions)
`redis-cli --latency` | Continuous round-trip latency
`redis-cli --latency-history` | Latency in time slices
`redis-cli --intrinsic-latency 5` | Host baseline latency (run on the server)
`redis-cli --stat` | Rolling stats line
`redis-cli --rdb backup.rdb` | Download an RDB snapshot from a server
`redis-cli -x SET key < file` | Read the value from stdin
`redis-cli --pipe < commands.txt` | Fast bulk load of raw commands

`--bigkeys`, `--memkeys` and `--keystats` scan the whole keyspace. Run them against a replica or off-hours on large instances.

### Inside redis-cli
COMMAND | DESCRIPTION
---|---
`SELECT 1` | Switch database (0-15 by default)
`DBSIZE` | Number of keys
`SCAN 0 MATCH user:* COUNT 100` | Cursor-based iteration. Repeat with the returned cursor until `0`
`TYPE key` | Type of a key
`TTL key` / `PTTL key` | Seconds / milliseconds to expiry (`-1` none, `-2` missing)
`EXPIRE key 3600` | Set a TTL
`PERSIST key` | Remove the TTL
`EXISTS key` | 1 or 0
`DEL key` | Delete (blocks on huge keys)
`UNLINK key` | Delete in the background (use for large keys)
`RENAME old new` | Rename
`MEMORY USAGE key` | Bytes used by a key
`OBJECT ENCODING key` | Internal encoding
`FLUSHDB ASYNC` | Delete all keys in the current database
`FLUSHALL ASYNC` | Delete every key in every database. **Destructive**
`CONFIG GET maxmemory*` | Read settings
`CONFIG SET maxmemory 256mb` | Change at runtime (then `CONFIG REWRITE` to persist to the config file)
`CLIENT LIST` | Connected clients
`SLOWLOG GET 10` | Last 10 slow commands
`LATENCY DOCTOR` | Latency analysis report
`MEMORY DOCTOR` | Memory advice

---
## Data Types
TYPE | COMMANDS | USE
---|---|---
String | `SET k v`, `GET k`, `INCR k`, `SET k v EX 60 NX`, `MSET`, `APPEND` | Cache values, counters, locks (`SET lock id NX EX 30`)
Hash | `HSET user:1 name alice age 30`, `HGET`, `HGETALL`, `HINCRBY`, `HDEL` | Objects with fields
List | `LPUSH`, `RPUSH`, `LPOP`, `BRPOP q 0`, `LRANGE q 0 -1`, `LLEN` | Queues and stacks
Set | `SADD`, `SMEMBERS`, `SISMEMBER`, `SINTER`, `SUNION`, `SCARD` | Unique members, tags
Sorted set | `ZADD board 100 alice`, `ZRANGE board 0 -1 WITHSCORES`, `ZREVRANGE`, `ZINCRBY`, `ZRANK` | Leaderboards, rate limits, schedulers
Stream | `XADD s * k v`, `XRANGE s - +`, `XREAD`, `XGROUP CREATE`, `XREADGROUP`, `XACK` | Event logs, consumer groups
Bitmap / HyperLogLog | `SETBIT`, `BITCOUNT`, `PFADD`, `PFCOUNT` | Flags, approximate unique counts
Geo | `GEOADD`, `GEOSEARCH` | Location lookups
Pub/Sub | `SUBSCRIBE ch`, `PUBLISH ch msg` | Fire-and-forget messages (not stored)

```
SET greeting "hello" EX 300
HSET user:1 name alice email alice@example.com
HGETALL user:1
RPUSH jobs '{"id":1}'
BRPOP jobs 5
ZADD scores 42 alice 17 bob
ZREVRANGE scores 0 9 WITHSCORES
```
Use a naming convention such as `app:object:id` and always set TTLs on cache keys.

---
## Persistence
MODE | WHAT | TRADE-OFF
---|---|---
RDB | Point-in-time snapshots, written to `dump.rdb` | Compact, fast restart, can lose the last few minutes
AOF | Logs every write, replayed on start (`appendonly yes`) | Less data loss (`appendfsync everysec` loses at most about 1 s), bigger files, slower restart
RDB + AOF | Both on. At startup Redis loads the AOF | Common choice for data you cannot lose
None | `save ""` and `appendonly no` | Pure cache

`redis.conf`:
```
# RDB: snapshot after 3600 s if >=1 change, 300 s if >=100, 60 s if >=10000
save 3600 1 300 100 60 10000
dbfilename dump.rdb
dir /data

# AOF
appendonly yes
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```
COMMAND | DESCRIPTION
---|---
`BGSAVE` | Start an RDB snapshot in the background
`LASTSAVE` | Unix time of the last successful save
`BGREWRITEAOF` | Compact the AOF in the background
`INFO persistence` | Status of RDB and AOF
`CONFIG SET appendonly yes` | Turn AOF on at runtime

Back up by copying `dump.rdb` (after `BGSAVE`) or the AOF directory (`appendonlydir/` in 7+) while Redis runs, or with `redis-cli --rdb`. To restore, stop Redis, put the file in `dir`, start. If AOF is enabled it takes precedence over `dump.rdb` on start, so move the old AOF away or restore the AOF itself. Keep copies off the host.

Memory and eviction:
```
maxmemory 512mb
maxmemory-policy allkeys-lru
```
POLICY | EVICTS
---|---
`noeviction` | Nothing. Writes fail when full (default)
`allkeys-lru` / `allkeys-lfu` | Any key, least recently or frequently used. Good for caches
`volatile-lru` / `volatile-ttl` | Only keys with a TTL
`allkeys-random` | Random

Run Redis with `vm.overcommit_memory=1` on the host so snapshots and rewrites (which fork) do not fail: `echo 'vm.overcommit_memory = 1' | sudo tee /etc/sysctl.d/99-redis.conf && sudo sysctl --system`. Disable Transparent Huge Pages if Redis warns about it.

---
## Security and ACLs
Defaults: bind to localhost only, protected mode on. Keep it that way, and always use a password or ACL when it is reachable by anything but localhost.

`redis.conf` basics:
```
bind 127.0.0.1 -::1
protected-mode yes
requirepass <LONG-RANDOM-PASSWORD>
rename-command FLUSHALL ""
```
(`rename-command` is deprecated: prefer ACLs.)

ACLs (Redis 6+):
COMMAND | DESCRIPTION
---|---
`ACL LIST` | All users and rules
`ACL WHOAMI` | Current user
`ACL SETUSER app on '>S3cretPassw0rd' '~app:*' '&*' +@read +@write -@dangerous` | Create user `app`: enabled, password, keys matching `app:*`, all pub/sub channels, read and write commands, no dangerous commands
`ACL SETUSER readonly on '>Pass' '~*' +@read` | Read-only user
`ACL SETUSER default off` | Disable the `default` user (after a replacement admin exists)
`ACL DELUSER app` | Delete a user
`ACL CAT` | Command categories
`ACL GETUSER app` | Show one user
`ACL LOG` | Recent denied attempts
`ACL SAVE` / `ACL LOAD` | Write / read the ACL file (`aclfile /etc/redis/users.acl`)

Rule syntax: `on|off`, `>password`, `~keypattern`, `&channelpattern`, `+command`, `-command`, `+@category`. The passwords above are placeholders: use your own and keep them out of shell history.

Use TLS for traffic across hosts (`tls-port`, `tls-cert-file`, `tls-key-file`, `tls-ca-cert-file`), or keep Redis on a private network or a WireGuard tunnel.

---
## Replication
A replica copies a primary asynchronously and serves reads.

On the replica (`redis.conf`) or at runtime:
```
replicaof <PRIMARY-HOST> 6379
masterauth <PRIMARY-PASSWORD>
masteruser <ACL-USER-IF-USED>
replica-read-only yes
```
COMMAND | DESCRIPTION
---|---
`REPLICAOF <HOST> 6379` | Make this server a replica now
`REPLICAOF NO ONE` | Promote a replica to primary
`INFO replication` | Role, connected replicas, offset, `master_link_status`
`ROLE` | Short role and offset view
`WAIT 1 100` | Block until 1 replica acknowledged the writes, or 100 ms pass
`CONFIG SET min-replicas-to-write 1` | Refuse writes if fewer than 1 replica is connected

Notes:
- Replication is asynchronous. A failover can lose the last writes.
- A new replica does a full sync: the primary forks, writes an RDB and sends it. Plan memory headroom.
- Automatic failover needs **Redis Sentinel** (three or more sentinels, `SENTINEL` config, clients that support it) or **Redis Cluster** for sharding. For a homelab a single instance with AOF is usually enough.
- Docker: give the replica `command: redis-server --replicaof redis 6379` on a shared network.

---
## Troubleshooting
SYMPTOM | CHECK
---|---
High memory | `INFO memory`, `redis-cli --bigkeys`, `MEMORY USAGE key`, add TTLs, set `maxmemory`
Slow commands | `SLOWLOG GET 10`, avoid `KEYS *`, big `HGETALL`/`SMEMBERS`, use `SCAN`/`UNLINK`
Latency spikes | `redis-cli --latency`, `LATENCY DOCTOR`, fork time from snapshots (`INFO stats` `latest_fork_usec`), swapping
`MISCONF Redis is configured to save RDB snapshots, but it's currently unable to persist` | Disk full or no write permission on `dir`. Check `df -h` and file ownership
`OOM command not allowed when used memory > 'maxmemory'` | Raise `maxmemory` or set an eviction policy
`NOAUTH Authentication required` | Pass the password (`-a`, `REDISCLI_AUTH`)
`DENIED Redis is running in protected mode` | It is listening on a non-loopback address without a password: set `requirepass`/ACL first
Keys vanish | TTLs, eviction policy, a `FLUSHALL`, or a non-persistent restart
Replica stuck syncing | `INFO replication`, primary logs, `repl-timeout`, `client-output-buffer-limit replica`

`redis-benchmark -q -n 100000` gives a quick throughput test (run it against a test instance).
