# Notes Server

A personal notes MCP server that stores plain-text / Markdown notes as
individual `.md` files on your local filesystem.

## Tools

| Tool | Description |
|------|-------------|
| `create_note` | Create a new note with a title, body, and optional tags |
| `read_note` | Read the full content of a note by its id |
| `list_notes` | List all notes, optionally filtered by tag |
| `search_notes` | Full-text search across all notes |
| `update_note` | Replace the body of an existing note |
| `delete_note` | Permanently delete a note |

## Storage

Notes are stored in `~/.mcps/notes/` by default. Override with the
`NOTES_DIR` environment variable.

## Usage

### Run directly

```bash
python server.py
```

### Configure in Claude Desktop / VS Code Copilot

```json
{
  "mcpServers": {
    "notes": {
      "command": "python",
      "args": ["/path/to/notes-server/server.py"],
      "env": {
        "NOTES_DIR": "/path/to/your/notes"
      }
    }
  }
}
```

## Development

```bash
pip install mcp
python server.py
```
