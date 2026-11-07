# CI Docker Builds
Building, tagging, scanning and publishing container images from CI with Buildx. The examples target [GitHub Actions](github-actions.md) with Woodpecker ([Woodpecker CI](woodpecker-ci.md)) and GitLab ([GitLab CI/CD](gitlab-ci.md)) equivalents. For Dockerfile and CLI basics see [Docker](../docker/docker.md) and [Dockerfile](../docker/docker-file.md); for general pipeline structure see [CI/CD Overview](cicd.md).

Documentation: [Docker GitHub Actions](https://docs.docker.com/build/ci/github-actions/), [Cache backends](https://docs.docker.com/build/cache/backends/), [metadata-action](https://github.com/docker/metadata-action), [Trivy action](https://github.com/aquasecurity/trivy-action)

---
## Full GitHub Actions Workflow
Builds on every PR (no push), publishes to GHCR on `main` and on version tags, multi-arch, with cache, provenance and SBOM.
```yaml
name: Docker

on:
  push:
    branches: [main]
    tags: ["v*.*.*"]
  pull_request:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write          # push to GHCR
      id-token: write          # attestations
      attestations: write
    steps:
      - uses: actions/checkout@v7.0.1

      - uses: docker/setup-qemu-action@v4.4.0          # only needed for multi-arch via emulation
      - uses: docker/setup-buildx-action@v4.4.1

      - name: Log in to GHCR
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v4.8.0
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@v6.2.0
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,format=short
            type=raw,value=latest,enable={{is_default_branch}}

      - id: build
        uses: docker/build-push-action@v7.4.0
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          provenance: mode=max
          sbom: true

      - name: Attest build provenance
        if: github.event_name != 'pull_request'
        uses: actions/attest-build-provenance@v4.2.2
        with:
          subject-name: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          subject-digest: ${{ steps.build.outputs.digest }}
          push-to-registry: true
```
Image names must be lowercase; if your owner has capitals use `${{ github.repository_owner }}` lowercased in a prior step (`echo "IMAGE=${GITHUB_REPOSITORY,,}" >> "$GITHUB_ENV"`).

## metadata-action Tag Types
TAG RULE | OUTPUT
---|---
`type=ref,event=branch` | `main`, `feature-x`
`type=ref,event=pr` | `pr-42`
`type=ref,event=tag` | the git tag as-is
`type=semver,pattern={{version}}` | `1.2.3` from tag `v1.2.3`
`type=semver,pattern={{major}}.{{minor}}` | `1.2`
`type=sha` | `sha-abc1234` (add `format=long` for the full SHA)
`type=schedule,pattern=nightly` | `nightly` for scheduled runs
`type=raw,value=latest,enable={{is_default_branch}}` | `latest` only from the default branch
`flavor: latest=false` | Stop it adding `latest` automatically on tags

The action also emits OCI labels (`org.opencontainers.image.source`, `.revision`, `.created`, ...), which GHCR uses to link the package to the repo.

## Multi-Arch
APPROACH | NOTES
---|---
QEMU emulation (`setup-qemu-action` + `platforms: linux/amd64,linux/arm64`) | Simple, but arm64 builds on amd64 can be 5-20 times slower
Native runners (matrix with `runs-on: ubuntu-24.04-arm`, push by digest, merge manifests with `docker buildx imagetools create`) | Fast; more YAML
Cross-compile in the Dockerfile (`FROM --platform=$BUILDPLATFORM`, use `TARGETARCH`) | Best for Go/Rust, avoids emulation

```dockerfile
FROM --platform=$BUILDPLATFORM golang:1.24 AS build
ARG TARGETOS TARGETARCH
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o /out/app .

FROM gcr.io/distroless/static-debian12
COPY --from=build /out/app /app
ENTRYPOINT ["/app"]
```

## Layer Caching
BACKEND | USE | NOTES
---|---|---
`type=gha` | GitHub Actions cache | Easiest on GitHub; shares the 10 GB repo cache budget; `mode=max` caches intermediate stages
`type=registry,ref=<IMAGE>:buildcache` | Any CI | Works everywhere; add `mode=max,image-manifest=true,oci-mediatypes=true` for broad registry compatibility
`type=local,src=...,dest=...` | Self-hosted runners | Directory on disk; persist it between runs
`type=inline` | Quick start | Cache stored in the image itself; only `mode=min`

Registry cache example (works on Woodpecker, GitLab and GitHub):
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --cache-from type=registry,ref=ghcr.io/<OWNER>/<IMAGE>:buildcache \
  --cache-to type=registry,ref=ghcr.io/<OWNER>/<IMAGE>:buildcache,mode=max \
  --tag ghcr.io/<OWNER>/<IMAGE>:<TAG> --push .
```
Order Dockerfile instructions from least to most frequently changing (copy dependency manifests and install before copying the source), and use `.dockerignore`.

## Registries
REGISTRY | LOGIN
---|---
GHCR | username `${{ github.actor }}`, password `GITHUB_TOKEN` (job needs `packages: write`); outside Actions use a PAT with `write:packages`
Docker Hub | username + an access token (not the password) in secrets `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN`
GitLab registry | `$CI_REGISTRY_USER` / `$CI_REGISTRY_PASSWORD` for `$CI_REGISTRY`
Gitea/Forgejo | Personal access token with package scope against your host, see [Gitea (and Forgejo)](../tools/gitea.md)

Push to more than one registry by listing both in `images:` of metadata-action (one per line) and logging in to each.

## Scan with Trivy (Gate on Severity)
Build, scan, and only push if the scan passes.
```yaml
      - name: Build (load locally for scanning)
        uses: docker/build-push-action@v7.4.0
        with:
          context: .
          load: true
          tags: local/app:scan
          cache-from: type=gha

      - name: Trivy scan
        uses: aquasecurity/trivy-action@v0.36.0
        with:
          image-ref: local/app:scan
          format: table
          severity: CRITICAL,HIGH
          ignore-unfixed: true
          exit-code: "1"          # fail the job on findings

      - name: Push
        if: github.event_name != 'pull_request'
        uses: docker/build-push-action@v7.4.0
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
```
`load: true` only works for a single platform; scan the amd64 build and push the multi-arch one afterwards (cached, so cheap). Trivy from the CLI or in other CI systems:
```bash
trivy image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 ghcr.io/<OWNER>/<IMAGE>:<TAG>
trivy fs --scanners vuln,secret,misconfig .         # repo files, secrets and IaC
trivy config .                                      # Dockerfile / Compose / Terraform misconfig
```
Add accepted risks to a `.trivyignore` file with a comment and expiry. Pin the Trivy action to a full commit SHA (it is a security tool that runs with your registry context) and let [Renovate](renovate.md) bump it.

## Provenance, SBOM and Signing
FEATURE | HOW
---|---
Provenance attestation (BuildKit) | `provenance: mode=max` on build-push-action (default `mode=min` on push)
SBOM attestation (BuildKit) | `sbom: true`
GitHub artifact attestation | `actions/attest-build-provenance` with the image digest, `push-to-registry: true`
Verify attestation | `gh attestation verify oci://ghcr.io/<OWNER>/<IMAGE>@sha256:<DIGEST> --owner <OWNER>`
Inspect attestations | `docker buildx imagetools inspect ghcr.io/<OWNER>/<IMAGE>:<TAG> --format '{{ json .Provenance }}'`
Keyless signing | `cosign sign --yes ghcr.io/<OWNER>/<IMAGE>@sha256:<DIGEST>` using the job's OIDC token (`id-token: write`)

Attestations add extra manifests to the index; some old tools and registries show "unknown/unknown" platform entries. Set `provenance: false` if a consumer chokes on them.

## Woodpecker Version
```yaml
# .woodpecker/docker.yaml
when:
  - event: push
    branch: main
  - event: tag

steps:
  - name: publish
    image: woodpeckerci/plugin-docker-buildx
    settings:
      registry: ghcr.io
      repo: ghcr.io/<OWNER>/<IMAGE>
      tags: [latest, "${CI_COMMIT_SHA:0:8}"]
      platforms: linux/amd64,linux/arm64
      username: <USER>
      password:
        from_secret: ghcr_token
```
The plugin builds with BuildKit in a container and needs the repo to be **Trusted** (privileged). Check the plugin docs for the current tag-from-git-tag settings (`auto_tag`).

## GitLab Version
See the `docker:dind` job in [GitLab CI/CD](gitlab-ci.md); replace `docker build` with `docker buildx build --push` after `docker buildx create --use`, and use `$CI_REGISTRY_IMAGE` as the repo.

## Deploying the Image
Push the image, then update the host: `docker compose pull && docker compose up -d` ([Docker-Compose](../docker/docker-compose.md)), or run an update job over SSH/[Ansible-Playbook Cheat-Sheet](../tools/ansible-playbook.md). Deploy by digest or immutable tag (`sha-...`, `1.2.3`), not `latest`, so a rollback is a one-line change. Let [Renovate](renovate.md) bump image tags in Compose files.

## Troubleshooting
SYMPTOM | CAUSE AND FIX
---|---
`denied: permission_denied: write_package` (GHCR) | Job lacks `packages: write`, the package is linked to another repo, or the token is a PAT without `write:packages`
`invalid reference format` | Uppercase letters in the image name, or an empty tag from metadata-action (e.g. on a PR with no matching rule)
`exec format error` at run time | Image built for the wrong architecture; add the platform, or check `docker buildx imagetools inspect`
arm64 build takes 40 minutes | QEMU emulation; use native arm runners or cross-compile
`load` does not support multi-platform | Build a single platform with `load: true`, or push to a registry and scan the pushed image
Cache never hits | Cache key changed (different `scope`), `COPY . .` before dependency install, or `mode=min` hides intermediate layers
`unauthorized` pulling base image | Docker Hub rate limit; log in to Docker Hub in CI or mirror base images
Rate limit exceeded on `gha` cache | 10 GB repo budget; use `scope=` per image or switch to the registry backend
`Cannot connect to the Docker daemon` | No daemon on the runner: use the Docker socket, `docker:dind` service, or a container-less builder

## See Also
- [Docker Buildx](../docker/buildx.md)
- [Buildah](../docker/buildah.md)
