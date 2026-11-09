# Cloudflare TXT Records
TXT records hold free text in DNS. They carry SPF, DKIM and DMARC, domain ownership checks, ACME challenges and more. This sheet covers adding them in Cloudflare and the length and quoting rules. General record management is in [Cloudflare DNS Records](cloudflare-dns-records.md).

Documentation: [Cloudflare record types](https://developers.cloudflare.com/dns/manage-dns-records/reference/dns-record-types/) · [Record attributes](https://developers.cloudflare.com/dns/manage-dns-records/reference/record-attributes/)

> **Verification:** the Cloudflare limits and quoting behaviour were read on developers.cloudflare.com. The 255-character string rule and the SPF lookup limit are standard DNS and SPF behaviour not re-read here *(unverified)*.

## Common Uses
NAME | CONTENT | PURPOSE
---|---|---
`example.com` | `v=spf1 include:<PROVIDER> ~all` | SPF sender policy, see [Mail Server DNS Records](../../networking/dns-record-mailserver.md)
`<SELECTOR>._domainkey.example.com` | `v=DKIM1; k=rsa; p=<PUBLIC_KEY>` | DKIM key, see [Generate a DKIM Keypair](../../networking/create-dkim-keypair.md)
`_dmarc.example.com` | `v=DMARC1; p=none; rua=mailto:<ADDRESS>` | DMARC, see [Cloudflare DMARC](cloudflare-dmarc.md)
`_acme-challenge.example.com` | token from your ACME client | DNS-01 certificates, see [Cloudflare](cloudflare.md#certificates-with-dns-01)
`example.com` | provider-supplied token | Domain ownership verification

## Add in Cloudflare
**DNS > Records > Add record**, type `TXT`, enter the name and content. Unquoted content gets quotes added automatically. Over the API use `"type":"TXT"` and `"content"` as in [Cloudflare DNS Records](cloudflare-dns-records.md#api).

## Length and Quoting
RULE | VALUE
---|---
One string | 255 characters in the DNS wire format. Longer values are split into several strings that resolvers join
Cloudflare API | Strings over 255 bytes are split automatically
Cloudflare limits | 4,096 bytes per record, 8,192 characters per name and type
Proxying | TXT records cannot be proxied

Long DKIM keys are the usual case. Paste the whole value and let Cloudflare split it. In a BIND-style file, write the strings quoted and side by side: `"v=DKIM1; k=rsa; p=AAAA" "BBBB"`.

SPF allows at most 10 DNS lookups (`include`, `a`, `mx` and similar). Flatten or trim an SPF record that goes over.

## Check
COMMAND | DESCRIPTION
---|---
`dig TXT example.com +short` | List TXT records
`dig TXT _dmarc.example.com +short` | DMARC record
`dig TXT <SELECTOR>._domainkey.example.com +short` | DKIM key
`nslookup -type=TXT example.com` | Same, without dig

## See Also
- [Cloudflare DNS Records](cloudflare-dns-records.md)
- [Cloudflare DMARC](cloudflare-dmarc.md)
- [DNS Record Types](../../networking/dns-record-types.md)
- [Mail Server DNS Records](../../networking/dns-record-mailserver.md)
- [dig](../../networking/dig.md)
