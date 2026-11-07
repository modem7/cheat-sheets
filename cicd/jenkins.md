# Jenkins
Jenkins is the long-standing self-hosted automation server. Pipelines are written as a `Jenkinsfile` in the repository (Groovy based, either declarative or scripted syntax), run on a controller plus agents, and extended with plugins. Use this sheet for pipeline syntax, the CLI, Docker deployment and backup. Nothing here was run against a live Jenkins: the syntax, commands and paths come from the Jenkins documentation and the official Docker image README, so treat the whole sheet as unverified until you have tried it, and use the built-in Pipeline Syntax snippet generator (`/pipeline-syntax` on your server) to confirm step arguments.

Documentation: [Jenkins docs](https://www.jenkins.io/doc/), [Pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
Project: [jenkinsci/jenkins](https://github.com/jenkinsci/jenkins), [jenkinsci/docker](https://github.com/jenkinsci/docker)

---
## Declarative Jenkinsfile
```groovy
pipeline {
    agent { label 'linux' }

    options {
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    parameters {
        string(name: 'TARGET', defaultValue: 'staging', description: 'Deploy target')
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Run the tests')
    }

    triggers {
        pollSCM('H/5 * * * *')
    }

    environment {
        REGISTRY = 'registry.example.com'
        REGISTRY_CREDS = credentials('registry-creds')
    }

    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
        stage('Test') {
            when { expression { params.RUN_TESTS } }
            parallel {
                stage('Unit') {
                    steps { sh 'make test-unit' }
                }
                stage('Lint') {
                    steps { sh 'make lint' }
                }
            }
        }
        stage('Deploy') {
            when { branch 'main' }
            steps {
                sh './deploy.sh "$TARGET"'
            }
        }
    }

    post {
        always { junit allowEmptyResults: true, testResults: 'reports/*.xml' }
        failure { echo 'Build failed' }
        cleanup { cleanWs() }
    }
}
```

`credentials('ID')` in `environment` for a username and password credential also defines `NAME_USR` and `NAME_PSW`. `cleanWs()` comes from the Workspace Cleanup plugin.

## Declarative Sections
SECTION | PURPOSE
---|---
`agent` | Where to run: `any`, `none`, `{ label 'X' }`, `{ docker { image 'IMG' args '-v ...' } }`, `{ dockerfile true }`, `{ kubernetes { ... } }` (needs the matching plugin)
`stages` / `stage` / `steps` | The pipeline body
`environment` | Environment variables, including `credentials('ID')`
`options` | `timeout`, `retry`, `timestamps`, `disableConcurrentBuilds`, `buildDiscarder`, `skipDefaultCheckout`
`parameters` | `string`, `booleanParam`, `choice`, `password`, `text`, `file`
`triggers` | `cron('...')`, `pollSCM('...')`, `upstream(...)`
`tools` | Tools configured under Manage Jenkins (for example `maven`, `jdk`)
`when` | `branch`, `tag`, `expression { }`, `environment`, `changeRequest`, `not`, `allOf`, `anyOf`; add `beforeAgent true` to skip agent allocation
`parallel` | Run nested stages at the same time
`matrix` | Run a stage over combinations of `axes`
`input` | Pause for approval (`input message: 'Deploy?'`)
`post` | `always`, `success`, `failure`, `unstable`, `changed`, `fixed`, `regression`, `aborted`, `cleanup`

## Scripted Pipeline
```groovy
node('linux') {
    try {
        stage('Checkout') {
            checkout scm
        }
        stage('Build') {
            sh 'make build'
        }
        stage('Test') {
            parallel(
                unit: { sh 'make test-unit' },
                lint: { sh 'make lint' }
            )
        }
    } catch (err) {
        currentBuild.result = 'FAILURE'
        throw err
    } finally {
        cleanWs()
    }
}
```

Use scripted syntax when you need real Groovy control flow; otherwise prefer declarative, which is validated before it runs.

## Common Steps
STEP | DESCRIPTION
---|---
`sh 'cmd'` / `bat 'cmd'` / `pwsh 'cmd'` | Run a shell command (Unix, Windows batch, PowerShell)
`sh(script: 'cmd', returnStdout: true).trim()` | Capture output
`checkout scm` | Check out the repository that holds the Jenkinsfile
`git url: 'URL', branch: 'main'` | Clone a repository
`dir('path') { ... }` | Run steps in a directory
`withEnv(['A=1']) { ... }` | Set environment variables for a block
`withCredentials([string(credentialsId: 'ID', variable: 'TOKEN')]) { ... }` | Bind a secret for the block (also `usernamePassword`, `file`, `sshUserPrivateKey`)
`stash name: 'x', includes: 'dist/**'` / `unstash 'x'` | Pass files between stages or agents
`archiveArtifacts artifacts: 'dist/**', fingerprint: true` | Keep build outputs
`junit 'reports/*.xml'` | Publish test results
`timeout(time: 10, unit: 'MINUTES') { ... }` / `retry(3) { ... }` | Limit or repeat a block
`input message: 'Proceed?'` | Wait for a person
`build job: 'other-job', wait: false` | Trigger another job
`error 'message'` | Fail the build
`@Library('NAME') _` | Load a shared library at the top of the Jenkinsfile

## Credentials
KIND | USE
---|---
Secret text | `string(credentialsId: 'ID', variable: 'VAR')` or `credentials('ID')`
Username and password | `usernamePassword(credentialsId: 'ID', usernameVariable: 'U', passwordVariable: 'P')`
SSH key | `sshUserPrivateKey(credentialsId: 'ID', keyFileVariable: 'KEY')`
Secret file | `file(credentialsId: 'ID', variable: 'FILE')`

Add them under Manage Jenkins, Credentials, scoped to the narrowest folder or system scope that works. Single quote `sh` strings that use secrets (`sh 'echo "$TOKEN" | tool login --stdin'`) so Groovy does not interpolate the secret into the command line, and see [CI/CD Overview](cicd.md#secrets-handling).

## jenkins-cli
Download the client jar from your own server and use an API token for authentication.

```bash
curl -O https://jenkins.example.com/jnlpJars/jenkins-cli.jar
export JENKINS_URL=https://jenkins.example.com
java -jar jenkins-cli.jar -auth USER:API_TOKEN who-am-i
```

COMMAND | DESCRIPTION
---|---
`java -jar jenkins-cli.jar -s URL -auth USER:TOKEN help` | List every command available on that server
`... version` / `who-am-i` | Server version, current identity
`... list-jobs [FOLDER]` | List jobs
`... build JOB -s -v -p KEY=VALUE` | Start a job, wait (`-s`), show output (`-v`), pass parameters (`-p`)
`... console JOB [BUILD]` | Show a build's console output
`... get-job JOB > job.xml` / `create-job NAME < job.xml` / `update-job JOB < job.xml` | Export, create or replace a job definition
`... delete-job JOB` | Delete a job (destructive)
`... disable-job JOB` / `enable-job JOB` | Disable or enable a job
`... list-plugins` | Installed plugins
`... install-plugin NAME` | Install a plugin (`-restart` restarts afterwards)
`... safe-restart` / `restart` | Restart once running builds finish, or immediately
`... quiet-down` / `cancel-quiet-down` | Stop starting new builds, or resume
`... reload-configuration` | Reload configuration from disk
`... declarative-linter < Jenkinsfile` | Validate a declarative Jenkinsfile
`... groovy = < script.groovy` | Run a Groovy script on the controller (powerful: admin only)

Authentication options (`-auth`, `-http`, `-ssh`, `-webSocket`) and the exact command list vary by version and installed plugins: `help` on your server is authoritative.

## Plugins
TASK | HOW
---|---
Install in the UI | Manage Jenkins, Plugins
Install in a Docker image | `jenkins-plugin-cli --plugins git workflow-aggregator` or `-f plugins.txt` (one `name:version` per line)
List what the CLI would install | `jenkins-plugin-cli --list` (flag per the image README, unverified)
Pin versions | Put `name:version` in `plugins.txt` so image builds are reproducible
Update | Manage Jenkins, Plugins, Updates; back up first

```dockerfile
FROM jenkins/jenkins:lts-jdk21
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli -f /usr/share/jenkins/ref/plugins.txt
```

## Running in Docker
```bash
docker run -d --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts-jdk21
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

```yaml
services:
  jenkins:
    image: jenkins/jenkins:lts-jdk21
    restart: unless-stopped
    ports:
      - "8080:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
    environment:
      JAVA_OPTS: "-Xmx1g"
volumes:
  jenkins_home:
```

SETTING | MEANING
---|---
Port `8080` | Web UI
Port `50000` | Inbound (JNLP) agent connections
`/var/jenkins_home` | All state; keep it on a volume
`JAVA_OPTS` | JVM options for the controller
`JENKINS_OPTS` | Jenkins options such as `--prefix=/jenkins`
Pin the tag | Use an explicit LTS tag rather than `latest`

Running builds in Docker from Jenkins needs a Docker CLI and socket (or a Docker cloud). Mounting `/var/run/docker.sock` gives builds control of the host, so prefer separate agents.

## Agents
METHOD | DETAILS
---|---
Inbound (WebSocket or JNLP) agent | Create the node in Manage Jenkins, Nodes, then run the agent with the node's secret
`jenkins/inbound-agent` image | `docker run -d jenkins/inbound-agent -url https://jenkins.example.com -secret SECRET -name AGENT_NAME` (add `-webSocket` to use WebSocket); `JENKINS_URL`, `JENKINS_SECRET` and `JENKINS_AGENT_NAME` environment variables are also read
SSH agent | Jenkins connects out to the agent over SSH with a credential
Cloud agents | Docker or Kubernetes plugins create agents per build
Labels | Select with `agent { label 'linux && docker' }`

Keep the controller's executors at zero in production and run builds on agents.

## Configuration as Code
The Configuration as Code plugin (JCasC) describes the controller in YAML. Point Jenkins at the file with the `CASC_JENKINS_CONFIG` environment variable.

```yaml
jenkins:
  systemMessage: "Managed by configuration as code"
  numExecutors: 0
unclassified:
  location:
    url: https://jenkins.example.com/
```

## Backup and Restore
WHAT | NOTES
---|---
`$JENKINS_HOME/config.xml` and other top level `*.xml` | Global configuration
`jobs/` | Job definitions and build history (history can be large; exclude `builds/` if you only need configuration)
`nodes/` | Agent definitions
`plugins/*.jpi` | Plugin files (or record the list in `plugins.txt` and reinstall)
`secrets/` and `credentials.xml` | Needed to decrypt credentials; protect the backup
`users/` | User records
Skip | `workspace/`, caches, `logs/`

```bash
docker run --rm -v jenkins_home:/data:ro -v "$PWD":/backup alpine:3.22 \
  tar czf /backup/jenkins-home.tgz -C /data .
```

Stop Jenkins (or use `safe-restart` and a quiet period) for a consistent copy, and test a restore. Moving to a new server means restoring the same `secrets/` along with `credentials.xml`.

## Useful URLs
PATH | PURPOSE
---|---
`/pipeline-syntax` | Snippet generator for step arguments
`/manage` | Manage Jenkins
`/script` | Script console (Groovy on the controller, admin only)
`/safeRestart` | Restart when idle (POST in current versions)
`/quietDown` / `/cancelQuietDown` | Stop or resume starting builds
`/restart` | Restart now (POST)

## Troubleshooting
SYMPTOM | FIX
---|---
Locked out or forgot the admin password | Read `secrets/initialAdminPassword` for a new install; otherwise disable security temporarily in `config.xml` with the controller stopped (restore it straight after)
Pipeline waits for an executor | No agent with that label, or all busy; check Manage Jenkins, Nodes
Secret printed in the log | Use `withCredentials` or `credentials()`; masking only covers the exact string
`script not permitted` | Sandbox blocks the method: use a plugin step, or an admin approves it under In-process Script Approval
Plugin upgrade broke Jenkins | Restore `plugins/` from backup or pin the earlier version in `plugins.txt`
Agent will not connect | Check `-url`, secret, the node name, and that port `50000` (or WebSocket over `8080`) is reachable
Build disk fills up | Set `buildDiscarder`, clean workspaces, move `JENKINS_HOME` to larger storage

## See Also
- [CI/CD Overview](cicd.md)
- [Drone CI](drone-ci.md)
- [Woodpecker CI](woodpecker-ci.md)
- [GitLab CI/CD](gitlab-ci.md)
- [Docker Compose](../docker/docker-compose.md)
- [Docker](../docker/docker.md)
