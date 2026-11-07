# LastPass CLI Cheat-Sheet
`lpass` is the LastPass command-line client. It keeps an encrypted local cache, runs a short-lived agent so you do not retype the master password, and can export or import your vault as CSV.

Project: [lastpass-cli](https://github.com/lastpass/lastpass-cli)
Documentation: `man lpass`

Checked against the `lpass` 1.3.7 man page (Ubuntu 24.04 package). Nothing was run against a real LastPass account.

Related sheets: [Bitwarden](bitwarden.md), [1Password CLI](1password-cli.md), [pass](pass.md), [gopass](gopass.md).

## Install
COMMAND | DESCRIPTION
---|---
`sudo apt install lastpass-cli` | Install on Debian and Ubuntu
`brew install lastpass-cli` | Install on macOS
`lpass --version` | Check the install

## Log In
COMMAND | DESCRIPTION
---|---
`lpass login <EMAIL>` | Log in; prompts for the password and any multi-factor code
`lpass login --trust <EMAIL>` | Do not ask for multi-factor on later logins from this machine
`lpass login --plaintext-key --force <EMAIL>` | Store the decryption key unencrypted on disk (discouraged by the man page)
`lpass status` | Show whether you are logged in (`-q` for quiet)
`lpass logout` | Remove the local cache and stored keys (`--force` skips the prompt)
`lpass passwd` | Change your master password and re-encrypt every record
`lpass sync` | Force a sync with the server (`--background` runs it in the background)

## Read
Names are folder paths such as `work/email`. A name must match exactly and be unique, or use the numeric ID.

COMMAND | DESCRIPTION
---|---
`lpass ls` | List everything as a tree
`lpass ls <GROUP>` | List one folder
`lpass ls -l` | Include last-modified times (GMT)
`lpass show <NAME>` | Show an entry
`lpass show --password <NAME>` | Only the password (also `--username`, `--url`, `--notes`, `--id`, `--name`)
`lpass show --field=<FIELD> <NAME>` | One custom field
`lpass show -c --password <NAME>` | Copy the password to the clipboard
`lpass show --json <NAME>` | JSON output
`lpass show -x <NAME>` | Show every match instead of warning on duplicates
`lpass show -G '<REGEX>'` / `lpass show -F '<TEXT>'` | Match by case-insensitive regex or substring
`lpass show --attach=<ATTACH_ID> <NAME>` | Print an attachment
`lpass ls --format="%/as%/ag%an"` | Custom output with `printf`-style placeholders (`%ai` ID, `%an` name, `%au` user, `%ap` password, `%al` URL)

## Write
COMMAND | DESCRIPTION
---|---
`lpass add <NAME>` | Add an entry, filled in through `$EDITOR`
`lpass add --non-interactive --username <NAME>` | Read the field value from stdin instead of an editor
`lpass add --note-type=<TYPE> <NAME>` | Add a typed secure note
`lpass edit --password <NAME>` | Edit one field (`--name`, `--username`, `--url`, `--notes`, `--field=<FIELD>`)
`lpass generate <NAME> <LENGTH>` | Generate and store a password
`lpass generate --no-symbols --username <USER> --url <URL> <NAME> <LENGTH>` | Alphanumeric password with user and URL
`lpass generate -c <NAME> <LENGTH>` | Copy it instead of printing
`lpass duplicate <NAME>` | Copy an entry under a new ID
`lpass mv <NAME> <GROUP>` | Move an entry to a folder
`lpass rm <NAME>` | Remove an entry (use the ID if the name is not unique)

Interactive `edit` can leave field contents in temporary files, depending on your system.

## Sync Control
OPTION | DESCRIPTION
---|---
`--sync=auto` | Default: sync in the background after changes; refresh the cache before showing if it is over 5 seconds old
`--sync=now` | Wait for the server round trip
`--sync=no` | Never contact the server for this command; changes queue until the next sync

## Backup
COMMAND | DESCRIPTION
---|---
`lpass export > vault.csv` | Dump every entry, including passwords, as unencrypted CSV
`lpass export --fields=name,username,password,url` | Export a subset of fields
`lpass import vault.csv` | Upload accounts from a CSV file (`--keep-dupes` keeps duplicates)
`lpass export \| gpg -c -o vault.csv.gpg` | Encrypt the export as it is written

Delete or encrypt any plain CSV straight away; it holds every password in clear text.

## Shared Folders
COMMAND | DESCRIPTION
---|---
`lpass share create <SHARE>` / `lpass share rm <SHARE>` | Create or delete a shared folder
`lpass share userls <SHARE>` | List members
`lpass share useradd <SHARE> <USERNAME>` | Add a member (`--read-only`, `--hidden`, `--admin` take `true` or `false`)
`lpass share usermod --read-only=true <SHARE> <USERNAME>` | Change a member's rights
`lpass share userdel <SHARE> <USERNAME>` | Remove a member
`lpass share limit --deny --add <SHARE> <USERNAME> <SITES>` | Restrict which sites a member can access

## Configuration
VARIABLE | DESCRIPTION
---|---
`LPASS_HOME` | Config directory (otherwise XDG directories or `~/.lpass`)
`LPASS_AGENT_TIMEOUT` | Seconds before the agent quits (default one hour; `0` means never)
`LPASS_AGENT_DISABLE` | Set to `1` to run without the agent
`LPASS_AUTO_SYNC_TIME` | Seconds before the cache counts as stale (default 5)
`LPASS_PINENTRY` / `LPASS_DISABLE_PINENTRY` | Pick the pinentry program, or read passwords from stdin
`LPASS_ASKPASS` | Program used to ask for the password
`LPASS_CLIPBOARD_COMMAND` | Override the clipboard command (`xclip`, `xsel`, `pbcopy` by default)

Aliases: put default options in `~/.config/lpass/alias.COMMAND`, for example `echo 'ls --color=never' > ~/.config/lpass/alias.ls`.

## Troubleshooting
SYMPTOM | FIX
---|---
Stale data after changing something in the browser | `lpass sync`
Command refuses a name that is used more than once | Use the numeric ID from `lpass ls`
No password prompt in a script | Set `LPASS_DISABLE_PINENTRY=1` and feed the password on stdin, or log in beforehand
Clipboard copy does nothing | Install `xclip` or `xsel`, or set `LPASS_CLIPBOARD_COMMAND`

## See Also
- [Bitwarden](bitwarden.md)
- [1Password CLI](1password-cli.md)
- [pass](pass.md)
- [gopass](gopass.md)
