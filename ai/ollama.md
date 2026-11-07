# Ollama
Run open-weight language models locally with one command and a local HTTP API. Use it as the model backend for [Open WebUI](open-webui.md), [Aider](aider.md) and scripts.

Project: [Ollama](https://ollama.com/)
Documentation: [Ollama docs](https://github.com/ollama/ollama/tree/main/docs) · [Model library](https://ollama.com/library)

> **Verification:** commands, environment variables and API paths are from the official docs and CLI help from memory; Ollama was not installed here, so nothing was executed. Model tags change; check the library. Items marked `(unverified)` need confirming.

## Basics
COMMAND | DESCRIPTION
---|---
`ollama serve` | Start the server (the Linux installer sets this up as a systemd service)
`ollama run MODEL` | Chat with a model, pulling it first if needed
`ollama run MODEL "PROMPT"` | One-shot prompt
`ollama pull MODEL` | Download a model
`ollama list` | Show downloaded models
`ollama ps` | Show loaded models and memory use
`ollama stop MODEL` | Unload a model from memory
`ollama show MODEL` | Show details (parameters, template, licence)
`ollama cp SOURCE TARGET` | Copy a model under a new name
`ollama rm MODEL` | Delete a model and free disk
`ollama create NAME -f Modelfile` | Build a model from a Modelfile
`ollama push NAME` | Publish to ollama.com (needs an account)

Model tags look like `llama3.2:3b` (name, then size or variant). Pick a size that fits your VRAM; see [quantisation](hugging-face.md#quantisation).

## Modelfile
```text
FROM llama3.2:3b
PARAMETER temperature 0.3
PARAMETER num_ctx 8192
SYSTEM You are a terse homelab assistant.
```

INSTRUCTION | MEANING
---|---
`FROM` | Base model or a GGUF path
`PARAMETER` | Runtime option such as `temperature`, `num_ctx`, `top_p`
`SYSTEM` | System prompt
`TEMPLATE` | Prompt template (rarely needed)
`ADAPTER` | Apply a LoRA adapter

## Environment Variables
Set them in the service environment (`sudo systemctl edit ollama`), not just your shell.

VARIABLE | USE
---|---
`OLLAMA_HOST` | Bind address and port (default `127.0.0.1:11434`). `0.0.0.0` exposes it to the network, so firewall it
`OLLAMA_MODELS` | Model storage directory
`OLLAMA_KEEP_ALIVE` | How long a model stays loaded (for example `10m`, `-1` forever)
`OLLAMA_NUM_PARALLEL` | Concurrent requests per model
`OLLAMA_MAX_LOADED_MODELS` | Models kept loaded at once
`OLLAMA_ORIGINS` | Allowed CORS origins `(unverified)`

## HTTP API
The API has no authentication. Do not publish port 11434; put an authenticating [reverse proxy](../homelab/reverse-proxy-patterns.md) in front if you must.

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "Why is the sky blue?",
  "stream": false
}'

curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2:3b",
  "messages": [{"role": "user", "content": "Hello"}],
  "stream": false
}'

curl http://localhost:11434/api/tags
```

ENDPOINT | USE
---|---
`POST /api/generate` | Single prompt completion
`POST /api/chat` | Chat with message history
`GET /api/tags` | List local models
`POST /api/embed` | Embeddings `(unverified: older versions used /api/embeddings)`
`/v1/chat/completions` | OpenAI-compatible endpoint; see [OpenAI API](openai-api.md#openai-compatible-local-servers)

## Docker
GPU use needs the NVIDIA Container Toolkit on the host. For a VM, pass the GPU through first: [Proxmox GPU and PCIe Passthrough](../proxmox/proxmox-passthrough.md). See [Docker Compose](../docker/docker-compose.md) for the file format.

```yaml
services:
  ollama:
    image: ollama/ollama:<TAG>
    restart: unless-stopped
    ports:
      - "127.0.0.1:11434:11434"
    volumes:
      - ollama:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
volumes:
  ollama:
```

COMMAND | DESCRIPTION
---|---
`docker exec -it ollama ollama pull MODEL` | Pull inside the container
`docker exec -it ollama ollama ps` | Check whether the model is on GPU (`PROCESSOR` column)

## Troubleshooting
SYMPTOM | FIX
---|---
Runs on CPU only | Check `nvidia-smi` works on the host and the container has the GPU; read `journalctl -u ollama`
Model slow or out of memory | Use a smaller size or heavier quantisation; lower `num_ctx`
Remote client cannot connect | Server binds to loopback by default; set `OLLAMA_HOST` and open the firewall deliberately
Disk fills up | `ollama list` then `ollama rm MODEL`

## See Also
- [Open WebUI and Self-Hosted AI Stacks](open-webui.md)
- [llama.cpp](llama-cpp.md)
- [Hugging Face CLI and Model Formats](hugging-face.md)
- [Docker](../docker/docker.md)
- [AI](ai.md)
