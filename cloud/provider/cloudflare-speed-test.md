# Cloudflare Speed Test
Measure your connection against Cloudflare's network from the browser or the command line. Useful for checking what your link really delivers before blaming a [Cloudflare Tunnel](../../recipes/expose-service-cloudflare-tunnel.md) or a [reverse proxy](../../homelab/reverse-proxy-patterns.md). Account-level Cloudflare topics are in [Cloudflare](cloudflare.md).

Documentation: [@cloudflare/speedtest](https://github.com/cloudflare/speedtest) · [worker-speedtest-template](https://github.com/cloudflare/worker-speedtest-template)

> **Verification:** the `curl` commands below were run once and worked. The `__down` and `__up` endpoints are **community-documented only**: Cloudflare publishes no official curl guide for them, and they may change. For a single transfer they measure one connection, so use [iperf3](../../tools/iperf3.md) for a LAN or server-to-server test.

## Browser
Open [speed.cloudflare.com](https://speed.cloudflare.com). It reports download, upload, latency, jitter and the Cloudflare data centre you reached.

## curl
COMMAND | DESCRIPTION
---|---
`curl -sS -o /dev/null -w '%{speed_download}\n' 'https://speed.cloudflare.com/__down?bytes=100000000'` | Download speed in **bytes per second** (here a 100 MB transfer)
`head -c 5000000 /dev/zero \| curl -sS -o /dev/null -w '%{speed_upload}\n' -X POST --data-binary @- https://speed.cloudflare.com/__up` | Upload speed in bytes per second (5 MB of zeros)
`curl https://www.cloudflare.com/cdn-cgi/trace` | `key=value` lines about your connection: IP, data centre (`colo`), country (`loc`), HTTP and TLS versions, and WARP and gateway state. No official docs page was found

Multiply bytes per second by 8 for bits per second. A larger `bytes` value gives steadier results on a fast link.

## Run Your Own Test Endpoint
`worker-speedtest-template` is a Cloudflare Worker that serves `GET /down?bytes=N` and `POST /up` on your own domain, so you can test against your own Workers deployment. See [Cloudflare Pages and Workers](cloudflare-pages-workers.md) for deploying one.

## JavaScript Library
`npm install @cloudflare/speedtest` provides the engine behind speed.cloudflare.com. Its defaults use the public `__down` and `__up` endpoints, which the README marks as deprecated in favour of `measurementTargets`. The README does not say third-party use of the public host is supported, so point `measurementTargets` at your own Worker for anything automated.

## See Also
- [Cloudflare](cloudflare.md)
- [iperf3](../../tools/iperf3.md)
- [Cloudflare Tunnel Recipe](../../recipes/expose-service-cloudflare-tunnel.md)
- [Reverse Proxy Patterns](../../homelab/reverse-proxy-patterns.md)
