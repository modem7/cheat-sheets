# Generate a DKIM Keypair
DKIM signs outgoing mail with a private key. The public key is published in DNS as a TXT record so receivers can verify it. We use [OpenSSL](../tools/openssl.md) to generate the keypair. See [Mail Server DNS Records Cheat-Sheet](dns-record-mailserver.md) for the other mail records and [DNS Record Types](dns-record-types.md) for TXT.

## Generate
Private key:

`openssl genrsa -out dkim_private.pem 2048`

Public key, as a single base64 line ready for the DNS record:

`openssl rsa -in dkim_private.pem -pubout -outform der 2>/dev/null | openssl base64 -A`

Keep the private key secret (`chmod 600 dkim_private.pem`) and give it only to your mail server.

## Publish the DNS Record
Create a TXT record at `<selector>._domainkey.<yourdomain>`:

```
selector1._domainkey.example.com.  IN TXT  "v=DKIM1; k=rsa; p=<PUBLIC-KEY-BASE64>"
```
- The selector (`selector1`) is any name you choose. Use a new one (for example a date) when you rotate keys.
- 2048-bit keys exceed 255 characters, so some DNS providers need the value split into several quoted strings.

## Verify
COMMAND | DESCRIPTION
---|---
`dig +short TXT selector1._domainkey.example.com` | Check the record is published
`opendkim-testkey -d example.com -s selector1 -vvv` | Test key and DNS match (`opendkim-tools`)

Then send a test mail to a mailbox that shows authentication headers and look for `dkim=pass`.

## Good Practice
- Rotate keys yearly.
- Combine with SPF and DMARC (`_dmarc.example.com TXT "v=DMARC1; p=none; rua=mailto:dmarc@example.com"`, then tighten to `quarantine` or `reject`).
