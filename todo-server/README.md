# Todo Server

A personal todo-list MCP server that persists tasks in a single JSON file on
your local filesystem.

## Tools

| Tool | Description |
|------|-------------|
| `add_todo` | Add a new task with title, priority, and optional due date |
| `list_todos` | List pending (or all) tasks, optionally filtered by priority |
| `complete_todo` | Mark a task as done |
| `update_todo` | Update the title, priority, or due date of a task |
| `delete_todo` | Permanently remove a task |
| `clear_done` | Remove all completed tasks in one go |

## Storage

Todos are stored in `~/.mcps/todo/todos.json` by default. Override with the
`TODO_DIR` environment variable.

## Usage

### Run directly

```bash
python server.py
```

### Configure in Claude Desktop / VS Code Copilot

```json
{
  "mcpServers": {
    "todo": {
      "command": "python",
      "args": ["/path/to/todo-server/server.py"],
      "env": {
        "TODO_DIR": "/path/to/your/todo/dir"
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
