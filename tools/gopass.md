# gopass Cheat-Sheet
`gopass` is a Go rewrite of [pass](pass.md) for teams: the same one-file-per-secret store in git, plus multiple mounted stores, recipients, OTP, audits and `age` as an alternative to GPG. Use it when a store is shared or you want more than `pass` offers.

Project: [gopass](https://www.gopass.pw/)
Documentation: [gopass docs](https://github.com/gopasspw/gopass/tree/master/docs)

Checked against `gopass --help` for 1.17.4 (built from source in a container). The `gopass` package in some distributions is an older, unrelated tool; check `gopass version`.

Related sheets: [pass](pass.md), [GPG](../security/gpg.md), [SOPS and age](../security/sops-age.md), [1Password CLI](1password-cli.md), [Bitwarden](bitwarden.md).

## Set Up
COMMAND | DESCRIPTION
---|---
`gopass setup` | Guided first-time setup (alias of `init`)
`gopass init <GPG_ID>` | Create a store encrypted to a GPG key
`gopass init --crypto age` | Use `age` instead (backends: `age`, `gpgcli`, `plain`; default `gpgcli`)
`gopass init --storage fs` | Pick the storage backend (`cryptfs`, `fossilfs`, `fs`, `gitfs`, `jjfs`; default `gitfs`)
`gopass clone <GIT_URL>` | Clone an existing store
`gopass clone <GIT_URL> <MOUNT_POINT>` | Clone it as a named mount
`gopass doctor` | Check the installation for common problems
`gopass config` | Show and edit the configuration

## Read
COMMAND | DESCRIPTION
---|---
`gopass ls` | List secrets (alias `list`)
`gopass show <NAME>` or `gopass <NAME>` | Show a secret
`gopass show -o <NAME>` | Only the password
`gopass show -c <NAME>` | Copy the password to the clipboard
`gopass show -C <NAME>` | Copy the password and still show the rest
`gopass show --qr <NAME>` | Password as a QR code
`gopass show -r <REVISION> <NAME>` | Show a past revision
`gopass show --chars 1,3,5 <NAME>` | Print only some characters of the secret
`gopass show -n <NAME>` | Do not parse the output
`gopass find <TEXT>` | Search names (alias `search`)
`gopass find -r '<REGEX>'` / `gopass find -j <TEXT>` | Regex match, or JSON output
`gopass grep <TEXT>` | Search inside decrypted secrets
`gopass history <NAME>` | Change history (`-p` includes passwords)
`gopass cat <NAME>` | Print a binary secret to stdout; pipe stdin in to store one

## Write
COMMAND | DESCRIPTION
---|---
`gopass insert <NAME>` | Add a secret (prompts)
`gopass insert -m <NAME>` | Enter it in `$EDITOR`
`gopass insert -a <NAME>` | Append stdin to an existing secret
`gopass insert -f <NAME>` | Overwrite without confirming
`gopass edit <NAME>` | Edit in `$EDITOR` (`-c` creates it if missing)
`gopass create` | Wizard for new secrets (alias `new`); uses templates
`gopass generate <NAME> <LENGTH>` | Generate and store a password
`gopass generate -s <NAME> <LENGTH>` | Include symbols
`gopass generate -g xkcd <NAME>` | Passphrase generator (`cryptic`, `memorable`, `xkcd` and others; see `gopass generate --help`)
`gopass generate -p <NAME>` | Print instead of only storing
`gopass pwgen` | Generate passwords without storing them
`gopass copy <FROM> <TO>` / `gopass move <FROM> <TO>` | Copy or move (aliases `cp`, `mv`; `-f` overwrites)
`gopass delete -r <NAME>` | Delete a secret or folder (aliases `rm`, `remove`)
`gopass merge <NAME_1> <NAME_2>` | Merge secrets into one
`-m "<MESSAGE>"` or `-i` | Set the commit message, or open an editor for it

## OTP
COMMAND | DESCRIPTION
---|---
`gopass otp <NAME>` | Print the current TOTP or HOTP token (aliases `totp`, `hotp`)
`gopass otp -c <NAME>` | Copy the token to the clipboard
`gopass otp -o <NAME>` | Only the token
`gopass otp -q <FILE> <NAME>` | Write the QR code to a file
`gopass otp -s <NAME>` | Scan the screen for an OTP QR code and store it in the entry

The entry must hold a full `otpauth://` URI.

## Run Commands With Secrets
COMMAND | DESCRIPTION
---|---
`gopass env <NAME> <COMMAND>` | Run a command with the secret's keys as environment variables
`gopass env --keep-case <NAME> <COMMAND>` | Do not upper-case the variable names
`gopass env --file <NAME> <COMMAND>` | Write to a RAM-disk temp file and export `KEY_FILE`
`gopass env --stdin <NAME> <COMMAND>` | Pipe the password to the command's stdin
`gopass process <TEMPLATE_FILE>` | Fill a template file from the store

## Stores, Sync and Recipients
COMMAND | DESCRIPTION
---|---
`gopass sync` | Pull and push all stores; `-s <STORE>` limits to one
`gopass git <ARGS>` | Run git in the store (`--store <STORE>` to pick one)
`gopass --nosync show <NAME>` | Skip auto-sync for one command
`gopass mounts` | List mounted stores
`gopass mounts add <MOUNT> <PATH>` | Mount a store (alias `mount`)
`gopass mounts remove <MOUNT>` | Unmount (aliases `rm`, `umount`)
`gopass recipients` | List who can decrypt each store
`gopass recipients add <ID>` | Authorise a recipient (re-encrypts the store)
`gopass recipients remove <ID>` | Remove a recipient
`gopass recipients update` | Refresh recipients' public keys
`gopass templates` | List, show, edit and remove secret templates

Removing a recipient does not revoke access to secrets they already saw; rotate those secrets.

## Maintenance
COMMAND | DESCRIPTION
---|---
`gopass audit` | Decrypt everything and check for weak or leaked passwords
`gopass audit --format html --output-file <FILE>` | Write a report (formats: `text`, `csv`, `html`, `json`)
`gopass fsck` | Check store integrity and fix artefacts (`--decrypt` re-encrypts)
`gopass reorg` | Reorganise secrets by editing a text file
`gopass update` | Check for a new gopass release
`gopass --exit-codes` | List exit codes and meanings

## Troubleshooting
SYMPTOM | FIX
---|---
`gopass: command not found` after installing | Check the package; some distributions ship a different, older program of the same name
Prompted for a passphrase every time | Use `gpg-agent`; see [GPG](../security/gpg.md)
Fuzzy search starts when a name is wrong | Add `--nofuzzysearch`
Secrets stop decrypting after a recipient change | Run `gopass recipients update`, then `gopass sync`

## See Also
- [pass](pass.md)
- [GPG](../security/gpg.md)
- [SOPS and age](../security/sops-age.md)
- [1Password CLI](1password-cli.md)
