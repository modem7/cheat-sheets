# Hugging Face CLI and Model Formats
Download, cache and upload models with the `hf` CLI, and understand the file formats (GGUF, safetensors) and quantisation levels you will meet.

Project: [Hugging Face Hub](https://huggingface.co/)
Documentation: [hf CLI guide](https://huggingface.co/docs/huggingface_hub/guides/cli) · [GGUF](https://huggingface.co/docs/hub/gguf)

> **Verification:** `hf` commands and options were checked against `hf --help` and subcommand help (huggingface_hub 2.2.0). Format and quantisation notes are general guidance from the docs; size estimates are rough and marked `(approximate)`.

## Install
COMMAND | DESCRIPTION
---|---
`uv tool install huggingface_hub` | Install the `hf` command `(unverified: package extras may be needed)`
`hf update` | Update the CLI
`hf version` / `hf env` | Version and environment info

## Authenticate
Gated models need an account token from your Hub settings.

COMMAND | DESCRIPTION
---|---
`hf auth login` | Log in with a token or the browser
`hf auth whoami` | Show the current account
`hf auth list` / `hf auth switch` | Manage several tokens
`hf auth logout` | Remove a token
`HF_TOKEN` | Environment variable alternative; keep it out of git

## Download
COMMAND | DESCRIPTION
---|---
`hf download REPO_ID` | Download a whole repo into the cache
`hf download REPO_ID FILENAME` | One file
`hf download REPO_ID --include "*Q4_K_M*.gguf"` | Only matching files
`hf download REPO_ID --exclude "*.bin"` | Skip matching files
`hf download REPO_ID --local-dir DIR` | Put files in a normal folder instead of the cache
`hf download REPO_ID --revision BRANCH_OR_SHA` | Pin a revision
`hf download REPO_ID --dry-run` | Show what would download
`hf download REPO_ID --type dataset` | Datasets (`model`, `dataset`, `space`, `kernel`)

```bash
hf download TheOrg/Some-Model-GGUF --include "*Q4_K_M.gguf" --local-dir ./models
```

## Cache
Default location is `~/.cache/huggingface`. Override with `HF_HOME`.

COMMAND | DESCRIPTION
---|---
`hf cache ls` | List cached repos
`hf cache ls --sort size:desc` | Largest first
`hf cache rm model/OWNER/NAME` | Delete a cached repo (frees disk, cannot be undone)
`hf cache prune` | Remove detached revisions and incomplete downloads
`hf cache verify REPO_ID` | Check checksums

## Browse and Upload
COMMAND | DESCRIPTION
---|---
`hf models ls` | List models on the Hub (see `--help` for filters)
`hf models info REPO_ID` | Model details
`hf models card REPO_ID` | Show the model card
`hf repos create REPO_ID` | Create a repo
`hf upload REPO_ID LOCAL_PATH [PATH_IN_REPO]` | Upload a file or folder (re-run to resume)
`hf upload REPO_ID . . --private` | Upload the current folder, creating a private repo
`hf repos delete REPO_ID` | Delete a repo (destructive)

## Formats
FORMAT | NOTES
---|---
safetensors | Safe tensor storage (no code execution); the standard for original Hugging Face weights, used with Transformers, vLLM
GGUF | Single-file format for llama.cpp, [Ollama](ollama.md) and [LM Studio](lm-studio.md); carries metadata and quantised weights
PyTorch `.bin` / `.pt` | Pickle-based; can run code on load, so avoid untrusted files
ONNX, MLX | Other runtimes (ONNX Runtime, Apple MLX)

## Quantisation
Quantisation stores weights in fewer bits to cut memory and disk at some quality cost. In GGUF the names encode the bits per weight.

NAME | MEANING
---|---
`F16` / `BF16` | Unquantised half precision; about 2 bytes per parameter
`Q8_0` | 8-bit; near-lossless, about 1 byte per parameter
`Q6_K`, `Q5_K_M` | Higher quality mid-size options
`Q4_K_M` | Common default balance of size and quality; about 0.5 to 0.6 bytes per parameter `(approximate)`
`Q3_K`, `Q2_K` | Small but noticeably worse
`IQ` variants | Importance-matrix quants, better quality at low bits

Rough memory: parameters (in billions) × bytes per parameter, plus several GB for context (KV cache) and overhead `(approximate)`. A 7B model at `Q4_K_M` is around 4 to 5 GB. If it does not fit in VRAM, layers spill to CPU and speed drops sharply. See [llama.cpp](llama-cpp.md) for `-ngl` and `llama-quantize`.

## See Also
- [Ollama](ollama.md)
- [llama.cpp](llama-cpp.md)
- [LLM Glossary](llm-glossary.md)
- [AI](ai.md)
