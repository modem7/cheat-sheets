# Backblaze B2
Backblaze B2 is cheap S3-compatible object storage, popular as an off-site target for homelab backups. Covers pricing basics, application keys, versioning and lifecycle behaviour, the `b2` CLI and tool integration.

Documentation: [B2 pricing](https://www.backblaze.com/cloud-storage/pricing) · [Application keys](https://www.backblaze.com/docs/cloud-storage-application-keys) · [Lifecycle rules](https://www.backblaze.com/docs/cloud-storage-lifecycle-rules) · [B2 CLI](https://github.com/Backblaze/B2_Command_Line_Tool) · [Terraform B2 provider](https://registry.terraform.io/providers/Backblaze/b2/latest) (see [Terraform](../../tools/terraform.md))

> **Verification:** pricing, key and lifecycle behaviour and CLI commands were checked against the Backblaze docs and the CLI repository (November 2026). No command was run against an account. Items marked *(unverified)* were not confirmed. Prices change, so check the pricing page.

## Pricing
ITEM | DETAIL
---|---
Storage | From $6.95 per TB per month; the first 10 GB are free
Egress | Free up to 3x your average monthly stored data, then $0.01 per GB
API calls | Classes A, B and C are free; Class D is $0.004 per 10,000 with the first 2,500 per day free
Cloudflare egress | Backblaze advertises free transfer to Cloudflare through the Bandwidth Alliance *(unverified, seen in search snippets only)*

## Application Keys
- The **master application key** has every capability and is invalidated if you regenerate it. Do not use it in tools.
- Create **standard application keys** and restrict them to one bucket, optionally to a file-name prefix, and optionally with an expiry.
- A key restricted to a single bucket may also need the `listAllBucketNames` capability for some tools.
- The key ID and the key itself are shown once at creation.

## B2 CLI (v5)
The `b2` command is documented as unstable between versions; the README recommends `b2v5` in scripts. Commands are grouped as `account`, `bucket`, `file`, `key`, `ls`, `rm` and `sync`. Older `b2 authorize-account` style commands and the `bucketName fileName` argument form are deprecated in favour of `b2://bucket/file` URIs.

COMMAND | DESCRIPTION
---|---
`b2 account authorize` | Authorise with a key ID and key (prompts if not given)
`b2 bucket create <BUCKET> allPrivate` | Create a private bucket
`b2 bucket list` | List buckets
`b2 file upload <BUCKET> <LOCAL_FILE> <REMOTE_NAME>` | Upload a file
`b2 ls b2://<BUCKET>` | List files (URI form *unverified for this command*)
`b2 rm b2://<BUCKET>/<PATH>` | Delete files (destructive; URI form *unverified*)
`b2 sync <SOURCE> <DESTINATION>` | Sync a directory with a bucket (destructive with `--delete`, check `b2 sync --help`)
`b2 key create [--bucket <BUCKET>] [--name-prefix <PREFIX>] [--duration <SECONDS>] <KEY_NAME> <CAPABILITIES>` | Create a restricted key with comma-separated capabilities (or `--all-capabilities`)

## Versioning and Lifecycle
- Versions are kept **forever** by default. Uploading a new file with the same name hides the old version, it does not delete it, so storage grows.
- Lifecycle rules use `daysFromUploadingToHiding` and `daysFromHidingToDeleting`. The minimum value is 1 day and rules run once a day.
- Object Lock blocks lifecycle deletion until the retention ends.

Example lifecycle rule keeping 30 days of old versions:

```json
[
  {
    "fileNamePrefix": "",
    "daysFromHidingToDeleting": 30,
    "daysFromUploadingToHiding": null
  }
]
```

The JSON shape above is an adaptation of the documented field names *(unverified)*.

## S3-Compatible API
Endpoint: `https://s3.<REGION>.backblazeb2.com` (HTTPS and Signature V4 only; endpoint form from a search summary, *unverified* on the docs page). Use the application key ID as the access key and the key as the secret. Create the bucket and key in the same region.

Backup tool setup (rclone, restic, Borg) is *not verified here*; follow each tool's own B2 or S3 documentation:
- [restic](../../backup/restic.md)
- [rclone](../../backup/rclone.md)
- [BorgBackup](../../backup/borg.md)

## Pitfalls
PITFALL | DETAIL
---|---
Hidden versions cost money | Old versions stay until a lifecycle rule deletes them
Master key in tools | Use a bucket-restricted key instead
Egress beyond 3x stored | Billed per GB, so restore tests count
No built-in cold tier | B2 has one storage class; cost savings come from price, not tiers

## See Also
- [Cloud-Provider Comparison](cloud-provider-comparison.md)
- [restic](../../backup/restic.md)
- [rclone](../../backup/rclone.md)
- [Backup Strategy](../../backup/backup.md)
- [Terraform](../../tools/terraform.md)
