# msmtp
msmtp is a small SMTP client that sends mail from the command line and scripts through an existing mail account. Use it so cron, backup scripts and tools such as `smartd` can email you without running a full mail server. For push-style alerts see [Notification Services](../homelab/notification-services.md).

Documentation: [msmtp manual](https://marlam.de/msmtp/msmtp.html), [example config](https://marlam.de/msmtp/msmtprc.txt)

## Install
```bash
sudo apt install msmtp msmtp-mta
```

`msmtp-mta` makes `sendmail` point at msmtp, so programs that call `sendmail` just work (package names are the Debian and Ubuntu ones, not checked against the manual).

## Config
`~/.msmtprc`, or `/etc/msmtprc` for system-wide use, or `$XDG_CONFIG_HOME/msmtp/config`. Lines starting with `#` are comments, and an account can inherit another with `account NAME : OTHER`.

```text
defaults
port 587
tls on
tls_starttls on

account relay
host smtp.example.com
from alerts@example.com
auth on
user alerts@example.com
passwordeval "cat /etc/msmtp-password"

account default : relay
```

DIRECTIVE | DESCRIPTION
---|---
`host`, `port` | Server. The default port is 25
`tls on` | Use TLS
`tls_starttls on` | STARTTLS (the default). Use `off` for implicit TLS, usually port 465
`tls_trust_file` | CA bundle, default `system`
`auth on` | Authenticate (or name a method)
`user` | Username
`passwordeval <COMMAND>` | Run a command and use its output as the password
`password` | Plain text password. Avoid it
`from` | Envelope sender
`allow_from_override off` | Stop callers overriding the sender with `-f`

The `passwordeval` command must not read standard input, so append `< /dev/null` if in doubt. Keep the config and any password file readable only by you (`chmod 600 ~/.msmtprc`). The manual says to restrict a plain-text password file but does not give a numeric mode.

## Send
COMMAND | DESCRIPTION
---|---
`printf 'Subject: Backup\n\nDone.\n' \| msmtp -a relay -t user@example.com` | Send a message, `-t` also reads `To`, `Cc` and `Bcc` from the headers
`echo "Done." \| msmtp -a relay user@example.com` | Send a body with no headers (a bare message)
`msmtp -a <ACCOUNT> -f <ADDRESS> ...` | Choose the account and envelope sender
`msmtp -P -a <ACCOUNT>` | Pretend: show the config that would be used, passwords as `*`
`msmtp -v -a <ACCOUNT> ...` | Verbose, may print the password to the terminal
`msmtp --serverinfo -a <ACCOUNT>` | Query the server's capabilities
`msmtp --configure you@example.com` | Suggest settings for an address

Exit codes follow `sysexits.h`. The `mail` command needs a default account in the config because it does not accept extra options (from a summary of the manual).

## Gotchas
- Some providers reject mail whose `From` header does not match the authenticated account. `set_from_header on` changes the header.
- Use an app password or a dedicated sending account where the provider offers one.
- A failed send is easy to miss, so check the exit code in scripts or pair with [Healthchecks](../apps/healthchecks.md).

## See Also
- [Notification Services](../homelab/notification-services.md)
- [Healthchecks](../apps/healthchecks.md)
- [smartctl](../linux/smartctl.md)
- [SMTP](../networking/smtp.md)
