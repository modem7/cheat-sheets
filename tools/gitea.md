# Gitea (and Forgejo)
Gitea is a lightweight, self-hosted Git service written in Go with issues, pull requests, packages and built-in CI (Gitea Actions, mostly compatible with GitHub Actions workflows). **Forgejo** is a community fork with the same layout and a very similar setup. Compare with [[github-cli]] and [[gitlab]]; basics of Git itself are in [[git]].

Documentation: [Gitea Docs](https://docs.gitea.com), [Forgejo Docs](https://forgejo.org/docs/latest/)

---
## Run with Docker Compose
```yaml
services:
  gitea:
    image: gitea/gitea:latest
    container_name: gitea
    restart: unless-stopped
    environment:
      - USER_UID=1000
      - USER_GID=1000
      - GITEA__database__DB_TYPE=sqlite3
    ports:
      - "3000:3000"
      - "2222:22"
    volumes:
      - ./gitea:/data
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
```
Open `http://<HOST>:3000` and complete the install page (the first registered user, or the admin you create, becomes the administrator). Pin a version tag instead of `latest`, and check the docs for the current image name, as the registry location has moved. Use PostgreSQL or MariaDB for more than a few users ([[postgres]], [[mariadb]]). See [[docker-compose]].

Settings can be given as `GITEA__section__KEY` environment variables, matching `app.ini` (for example `GITEA__server__ROOT_URL`).

## Git over SSH
The container's SSH is mapped to host port 2222. Clone with `git clone ssh://git@HOST:2222/USER/REPO.git`, or add `Port 2222` for the host in `~/.ssh/config` ([[openssh]]).

## tea CLI
`tea` is the official Gitea CLI (`brew install tea`, see [[homebrew]]).

COMMAND | DESCRIPTION
---|---
`tea login add --name home --url https://git.example.com --token <TOKEN>` | Add a login
`tea login list` | List logins
`tea repos list` | List repositories
`tea repos create --name NAME` | Create a repository
`tea pulls create --title "T"` | Open a PR
`tea pulls list` | List PRs
`tea issues create --title "T"` | Create an issue
`tea issues list` | List issues
`tea open` | Open the repo in the browser

## Admin Commands (inside the container)
```bash
docker exec -u git gitea gitea admin user create --username admin --password 'CHANGE-ME' --email admin@example.com --admin
docker exec -u git gitea gitea admin user list
docker exec -u git gitea gitea dump -c /data/gitea/conf/app.ini
```
`gitea dump` creates a backup archive of data and config. Run it as the `git` user (`-u git`).

## Actions Runner
Enable Actions in `app.ini` (`[actions] ENABLED = true`), then run `act_runner` and register it with a token from Site Administration > Actions > Runners:
```bash
docker run -d --name gitea-runner --restart unless-stopped \
  -e GITEA_INSTANCE_URL=https://git.example.com \
  -e GITEA_RUNNER_REGISTRATION_TOKEN=<TOKEN> \
  -v /var/run/docker.sock:/var/run/docker.sock \
  gitea/act_runner:latest
```
Workflows live in `.gitea/workflows/` (`.github/workflows/` is also read).

## Mirroring
A repository can mirror another (pull) or push to another host on a schedule. Use it to keep a copy of GitHub repositories locally. Set it under New Migration or the repository settings.

## Not Verified
Written from knowledge and not run here. Image names, runner variables and `tea` flags change between releases, so check the docs.
