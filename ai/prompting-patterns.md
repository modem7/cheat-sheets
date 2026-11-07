# Prompting and Context Engineering
Patterns for writing prompts and managing what an agent sees. Applies to [Claude](claude-api.md), [OpenAI](openai-api.md) and local models alike; details differ per model.

Documentation: [Anthropic prompt engineering overview](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview) · [Claude Code best practices](https://www.anthropic.com/engineering/claude-code-best-practices)

> **Verification:** conceptual guidance with no commands. Effectiveness varies by model, so test on your own tasks.

## Writing a Prompt
PATTERN | HOW
---|---
Be specific | State the goal, audience, format and constraints; vague asks get generic answers
Give context and the why | A reason lets the model generalise ("no jargon because readers are new")
Show examples | Two or three input and output pairs fix format better than description
Say what to do | Prefer "write plain prose" to "do not use lists"
Separate parts | Wrap documents, instructions and examples in labelled tags such as `<document>`
Ask for structure | Request JSON, a table or a fixed template when a program reads the output
Allow "I don't know" | Tell it to say so when evidence is missing, to reduce invented answers
Let it think first | For hard problems ask for reasoning or enable extended thinking before the answer

## Roles and Prompt Layout
- Put stable rules in the system prompt and the task in the user message.
- Put long documents first and the question last.
- Keep a reusable prompt in a file under version control and change one thing at a time.

## Agent Context
PATTERN | HOW
---|---
Short project file | Keep `CLAUDE.md` or `AGENTS.md` to build and test commands, conventions and gotchas; long files get ignored
Point, do not paste | Reference file paths and let the agent read them on demand
Fresh context per task | Clear or restart between unrelated tasks; stale history costs tokens and focus
Compact deliberately | Summarise long sessions yourself with a focus hint rather than letting them degrade
Subagents | Delegate searches or reviews so noisy output stays out of the main context
Plan first | Ask for a plan, review it, then implement; cheaper than fixing the wrong build
Verify by running | Give the agent a test or command that proves success
Narrow tools | Allow only the tools a task needs; see [MCP](mcp.md) safety

## Retrieval (RAG)
1. Split documents into chunks.
2. Embed chunks and store the vectors.
3. Embed the question and fetch the nearest chunks.
4. Put those chunks in the prompt and ask the model to answer only from them, citing the source.

Tune chunk size and overlap, and test retrieval on its own before blaming the model.

## Failure Modes
SYMPTOM | LIKELY CAUSE AND FIX
---|---
Invented commands or facts | Ask for sources, supply the docs, verify by running
Ignores an instruction | Too buried or contradicted; move it up, shorten the prompt, remove conflicts
Output format drifts | Add an example, or use structured outputs or a JSON schema
Repeats or loops | Lower the temperature, restate the goal, restart the session
Prompt injection from tool or web content | Treat fetched text as data; limit tool permissions; require confirmation for writes

## See Also
- [LLM Glossary](llm-glossary.md)
- [Claude Code](claude-code.md)
- [Claude API and SDKs](claude-api.md)
- [AI](ai.md)
