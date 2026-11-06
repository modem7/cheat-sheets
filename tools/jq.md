# jq
`jq` is a command-line JSON processor. Think of it as `sed` or `awk` for JSON ([[sed]], [[awk]]).

Documentation: [jq Manual](https://jqlang.github.io/jq/manual/)

## Options
OPTION | DESCRIPTION
---|---
`-r` | Raw output, strip quotes from strings
`-c` | Compact one-line output
`-e` | Exit non-zero if the last output is `false` or `null`
`-s` | Slurp all inputs into one array
`-n` | No input, build from scratch
`--arg <NAME> <VALUE>` | Pass a string variable (`$NAME`)
`--argjson <NAME> '<JSON>'` | Pass a JSON variable
`-S` | Sort object keys
`--tab` | Indent with tabs

## Selecting
FILTER | DESCRIPTION
---|---
`.` | Pretty-print the input
`.name` | Field
`.a.b.c` | Nested field
`.["key-with-dash"]` | Awkward key names
`.items[0]` | First element
`.items[-1]` | Last element
`.items[]` | Every element
`.items[2:5]` | Slice
`.name?` | Suppress errors if missing
`.a // "default"` | Default when null or false
`keys` | Object keys
`length` | Length of array, object or string
`.. \| .id? // empty` | Recursively find every `id`

## Filtering and Transforming
FILTER | DESCRIPTION
---|---
`.items[] \| select(.status == "ok")` | Keep matching elements
`.items[] \| select(.name \| test("^web"))` | Regex match
`.items[] \| select(.tags \| index("prod"))` | Array contains
`map(.id)` | Transform an array
`map(select(.age > 30))` | Filter an array
`[.items[] \| {name, id}]` | Build smaller objects
`{name: .title, tags: (.labels \| join(","))}` | Reshape
`sort_by(.date)` | Sort
`group_by(.type) \| map({type: .[0].type, n: length})` | Group and count
`unique_by(.id)` | Deduplicate
`add` | Sum numbers or concatenate
`to_entries`, `from_entries`, `with_entries(...)` | Convert objects to key/value lists and back
`del(.password)` | Remove a key
`.a = 5` / `.a \|= . + 1` | Set or update
`first`, `last`, `min_by(.x)`, `max_by(.x)` | Pick one

## Output Formats
COMMAND | DESCRIPTION
---|---
`jq -r '.items[] \| [.name, .id] \| @csv'` | CSV
`jq -r '.items[] \| [.name, .id] \| @tsv'` | TSV
`jq -r '.name \| @sh'` | Shell-safe quoting
`jq -r '.data \| @base64'` / `@base64d` | Base64 encode / decode
`jq -r '.q \| @uri'` | URL-encode
`jq -r '"Name: \(.name)"'` | String interpolation

## Everyday Examples
COMMAND | DESCRIPTION
---|---
`curl -s <URL> \| jq .` | Pretty-print an API response
`docker inspect <C> \| jq -r '.[0].NetworkSettings.IPAddress'` | Container IP
`kubectl get pods -o json \| jq -r '.items[] \| select(.status.phase!="Running") \| .metadata.name'` | Pods not running
`jq -s 'add' a.json b.json` | Merge arrays from files
`jq -s '.[0] * .[1]' a.json b.json` | Deep merge two objects
`jq --arg v "1.2.3" '.version = $v' package.json` | Set a value from a shell variable
`jq 'paths(scalars) as $p \| "\($p \| join(".")) = \(getpath($p))"' -r f.json` | Flatten to dotted paths
`jq -n '[inputs]' file.ndjson` | NDJSON to an array
`jq -e '.ok == true' resp.json >/dev/null` | Use as a test in scripts
