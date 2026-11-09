# MinIO
MinIO is an S3-compatible object storage server, used in homelabs as a target for backups ([Restic](../backup/restic.md), [rclone](../backup/rclone.md), Loki chunks) and as a local S3 for development. The `mc` client works with any S3-compatible service.

Documentation: [MinIO AIStor docs](https://docs.min.io/enterprise/aistor-object-store/), [mc reference](https://docs.min.io/enterprise/aistor-object-store/reference/cli/), [Project](https://github.com/minio/minio)

## Check the Current Licence and Release State First
The old `min.io/docs/minio/linux/` URLs now redirect to the **AIStor** documentation, and the AIStor pages state it is licensed under the MinIO Software License. They say nothing about the community edition, AGPL, source-only distribution or console changes, so none of that is verified here. Before you deploy, read the `LICENSE` and `README` in the project repository and check how prebuilt images and binaries are distributed today. Alternatives such as Garage, SeaweedFS and RustFS exist but were not checked here.

## Server
Server flags and environment variables below are the long-standing MinIO ones and were not re-checked against the AIStor docs. Confirm with `minio server --help`.

```yaml
services:
  minio:
    image: IMAGE_YOU_HAVE_VERIFIED
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ROOT_USER
      MINIO_ROOT_PASSWORD: LONG_RANDOM_PASSWORD
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio-data:/data
volumes:
  minio-data:
```

PORT | USE
---|---
`9000` | S3 API
`9001` | Web console (when `--console-address` is set; may not exist in every edition)

Put TLS in front of the S3 API ([reverse proxy](../homelab/reverse-proxy-patterns.md)) and use a dedicated access key per application, not the root credentials.

## mc Client
Verified from the AIStor `mc` docs: `mc alias set`, `mc admin info` and the command list below. Config lives in `~/.mc/config.json` (or `--config-dir` / `MC_CONFIG_DIR`). Global flags include `--insecure`, `--json`, `--debug` and `--resolve`.

COMMAND | DESCRIPTION
---|---
`mc alias set <ALIAS> https://s3.example.com ACCESS_KEY SECRET_KEY` | Save a server (secret key at least 8 characters)
`mc admin info <ALIAS>` | Test the connection and show server info
`mc mb <ALIAS>/<BUCKET>` | Make a bucket
`mc ls <ALIAS>/<BUCKET>` | List objects
`mc cp <FILE> <ALIAS>/<BUCKET>/` | Copy a file in (`--recursive` for folders)
`mc mirror <DIR> <ALIAS>/<BUCKET>` | Sync a folder, similar to `rsync`
`mc rm --recursive <ALIAS>/<BUCKET>/<PREFIX>` | **Delete** objects under a prefix
`mc rb <ALIAS>/<BUCKET>` | **Remove** a bucket
`mc anonymous` | Manage public (anonymous) access to a bucket
`mc version` | Manage bucket versioning
`mc ilm` | Manage lifecycle rules (expiry, tiering)
`mc retention` | Object retention
`mc replicate` | Bucket replication
`mc share` | Pre-signed URLs
`mc quota` | Bucket quotas
`mc admin` | Server administration (users, policies)

`mc cp` treats `*` literally. Use `--recursive` with a prefix. Exact subcommand syntax for `mc admin user add`, `mc admin policy`, `mc anonymous set`, `mc version enable` and `mc ilm` was not read here, so use `mc <COMMAND> --help`.

## Use It as a Backup Target
Restic and rclone both speak S3. With restic the repository is `s3:https://s3.example.com/BUCKET` with `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` set. Keep a copy of backups off the host that runs the object store. See [Restic](../backup/restic.md) and [rclone](../backup/rclone.md).

## See Also
- [Restic](../backup/restic.md)
- [rclone](../backup/rclone.md)
- [Loki and Grafana Alloy](loki-alloy.md)
- [Backblaze B2](../cloud/provider/backblaze-b2.md)
