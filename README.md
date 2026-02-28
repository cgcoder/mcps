# mcps

Personal custom-built MCP (Model Context Protocol) servers.

## Servers

| Server | Language | Description |
|--------|----------|-------------|
| [notes-server](notes-server/) | Python | Create, read, search, and manage personal Markdown notes stored locally |
| [todo-server](todo-server/) | Python | Manage a personal todo list with priorities and due dates |

## Quick start

Each server requires Python 3.11+ and the `mcp` package:

```bash
pip install mcp
```

Then run a server directly:

```bash
python notes-server/server.py
# or
python todo-server/server.py
```

### Configure in Claude Desktop

Add the following to your Claude Desktop config
(`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "notes": {
      "command": "python",
      "args": ["/path/to/mcps/notes-server/server.py"]
    },
    "todo": {
      "command": "python",
      "args": ["/path/to/mcps/todo-server/server.py"]
    }
  }
}
```

See each server's own `README.md` for detailed configuration and environment
variables.
