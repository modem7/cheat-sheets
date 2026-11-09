# llama.cpp
C and C++ inference engine for GGUF models on CPU and GPU. It is the engine behind many local tools; use it directly for control over offload, context and quantisation.

Project: [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)
Documentation: [llama-server README](https://github.com/ggml-org/llama.cpp/tree/master/tools/server) · [llama-cli README](https://github.com/ggml-org/llama.cpp/tree/master/tools/cli)

> **Verification:** binary and flag names are from the project README and tool help as remembered; llama.cpp was not installed here and nothing was executed. Flags change between builds, so check `llama-server --help`. Items marked `(unverified)` need confirming.

## Binaries
BINARY | USE
---|---
`llama-cli` | Interactive or one-shot generation
`llama-server` | OpenAI-compatible HTTP server and web UI
`llama-quantize` | Convert a GGUF to a smaller quantisation
`llama-bench` | Benchmark speed
`llama-perplexity` | Measure quality loss
`convert_hf_to_gguf.py` | Convert a Hugging Face model to GGUF (script in the repo)

## Run
COMMAND | DESCRIPTION
---|---
`llama-cli -m MODEL.gguf -p "PROMPT"` | One-shot prompt
`llama-cli -m MODEL.gguf -cnv` | Conversation mode `(unverified)`
`llama-cli -hf USER/REPO[:QUANT]` | Download from Hugging Face and run
`llama-server -m MODEL.gguf --host 127.0.0.1 --port 8080` | Start the server
`llama-server -hf USER/REPO[:QUANT]` | Download and serve

FLAG | MEANING
---|---
`-m FILE` | Model path
`-c N` / `--ctx-size N` | Context length in tokens
`-ngl N` / `--n-gpu-layers N` | Layers to offload to the GPU
`-t N` | CPU threads
`-b N` | Batch size
`--api-key KEY` | Require a key on the server `(unverified)`
`--parallel N` | Concurrent server slots `(unverified)`

## Query the Server
```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "content-type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

The server also exposes a browser UI at the same address.

## Quantise
```bash
python3 convert_hf_to_gguf.py /path/to/HF_MODEL --outfile model-f16.gguf --outtype f16
llama-quantize model-f16.gguf model-Q4_K_M.gguf Q4_K_M
```

See [quantisation](hugging-face.md#quantisation) for what the names mean.

## Docker
Image names and tags move; check the project's Docker docs `(unverified)`.

```yaml
services:
  llama:
    image: ghcr.io/ggml-org/llama.cpp:server
    command: -m /models/MODEL.gguf --host 0.0.0.0 --port 8080 -ngl 99
    ports:
      - "127.0.0.1:8080:8080"
    volumes:
      - ./models:/models:ro
```

The plain image is CPU only; GPU builds use a separate tag such as `server-cuda` `(unverified)`.

## See Also
- [Ollama](ollama.md)
- [LM Studio](lm-studio.md)
- [Hugging Face CLI and Model Formats](hugging-face.md)
- [Docker Compose](../docker/docker-compose.md)
- [AI](ai.md)
