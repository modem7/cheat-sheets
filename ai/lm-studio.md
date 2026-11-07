# LM Studio
Desktop app for downloading and chatting with local models, with a local OpenAI-compatible server and the `lms` command line. Suits a workstation more than a headless server; for servers prefer [Ollama](ollama.md) or [llama.cpp](llama-cpp.md).

Project: [LM Studio](https://lmstudio.ai/)
Documentation: [LM Studio docs](https://lmstudio.ai/docs) · [lms CLI](https://lmstudio.ai/docs/cli)

> **Verification:** the whole sheet is `(unverified)`: LM Studio was not installed here and the commands are from the vendor docs as remembered. Run `lms --help` to confirm.

## CLI (`lms`)
COMMAND | DESCRIPTION
---|---
`lms status` | Show server and model state
`lms ls` | List downloaded models
`lms get MODEL` | Download a model
`lms load MODEL` | Load a model into memory
`lms unload --all` | Unload all models
`lms ps` | Show loaded models
`lms server start` | Start the local API server
`lms server stop` | Stop it

## Local Server
The server listens on port `1234` by default and speaks the OpenAI API. See [OpenAI API](openai-api.md#openai-compatible-local-servers).

```bash
curl http://localhost:1234/v1/models
```

## Notes
- Models are GGUF (and MLX on Apple silicon). See [Hugging Face CLI and Model Formats](hugging-face.md).
- Bind the server to the network only if you need to, and firewall it. It has no authentication by default `(unverified)`.

## See Also
- [Ollama](ollama.md)
- [llama.cpp](llama-cpp.md)
- [AI](ai.md)
