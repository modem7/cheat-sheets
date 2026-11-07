# OpenAI API
The OpenAI HTTP API with curl and the Python SDK, plus how to point OpenAI-compatible clients at local servers such as [Ollama](ollama.md) and [llama.cpp](llama-cpp.md). For the Anthropic equivalent see [Claude API and SDKs](claude-api.md).

Documentation: [OpenAI API reference](https://platform.openai.com/docs/api-reference) · [Python SDK](https://github.com/openai/openai-python)

> **Verification:** request shapes are from the official docs as remembered and were not executed (no key used). Model names are placeholders; list yours with `GET /v1/models`. Items marked `(unverified)` need confirming.

## Setup
```bash
export OPENAI_API_KEY="YOUR_API_KEY"
```

COMMAND | DESCRIPTION
---|---
`pip install openai` / `uv add openai` | Python SDK
`npm install openai` | JavaScript SDK
`curl --oauth2-bearer "$OPENAI_API_KEY" https://api.openai.com/v1/models` | List models (curl sends the bearer token for you)

## Chat Completions
```bash
curl https://api.openai.com/v1/chat/completions \
  --oauth2-bearer "$OPENAI_API_KEY" \
  -H "content-type: application/json" \
  -d '{
    "model": "MODEL_NAME",
    "messages": [
      {"role": "system", "content": "You are terse."},
      {"role": "user", "content": "Explain DNS in one sentence."}
    ]
  }'
```

```python
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY
resp = client.chat.completions.create(
    model="MODEL_NAME",
    messages=[{"role": "user", "content": "Explain DNS in one sentence."}],
)
print(resp.choices[0].message.content)
```

## Responses API
OpenAI's newer interface, with built-in tools and conversation state `(unverified: check current guidance on which API to use)`.

```bash
curl https://api.openai.com/v1/responses \
  --oauth2-bearer "$OPENAI_API_KEY" \
  -H "content-type: application/json" \
  -d '{"model": "MODEL_NAME", "input": "Explain DNS in one sentence."}'
```

## Endpoints
ENDPOINT | USE
---|---
`POST /v1/chat/completions` | Chat; the de facto standard that many servers copy
`POST /v1/responses` | Newer unified interface
`POST /v1/embeddings` | Embeddings
`GET /v1/models` | List models
`POST /v1/batches` | Asynchronous batch jobs `(unverified)`

## OpenAI-Compatible Local Servers
Most clients let you override the base URL. Local servers usually ignore the key but clients still require one, so any non-empty string works.

SERVER | BASE URL
---|---
[Ollama](ollama.md) | `http://localhost:11434/v1`
[llama.cpp](llama-cpp.md) `llama-server` | `http://localhost:8080/v1`
[LM Studio](lm-studio.md) | `http://localhost:1234/v1`

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="unused")
resp = client.chat.completions.create(
    model="llama3.2:3b",
    messages=[{"role": "user", "content": "Hello"}],
)
```

```bash
export OPENAI_BASE_URL="http://localhost:11434/v1"
export OPENAI_API_KEY="unused"
```

`OPENAI_BASE_URL` is read by the official Python SDK; other tools may use a different name.

## See Also
- [Claude API and SDKs](claude-api.md)
- [Codex, Gemini and Copilot CLIs](coding-agent-clis.md)
- [Open WebUI and Self-Hosted AI Stacks](open-webui.md)
- [AI](ai.md)
