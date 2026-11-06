# TOPIC NAME
One or two sentences: what the tool or topic is and when to use it. Link related sheets with wikilinks by file basename, e.g. `[[docker]]` and `[[docker-compose]]`.

Project: [PROJECT NAME](https://example.com/)
Documentation: [DOCS NAME](https://example.com/docs/)

## Basics
COMMAND | DESCRIPTION
---|---
`tool command <ARGUMENT>` | What it does, in a short phrase
`tool command --flag <VALUE>` | What the flag changes
`tool a` / `tool b` | Paired commands share a row

## Common Tasks
Explain a multi-step task in one sentence, then show it as a fenced block with a language tag.

```bash
tool init PROJECT_NAME
tool run --config CONFIG_FILE
```

## Configuration
Show a minimal, working config. Use ALL-CAPS placeholders for anything the reader must replace.

```yaml
name: EXAMPLE_NAME
host: HOSTNAME
token: API_TOKEN
```

## Troubleshooting
SYMPTOM | FIX
---|---
Short description of the error | What to check or run

## See Also
- [[docker]] (replace with a real sheet; every wikilink must resolve)
