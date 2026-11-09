# Cloudflare DMARC
DMARC tells receivers what to do with mail that fails SPF and DKIM alignment, and where to send reports. This sheet covers the record, a safe rollout, and Cloudflare's DMARC Management feature. The basic record is also in [Mail Server DNS Records](../../networking/dns-record-mailserver.md), and TXT handling in [Cloudflare TXT Records](cloudflare-txt-records.md).

Documentation: [Cloudflare DMARC Management](https://developers.cloudflare.com/dmarc-management/enable) · [RFC 9989 (DMARC)](https://www.rfc-editor.org/rfc/rfc9989) · [RFC 9990 (aggregate reporting)](https://www.rfc-editor.org/rfc/rfc9990)

> **Verification:** the tag list follows RFC 9989, which the research read directly. It obsoletes RFC 7489. The old `pct`, `ri` and `rf` tags are removed in it, and I did not re-read RFC 7489 for their old defaults. Cloudflare's own `rua` address was not confirmed *(unverified)*.

## The Record
A TXT record on `_dmarc.<DOMAIN>`:

```text
_dmarc.example.com  TXT  "v=DMARC1; p=none; rua=mailto:dmarc@example.com"
```

TAG | MEANING | DEFAULT
---|---|---
`v` | `DMARC1`. Must be first | required
`p` | Policy: `none`, `quarantine` or `reject` | `none` if absent
`sp` | Policy for subdomains | falls back to `p`
`np` | Policy for non-existent subdomains | falls back to `sp`, then `p`
`rua` | Where aggregate reports go (`mailto:`) | none
`ruf` | Where failure reports go | none
`adkim` / `aspf` | DKIM and SPF alignment: `r` relaxed, `s` strict | `r`
`fo` | Failure report options | `0`
`psd` | Public suffix domain marker: `y`, `n` or `u` | `u`
`t` | Testing mode: `y` or `n` | `n`

Removed in RFC 9989: `pct`, `ri` and `rf`. A Tree Walk (at most 8 queries) replaces the Public Suffix List lookup. Some receivers still use RFC 7489 behaviour, so older tags may still be honoured.

## Rollout
1. Start with `p=none` and a `rua` address. Read the reports for a few weeks.
2. Fix any legitimate sender that fails SPF or DKIM alignment.
3. Move to `p=quarantine`, then `p=reject` once reports are clean.

Make sure SPF and DKIM already pass for every service that sends as your domain first. See [Generate a DKIM Keypair](../../networking/create-dkim-keypair.md).

## Reports to Another Domain
If `rua` points at an address on a different domain, that domain must authorise it with a TXT record at `<POLICY_DOMAIN>._report._dmarc.<DEST_DOMAIN>` containing `v=DMARC1`. A wildcard `*._report._dmarc` record is allowed (RFC 9990).

## Cloudflare DMARC Management
Enable it under **Email > DMARC Management > Enable**. It works on apex domains only, not subdomain setups, and adds an extra `rua` address pointing at Cloudflare so it can build reports for you. The exact address was not confirmed. Check the record it creates in the dashboard, or call `GET /zones/<ZONE_ID>/email/auth/dmarc-reports`.

## Add the Record Manually
**DNS > Records > Add record**, type `TXT`, name `_dmarc`, content as above. See [Cloudflare DNS Records](cloudflare-dns-records.md#api) for the API.

## Check
COMMAND | DESCRIPTION
---|---
`dig TXT _dmarc.example.com +short` | Show the policy
`dig TXT example.com._report._dmarc.<DEST_DOMAIN> +short` | Check external report authorisation

## See Also
- [Cloudflare TXT Records](cloudflare-txt-records.md)
- [Cloudflare DNS Records](cloudflare-dns-records.md)
- [Mail Server DNS Records](../../networking/dns-record-mailserver.md)
- [Generate a DKIM Keypair](../../networking/create-dkim-keypair.md)
- [SMTP](../../networking/smtp.md)
