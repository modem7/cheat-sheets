# yq
`yq` (mikefarah/yq, version 4) is a command-line processor for YAML, with JSON, XML, CSV, TOML, properties and INI support. Its expressions are close to [jq](jq.md). Use it to read and edit YAML such as Docker Compose files, Kubernetes manifests and CI pipelines. There is a different, Python-based tool also called `yq`; this sheet covers the Go one.

Project: [mikefarah/yq](https://github.com/mikefarah/yq/)
Documentation: [yq docs](https://mikefarah.gitbook.io/yq/)

> **Verification:** flags and every example were run with yq v4.47.2 (Alpine package) in a throwaway container. Behaviour of `yq` from a package manager may be the Python `yq` instead: check `yq --version`.

See also: [jq](jq.md) · [Docker-Compose](../docker/docker-compose.md) · [Helm Cheat-Sheet](helm.md) · [Ansible Cheat-Sheet](ansible.md) · [Modern CLI Tools](modern-cli-tools.md)

---
## Reading
Examples use this file:

```yaml
services:
  web:
    image: nginx:1.27
    ports: ["80:80", "443:443"]
  db:
    image: postgres:17
```

COMMAND | DESCRIPTION
---|---
`yq '.services.web.image' FILE.yml` | One value
`yq '.services \| keys' FILE.yml` | Keys of a map
`yq '.services.web.ports[0]' FILE.yml` | Array element
`yq '.services.web.ports[]' FILE.yml` | Every element, one per line
`yq '.services.*.image' FILE.yml` | Wildcard over map values
`yq '.services.web.ports \| length' FILE.yml` | Count
`yq '.services[] \| select(.image == "postgres*")' FILE.yml` | Filter (`==` accepts `*` globs)
`yq '.services[] \| select(.image \| test("^postgres"))' FILE.yml` | Filter by regular expression
`yq '.services \| to_entries \| .[].key' FILE.yml` | Keys via entries
`yq '.a.b' < FILE.yml` | Read from stdin
`yq -e '.missing' FILE.yml` | Exit non-zero when nothing matches (prints `null`)

---
## Editing
COMMAND | DESCRIPTION
---|---
`yq -i '.services.web.image = "nginx:1.28"' FILE.yml` | Change a value in place
`yq '.services.web.image = "nginx:1.28"' FILE.yml` | Print the result without saving
`yq '.services.web.ports += ["8080:80"]' FILE.yml` | Append to an array
`yq 'del(.services.db)' FILE.yml` | Delete a key
`yq '(.services[] \| select(.image == "postgres:17") \| .image) = "postgres:16"' FILE.yml` | Update matching nodes
`yq '.a.b \|= . + 1' FILE.yml` | Update using the current value
`yq '.services.web.environment.TZ = strenv(TZ_VALUE)' FILE.yml` | Set from an environment variable as a string
`yq '.a.b = env(NUMBER)' FILE.yml` | Set from an environment variable, parsed as YAML (numbers stay numbers)
`yq '.services.web.image \| sub("nginx:", "")' FILE.yml` | String replacement (regex) on a value
`yq 'sort_keys(.)' FILE.yml` | Sort map keys
`yq -n '.a.b = 1'` | Build a document from nothing (`-n`)

`-i` rewrites the file. Commit or copy it first.

---
## Merging and Multiple Files
COMMAND | DESCRIPTION
---|---
`yq eval-all 'select(fileIndex == 0) * select(fileIndex == 1)' A.yml B.yml` | Deep-merge two files (the second wins)
`yq eval-all '. as $item ireduce ({}; . * $item)' A.yml B.yml` | Merge any number of files
`yq '.c = load("OTHER.yml").a' FILE.yml` | Pull a value in from another file
`yq 'explode(.)' FILE.yml` | Expand anchors and aliases
`yq '.a' MULTI_DOC.yml` | Runs against each document in a multi-document file

`eval` is the default command: it runs per document. `eval-all` loads every document of every file first.

---
## Formats
COMMAND | DESCRIPTION
---|---
`yq -o=json '.' FILE.yml` | YAML to JSON
`yq -o=json -I=0 '.' FILE.yml` | Compact JSON on one line
`yq -p=json -o=yaml '.' FILE.json` | JSON to YAML (also `-P` to pretty print)
`yq -o=props '.' FILE.yml` | Java properties style
`yq -p xml '.' FILE.xml` | Read XML
`yq -s '.services.web.image' FILE.yml` | Split results into files named by the expression
`yq -N '.' FILE.yml` | Omit the `---` document separators

Formats accepted by `-p` / `-o`: `yaml`, `json`, `props`, `csv`, `tsv`, `xml`, `base64`, `uri`, `toml`, `lua`, `ini` (and `shell` for output).

---
## Troubleshooting
SYMPTOM | FIX
---|---
`yq: command not found` or wrong syntax | Check which `yq` you have: `yq --version` should name mikefarah/yq
Formatting changed after `-i` | Quote style and list style can change (a `+=` on a flow list was printed with single quotes in testing): review the diff
Expression taken as a file name | Add `--expression '<EXPR>'`
Shell expanded `$VAR` or `*` | Quote the expression with single quotes

---
## See Also
- [jq](jq.md)
- [Docker-Compose](../docker/docker-compose.md)
- [Helm Cheat-Sheet](helm.md)
- [Ansible Cheat-Sheet](ansible.md)
