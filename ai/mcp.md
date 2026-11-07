# Model Context Protocol (MCP)
An open protocol that lets AI clients (Claude Code, Claude Desktop, IDEs, Open WebUI and others) call tools and read data exposed by servers. Use it to give an agent controlled access to files, Git hosts, databases and your homelab.

Documentation: [modelcontextprotocol.io](https://modelcontextprotocol.io/) · [Claude Code MCP docs](https://docs.claude.com/en/docs/claude-code/mcp) · [Reference servers](https://github.com/modelcontextprotocol/servers)

> **Verification:** `claude mcp` commands were checked against `claude --help`. Protocol concepts and the config shape are from the official docs. Package names of third-party servers change; confirm each before use (marked `(unverified)`).

## Concepts
TERM | MEANING
---|---
Client / host | The app the user talks to (Claude Code, Claude Desktop)
Server | A process that exposes capabilities
Tools | Actions the model can call
Resources | Data the client can read
Prompts | Reusable prompt templates the server offers
Transport `stdio` | Client launches the server locally and talks over stdin and stdout
Transport streamable HTTP | Remote server over HTTP; the current remote transport
Transport SSE | Older remote transport, deprecated in favour of HTTP

## Add Servers in Claude Code
COMMAND | DESCRIPTION
---|---
`claude mcp add --transport http NAME URL` | Remote HTTP server
`claude mcp add NAME -e KEY=VALUE -- COMMAND ARGS` | Local stdio server (everything after `--` is the command)
`claude mcp add -s project NAME ...` | Write to `.mcp.json` so the team shares it
`claude mcp add-json NAME 'JSON'` | From a JSON definition
`claude mcp list` / `claude mcp get NAME` | Inspect and health check
`claude mcp login NAME` | Complete OAuth for a server
`claude mcp remove NAME` | Remove
`/mcp` (in a session) | Status, authenticate, enable or disable

Scopes: `local` (default, you in this project), `project` (`.mcp.json`, shared), `user` (all your projects).

## Config File
`.mcp.json` in the project root (Claude Code) and the `mcpServers` block in Claude Desktop's config use the same shape.

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/srv/DATA_DIR"]
    },
    "example-remote": {
      "type": "http",
      "url": "https://mcp.example.com/mcp"
    },
    "example-local": {
      "command": "/usr/local/bin/SERVER_BINARY",
      "env": { "API_TOKEN": "${API_TOKEN}" }
    }
  }
}
```

Reference environment variables rather than pasting tokens. Do not commit secrets in `.mcp.json`.

## Common Servers
SERVER | PURPOSE
---|---
`@modelcontextprotocol/server-filesystem` | Read and write a limited set of directories
`@modelcontextprotocol/server-memory` | Simple knowledge-graph memory `(unverified)`
`@modelcontextprotocol/server-fetch` | Fetch web pages `(unverified: the reference fetch server is Python, run through uvx)`
GitHub's MCP server | Issues, pull requests and repos `(unverified: see the github/github-mcp-server repo)`
Context7 | Current library documentation `(unverified)`
Playwright MCP | Browser automation `(unverified)`

## Safety
- A server runs with your privileges (stdio) or holds your tokens (remote). Install only servers you trust and pin versions.
- Restrict filesystem servers to specific directories, not `/` or `$HOME`.
- Prefer read-only credentials. Tool output can contain prompt injection, so keep write access narrow.
- Debug a server with the MCP Inspector: `npx @modelcontextprotocol/inspector` `(unverified)`.

## See Also
- [Claude Code](claude-code.md)
- [Claude API and SDKs](claude-api.md)
- [Open WebUI and Self-Hosted AI Stacks](open-webui.md)
- [AI](ai.md)
