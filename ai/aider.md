# Aider
Terminal pair-programming tool that edits files in a Git repo and commits each change. It works with Anthropic, OpenAI and local models, so it suits switching providers.

Project: [Aider](https://aider.chat/)
Documentation: [aider.chat/docs](https://aider.chat/docs/)

> **Verification:** commands and options are from the official docs as remembered; Aider was not installed here and nothing was executed. Check `aider --help`. Items marked `(unverified)` need confirming.

## Install and Start
COMMAND | DESCRIPTION
---|---
`uv tool install aider-chat` | Install `(unverified: the docs also show the aider-install package)`
`aider` | Start in the current Git repo
`aider FILE...` | Start with files added to the chat
`aider --model MODEL` | Choose a model
`aider --message "PROMPT"` | Run one instruction and exit
`aider --help` | List every option

## Models and Keys
```bash
export ANTHROPIC_API_KEY="YOUR_API_KEY"
aider --model sonnet

export OPENAI_API_KEY="YOUR_API_KEY"
aider --model MODEL_NAME

export OLLAMA_API_BASE="http://127.0.0.1:11434"
aider --model ollama_chat/llama3.2:3b
```

Local models need a large context (`num_ctx`) set in [Ollama](ollama.md) or edits degrade `(unverified)`.

## Useful Flags
FLAG | MEANING
---|---
`--no-auto-commits` | Do not commit after every change
`--read FILE` | Add a file as read-only context
`--architect` | Use a planner model and an editor model
`--watch-files` | Act on `AI!` and `AI?` comments you add in files
`--yes` | Auto-confirm prompts; use carefully
`--dark-mode` | Colours for a dark terminal

## In-Chat Commands
COMMAND | DESCRIPTION
---|---
`/add FILE` | Add a file for editing
`/read-only FILE` | Add as reference only
`/drop FILE` | Remove from chat
`/ls` | List files in play
`/diff` | Show changes since the last message
`/undo` | Undo the last Aider commit
`/commit` | Commit outside changes
`/run COMMAND` | Run a command and offer its output to the chat
`/test COMMAND` | Run tests and fix failures
`/ask` / `/code` / `/architect` | Switch chat mode
`/model MODEL` | Change the main model
`/tokens` | Show context use
`/clear` | Clear chat history
`/exit` | Quit

## Configuration
`.aider.conf.yml` in the repo or home directory; keys mirror the long flag names. Keep API keys in the environment or an untracked `.env`.

```yaml
model: sonnet
auto-commits: false
read:
  - CONVENTIONS.md
```

## See Also
- [Claude Code](claude-code.md)
- [Codex, Gemini and Copilot CLIs](coding-agent-clis.md)
- [Ollama](ollama.md)
- [AI](ai.md)
