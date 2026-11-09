# SSH Hardening
Practical `sshd_config` settings to lock down an OpenSSH server: key-only login, no root password login, limited users and sane timeouts. Client usage is in [OpenSSH](../tools/openssh.md). Pair this with [fail2ban](fail2ban.md) or [CrowdSec](crowdsec.md), and run [Lynis](lynis-and-auditd.md) to check the result.

Documentation: [sshd_config](https://man.openbsd.org/sshd_config), [sshd](https://man.openbsd.org/sshd.8), [ssh-keygen](https://man.openbsd.org/ssh-keygen.1)

## Test Before You Reload
Keep an existing SSH session open while you change anything, and test from a second one.

COMMAND | DESCRIPTION
---|---
`sudo sshd -t` | Check the config file and host keys are valid
`sudo sshd -T` | Print the **effective** configuration after all drop-ins and defaults
`sudo sshd -T \| grep -i passwordauthentication` | Confirm one setting
`sudo sshd -T -C user=<USER>,host=<HOST>,addr=<IP>` | Test the result for a given connection (Match blocks)
`sudo systemctl reload ssh` | Apply changes (unit is `sshd` on RHEL and Fedora, `ssh` on Debian and Ubuntu)

## First Match Wins
In `sshd_config` **the first value obtained for a keyword is used**. This is the opposite of chrony. `Include` is processed in lexical order, and inside a `Match` block only the first instance applies. `AllowUsers` and `AllowGroups` are the exception, as they append. So a drop-in that sorts earlier overrides a later one, and it also beats your edit if it comes before it. Where the main file begins with `Include /etc/ssh/sshd_config.d/*.conf` (common on Debian and Ubuntu, not checked in this pass), put your hardening in `/etc/ssh/sshd_config.d/00-hardening.conf` so it sorts first, and check with `sshd -T`. Cloud images sometimes ship a drop-in such as `50-cloud-init.conf` that sets `PasswordAuthentication yes` (a common gotcha, not verified here).

## Recommended Settings
```text
# /etc/ssh/sshd_config.d/00-hardening.conf
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
PermitRootLogin prohibit-password
MaxAuthTries 3
LoginGraceTime 30
AllowUsers alice bob
X11Forwarding no
ClientAliveInterval 300
ClientAliveCountMax 2
```

SETTING | DEFAULT | NOTE
---|---|---
`PasswordAuthentication` | `yes` | Set `no` once keys work
`KbdInteractiveAuthentication` | `yes` | Also set `no`, or it can still allow passwords. `ChallengeResponseAuthentication` is the old alias
`PubkeyAuthentication` | `yes` | Key login
`PermitRootLogin` | `prohibit-password` | `no` blocks root completely. `prohibit-password` allows keys only
`MaxAuthTries` | `6` | Failed attempts per connection
`LoginGraceTime` | `120` seconds | Time to authenticate. `0` means no limit
`AllowUsers` / `AllowGroups` | all | Limit who can log in. Accepts `USER@HOST` with CIDR
`X11Forwarding` | `no` | Off by default
`AllowTcpForwarding` | `yes` | Set `no` if you do not need tunnels (see [OpenSSH](../tools/openssh.md))
`ClientAliveInterval` | `0` (off) | With a count of 3, an interval of 15 drops a dead client in about 45 seconds
`AuthenticationMethods` | any | e.g. `publickey,keyboard-interactive` to require a key and a second factor

Defaults can differ on distribution builds, so confirm with `sshd -T`. Do not disable password login before you have confirmed key login works from a second session.

## Keys
COMMAND | DESCRIPTION
---|---
`ssh-keygen -t ed25519 -C "<COMMENT>"` | Create an Ed25519 key (the default type)
`ssh-keygen -t ed25519-sk` | Hardware-backed FIDO2 key (needs a security key)
`ssh-copy-id -i ~/.ssh/id_ed25519.pub <USER>@<HOST>` | Install a public key on a server
`ssh-keygen -lf <KEY>.pub` | Show a key's fingerprint

`ssh-copy-id` is not part of the OpenBSD pages checked here.

## Certificates
Sign user keys with a CA so servers trust the CA instead of each key:

```bash
ssh-keygen -s /path/to/ca_key -I KEY_ID -n USER -V +52w /path/to/user_key.pub
```

That writes `user_key-cert.pub`. On the server set `TrustedUserCAKeys /etc/ssh/ca.pub`. A certificate with no principal list is not permitted. Add `-h` to sign a host key instead.

## Changing the Port
`Port 2222` moves the listener, which only reduces log noise and is not security. On recent Ubuntu, sshd may be started by socket activation, so a `Port` change may also need `ssh.socket` adjusting (not verified here, check `systemctl status ssh.socket`). Open the new port in the firewall before reloading ([ufw](../linux/ufw.md), [nftables](../linux/nftables.md)).

## Moduli
`/etc/ssh/moduli` holds the Diffie-Hellman groups. Regenerating is optional (`ssh-keygen -M generate` then `-M screen`), and the file should keep moduli of several bit lengths.

## See Also
- [OpenSSH](../tools/openssh.md)
- [fail2ban](fail2ban.md)
- [CrowdSec](crowdsec.md)
- [Lynis and auditd](lynis-and-auditd.md)
