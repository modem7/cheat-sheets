# 1Password CLI Cheat-Sheet
The 1Password CLI (`op`) reads and writes vault items from the terminal and injects secrets into commands and config files without writing them to disk. Use it to keep secrets out of `.env` files and shell history.

Documentation: [1Password CLI](https://www.1password.dev/cli/get-started)
Project: [1Password](https://1password.com/)

Related sheets: [Bitwarden](bitwarden.md), [pass](pass.md), [gopass](gopass.md), [LastPass CLI](lastpass-cli.md), [SOPS and age](../security/sops-age.md), [Secret Scanning](../security/secret-scanning.md).

## Install and Update
COMMAND | DESCRIPTION
---|---
`brew install 1password-cli` | Install on macOS
`winget install 1password-cli` | Install on Windows
`op --version` | Check the install
`op update` | Check for and download a newer `op`
`op update --channel beta --directory <PATH>` | Pick the channel (`stable` or `beta`) and download location

On Linux, use the package repository or the zip from the 1Password downloads page; see the install page in the documentation.

## Sign In
With the desktop app installed, turn on the CLI integration (Settings, Developer) and `op` signs in through the app (Touch ID and similar). Without it, sign in by hand.

COMMAND | DESCRIPTION
---|---
`op signin` | Sign in to an account (prompts if needed)
`eval $(op signin --account <SHORTHAND>.1password.com)` | Sign in and export the session token for this shell (manual sign-in only)
`op whoami` | Show which account or service account is active
`op account list` | List signed-in accounts
`op signout` | Sign out

## Global Flags and Variables
FLAG OR VARIABLE | DESCRIPTION
---|---
`--account <ACCOUNT>` / `OP_ACCOUNT` | Pick the account when you have several
`--format json` / `OP_FORMAT` | Output JSON instead of a table
`--vault <VAULT>` | Limit a command to one vault (per-command flag)
`--cache=false` / `OP_CACHE` | Turn the item cache off or on
`--debug` / `OP_DEBUG` | Print debug output
`OP_ISO_TIMESTAMPS` | Use ISO 8601 timestamps in output

## Secret References
A secret reference points at a field instead of holding its value. Format: `op://VAULT/ITEM/[SECTION/]FIELD`. Names and IDs both work.

COMMAND | DESCRIPTION
---|---
`op read "op://app-prod/db/password"` | Print one field
`op read "op://app-prod/db/one-time password?attribute=otp"` | Print the current one-time password
`op read --out-file ./key.pem op://app-prod/server/ssh/key.pem` | Save a file or key field to disk
`op read --no-newline op://app-prod/db/password` | Drop the trailing newline

Quote references that contain spaces or `?`.

## Run Commands With Secrets
`op run` swaps secret references in the environment for real values for the child process only.

COMMAND | DESCRIPTION
---|---
`op run --env-file=.env -- <COMMAND>` | Load references from an env file and run the command
`op run -- <COMMAND>` | Resolve references already in the environment
`op run --no-masking -- <COMMAND>` | Do not mask secrets in the command output (masking is on by default)
`op run --environment <ENVIRONMENT_ID> -- printenv` | Load a 1Password Environment

```bash
# .env holds references, not secrets
# DB_PASSWORD=op://app-prod/db/password
op run --env-file=.env -- docker compose up -d
```

## Inject Into Config Files
`op inject` fills `{{ op://... }}` placeholders in a template.

COMMAND | DESCRIPTION
---|---
`op inject -i config.yml.tpl -o config.yml` | Render a template to a file
`echo "db_password: {{ op://app-prod/db/password }}" \| op inject` | Render from stdin to stdout
`op inject --in-file <TEMPLATE> --out-file <FILE> --force` | Overwrite the output file without asking

Do not commit the rendered file; see [Secret Scanning](../security/secret-scanning.md).

## Items
COMMAND | DESCRIPTION
---|---
`op item list` | List items
`op item list --vault <VAULT> --tags <TAG> --categories Login` | Filter the list
`op item list --long --favorite` | More detail, favourites only
`op item get "<ITEM>"` | Show an item
`op item get "<ITEM>" --fields label=username,label=password` | Pick fields by label
`op item get "<ITEM>" --fields type=concealed --reveal` | Pick fields by type and show hidden values
`op item get "<ITEM>" --otp` | Print the one-time password
`op item get "<ITEM>" --share-link` | Get a shareable link
`op item get "<ITEM>" --format json` | Full item as JSON
`op item create --category login --title "<TITLE>" --vault <VAULT> --url <URL> 'username=<USER>'` | Create a login
`op item create --category login --title "<TITLE>" --generate-password='letters,digits,symbols,32'` | Create with a generated password
`op item create --dry-run ...` | Preview without saving
`op item edit "<ITEM>" 'field=<VALUE>'` | Change a field
`op item edit "<ITEM>" --generate-password='letters,digits,symbols,32'` | New generated password
`op item edit "<ITEM>" 'section.field[delete]'` | Delete a field
`op item move "<ITEM>" --current-vault <FROM> --destination-vault <TO>` | Move to another vault
`op item share "<ITEM>" --emails <EMAIL> --expires-in 24h --view-once` | Share a link that expires
`op item delete "<ITEM>" --archive` | Move to the Archive (without `--archive` the delete is permanent)
`op item template list` | List item categories
`op item template get <CATEGORY> --out-file <FILE>` | Get a JSON template for a category

Assignments use `section.field[type]=value`; types include `text`, `password`, `phone` and `monthyear`.

## Documents
COMMAND | DESCRIPTION
---|---
`op document list` | List documents
`op document create <FILE> --title "<TITLE>" --vault <VAULT>` | Upload a file
`op document get "<TITLE>" --out-file <FILE>` | Download a file
`op document edit "<TITLE>" <FILE>` | Replace the file
`op document delete "<TITLE>" --archive` | Archive the document

## Vaults
COMMAND | DESCRIPTION
---|---
`op vault list` | List vaults
`op vault get <VAULT>` | Show a vault
`op vault create <NAME> --description "<TEXT>"` | Create a vault
`op vault edit <VAULT> --name <NEW_NAME>` | Rename a vault
`op vault edit <VAULT> --travel-mode on` | Turn Travel Mode on or off
`op vault delete <VAULT>` | Delete a vault
`op vault group list <VAULT>` | Show which groups can access it
`op vault group grant --vault <VAULT> --group <GROUP> --permissions <PERMISSIONS>` | Give a group access
`op vault group revoke --vault <VAULT> --group <GROUP>` | Remove access

## Scripts and CI
COMMAND | DESCRIPTION
---|---
`OP_SERVICE_ACCOUNT_TOKEN=<TOKEN> op vault list` | Authenticate non-interactively with a service account (unverified here: variable name not in the pages checked, see the service accounts page)
`op item list --format json \| jq -r '.[].title'` | Parse JSON output with `jq`
`op item list --tags <TAG> --format json \| op item get - --fields label=password` | Pipe a list into `get`

Keep the token in your CI secret store, never in the repository.

## Troubleshooting
SYMPTOM | FIX
---|---
`not signed in` or a prompt in scripts | Run `op whoami`; use the app integration or a service account for scripts
Wrong account | Pass `--account` or set `OP_ACCOUNT`
Reference not found | Check names with `op item get`; quote names that contain spaces
Secret printed in plain output | Prefer `op run` (masks output) over `op read` in logs

## See Also
- [Bitwarden](bitwarden.md)
- [pass](pass.md)
- [SOPS and age](../security/sops-age.md)
- [Secret Scanning](../security/secret-scanning.md)
