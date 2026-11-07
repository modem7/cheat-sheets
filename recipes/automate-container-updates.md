# Automate Container Updates Safely
Keep Docker Compose stacks current without surprises: pin image tags and digests in git, let Renovate propose each update as a pull request, let Diun tell you about images Renovate does not manage, and apply merged changes with a tested pull-and-recreate routine that can be rolled back.

Documentation: [Renovate docs](https://docs.renovatebot.com) · [Renovate: Docker](https://docs.renovatebot.com/docker/) · [Diun documentation](https://crazymax.dev/diun/)
Project: [crazy-max/diun](https://github.com/crazy-max/diun)

> **Verification:** the `renovate.json` below passed `renovate-config-validator --strict` (via `npx`), and Diun (v4.33.1) was started in a container with the environment variables below, loaded its configuration, scheduled the cron job and reported healthy through `diun healthcheck`. Not run: a real Renovate pull request, the Diun notification delivery, and the update script on a live stack *(unverified)*.

## Goal
Every image in your stacks has an explicit version. New versions arrive as reviewable pull requests (patch updates merge themselves after a waiting period, majors need your approval), you get a notification for anything that falls outside Renovate, and a failed update can be undone by reverting one commit.

## Prerequisites
- Compose stacks kept in a Git repository (the directory layout of [Docker Service Deploy](docker-service-deploy.md)), with secrets and `.env` files **not** committed ([SOPS and age](../security/sops-age.md) if you want them in git encrypted)
- Renovate running for that repository, either the hosted Mend app or self-hosted ([Renovate](../cicd/renovate.md))
- A tested backup before you automate anything ([Off-Site Docker Host Backup with restic](offsite-docker-host-backup.md))
- Healthchecks in your Compose files, so a bad update shows as `unhealthy`

## Steps
### 1. Know the three kinds of update tool
TOOL | WHAT IT DOES | RISK
---|---|---
Renovate | Opens a pull request that edits the tag or digest in your files; you merge it | Low: every change is reviewed and recorded in git
Diun | Watches registries and **notifies** you about new tags or digests; changes nothing | Low: information only
Watchtower | Pulls new images and recreates containers by itself | High: unreviewed, no history. The `containrrr/watchtower` repository is **archived** (checked 7 November 2026, last push 17 December 2025), so it no longer receives fixes. Do not start new set-ups on it

The rest of this recipe uses Renovate to change things and Diun to watch.

### 2. Pin everything
`latest` and floating tags make an update happen on whichever day you recreate a container. Use an exact version tag, and add the digest so a retagged image cannot change under you:
```yaml
services:
  app:
    image: ghcr.io/example/app:1.2.3@sha256:<DIGEST>
```
Renovate adds the digests for you (step 3), so write only the tag. Keep the tag exact (`1.2.3`, not `1` or `latest`) except where the upstream project documents a rolling tag you accept. Do the same for the `FROM` lines of your own Dockerfiles ([Dockerfile](../docker/docker-file.md), [OCI Images](../docker/oci-images.md)).

### 3. Configure Renovate
`renovate.json` in the stacks repository:
```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended", "docker:pinDigests"],
  "timezone": "Europe/London",
  "schedule": ["before 6am on monday"],
  "packageRules": [
    {
      "description": "Automerge patch updates of images, once they have been out for a few days",
      "matchManagers": ["docker-compose", "dockerfile"],
      "matchUpdateTypes": ["patch", "digest"],
      "minimumReleaseAge": "3 days",
      "automerge": true
    },
    {
      "description": "Majors need a human and a wait",
      "matchUpdateTypes": ["major"],
      "dependencyDashboardApproval": true,
      "minimumReleaseAge": "7 days",
      "addLabels": ["major"]
    },
    {
      "description": "Databases are upgraded by hand, with a dump and a restore",
      "matchPackageNames": ["postgres", "mariadb", "mysql", "redis"],
      "matchUpdateTypes": ["major", "minor"],
      "enabled": false
    }
  ]
}
```
```bash
npx --yes --package renovate -- renovate-config-validator --strict
```
What the rules do ([Renovate](../cicd/renovate.md), `packageRules`, automerge and schedules):
- `docker:pinDigests` makes Renovate pin the digest of every image it finds.
- Patches and digest-only updates automerge after three days. Automerge only merges when required checks are green, so give the repository a CI check such as `docker compose config` ([CI Recipes](../cicd/ci-recipes.md)). Without any check, Renovate will merge as soon as the schedule allows.
- Majors wait seven days and need a tick on the **Dependency Dashboard** before a pull request is created.
- Database engines are left alone: a major or minor upgrade needs a dump and a restore ([Database Dumps](../backup/database-dumps.md)).
- The Dependency Dashboard issue lists every detected image, so open it after the first run and check that your Compose files were found.

### 4. Watch what Renovate does not see
Images started outside Git (a quick `docker run`), or tags you deliberately do not pin, are covered by Diun. `/opt/stacks/diun/compose.yaml`:
```yaml
services:
  diun:
    image: crazymax/diun:<VERSION>
    command: serve
    restart: unless-stopped
    environment:
      TZ: Europe/London
      DIUN_WATCH_SCHEDULE: "0 6 * * *"
      DIUN_WATCH_JITTER: 30s
      DIUN_PROVIDERS_DOCKER: "true"
      DIUN_PROVIDERS_DOCKER_WATCHBYDEFAULT: "false"
      DIUN_NOTIF_NTFY_ENDPOINT: https://ntfy.example.com
      DIUN_NOTIF_NTFY_TOPIC: homelab-updates
    volumes:
      - ./data:/data
      - /var/run/docker.sock:/var/run/docker.sock:ro
    healthcheck:
      test: ["CMD", "diun", "healthcheck"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 60s
```
Opt a container in with a label, in its own Compose file:
```yaml
    labels:
      - diun.enable=true
```
With `WATCHBYDEFAULT` set to `false`, only labelled containers are watched. Other labels: `diun.watch_repo=true` (watch all tags), `diun.include_tags` and `diun.exclude_tags` (semicolon-separated regular expressions) and `diun.max_tags`. The database in `./data` holds the image manifests Diun has seen. Diun supports many notifiers besides ntfy (e-mail, Slack, Telegram, webhook); see its [notification docs](https://crazymax.dev/diun/notif/). The Docker socket gives the container control of Docker, so it is mounted read-only (read-only still allows reading everything about your containers); consider a socket proxy on exposed hosts ([Docker Service Deploy](docker-service-deploy.md)).

Do not run Diun and Renovate pull requests for the same images if the noise bothers you: label only what Renovate does not manage.

### 5. Apply merged updates
Renovate edits the repository, not your host. Apply on the host with an explicit routine that backs up first and checks health afterwards. `/usr/local/bin/stack-update.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail

STACK_DIR=/opt/stacks/${1:?usage: stack-update.sh STACK}
cd "$STACK_DIR"

git pull --ff-only
docker compose config -q
docker compose pull
docker compose up -d --remove-orphans

# Wait up to two minutes for every service with a healthcheck to be healthy.
for _ in $(seq 1 24); do
  if ! docker compose ps --format '{{ .Health }}' | grep -qE 'starting|unhealthy'; then
    echo "stack is healthy"
    exit 0
  fi
  sleep 5
done
echo "stack did not become healthy" >&2
docker compose ps
exit 1
```
Run it by hand while you build trust (`stack-update.sh app`), or from a systemd timer or a CI job that connects over SSH once you are happy ([Woodpecker CI](../cicd/woodpecker-ci.md), [GitHub Actions](../cicd/github-actions.md)). Take a fresh backup before any update that includes a database image or a major version.

### 6. Prune old images
```bash
docker image prune -f
```
`docker image prune -f` removes dangling images only. Keep the previous image until the update has proven itself; see [Docker Cleanup](../docker/docker-cleanup.md) before adding `-a`.

## Verify
```bash
npx --yes --package renovate -- renovate-config-validator --strict
docker compose -f /opt/stacks/diun/compose.yaml ps
docker exec diun diun healthcheck
docker compose -f /opt/stacks/app/compose.yaml ps
```
Open the Dependency Dashboard issue and check that it lists your images. Wait for the first Renovate pull request and check that it edits the tag or digest and nothing else. Test the whole path once on a low-risk stack: merge a patch update, run the update script and confirm the stack is healthy. Test Diun's notification by adding the `diun.enable=true` label to one container running an older tag.

## Troubleshooting
SYMPTOM | FIX
---|---
Renovate opens no pull requests | Is the repository onboarded; check the Dependency Dashboard and the Renovate logs; the schedule may be outside the window
Compose images are not listed on the dashboard | The file name or location is not matched by the `docker-compose` manager; check the manager's file patterns in the Renovate docs
Renovate cannot pin a digest for a private image | Add registry credentials in the Renovate host rules ([Renovate](../cicd/renovate.md))
Automerge merged something that broke the stack | Add a real CI check, raise `minimumReleaseAge`, or turn `automerge` off for that package
Diun sends nothing | `docker logs diun`; the container needs the label, and `firstCheckNotif` defaults to `false` so images already known are not announced on the first run
Diun reports a tag you do not care about | Add `diun.include_tags` or `diun.exclude_tags`, or `diun.max_tags`
Update left a container `unhealthy` | Roll back (below), then read `docker compose logs` before trying again
Pull is slow or rate limited | Authenticate to the registry (`docker login`) or use a pull-through cache ([Docker Registry](../docker/docker-registry.md))

## Rollback / Cleanup
- **Roll back one update:** revert the merge commit in the stacks repository (`git revert <COMMIT>`), then run the update script again. Because the old digest is in git, you get the same image back. Restore the database from the pre-update backup if a migration has run ([Restore-Test a Backup](restore-test-a-backup.md)).
- **Stop automatic merging:** set `"automerge": false` in the package rule, or disable the rule.
- **Remove Diun:** `docker compose down` in `/opt/stacks/diun`, then delete `./data` (destructive: forgets the known manifests).
- **Remove Renovate:** uninstall the app or remove the repository from its configuration, and delete `renovate.json`.

## Related Sheets
- [Renovate](../cicd/renovate.md) · [CI Recipes](../cicd/ci-recipes.md) · [CI Docker Builds](../cicd/ci-docker-builds.md) · [Woodpecker CI](../cicd/woodpecker-ci.md) · [GitHub Actions](../cicd/github-actions.md)
- [Docker-Compose](../docker/docker-compose.md) · [Docker Cleanup](../docker/docker-cleanup.md) · [Docker Registry](../docker/docker-registry.md) · [OCI Images](../docker/oci-images.md) · [Dockerfile](../docker/docker-file.md)
- [Container Scanning](../security/container-scanning.md) · [SOPS and age](../security/sops-age.md) · [Database Dumps](../backup/database-dumps.md)
- [Docker Service Deploy](docker-service-deploy.md) · [Off-Site Docker Host Backup with restic](offsite-docker-host-backup.md) · [Restore-Test a Backup](restore-test-a-backup.md)
