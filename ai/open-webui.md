# Open WebUI and Self-Hosted AI Stacks
Open WebUI is a self-hosted chat interface for Ollama and any OpenAI-compatible API. Run it with [Ollama](ollama.md) in [Docker Compose](../docker/docker-compose.md) for a private ChatGPT-style stack.

Project: [Open WebUI](https://github.com/open-webui/open-webui)
Documentation: [Open WebUI docs](https://docs.openwebui.com/)

> **Verification:** image name, port, volume path and environment variables are from the official docs as remembered; nothing was run here. Check the docs for current variable names. Items marked `(unverified)` need confirming.

## Compose Stack
Replace `<TAG>` with a pinned version. The first account created becomes the administrator.

```yaml
services:
  ollama:
    image: ollama/ollama:<TAG>
    restart: unless-stopped
    volumes:
      - ollama:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  open-webui:
    image: ghcr.io/open-webui/open-webui:<TAG>
    restart: unless-stopped
    depends_on:
      - ollama
    ports:
      - "127.0.0.1:3000:8080"
    environment:
      OLLAMA_BASE_URL: http://ollama:11434
      WEBUI_SECRET_KEY: ${WEBUI_SECRET_KEY}
      ENABLE_SIGNUP: "false"
    volumes:
      - open-webui:/app/backend/data

volumes:
  ollama:
  open-webui:
```

COMMAND | DESCRIPTION
---|---
`openssl rand -hex 32` | Generate a value for `WEBUI_SECRET_KEY` (store in `.env`, not in git)
`docker compose up -d` | Start the stack
`docker compose pull && docker compose up -d` | Update
`docker compose exec ollama ollama pull MODEL` | Download a model; it appears in the UI

## Key Settings
VARIABLE | USE
---|---
`OLLAMA_BASE_URL` | Where Ollama is
`OPENAI_API_BASE_URL` / `OPENAI_API_KEY` | Connect an OpenAI-compatible provider or a local server
`WEBUI_SECRET_KEY` | Session signing key; set it so logins survive restarts
`ENABLE_SIGNUP` | Allow self-registration; turn off after creating admin `(unverified)`
`WEBUI_AUTH` | Disabling auth is for single-user local use only `(unverified)`

Data lives in the `/app/backend/data` volume (users, chats, settings). Back it up: [Docker Volume Backup](../backup/docker-volume-backup.md).

## Exposure
- Keep the port on loopback and publish through a [reverse proxy](../homelab/reverse-proxy-patterns.md) with TLS.
- For single sign-on use OIDC with [authentik](../security/authentik.md) `(unverified: check the OAuth/OIDC variables in the docs)`.
- Do not expose the Ollama port itself.

## Related Self-Hosted Pieces
PIECE | PURPOSE
---|---
[Ollama](ollama.md) / [llama.cpp](llama-cpp.md) | Model backends
LiteLLM proxy | One OpenAI-style gateway in front of many providers `(unverified)`
SearXNG | Self-hosted search for web-search features `(unverified)`
[MCP](mcp.md) servers | Tools for agents

## See Also
- [Docker](../docker/docker.md)
- [Ollama](ollama.md)
- [OpenAI API](openai-api.md)
- [AI](ai.md)
