# ASPM
Application Security Posture Management (ASPM) means pulling findings from your separate security tools (SAST, dependency scanning, secrets, containers, IaC) into one place, deduplicating them, adding context about the app and its deployment, and ranking what to fix first. For a homelab you rarely need a commercial platform. DefectDojo and Dependency-Track cover the same job with open source.

The definition below is a vendor-neutral paraphrase. Gartner introduced the term in 2023, and the vendor pages that describe it (Wiz, Apiiro, Veracode) broadly agree.

## What It Does
CAPABILITY | MEANING
---|---
Ingest | Import results from many scanners
Deduplicate | One finding per issue across tools and scans
Inventory | Know which apps, repos and images exist
Prioritise | Rank by exploitability, exposure and business context
Gate | Fail builds or block releases by policy
Ticket | Create issues in Jira or GitHub
Supply chain | Track SBOMs and component versions

This capability list is typical of vendors, not from a single standard.

## Options
TOOL | TYPE
---|---
DefectDojo | Open source finding management
OWASP Dependency-Track | Open source SBOM and component risk
Snyk AppRisk, Wiz, Apiiro, Cycode, Aikido | Commercial platforms (names only, not covered here)

## DefectDojo
Docker install from the project README:

```bash
git clone https://github.com/DefectDojo/django-DefectDojo
cd django-DefectDojo
docker compose up
docker compose logs initializer | grep "Admin password:"
```

Log in as `admin` at `http://localhost:8080`. The first start can take up to about 3 minutes.

The data model is Product Type, then Product, then Engagement, then Test, then Findings. The import API is commonly used from CI:

```bash
curl -X POST "https://defectdojo.example.com/api/v2/import-scan/" \
  -H "Authorization: Token ${DEFECTDOJO_TOKEN}" \
  -F "scan_type=Trivy Scan" \
  -F "file=@trivy.json" \
  -F "product_name=<PRODUCT>" \
  -F "engagement_name=<ENGAGEMENT>" \
  -F "auto_create_context=true"
```

This API call and the scan type names are **unverified** (the docs pages were not reachable). Check the parser list in your version's docs and pick the `scan_type` exactly as listed.

## Dependency-Track
Compose from the project docs:

```bash
curl -LO https://dependencytrack.org/docker-compose.yml
docker compose up -d
```

The UI is on port 8080 and the API on 8081. Upload an SBOM from CI with an API key:

COMMAND | DESCRIPTION
---|---
`PUT /api/v1/bom` | JSON body with base64 `bom` plus `project` UUID, or `projectName`, `projectVersion` and `autoCreate=true`
`POST /api/v1/bom` | Multipart upload with the file unencoded

Authenticate with the `X-Api-Key` header. Generate an SBOM with [Syft or Trivy](appsec-tools.md).

## Practical Pipeline
1. CI runs scanners ([Trivy](container-scanning.md), [Semgrep](appsec-tools.md), [gitleaks](secret-scanning.md), [Snyk](snyk.md)).
2. Results go to DefectDojo, and SBOMs to Dependency-Track.
3. Review and triage there, and keep the CI gate on high and critical only.
4. Keep dependencies current with [Renovate](../cicd/renovate.md).

## Not Verified
Gartner's wording, the DefectDojo import API and parser names, the Dependency-Track default login, and CycloneDX support details.

## See Also
- [Application Security Tools](appsec-tools.md)
- [Container Scanning](container-scanning.md)
- [Secret Scanning](secret-scanning.md)
- [Snyk](snyk.md)
