# Mail Server DNS Records Cheat-Sheet
If you want to run a mail server on the public internet, you need to set up your DNS records correctly. While some DNS Records ([DNS Record Types](dns-record-types.md)) are necessary to send and receive emails, others are recommended to build a good reputation.

## Required Mail Server DNS Records
### A Record
DNS A Record that will resolve to the public IP address of your mail server. This is also needed when your web server has a different IP address than your mail server.

**Recommended Settings Example:**

Type | Host | Points to | TTL
---|---|---|---
`A`|`mail`|`your-mail-servers-ipv4`|`1 hour`

### MX Record
The MX record is important when you want to receive emails. This tells everyone which IP address to contact.

The MX target must be a hostname (the A record above), never an IP address or a CNAME. If you have multiple Mail Servers that need to be load-balanced use the same **priority**. Lower numbers are prioritized. Higher numbers can be used as backup servers.

**Recommended Settings:**

Type | Host | Points to | Priority | TTL
---|---|---|---|---
`MX`|`@`|`mail.your-domain`|`10`|`1 hour`

### RDNS or PTR Record
The reverse DNS record or also called PTR (Pointer Resource Record) is important when you want to send mails. Almost all mail servers check the RDNS record to perform simple anti-spam checks. RDNS is just like a DNS query, just backward.

>Your RDNS record is not configured on your DNS server, instead, it’s configured on your hosting provider where you got your public IP address from.

## (Optional but recommended) DNS Records

### SPF Record
The SPF (Sender Policy Framework) is a TXT record on your DNS server that specifies which hosts are allowed to send mails for a given domain. When a mail server receives a mail that seems to come from your domain it can check if it’s a valid message. Some mail servers reject mails if they can’t validate that the message comes from an authorized mail server.

Use `include:_spf.provider.com` for a third-party sender, and use `~all` (soft fail) while testing. Only one SPF record is allowed per domain, with at most 10 DNS lookups.

**Recommended Settings:**

Type | Host | TXT Value | TTL
---|---|---|---
`TXT`|`@`|`v=spf1 ip4:your-mail-servers-ipv4 -all`|`1 hour`

### DKIM Record
DKIM (Domain Keys Identified Mail) allows the receiving mail server to check that an email was indeed sent by the owner of that domain. The sending mail server adds a digital signature to every mail that is sent. This signature is added as a header and secured with encryption. These signatures are not visible to the end-user.

>If you want to add DKIM to your mail server you first need to create a private and a public keypair ([Generate a DKIM Keypair](create-dkim-keypair.md))
 
`dkim` is the selector name, so use whatever selector your mail server signs with. Use a 2048-bit key. Long keys may need splitting into several quoted strings in some DNS panels.

**Recommended Settings:**

Type | Host | TXT Value | TTL
---|---|---|---
`TXT`|`dkim._domainkey`|`v=DKIM1;k=rsa;p=public-dkim-key`|`1 hour`

### DMARC Record
DMARC (Domain-based Message Authentication, Reporting, and Conformance) extends your existing SPF and DKIM records. It makes sure that the sender's emails are protected by SPF and DKIM and tells the receiving mail server what to do if these checks fail.
 
Start with `p=none` to collect reports only, then move to `quarantine` and `reject` once legitimate mail passes. `rua` is where aggregate reports are sent. Large mailbox providers now expect SPF, DKIM and DMARC for bulk senders (check each provider's current rules).

**Recommended Settings:**

Type | Host | TXT Value | TTL
---|---|---|---
`TXT`|`_dmarc`|`v=DMARC1;p=quarantine;rua=mailto:dmarc@your-domain`|`1 hour`

## (Optional) DNS Records
### Autoconfiguration DNS Records
If you’re using mail clients like Outlook, Thunderbird on your Computer, or Mobile devices they offer the ability to do an “autoconfiguration” also called “Autodiscover”. That means you just need to enter your email address and password and the mail client tries to resolve the mail server IP addresses, used ports, and encryption settings for IMAP and SMTP. You can achieve this by adding SRV DNS records that are defined in the [RFC 6186 standard](https://tools.ietf.org/html/rfc6186) and some specific records that are used in Outlook clients.

### MTA-STS and TLS-RPT
MTA-STS tells sending servers to require TLS to your server. It needs a TXT record `_mta-sts` (`v=STSv1; id=2026110601`) plus a policy file served over HTTPS at `https://mta-sts.your-domain/.well-known/mta-sts.txt`. TLS-RPT (`_smtp._tls`, `v=TLSRPTv1; rua=mailto:tls@your-domain`) requests failure reports. See [SMTP](smtp.md) and [TLS (Transport Layer Security)](tls.md).

## Check Your Records
COMMAND | DESCRIPTION
---|---
`dig MX your-domain +short` | MX records
`dig TXT your-domain +short` | SPF
`dig TXT dkim._domainkey.your-domain +short` | DKIM
`dig TXT _dmarc.your-domain +short` | DMARC
`dig -x <your-mail-servers-ipv4> +short` | Reverse DNS should return `mail.your-domain`
`openssl s_client -starttls smtp -connect mail.your-domain:25` | Check STARTTLS and the certificate ([OpenSSL](../tools/openssl.md))

Also check that the PTR name matches the server's HELO name, and that the IP is not on a blocklist. Send a test message to a checker such as mail-tester.com and read the full headers (`Authentication-Results`).
