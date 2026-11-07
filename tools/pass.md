# pass Cheat-Sheet
`pass` is the standard Unix password manager: one GPG-encrypted file per secret under `~/.password-store`, with optional git history. Use it when you want a small, scriptable store you can sync with plain git.

Project: [pass](https://www.passwordstore.org/)
Documentation: `man pass`

Related sheets: [gopass](gopass.md), [GPG](../security/gpg.md), [Git](git.md), [Bitwarden](bitwarden.md), [1Password CLI](1password-cli.md).

## Set Up
COMMAND | DESCRIPTION
---|---
`gpg --list-secret-keys --keyid-format long` | Find the key ID to encrypt to
`pass init <GPG_ID>` | Create the store; run this first
`pass init <GPG_ID_1> <GPG_ID_2>` | Encrypt every secret to several keys
`pass init --path <SUBFOLDER> <GPG_ID>` | Use a different key for one subfolder
`pass init --path <SUBFOLDER> ""` | Remove that subfolder's own key file
`pass git init` | Turn the store into a git repository (every change then commits)
`pass git remote add origin <GIT_URL>` | Add a remote
`pass git push -u --all` | First push; later pushes can use `pass git push`

## Read
COMMAND | DESCRIPTION
---|---
`pass` / `pass ls` | Show the tree of names (uses `tree`)
`pass ls <SUBFOLDER>` | Show one subfolder
`pass find <TEXT>` | List names that match (alias `search`)
`pass grep <TEXT>` | Search inside decrypted secrets (extra options go to `grep`)
`pass show <NAME>` or `pass <NAME>` | Decrypt and print
`pass show -c <NAME>` | Copy the first line to the clipboard (cleared after 45 seconds)
`pass show -c<LINE> <NAME>` | Copy another line
`pass show -q <NAME>` | Show as a QR code

## Write
COMMAND | DESCRIPTION
---|---
`pass insert <NAME>` | Add a secret, typed twice (alias `add`)
`pass insert -m <NAME>` | Multi-line, end with Ctrl+D
`pass insert -e <NAME>` | Echo input while typing
`pass insert -f <NAME>` | Overwrite without asking
`pass edit <NAME>` | Edit in `$EDITOR` (temporary file goes in `/dev/shm`)
`pass generate <NAME> <LENGTH>` | Generate and store a password
`pass generate -n <NAME> <LENGTH>` | No symbols
`pass generate -c <NAME> <LENGTH>` | Copy instead of printing
`pass generate -i <NAME> <LENGTH>` | Replace only the first line, keep the rest
`pass rm -r <NAME>` | Remove a secret or folder (aliases `remove`, `delete`)
`pass mv <OLD> <NEW>` / `pass cp <OLD> <NEW>` | Rename or copy; re-encrypts to the new folder's keys
`-f` on `rm`, `mv`, `cp`, `insert` | Skip the confirmation

## Environment Variables
VARIABLE | DESCRIPTION
---|---
`PASSWORD_STORE_DIR` | Use a store other than `~/.password-store`
`PASSWORD_STORE_KEY` | Key IDs to use when initialising
`PASSWORD_STORE_GPG_OPTS` | Extra options passed to `gpg`
`PASSWORD_STORE_CLIP_TIME` | Seconds before the clipboard is cleared (default 45)
`PASSWORD_STORE_GENERATED_LENGTH` | Default password length
`PASSWORD_STORE_CHARACTER_SET` / `PASSWORD_STORE_CHARACTER_SET_NO_SYMBOLS` | Characters used by `generate`
`PASSWORD_STORE_ENABLE_EXTENSIONS` | Set to `true` to allow `.extensions/*.bash` extensions
`PASSWORD_STORE_SIGNING_KEY` | Require `.gpg-id` files to carry a detached signature from these key fingerprints

## Common Tasks
Use a secret in a script without it reaching the shell history:

```bash
DB_PASSWORD="$(pass show servers/db | head -n 1)" ./deploy.sh
```

Store the password on the first line and metadata below it, so `pass show -c` still copies only the password:

```text
CORRECT-HORSE-BATTERY
user: <USERNAME>
url: https://example.com/login
```

Share a store between two people by listing both keys at `init`, and keep it in a private git remote.

## Troubleshooting
SYMPTOM | FIX
---|---
`Error: password store is empty. Try "pass init".` | Run `pass init <GPG_ID>`
`gpg: decryption failed: No secret key` | The secret was not encrypted to a key you hold; see `.gpg-id` and re-init with the right key
Passphrase prompt on every call | Use `gpg-agent` (the man page recommends it)
Clipboard copy does nothing | Install `xclip` (X11) or `wl-clipboard` (Wayland)

## See Also
- [gopass](gopass.md)
- [GPG](../security/gpg.md)
- [Bitwarden](bitwarden.md)
- [1Password CLI](1password-cli.md)
