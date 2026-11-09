# Application Security Tools
Command-line scanners that complement [Trivy](container-scanning.md) and [gitleaks](secret-scanning.md): Semgrep for code, OSV-Scanner and Grype for dependencies, Syft for SBOMs, Checkov for IaC, OpenSSF Scorecard for repo hygiene and cosign for signing. Feed their output into [ASPM](aspm.md) tooling or fail CI on it.

## Semgrep
Static analysis of source code with rules.

Documentation: [Semgrep CLI](https://docs.semgrep.dev/cli-reference)

COMMAND | DESCRIPTION
---|---
`semgrep scan --config auto` | Scan with recommended rules (sends pseudonymous metrics by default, see `--metrics`)
`semgrep scan --config <RULES>` | Use a rule file, directory or registry ruleset
`semgrep scan --sarif --sarif-output=<FILE>` | SARIF output
`semgrep scan --error` | Exit 1 when findings exist
`semgrep ci` | CI mode. Does not accept `--config` and reports only new findings on pull requests
`.semgrepignore` | Paths to skip, gitignore syntax

## OSV-Scanner
Google's scanner using the OSV vulnerability database.

Documentation: [OSV-Scanner usage](https://google.github.io/osv-scanner/usage/)

COMMAND | DESCRIPTION
---|---
`osv-scanner scan -r <DIR>` | Scan a directory recursively
`osv-scanner scan -L package-lock.json` | Scan one lockfile
`osv-scanner scan image <IMAGE>:<TAG>` | Scan a container image
`osv-scanner scan --format <FORMAT> --output-file <FILE>` | Choose output format and file
`osv-scanner fix -M package.json -L package-lock.json` | Experimental fix suggestions

## Syft and Grype
Anchore's SBOM generator and vulnerability scanner.

Documentation: [Syft](https://github.com/anchore/syft) · [Grype](https://github.com/anchore/grype)

COMMAND | DESCRIPTION
---|---
`syft <IMAGE> -o cyclonedx-json` | SBOM for an image in CycloneDX
`syft <IMAGE> -o spdx-json=./spdx.json` | SBOM in SPDX, written to a file
`syft ./<DIR>` | SBOM for a directory
`grype <IMAGE>` | Scan an image
`grype ./<DIR>` | Scan a directory
`grype sbom:./sbom.json` | Scan an existing SBOM
`grype <IMAGE> --fail-on high` | Exit 2 at this severity or above (`negligible`, `low`, `medium`, `high`, `critical`)
`grype <IMAGE> -o sarif` | Output as `json`, `table`, `cyclonedx`, `cyclonedx-json`, `sarif` or a template

## Checkov
Infrastructure as code scanner (Terraform, Kubernetes, Dockerfiles, CI files).

Documentation: [Checkov CLI](https://www.checkov.io/2.Basics/CLI%20Command%20Reference.html)

COMMAND | DESCRIPTION
---|---
`checkov -d <DIR>` | Scan a directory
`checkov -f <FILE>` | Scan one file
`checkov -d <DIR> --framework terraform` | Limit to a framework
`checkov -d <DIR> --soft-fail` | Report but exit 0
`checkov -d <DIR> -o sarif` | SARIF output
`checkov -d <DIR> --skip-check <ID>` | Skip a check
`checkov -d <DIR> --compact --quiet` | Less output

`trivy config <DIR>` overlaps with Checkov for IaC, see [Container Scanning](container-scanning.md).

## OpenSSF Scorecard
Scores a repository's security practices (branch protection, pinned dependencies, CI tests and more).

Documentation: [Scorecard](https://github.com/ossf/scorecard)

COMMAND | DESCRIPTION
---|---
`scorecard --repo=github.com/<OWNER>/<REPO>` | Score a GitHub repository
`scorecard --repo=github.com/<OWNER>/<REPO> --format=json` | JSON output
`scorecard --repo=... --checks=<CHECK_A>,<CHECK_B>` | Only some checks
`scorecard --repo=... --show-details` | Reasons for each score

Set `GITHUB_AUTH_TOKEN` (or `GITHUB_TOKEN`, `GH_AUTH_TOKEN`, `GH_TOKEN`) to avoid rate limits. A container image is `ghcr.io/ossf/scorecard`.

## cosign
Sign and verify container images with Sigstore.

Documentation: [cosign](https://docs.sigstore.dev/cosign/signing/overview/)

COMMAND | DESCRIPTION
---|---
`cosign sign <IMAGE>` | Keyless signing (browser or CI identity)
`cosign verify <IMAGE> --certificate-identity=<IDENTITY> --certificate-oidc-issuer=<ISSUER_URL>` | Verify a keyless signature
`cosign verify --key cosign.pub <IMAGE>` | Verify against a public key

Sign by digest rather than by tag. Key generation and `sign --key` were not confirmed here, so check `cosign --help`.

## Not Verified
SLSA, in-toto and KICS were not researched. `osv-scanner --sbom` and `--lockfile` flags and the exact GitHub issuer URL for cosign were not confirmed.

## See Also
- [Container Scanning](container-scanning.md)
- [Secret Scanning](secret-scanning.md)
- [ASPM](aspm.md)
- [Snyk](snyk.md)
