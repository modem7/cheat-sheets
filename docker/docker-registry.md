# Docker Registry
Working with image registries: Docker Hub and its pull limits, GitHub Container Registry (GHCR), running your own `registry:2`, a pull-through cache, copying images with `skopeo` and `crane`, and tagging strategy.

Documentation: [Docker Hub usage and pull limits](https://docs.docker.com/docker-hub/usage/pulls/) · [Registry mirror](https://docs.docker.com/docker-hub/image-library/mirror/) · [Distribution registry](https://distribution.github.io/distribution/) · [GHCR](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry) · [skopeo](https://github.com/containers/skopeo) · [crane](https://github.com/google/go-containerregistry/blob/main/cmd/crane/doc/crane.md)

> **Verification:** Docker Hub limits, the rate-limit check, the `docker login ghcr.io` command and PAT scopes, the `proxy.remoteurl` mirror setting and `registry-mirrors` were checked against the official docs. **Not verified against the docs:** `registry:2` storage and htpasswd examples, `skopeo` and `crane` flags, and the tagging advice (common practice). No command was executed. Docker Hub limits change over time, so re-check the link above.

See also: [OCI Images](oci-images.md) · [Podman](podman.md) · [Cloudsmith CLI](../tools/cloudsmith-cli.md) · [Docker](docker.md) · [Docker Troubleshooting](docker-troubleshooting.md) · [Docker Cleanup](docker-cleanup.md) · [Docker-Compose](docker-compose.md) · [GitHub and the gh CLI](../tools/github-cli.md) · [SSL Certificates Cheat-Sheet](../misc/ssl-certs.md)

---
## Docker Hub
COMMAND | DESCRIPTION
---|---
`docker login` | Log in to Docker Hub (prompts, or use an access token)
`docker login -u USER --password-stdin < token.txt` | Non-interactive, token read from a file
`docker logout` | Remove stored credentials
`docker search NAME` | Search Hub
`docker pull NAME:TAG` | Pull
`docker push USER/NAME:TAG` | Push (repo must belong to you or your org)

Use a **personal access token** (Account settings, Security) rather than your password, especially in CI.

### Pull Rate Limits
Pulls are limited per 6 hours:

ACCOUNT | LIMIT
---|---
Unauthenticated | 100 pulls per IPv4 address or IPv6 /64 subnet
Personal (free, logged in) | 200 pulls
Pro, Team, Business | Unlimited (fair use)

The `toomanyrequests` error means you hit it. Logging in raises the limit, and many hosts behind one NAT share the anonymous quota.

Check what is left (HEAD requests do not count as a pull):
```bash
TOKEN=$(curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:ratelimitpreview/test:pull" | jq -r .token)
curl -sI -H "Authorization: Bearer $TOKEN" https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest | grep -i ratelimit
```
`ratelimit-limit: 100;w=21600` is the limit and window in seconds. `ratelimit-remaining` is what is left. Add `-u USER:TOKEN` to the token request to check the authenticated limit. See [jq](../tools/jq.md).

Ways to cut Hub pulls:
- Log in on every build host and CI runner.
- Run a pull-through cache (below) so each image is fetched once.
- Pin versions and avoid `docker pull` on every deploy. Compose only pulls when you ask.
- Mirror important base images into your own registry or GHCR.

---
## GitHub Container Registry (GHCR)
Images live at `ghcr.io/OWNER/NAME:TAG` (owner in lowercase).

1. Create a **personal access token (classic)** with `read:packages` (pull), `write:packages` (push), and `delete:packages` (delete). In GitHub Actions use the built-in `GITHUB_TOKEN` with `packages: write` permission instead.
2. Store it in an environment variable or secret manager, then:
```bash
echo "$CR_PAT" | docker login ghcr.io -u <GITHUB-USERNAME> --password-stdin
```
3. Tag and push:
```bash
docker tag myapp:latest ghcr.io/<OWNER>/myapp:1.2.3
docker push ghcr.io/<OWNER>/myapp:1.2.3
docker pull ghcr.io/<OWNER>/myapp:1.2.3
```
- New packages are **private** by default. Change visibility on the package page. Link the package to its repository with the label `org.opencontainers.image.source=https://github.com/<OWNER>/<REPO>` in the Dockerfile.
- A CI example, see [GitHub and the gh CLI](../tools/github-cli.md) for the `gh` tool:
```yaml
- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```
- Other registries follow the same pattern: `docker login REGISTRY`. Examples: `registry.gitlab.com`, `quay.io`, `<ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com` (use `aws ecr get-login-password`, see [AWS CLI](../tools/aws-cli.md)).

Credentials end up in `~/.docker/config.json`. Install a credential helper (`docker-credential-pass`, `docker-credential-secretservice`) on workstations so they are not stored as base64.

---
## Run a Local Registry (`registry:2`)
Quick, no authentication (LAN testing only):
```bash
docker run -d --name registry --restart unless-stopped \
  -p 5000:5000 \
  -v registry-data:/var/lib/registry \
  registry:2

docker tag alpine:3 localhost:5000/alpine:3
docker push localhost:5000/alpine:3
curl http://localhost:5000/v2/_catalog
curl http://localhost:5000/v2/alpine/tags/list
```
`localhost` is allowed over plain HTTP. Any other hostname needs TLS or an `insecure-registries` entry in `/etc/docker/daemon.json` on every client (`{"insecure-registries": ["registry.lan:5000"]}`), which is only for lab use.

### With TLS and Basic Authentication
```bash
mkdir -p auth certs
docker run --rm --entrypoint htpasswd httpd:2 -Bbn <USER> <PASSWORD> > auth/htpasswd

docker run -d --name registry --restart unless-stopped -p 443:5000 \
  -v registry-data:/var/lib/registry \
  -v "$PWD/certs":/certs -v "$PWD/auth":/auth \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/fullchain.pem \
  -e REGISTRY_HTTP_TLS_KEY=/certs/privkey.pem \
  -e REGISTRY_AUTH=htpasswd \
  -e REGISTRY_AUTH_HTPASSWD_REALM="Registry" \
  -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd \
  -e REGISTRY_STORAGE_DELETE_ENABLED=true \
  registry:2
```
Alternatively put it behind a reverse proxy that does TLS (Caddy, Traefik, Nginx) and run the registry on an internal network. If you proxy it, allow large uploads (`client_max_body_size 0` in Nginx). For certificates see [SSL Certificates Cheat-Sheet](../misc/ssl-certs.md).

Clients with a private CA: put the CA file in `/etc/docker/certs.d/registry.lan:5000/ca.crt`.

### Compose
```yaml
services:
  registry:
    image: registry:2
    restart: unless-stopped
    ports: ["5000:5000"]
    environment:
      REGISTRY_STORAGE_DELETE_ENABLED: "true"
    volumes:
      - registry-data:/var/lib/registry
volumes:
  registry-data:
```
See [Docker-Compose](docker-compose.md).

### Manage and Clean Up
COMMAND | DESCRIPTION
---|---
`curl -s http://HOST:5000/v2/_catalog \| jq` | List repositories
`curl -s http://HOST:5000/v2/NAME/tags/list \| jq` | List tags
`curl -sI -H 'Accept: application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json' http://HOST:5000/v2/NAME/manifests/TAG` | Digest is in `Docker-Content-Digest`
`curl -X DELETE http://HOST:5000/v2/NAME/manifests/DIGEST` | Delete by digest (needs `REGISTRY_STORAGE_DELETE_ENABLED=true`)
`docker exec registry registry garbage-collect /etc/docker/registry/config.yml --delete-untagged` | Free the blob storage after deletes
`docker exec registry registry garbage-collect --dry-run /etc/docker/registry/config.yml` | Show what would go

The registry has no web UI. Third-party UIs exist (for example `joxit/docker-registry-ui`), and Harbor is the full-featured, heavier alternative with scanning and projects. Stop writes to the registry (or make it read-only) during garbage collection.

---
## Pull-Through Cache (Mirror of Docker Hub)
A local `registry:2` that proxies Docker Hub and stores what it has fetched. Only **Docker Hub** can be mirrored this way, and only one remote per registry instance.

`config.yml`:
```yaml
version: 0.1
storage:
  filesystem:
    rootdirectory: /var/lib/registry
http:
  addr: :5000
proxy:
  remoteurl: https://registry-1.docker.io
  username: <DOCKERHUB-USER>        # optional: use authenticated limits
  password: <DOCKERHUB-TOKEN>
```
```bash
docker run -d --name hub-mirror --restart unless-stopped -p 5001:5000 \
  -v "$PWD/config.yml":/etc/docker/registry/config.yml:ro \
  -v mirror-data:/var/lib/registry \
  registry:2
```
Point each Docker daemon at it, in `/etc/docker/daemon.json`:
```json
{
  "registry-mirrors": ["http://mirror.lan:5001"]
}
```
Plain HTTP mirrors also need `"insecure-registries": ["mirror.lan:5001"]`. Restart Docker, then `docker info` lists the mirror under `Registry Mirrors`.

- `registry-mirrors` only affects pulls of **Docker Hub** images with no registry name in them (`nginx`, `library/nginx`, `user/app`).
- Pulls fall back to Hub if the mirror is down.
- Store the Hub credentials in `config.yml` as a token with read access only.
- A mirror shares the storage of anything cached. Use `REGISTRY_STORAGE_DELETE_ENABLED` and the garbage-collect step above, or set a TTL: `proxy.ttl: 168h`.
- Alternatives that cover several upstream registries: Harbor proxy cache projects, Nexus, Artifactory, or `zot`.

---
## skopeo (copy and inspect without a daemon)
Works on registry-to-registry, no Docker daemon needed. Install: `sudo apt install skopeo`.

COMMAND | DESCRIPTION
---|---
`skopeo inspect docker://nginx:1.27` | Image metadata, tags and digest, without pulling
`skopeo inspect --raw docker://nginx:1.27 \| jq` | The raw manifest or manifest list
`skopeo list-tags docker://ghcr.io/OWNER/NAME` | Tags in a repository
`skopeo copy docker://nginx:1.27 docker://registry.lan:5000/nginx:1.27` | Copy between registries
`skopeo copy --all docker://nginx:1.27 docker://registry.lan:5000/nginx:1.27` | Copy all platforms of a multi-arch image
`skopeo copy docker://nginx:1.27 docker-archive:nginx.tar` | Save to a tar file
`skopeo copy docker-archive:nginx.tar docker://registry.lan:5000/nginx:1.27` | Load a tar into a registry
`skopeo copy docker://nginx:1.27 docker-daemon:nginx:1.27` | Load into the local Docker daemon
`skopeo sync --src docker --dest docker nginx registry.lan:5000/` | Sync all tags of a repository
`skopeo login ghcr.io` | Log in (shares `~/.docker/config.json` or the auth file)
`skopeo copy --dest-tls-verify=false ...` | Allow a plain HTTP or self-signed destination

## crane (go-containerregistry)
Small static binary for registry operations. Install: `go install github.com/google/go-containerregistry/cmd/crane@latest` or download a release.

COMMAND | DESCRIPTION
---|---
`crane ls REGISTRY/REPO` | List tags
`crane digest REGISTRY/REPO:TAG` | Digest of a tag (use it to pin)
`crane manifest REGISTRY/REPO:TAG \| jq` | Manifest
`crane config REGISTRY/REPO:TAG \| jq` | Image config (env, entrypoint, labels)
`crane copy SRC DST` | Copy an image between registries (preserves multi-arch)
`crane pull IMAGE out.tar` / `crane push out.tar IMAGE` | Save and load tarballs
`crane tag REGISTRY/REPO:TAG NEWTAG` | Add a tag server-side, no pull needed
`crane delete REGISTRY/REPO:TAG` | Delete (where the registry allows it)
`crane catalog REGISTRY` | List repositories
`crane auth login REGISTRY -u USER -p TOKEN` | Log in
`crane export IMAGE - \| tar -t` | List files in the image file system

`crane tag` is the clean way to promote an image from `1.2.3-rc1` to `1.2.3` or `latest` without rebuilding. The same registry operations are in `docker buildx imagetools create -t NEW:TAG OLD:TAG`.

---
## Tagging Strategy
RULE | WHY
---|---
Tag every build with an **immutable** identifier: the git short SHA (`app:3f2a9c1`) or build number | Reproducible, lets you roll back and trace a running container to a commit
Also publish **semver tags** for releases: `1.4.2`, `1.4`, `1` | Consumers choose how tightly to follow
Treat `latest` as "newest stable release" only, never as a deploy target | It moves, so two hosts can pull different images
Do not reuse a version tag after release | Moving tags break caches and rollbacks
Deploy by **digest** where it matters: `image: app@sha256:...` | Cannot change underneath you. Combine with a readable tag: `app:1.4.2@sha256:...` (Renovate can update both)
Add environment tags only as pointers (`staging`, `prod`) promoted with `crane tag` | Promotes the exact tested image
Set OCI labels: `org.opencontainers.image.source`, `.revision`, `.version`, `.created` | Traceability and GHCR repo linking
Build multi-arch (`--platform linux/amd64,linux/arm64`) under one tag | One name works on x86 and Arm hosts, see [Docker](docker.md)
Clean old tags with a retention rule (keep last N and all releases) | Registries grow forever otherwise, see [Docker Cleanup](docker-cleanup.md)

Example release tagging with Buildx:
```bash
SHA=$(git rev-parse --short HEAD)
docker buildx build --platform linux/amd64,linux/arm64 \
  -t ghcr.io/<OWNER>/app:"$SHA" \
  -t ghcr.io/<OWNER>/app:1.4.2 \
  -t ghcr.io/<OWNER>/app:1.4 \
  --label org.opencontainers.image.revision="$SHA" \
  --push .
```
Pin third-party images in Compose files to a version (and ideally a digest) and let Renovate propose updates, instead of following `latest`.

## See Also
- [Docker Buildx](buildx.md)
- [OCI Images](oci-images.md)
