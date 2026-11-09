# Cloudflare SSHFP Records
SSHFP records publish your SSH host key fingerprints in DNS so a client can check a server's key without a manual trust-on-first-use prompt. Use them with DNSSEC, because an unsigned answer can be forged. General record management is in [Cloudflare DNS Records](cloudflare-dns-records.md), and client use is in [OpenSSH](../../tools/openssh.md).

Documentation: [Cloudflare record types](https://developers.cloudflare.com/dns/manage-dns-records/reference/dns-record-types/) · [ssh-keygen](https://man.openbsd.org/ssh-keygen) · [ssh_config](https://man.openbsd.org/ssh_config) · [RFC 8709](https://www.rfc-editor.org/rfc/rfc8709)

> **Verification:** `ssh-keygen -r`, `ssh-keyscan -D` and `VerifyHostKeyDNS` were checked against the OpenBSD manual pages. Cloudflare's SSHFP dashboard fields and a worked API call were not confirmed *(unverified)*. The algorithm and fingerprint numbers for 1 to 4 and types 1 to 2 are from RFC 4255, 6594 and 7479 from memory. Only Ed448 (6, RFC 8709) was re-read.

## Record Format
`<NAME> SSHFP <ALGORITHM> <FP_TYPE> <FINGERPRINT>`

ALGORITHM | KEY TYPE
---|---
`1` | RSA
`2` | DSA
`3` | ECDSA
`4` | Ed25519
`6` | Ed448

FP TYPE | HASH
---|---
`1` | SHA-1
`2` | SHA-256

Use type `2` (SHA-256). Ed25519 with SHA-256 is `4 2 <FINGERPRINT>`.

## Generate the Records
COMMAND | DESCRIPTION
---|---
`ssh-keygen -r <HOSTNAME>` | Print SSHFP lines for the host keys on this machine
`ssh-keygen -r <HOSTNAME> -f /etc/ssh/ssh_host_ed25519_key.pub` | For one key file
`ssh-keygen -g -r <HOSTNAME>` | Generic record format
`ssh-keyscan -D <HOSTNAME>` | **Read** SSHFP records from DNS and print the keys. It does not generate them

## Add One in Cloudflare
In the dashboard choose **DNS > Records > Add record**, type `SSHFP`, and enter the algorithm, type and fingerprint from `ssh-keygen -r`. Over the API the `data` object takes `algorithm`, `type` and `fingerprint`, and `content` is generated from it:

```json
{
  "type": "SSHFP",
  "name": "server.example.com",
  "data": { "algorithm": 4, "type": 2, "fingerprint": "<FINGERPRINT_HEX>" },
  "ttl": 1
}
```

SSHFP records cannot be proxied. Post it as in [Cloudflare DNS Records](cloudflare-dns-records.md#api). Add one record per host key type.

## Client Side
Set `VerifyHostKeyDNS` in `~/.ssh/config` or on the command line.

COMMAND | DESCRIPTION
---|---
`ssh -o VerifyHostKeyDNS=yes <HOST>` | Trust a matching SSHFP record
`ssh -o VerifyHostKeyDNS=ask <HOST>` | Ask before trusting it
`dig SSHFP <HOST> +short` | Check the record exists
`dig SSHFP <HOST> +dnssec` | Check the answer is signed (look for the `ad` flag from a validating resolver)

`VerifyHostKeyDNS` defaults to `no`. The man page does not mention DNSSEC, only a "secure" fingerprint, so the requirement for a signed zone is inferred. Enable DNSSEC as in [Cloudflare DNS Records](cloudflare-dns-records.md#dnssec), and use a validating resolver.

## Tips
- Re-publish SSHFP records after you regenerate host keys.
- Keep the records in step with [SSH Hardening](../../security/ssh-hardening.md) settings such as which host key types you serve.

## See Also
- [Cloudflare DNS Records](cloudflare-dns-records.md)
- [DNSSEC](../../networking/dnssec.md)
- [OpenSSH](../../tools/openssh.md)
- [SSH Hardening](../../security/ssh-hardening.md)
- [DNS Record Types](../../networking/dns-record-types.md)
