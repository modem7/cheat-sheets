# Cloudflare DNS Records
Create, import and export DNS records in Cloudflare, with the API fields, TTL and proxy rules that catch people out. Record types are explained in [DNS Record Types](../../networking/dns-record-types.md). Specific records: [SSHFP](cloudflare-sshfp-records.md), [TXT](cloudflare-txt-records.md) and [DMARC](cloudflare-dmarc.md). Account setup and tokens are in [Cloudflare](cloudflare.md).

Documentation: [Manage DNS records](https://developers.cloudflare.com/dns/manage-dns-records/) · [Record attributes](https://developers.cloudflare.com/dns/manage-dns-records/reference/record-attributes/) · [TTL](https://developers.cloudflare.com/dns/manage-dns-records/reference/ttl/) · [Import and export](https://developers.cloudflare.com/dns/manage-dns-records/how-to/import-and-export/)

> **Verification:** read on developers.cloudflare.com, not run against a live zone. The `curl` example below follows the documented endpoint and fields but was not confirmed *(unverified)*.

## Dashboard
- Add a record: **DNS > Records > Add record**.
- Import or export a zone file: **DNS > Records > Import and Export**.

## API
`POST /zones/<ZONE_ID>/dns_records` creates a record. Use an [API token](cloudflare.md#api-tokens) with DNS edit permission on that zone.

```bash
curl -sS -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"type":"A","name":"app.example.com","content":"192.0.2.10","ttl":1,"proxied":false,"comment":"app server"}'
```

FIELD | NOTE
---|---
`type` | Record type
`name` | Hostname, or `@` for the apex in the dashboard
`content` | The value (generated from `data` for structured types such as SSHFP)
`ttl` | `1` means automatic in the API. Otherwise 60 to 86400 seconds (30 on Enterprise)
`proxied` | Only A, AAAA and CNAME records can be proxied
`comment` | 100 characters on Free, 500 on paid plans
`tags` | Not on Free, maximum 20 per record

The TTL docs page says Auto is 300 seconds and does not offer `1` in the dashboard. The API reference says `1` is automatic, so use that for API calls.

## Proxied Records
Only A, AAAA and CNAME can be proxied (orange cloud). TXT, MX, SSHFP and other types are always DNS-only. See [Cloudflare](cloudflare.md#proxied-records).

## Import and Export
ACTION | ENDPOINT
---|---
Import a BIND zone file | `POST /zones/<ZONE_ID>/dns_records/import`
Export the zone | `GET /zones/<ZONE_ID>/dns_records/export`

Limits: 256 KiB per import and 3 requests per minute. `$INCLUDE` is not supported.

## Limits
LIMIT | VALUE
---|---
Record count | Varies by plan (about 1,000 or 200 on Free depending on when the zone was created, 3,500 on Pro and Business). Source was a search snippet *(unverified)*, check the [DNS FAQ](https://developers.cloudflare.com/dns/faq/)
TXT content | 4,096 bytes per record

## DNSSEC
Enable it under the zone's **DNS > Settings > Enable DNSSEC**, then add the DS record at your registrar (algorithm 13). It is automatic for Cloudflare Registrar, `.ch` and `.cz`. DNSSEC is what makes [SSHFP](cloudflare-sshfp-records.md) trustworthy. Background: [DNSSEC](../../networking/dnssec.md).

## Check a Record
COMMAND | DESCRIPTION
---|---
`dig app.example.com A +short` | Query your resolver
`dig @<NAME>.ns.cloudflare.com app.example.com A +short` | Query Cloudflare's nameserver directly (name shown in the dashboard)

More in [dig](../../networking/dig.md).

## See Also
- [Cloudflare](cloudflare.md)
- [DNS Record Types](../../networking/dns-record-types.md)
- [DNSSEC](../../networking/dnssec.md)
- [dig](../../networking/dig.md)
- [Cloudflare SSHFP Records](cloudflare-sshfp-records.md)
- [Cloudflare TXT Records](cloudflare-txt-records.md)
- [Cloudflare DMARC](cloudflare-dmarc.md)
