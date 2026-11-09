# Snyk
Snyk is a developer security platform with a CLI that scans dependencies (`snyk test`), source code (`snyk code test`), container images and IaC. It needs a Snyk account and token and sends results to Snyk's service, unlike purely local scanners such as [Trivy](container-scanning.md). Use it where you already have a Snyk organisation, or on the free tier for personal projects.

Documentation: [Snyk CLI](https://docs.snyk.io/developer-tools/snyk-cli)

## Install
COMMAND | DESCRIPTION
---|---
`npm install snyk -g` | Via npm
`brew tap snyk/tap && brew install snyk/tap/snyk` | Homebrew
`scoop bucket add snyk https://github.com/snyk/scoop-snyk` then `scoop install snyk` | Scoop on Windows
`docker pull snyk/snyk` | Docker image (`snyk/snyk:node` and other language images exist)
`curl --compressed https://downloads.snyk.io/cli/stable/snyk-linux -o snyk` | Linux binary, then `chmod +x snyk` and move it onto `PATH`

Binary names for other platforms include `snyk-linux-arm64`, `snyk-alpine`, `snyk-macos` and `snyk-macos-arm64`.

## Authenticate
COMMAND | DESCRIPTION
---|---
`snyk auth` | Browser sign-in
`snyk auth <TOKEN>` | Token on the command line (ends up in shell history)
`snyk config set api=<TOKEN>` | Store the token
`export SNYK_TOKEN=<TOKEN>` | Environment variable, best for CI
`snyk config environment SNYK-EU-01` | Use a non-default region before authenticating (`SNYK-US-02` and `SNYK-AU-01` also exist)

In Docker pass `-e SNYK_TOKEN`. Keep tokens in CI secrets, never in the repository.

## Scan
COMMAND | DESCRIPTION
---|---
`snyk test` | Open source dependencies in the current project
`snyk monitor` | Snapshot the project to Snyk for ongoing monitoring
`snyk code test [<PATH>]` | Static analysis of your own code
`snyk container test <IMAGE>` | Image vulnerabilities
`snyk container test <IMAGE> --file=Dockerfile` | Add base image upgrade advice
`snyk container monitor <IMAGE> --project-name=<NAME>` | Monitor an image
`snyk iac test [<PATH>]` | Terraform, Kubernetes and similar misconfigurations
`snyk sbom --format=cyclonedx1.6+json` | Generate an SBOM (needs an Enterprise plan)
`snyk ignore --id=<ISSUE_ID> --reason=<TEXT> --expiry=<DATE>` | Ignore an issue in `.snyk`

## Common Flags
FLAG | DESCRIPTION
---|---
`--severity-threshold=<low\|medium\|high\|critical>` | Report only this level and above (`snyk code test` has no `critical`)
`--json` | JSON output
`--sarif`, `--sarif-file-output=<PATH>` | SARIF for code scanning tools
`--all-projects` | Scan every manifest in the tree
`--exclude=<A>,<B>` | Skip directories or files by name (with `--all-projects`)
`--detection-depth=<N>` | How deep to look for manifests
`--dev` | Include dev dependencies (default is production only)
`--org=<ID_OR_SLUG>` | Which Snyk organisation
`--project-name=<NAME>` | Name in the Snyk UI
`--fail-on=<all\|upgradable\|patchable>` | Fail only on fixable issues
`--file=<PATH>` | Manifest or Dockerfile to use
`-d` | Debug output

## Exit Codes
CODE | MEANING
---|---
`0` | No issues found
`1` | Issues found
`2` | Failure (run with `-d`)
`3` | No supported projects found

CI usually fails the build on `1`. Treat `2` as an infrastructure problem, not a clean result.

## The `.snyk` File
YAML policy file for ignores and exclusions.

```yaml
version: v1.25.0
ignore:
  SNYK-JS-EXAMPLE-0000000:
    - '*':
        reason: Not reachable in our usage
        expires: 2027-03-01T00:00:00.000Z
```

Ignores in `.snyk` are not supported for Snyk Code. Always set a reason and an expiry. The `version` value above is an example, so use what `snyk ignore` writes.

## CI
GitHub Actions with the official action:

```yaml
- uses: snyk/actions/node@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

Add `with: command: monitor` to monitor instead of test. Pin the action to a tag or commit, and see [GitHub Actions](../cicd/github-actions.md). The README says all Snyk actions support code scanning upload, but the exact step was not verified.

## Free Tier
The pricing page listed test limits for the free plan (Open Source, Code, IaC and Container). Whether each is monthly was unclear, so check [snyk.io/plans](https://snyk.io/plans/) before relying on it.

## Not Verified
`snyk redteam` (its docs page was not found), `snyk aibom test`, the Docker action's `uses:` line, and Snyk plan limits. `snyk aibom` is documented for Python, Java, JavaScript and Go projects and writes CycloneDX 1.6 JSON.

## See Also
- [Container Scanning](container-scanning.md)
- [Secret Scanning](secret-scanning.md)
- [ASPM](aspm.md)
- [Application Security Tools](appsec-tools.md)
