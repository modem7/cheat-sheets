# AI
Overview of the AI sheets: Claude and its tooling, local model runtimes, self-hosted front ends, other vendors' coding CLIs, and the concepts behind them. Start here to pick a sheet.

> **Verification:** this page is an index. Each linked sheet carries its own verification note. Fast-moving tools (model names, flags, CLI versions) change often, so check `--help` or the vendor docs before relying on a flag.

## Sheets
SHEET | USE IT FOR
---|---
[Claude Code](claude-code.md) | Anthropic's terminal coding agent: flags, settings, hooks, skills, subagents
[Claude API and SDKs](claude-api.md) | Messages API with curl, Python and TypeScript; streaming, tools, caching, batches
[Model Context Protocol (MCP)](mcp.md) | Connecting tools and data to AI clients; config snippets, common servers
[Ollama](ollama.md) | Easiest way to run local models; Modelfiles and the local API
[llama.cpp](llama-cpp.md) | `llama-cli`, `llama-server` and quantising GGUF files
[LM Studio](lm-studio.md) | Desktop app and `lms` CLI for local models
[Open WebUI and Self-Hosted AI Stacks](open-webui.md) | Web chat front end with Ollama or any OpenAI-compatible backend
[OpenAI API](openai-api.md) | Chat Completions and Responses with curl; OpenAI-compatible local servers
[Codex, Gemini and Copilot CLIs](coding-agent-clis.md) | Other vendors' terminal coding agents
[Aider](aider.md) | Git-aware pair-programming CLI that works with many providers
[Hugging Face CLI and Model Formats](hugging-face.md) | Downloading models, GGUF, safetensors and quantisation
[Prompting and Context Engineering](prompting-patterns.md) | Patterns that make prompts and agent context work
[LLM Glossary](llm-glossary.md) | Tokens, context window, temperature, RAG and other terms

## Picking Something
NEED | START WITH
---|---
Coding agent on a repo | [Claude Code](claude-code.md), or [Aider](aider.md) for provider choice
Call a hosted model from a script | [Claude API and SDKs](claude-api.md) or [OpenAI API](openai-api.md)
Private, offline model on a homelab box | [Ollama](ollama.md) plus [Open WebUI](open-webui.md)
Squeeze a model onto small hardware | [llama.cpp](llama-cpp.md) and [quantisation](hugging-face.md#quantisation)
Give an agent access to your tools | [MCP](mcp.md)

## Homelab Notes
- A GPU in a VM needs passthrough: see [Proxmox GPU and PCIe Passthrough](../proxmox/proxmox-passthrough.md) and identify the card with [Hardware Inspection](../linux/hardware-inspection.md).
- Containers: [Docker](../docker/docker.md) and [Docker Compose](../docker/docker-compose.md). GPU access in containers needs the NVIDIA Container Toolkit on the host (see the [Ollama](ollama.md#docker) sheet).
- Expose a web UI through a proxy with auth: [Reverse Proxy Patterns](../homelab/reverse-proxy-patterns.md) and [authentik](../security/authentik.md).
- Keep API keys out of repos: [Secret Scanning](../security/secret-scanning.md).
