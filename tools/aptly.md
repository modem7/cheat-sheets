# Aptly
Aptly manages Debian and Ubuntu package repositories: mirror upstream repositories, host your own `.deb` packages, take snapshots and publish them as an apt repository that machines can install from.

Homepage and docs: [aptly.info](https://www.aptly.info) · Source: [aptly-dev/aptly](https://github.com/aptly-dev/aptly)

---
## Install
```bash
sudo apt install aptly
```
If it is not in your distribution, use the repository on the aptly site. Config is `~/.aptly.conf` (JSON); data lives in `rootDir` (default `~/.aptly`). Check the effective config with `aptly config show`.

## Signing Key
Published repositories are signed with GPG so clients can verify them.
```bash
gpg --full-generate-key
gpg --list-secret-keys --keyid-format long
gpg --armor --export <KEYID> > mykey.asc
```
Clients import the public key; see Client Setup below. Use `-skip-signing` only for tests.

## Your Own Repository
COMMAND | DESCRIPTION
---|---
`aptly repo create -distribution=jammy -component=main myrepo` | Create a local repo
`aptly repo add myrepo mypackage_1.0_amd64.deb` | Add a package (or a directory)
`aptly repo show -with-packages myrepo` | List its packages
`aptly repo remove myrepo 'Name (= 1.0)'` | Remove by query
`aptly publish repo -architectures=amd64 myrepo` | Publish (signed with your default key)
`aptly publish update jammy` | Re-publish after changes
`aptly publish list` | List published repos
`aptly publish drop jammy` | Unpublish

## Mirror an Upstream Repository
```bash
gpg --no-default-keyring --keyring trustedkeys.gpg --keyserver keyserver.ubuntu.com --recv-keys <UPSTREAM-KEYID>
aptly mirror create -architectures=amd64 -filter='nginx' -filter-with-deps ubuntu-main http://archive.ubuntu.com/ubuntu jammy main
aptly mirror update ubuntu-main
```
Aptly checks upstream signatures against `trustedkeys.gpg`, so import the upstream key into that keyring first. Use `-filter` to avoid mirroring the whole archive (it is very large).

COMMAND | DESCRIPTION
---|---
`aptly mirror list` | List mirrors
`aptly mirror show ubuntu-main` | Details
`aptly mirror update ubuntu-main` | Fetch changes

## Snapshots
Snapshots are immutable point-in-time sets, so you can promote a tested state and roll back.

COMMAND | DESCRIPTION
---|---
`aptly snapshot create snap-2026-11-06 from mirror ubuntu-main` | Snapshot a mirror
`aptly snapshot create snap-mine from repo myrepo` | Snapshot a local repo
`aptly snapshot merge combined snap-2026-11-06 snap-mine` | Merge snapshots
`aptly snapshot list` | List
`aptly publish snapshot -distribution=jammy snap-2026-11-06` | Publish a snapshot
`aptly publish switch jammy snap-2026-12-01` | Atomically switch to a newer snapshot
`aptly snapshot diff snapA snapB` | Compare two snapshots

## Serve It
```bash
aptly serve                 # simple HTTP server on :8080, for testing
aptly api serve -listen=:8081   # REST API
```
In production publish to a directory and serve it with [[nginx]] (or any web server), and protect the API.

## Client Setup
```bash
curl -fsSL https://repo.example.com/mykey.asc | sudo gpg --dearmor -o /etc/apt/keyrings/myrepo.gpg
echo "deb [signed-by=/etc/apt/keyrings/myrepo.gpg] https://repo.example.com/ jammy main" | sudo tee /etc/apt/sources.list.d/myrepo.list
sudo apt update
```

## Cleanup
```bash
aptly db cleanup
```
Removes packages no longer referenced by any repo or snapshot. Run it after dropping snapshots.

## Not Verified
Written from knowledge of aptly and not run here. Check `aptly help <command>` for your version, especially mirror filter syntax and publish options.
