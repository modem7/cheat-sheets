# Container Scanning
Vulnerability scanners compare the packages in an image, filesystem or repo against CVE databases, and can also check IaC for misconfiguration and find embedded secrets. This sheet covers Trivy (all-rounder), Grype and Syft (scanner plus SBOM generator). Used with [Docker](../docker/docker.md), [Dockerfile](../docker/docker-file.md) and [Kubernetes](../kubernetes/kubernetes.md); for secrets in Git see [Secret Scanning](secret-scanning.md).

Documentation: [Trivy](https://trivy.dev/latest/docs/) · [Grype](https://github.com/anchore/grype) · [Syft](https://github.com/anchore/syft)

## Install
```bash
# Trivy (Debian/Ubuntu apt repo is documented at trivy.dev), or:
brew install trivy grype syft
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image <IMAGE>
```

## Trivy
COMMAND | DESCRIPTION
---|---
`trivy image <IMAGE>` | Scan an image (pulled from a registry, or the local Docker daemon)
`trivy image --severity HIGH,CRITICAL <IMAGE>` | Filter by severity
`trivy image --ignore-unfixed <IMAGE>` | Hide CVEs with no fix available
`trivy image --exit-code 1 --severity CRITICAL <IMAGE>` | Fail (for CI) on criticals
`trivy image --scanners vuln,secret,misconfig <IMAGE>` | Choose scanners (default is `vuln,secret`)
`trivy image -f json -o report.json <IMAGE>` | JSON report (`table`, `json`, `sarif`, `cyclonedx`, `spdx-json`)
`trivy image --input image.tar` | Scan a `docker save` tarball
`trivy fs .` | Scan a project directory (lockfiles, secrets)
`trivy repo https://github.com/<ORG>/<REPO>` | Scan a remote repo
`trivy config .` | Check Dockerfiles, Compose, Kubernetes and Terraform for misconfigurations
`trivy k8s --report summary cluster` | Scan a running Kubernetes cluster
`trivy image --format cyclonedx -o sbom.json <IMAGE>` | Generate an SBOM
`trivy sbom sbom.json` | Scan an existing SBOM
`trivy image --skip-db-update <IMAGE>` | Use the cached DB (offline/air-gapped)
`trivy image --download-db-only` | Just refresh the vulnerability DB
`trivy clean --all` | Clear caches

### Ignore Findings
`.trivyignore` (one CVE per line, optional expiry and comment):
```text
# not reachable, upstream fix pending
CVE-2024-12345 exp:2026-12-31
```
Rich ignores (paths, purls) go in `trivy.yaml` / `.trivyignore.yaml`; see the Trivy filtering docs.

### CI (GitHub Actions)
```yaml
- uses: aquasecurity/trivy-action@<TAG>
  with:
    image-ref: ghcr.io/<OWNER>/<IMAGE>:${{ github.sha }}
    severity: CRITICAL,HIGH
    ignore-unfixed: true
    exit-code: "1"
```
Pin the action to a tag or commit SHA. Scan the freshly built image before pushing the `latest` tag.

## Grype and Syft
COMMAND | DESCRIPTION
---|---
`grype <IMAGE>` | Scan an image
`grype dir:.` | Scan a directory
`grype sbom:./sbom.json` | Scan an SBOM
`grype <IMAGE> --fail-on high` | Exit non-zero at or above a severity
`grype <IMAGE> --only-fixed` | Only CVEs that have a fix
`grype <IMAGE> -o json` | Output as `table`, `json`, `sarif`, `cyclonedx`
`grype db update` | Update the vulnerability DB
`grype db status` | Show the DB build date
`syft <IMAGE> -o spdx-json=sbom.spdx.json` | Generate an SBOM
`syft <IMAGE> -o cyclonedx-json=sbom.cdx.json` | CycloneDX SBOM
`syft dir:.` | Catalogue a directory

`.grype.yaml` ignore rules:
```yaml
ignore:
  - vulnerability: CVE-2024-12345
  - package:
      name: busybox
      type: apk
```

## Reducing Findings
- Pick small bases (`alpine`, `debian-slim`, distroless) and multi-stage builds ([Dockerfile](../docker/docker-file.md)).
- Pin by digest (`image: nginx@sha256:...`) and let Renovate raise update PRs.
- Run containers as non-root, read-only filesystem, drop capabilities:
```yaml
services:
  app:
    image: ghcr.io/example/app:1.2.3
    user: "1000:1000"
    read_only: true
    cap_drop: [ALL]
    security_opt: ["no-new-privileges:true"]
    tmpfs: [/tmp]
```
See [Docker-Compose](../docker/docker-compose.md).
- Rescan on a schedule, because new CVEs appear against old images.

## Troubleshooting
SYMPTOM | FIX
---|---
`failed to download vulnerability DB` / rate limited | Retry later, or mirror the DB with `--db-repository`; use `--skip-db-update` once cached
Image not found | Pull it first, or use `--image-src docker,podman,remote` to pick where to look
Scan is slow in CI | Cache `~/.cache/trivy` between runs
Same CVE shows in Trivy but not Grype (or vice versa) | Databases and matching differ; pick one gate and use the other as a cross-check
Noise from unfixable OS CVEs | `--ignore-unfixed` / `--only-fixed`, or rebase to a newer base image
