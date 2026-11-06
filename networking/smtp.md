# SMTP
Simple Mail Transfer Protocol moves email between servers and from clients to servers. Related: [Mail Server DNS Records Cheat-Sheet](dns-record-mailserver.md), [Generate a DKIM Keypair](create-dkim-keypair.md), [TLS (Transport Layer Security)](tls.md).

## Ports
PORT | USE
---|---
`25` | Server to server delivery (often blocked for clients by ISPs)
`587` | Mail submission with STARTTLS (preferred for clients)
`465` | Submission with implicit TLS
`2525` | Unofficial alternative submission port some providers offer

## Quick Tests
COMMAND | DESCRIPTION
---|---
`nc -zv smtp.example.com 587` | Is the port open?
`dig +short MX example.com` | Mail servers for a domain
`dig +short TXT example.com` | SPF record
`dig +short TXT _dmarc.example.com` | DMARC policy
`swaks --to <TO> --from <FROM> --server smtp.example.com:587 --tls --auth LOGIN --auth-user <USER>` | Send a test mail with `swaks`
`openssl s_client -starttls smtp -connect smtp.example.com:587` | Manual STARTTLS session

## Troubleshooting
### TLS

1. Prepare encoded strings for your mail username and password

```bash
echo -ne "mail@example.net" | base64
echo -ne "password" | base64
```

2. Connect to mail server

```bash
openssl s_client -starttls smtp -connect smtp.example.com:587
```
For port 465 use `openssl s_client -connect smtp.example.com:465`.

3. Send HELO

```smtp
EHLO example.com
```

4. Authenticate

```smtp
AUTH LOGIN
<your-encoded-username>
<your-encoded-password>
```

If that's successful the mail server should return `235 2.7.0 Authentication successful`.

5. Send a test message

```smtp
MAIL FROM:<from@example.com>
RCPT TO:<to@example.net>
DATA
Subject: test

Hello
.
QUIT
```

## Common Reply Codes
CODE | MEANING
---|---
`220` | Service ready
`235` | Authentication successful
`250` | OK
`354` | Start mail input, end with `.` on its own line
`421` | Service unavailable, try later
`450` / `451` | Temporary mailbox or local error (greylisting)
`535` | Authentication failed
`550` | Mailbox unavailable or rejected (policy, SPF, blocklist)
`554` | Transaction failed

## Check Mail Queue (Postfix)
COMMAND | DESCRIPTION
---|---
`postqueue -p` | Show the queue
`postqueue -f` | Flush the queue
`postsuper -d ALL deferred` | Delete deferred mail
`tail -f /var/log/mail.log` | Follow the mail log
