# BorgBase
BorgBase is a hosted backup repository service for Borg (and Restic) over SSH. Use it as the off-site target for [Borg](borg.md) or [borgmatic](borgmatic.md) so a backup survives the loss of your lab. It supports append-only keys, so a compromised machine cannot delete history.

Documentation: [BorgBase docs](https://docs.borgbase.com/)

## Setup
1. Generate an SSH key per machine: `ssh-keygen -o -a 100 -t ed25519`.
2. In BorgBase add the public key under Account, SSH Keys.
3. Add a repository: name, quota, location (US or EU), and choose the key and its access level.
4. Use the repository URL BorgBase shows, for example `ssh://<REPO_ID>@<REPO_ID>.repo.borgbase.com/./repo`. The old `user@host:repo` form is deprecated.

Supported key types are RSA (over 1024 bits), ECDSA and Ed25519, with Ed25519 recommended. Use one key per machine so you can revoke one.

## Initialise
COMMAND | DESCRIPTION
---|---
`export BORG_REPO=ssh://<REPO_ID>@<REPO_ID>.repo.borgbase.com/./repo` | Set the repo
`borg init -e repokey-blake2` | Borg 1.x
`borg repo-create --encryption=repokey-blake2-chacha20-poly1305` | Borg 2.x

Store the repo passphrase and exported key in your password manager. Losing both means losing the backups, and BorgBase cannot recover them.

## borgmatic
In `~/.config/borgmatic/config.yaml` (borgmatic 1.8.5 and later):

```yaml
repositories:
  - path: ssh://<REPO_ID>@<REPO_ID>.repo.borgbase.com/./repo
    label: borgbase

encryption_passphrase: "${BORG_PASSPHRASE}"
compression: auto,zstd
keep_daily: 7
keep_weekly: 4
keep_monthly: 6
```

Older section-based configs still work with warnings. Whether `${BORG_PASSPHRASE}` interpolation works depends on your borgmatic version, so confirm in its docs, or use `encryption_passcommand` instead.

## Append-only vs Full Access
KEY TYPE | WHAT IT CAN DO
---|---
Append-only | Create backups. Cannot delete or truly prune history
Full access | Everything, including space reclaim

- A prune with an append-only key frees no space.
- To reclaim space, use a full-access key and run `borg compact` (Borg 1.2 and later), or use "Compact repo" in the BorgBase panel.
- Run routine backups with the append-only key, and keep the full-access key somewhere else for maintenance.

## Monitoring
BorgBase says it alerts on missing backups, but the docs do not give the thresholds. Add your own with [Healthchecks](../apps/healthchecks.md) and borgmatic's healthchecks hook, so you are told about a silent failure.

## Restic
BorgBase also hosts Restic repos through a REST endpoint, see [restic](restic.md):

```bash
export RESTIC_REPOSITORY="rest:https://<USER>:<PASSWORD>@<HOST>.repo.borgbase.com"
restic init
```

Take the exact repository string from the BorgBase panel. Do not commit it.

## API
GraphQL at `https://api.borgbase.com/graphql` with a bearer token. Token levels are Read Only, Create Only and Full Access. The docs list Ansible and GLPI integrations and do not mention a Terraform provider.

## Plans
A base plan with per-GB overage up to three times the included storage, and no traffic fees. A free 10 GB tier is mentioned. Prices were not stated, so check the pricing page.

## Not Verified
Two-factor authentication (seen only in a marketing snippet), the Restic URL format, and geo-redundancy. The FAQ says there is none within a single repo, so keep a second copy elsewhere.

## See Also
- [Borg](borg.md)
- [borgmatic](borgmatic.md)
- [restic](restic.md)
- [Healthchecks](../apps/healthchecks.md)
