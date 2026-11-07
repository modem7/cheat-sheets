# Claude API and SDKs
The Anthropic Messages API and its official Python and TypeScript SDKs: a request, streaming, tools, prompt caching and batches. For the terminal agent see [Claude Code](claude-code.md).

Documentation: [Anthropic API docs](https://docs.claude.com/en/api/overview) · [Models overview](https://docs.claude.com/en/docs/about-claude/models/overview) · [Python SDK](https://github.com/anthropics/anthropic-sdk-python) · [TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript)

> **Verification:** request shapes are from the official API docs and were not executed (no API key was used). Model IDs are the current family names; confirm with `GET /v1/models` before pinning. Items marked `(unverified)` need checking against the docs.

## Setup
Keep the key in an environment variable, never in a file you commit (see [Secret Scanning](../security/secret-scanning.md)).

```bash
export ANTHROPIC_API_KEY="YOUR_API_KEY"
```

COMMAND | DESCRIPTION
---|---
`pip install anthropic` / `uv add anthropic` | Python SDK
`npm install @anthropic-ai/sdk` | TypeScript SDK

## Models
Use the alias or dated ID your account lists. List them with the API.

MODEL ID | TIER
---|---
`claude-fable-5-1` | Most capable
`claude-opus-5-5` | High capability
`claude-sonnet-5-5` | Balanced default
`claude-haiku-5-5` | Fastest and cheapest

```bash
curl -s https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

## Messages Request
Required headers: `x-api-key`, `anthropic-version: 2023-06-01`, `content-type: application/json`. Required body fields: `model`, `max_tokens`, `messages`.

```bash
curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-5-5",
    "max_tokens": 1024,
    "system": "You are a terse assistant.",
    "messages": [{"role": "user", "content": "Explain DNS in one sentence."}]
  }'
```

```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
msg = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Explain DNS in one sentence."}],
)
print(msg.content[0].text)
```

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic(); // reads ANTHROPIC_API_KEY
const msg = await client.messages.create({
  model: "claude-sonnet-5-5",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Explain DNS in one sentence." }],
});
console.log(msg.content[0].type === "text" ? msg.content[0].text : "");
```

FIELD | NOTES
---|---
`system` | System prompt, a top-level field (not a message role)
`messages` | Alternating `user` and `assistant` turns; you resend the history each call
`max_tokens` | Cap on output tokens
`temperature`, `top_p`, `stop_sequences` | Sampling controls
`stop_reason` in the response | `end_turn`, `max_tokens`, `stop_sequence`, `tool_use`
`usage` in the response | `input_tokens`, `output_tokens` and cache counters

## Streaming
Add `"stream": true` to get server-sent events.

```python
with client.messages.stream(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a haiku about backups."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

```bash
curl -N https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-5-5","max_tokens":256,"stream":true,
       "messages":[{"role":"user","content":"Hello"}]}'
```

## Tool Use
Declare tools with a JSON Schema. When `stop_reason` is `tool_use`, run the tool and send back a `tool_result` block with the matching `tool_use_id`.

```json
{
  "model": "claude-sonnet-5-5",
  "max_tokens": 1024,
  "tools": [{
    "name": "get_disk_usage",
    "description": "Return disk usage for a mount point.",
    "input_schema": {
      "type": "object",
      "properties": { "path": { "type": "string" } },
      "required": ["path"]
    }
  }],
  "messages": [{ "role": "user", "content": "How full is /data?" }]
}
```

```json
{ "role": "user", "content": [
  { "type": "tool_result", "tool_use_id": "TOOL_USE_ID", "content": "72% used" }
] }
```

The `tool_choice` field forces or forbids a tool (`auto`, `any`, `tool`, `none`) `(unverified: exact values)`.

## Prompt Caching
Mark a stable prefix (long system prompt, documents, tool definitions) with `cache_control`. Later requests with the same prefix read it from cache at reduced cost. There is a minimum cacheable length and a short time-to-live; check the docs for current values.

```json
{
  "system": [
    { "type": "text", "text": "LONG_STABLE_INSTRUCTIONS",
      "cache_control": { "type": "ephemeral" } }
  ]
}
```

Check `usage.cache_creation_input_tokens` and `usage.cache_read_input_tokens` to confirm hits.

## Batches and Token Counting
ENDPOINT | USE
---|---
`POST /v1/messages/batches` | Submit many requests for asynchronous processing at lower cost
`GET /v1/messages/batches/BATCH_ID` | Check status
`GET /v1/messages/batches/BATCH_ID/results` | Download results (JSONL) `(unverified: path)`
`POST /v1/messages/count_tokens` | Count tokens without generating

## Errors
STATUS | MEANING
---|---
`400` | Malformed request
`401` | Bad or missing API key
`403` | Key lacks permission
`429` | Rate limited; back off and retry (SDKs retry automatically)
`529` | API overloaded `(unverified)`

## See Also
- [Claude Code](claude-code.md)
- [Model Context Protocol (MCP)](mcp.md)
- [Prompting and Context Engineering](prompting-patterns.md)
- [LLM Glossary](llm-glossary.md)
- [OpenAI API](openai-api.md)
