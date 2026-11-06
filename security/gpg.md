# GPG
GnuPG implements OpenPGP: public-key encryption, signatures and symmetric encryption for files, email, Git commits and package repositories. For SSH keys see [OpenSSH Cheat-Sheet](../tools/openssh.md); for X.509 certificates see [OpenSSL](../tools/openssl.md). For encrypting secrets in a repo, [SOPS and age](sops-age.md) is usually simpler.

Documentation: [GnuPG Manual](https://www.gnupg.org/documentation/manuals/gnupg/)

## Keys
COMMAND | DESCRIPTION
---|---
`gpg --full-generate-key` | Interactive key generation
`gpg --quick-generate-key "Name <mail@example.com>" ed25519 cert never` | Create a certify-only primary key
`gpg --quick-add-key <FPR> ed25519 sign 2y` | Add a signing subkey (expires in 2 years)
`gpg --quick-add-key <FPR> cv25519 encr 2y` | Add an encryption subkey
`gpg --quick-set-expire <FPR> 2y` | Change the primary key expiry
`gpg --list-keys --keyid-format long` | List public keys
`gpg --list-secret-keys --keyid-format long` | List secret keys (`sec#` means primary key is offline)
`gpg --fingerprint <KEYID>` | Show the fingerprint
`gpg --edit-key <KEYID>` | Interactive menu (`trust`, `adduid`, `expire`, `addkey`, `save`)
`gpg --delete-secret-and-public-key <FPR>` | Remove a key pair
`gpg --import key.asc` | Import a key
`gpg --keyserver keys.openpgp.org --search-keys <MAIL>` | Search a keyserver
`gpg --keyserver keys.openpgp.org --send-keys <FPR>` | Upload a public key

keys.openpgp.org only publishes a user ID after the owner verifies the email address. Never upload a secret key.

A good layout: an offline certify-only primary key, plus separate subkeys for signing, encryption and authentication. A stolen subkey can be revoked without losing your identity.

## Encrypt and Decrypt
COMMAND | DESCRIPTION
---|---
`gpg -e -r <MAIL> file` | Encrypt to a recipient (writes `file.gpg`)
`gpg -e -a -r <MAIL> file` | ASCII-armoured output (`file.asc`)
`gpg -c file` | Symmetric encryption with a passphrase
`gpg -c --cipher-algo AES256 file` | Choose the cipher
`gpg -d file.gpg > file` | Decrypt to stdout
`gpg -o file -d file.gpg` | Decrypt to a file
`gpg -e -r <A> -r <B> file` | Encrypt to several recipients

## Sign and Verify
COMMAND | DESCRIPTION
---|---
`gpg --detach-sign -a file` | Detached ASCII signature (`file.asc`)
`gpg --verify file.asc file` | Verify a detached signature
`gpg --clearsign file` | Cleartext signature (`file.asc`)
`gpg -s file` | Signed (not encrypted) binary wrapper
`gpg --verify file.sig` | Verify an embedded signature
`gpg -u <KEYID> --detach-sign file` | Sign with a specific key

## Backup and Restore
COMMAND | DESCRIPTION
---|---
`gpg --export -a <FPR> > public.asc` | Export the public key
`gpg --export-secret-keys -a <FPR> > secret.asc` | Export the primary and all secret subkeys
`gpg --export-secret-subkeys -a <FPR> > subkeys.asc` | Export subkeys only (primary key stays out)
`gpg --export-ownertrust > trust.txt` | Export trust settings
`gpg --import-ownertrust trust.txt` | Restore trust settings
`gpg --gen-revoke -a -o revoke.asc <FPR>` | Pre-generate a revocation certificate
`gpg --import revoke.asc` | Apply a revocation certificate

Generate the revocation certificate straight after creating the key and store it with the backup. Keep exported secret keys on encrypted offline media (and a copy in [Bitwarden Cheat-Sheet](../tools/bitwarden.md)); delete them from the machine afterwards.

Moving subkeys to a daily-use machine while the primary stays offline:
```bash
gpg --export-secret-subkeys -a <FPR> > subkeys.asc
# on the daily machine
gpg --import subkeys.asc
gpg --list-secret-keys          # primary shows as sec# (stub)
```

## Git Commit Signing
```bash
git config --global user.signingkey <KEYID>
git config --global commit.gpgsign true
git config --global tag.gpgsign true
gpg --armor --export <KEYID>     # paste into GitHub > Settings > SSH and GPG keys
```
Git can also sign with an SSH key (`gpg.format ssh`); see [Git](../tools/git.md).

## Agent and Passphrase
COMMAND | DESCRIPTION
---|---
`export GPG_TTY=$(tty)` | Needed in shells so pinentry can prompt (add to `~/.bashrc` or `~/.zshrc`)
`gpgconf --kill gpg-agent` | Restart the agent (fixes most stuck states)
`gpgconf --list-dirs` | Show agent socket and home paths
`gpg --pinentry-mode loopback -d file.gpg` | Prompt on the terminal instead of a GUI
`gpg --batch --pinentry-mode loopback --passphrase-file <FILE> -d file.gpg` | Non-interactive decrypt (protect the file)

`~/.gnupg/gpg-agent.conf` example:
```text
default-cache-ttl 600
max-cache-ttl 7200
pinentry-program /usr/bin/pinentry-curses
```

## Troubleshooting
SYMPTOM | FIX
---|---
`gpg: signing failed: Inappropriate ioctl for device` | `export GPG_TTY=$(tty)`
`gpg: decryption failed: No secret key` | Key not imported on this machine, or only the subkey stub exists
`gpg: WARNING: This key is not certified with a trusted signature` | Cosmetic. Run `gpg --edit-key <ID>`, then `trust`, if you've verified the fingerprint
`gpg: signing failed: No secret key` after moving to subkeys | Ensure a signing-capable subkey exists and isn't expired
Key expired | `gpg --edit-key <ID>`, `expire`, `key 1`, `expire`, `save` — then re-publish the public key
Agent hangs or `can't connect to the agent` | `gpgconf --kill gpg-agent` and retry
Permissions warnings | `chmod 700 ~/.gnupg && chmod 600 ~/.gnupg/*`
