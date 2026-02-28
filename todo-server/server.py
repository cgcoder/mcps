"""Personal Todo-List MCP Server.

Provides tools to add, complete, list, and delete todo items persisted as
a local JSON file.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATA_DIR = Path(os.environ.get("TODO_DIR", Path.home() / ".mcps" / "todo"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
TODOS_FILE = DATA_DIR / "todos.json"

mcp = FastMCP("todo-server")


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------


def _load() -> list[dict]:
    if TODOS_FILE.exists():
        try:
            return json.loads(TODOS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save(todos: list[dict]) -> None:
    TODOS_FILE.write_text(json.dumps(todos, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def add_todo(title: str, priority: str = "medium", due_date: str = "") -> str:
    """Add a new todo item.

    Args:
        title: Short description of the task.
        priority: One of 'low', 'medium', or 'high'. Defaults to 'medium'.
        due_date: Optional due date in ISO 8601 format (e.g. '2024-12-31').

    Returns:
        JSON object with the new todo item.
    """
    todos = _load()
    item = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "done": False,
        "priority": priority,
        "due_date": due_date,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": "",
    }
    todos.append(item)
    _save(todos)
    return json.dumps(item, indent=2)


@mcp.tool()
def list_todos(show_done: str = "false", priority: str = "") -> str:
    """List todo items.

    Args:
        show_done: Set to 'true' to include completed items. Defaults to 'false'.
        priority: Filter by priority ('low', 'medium', or 'high'). Leave empty
                  for all priorities.

    Returns:
        JSON array of todo items.
    """
    todos = _load()
    if show_done.lower() != "true":
        todos = [t for t in todos if not t["done"]]
    if priority:
        todos = [t for t in todos if t.get("priority") == priority]
    return json.dumps(todos, indent=2)


@mcp.tool()
def complete_todo(todo_id: str) -> str:
    """Mark a todo item as done.

    Args:
        todo_id: The short id of the todo item (from add_todo / list_todos).

    Returns:
        Confirmation message or error.
    """
    todos = _load()
    for item in todos:
        if item["id"] == todo_id:
            item["done"] = True
            item["completed_at"] = datetime.now(timezone.utc).isoformat()
            _save(todos)
            return f"Todo '{todo_id}' marked as done."
    return f"Error: todo '{todo_id}' not found."


@mcp.tool()
def delete_todo(todo_id: str) -> str:
    """Permanently remove a todo item.

    Args:
        todo_id: The short id of the todo item.

    Returns:
        Confirmation message or error.
    """
    todos = _load()
    new_todos = [t for t in todos if t["id"] != todo_id]
    if len(new_todos) == len(todos):
        return f"Error: todo '{todo_id}' not found."
    _save(new_todos)
    return f"Todo '{todo_id}' deleted."


@mcp.tool()
def update_todo(todo_id: str, title: str = "", priority: str = "", due_date: str = "") -> str:
    """Update fields of an existing todo item.

    Args:
        todo_id: The short id of the todo item.
        title: New title (leave empty to keep the current value).
        priority: New priority (leave empty to keep the current value).
        due_date: New due date (leave empty to keep the current value).

    Returns:
        JSON object of the updated todo item, or error message.
    """
    todos = _load()
    for item in todos:
        if item["id"] == todo_id:
            if title:
                item["title"] = title
            if priority:
                item["priority"] = priority
            if due_date:
                item["due_date"] = due_date
            _save(todos)
            return json.dumps(item, indent=2)
    return f"Error: todo '{todo_id}' not found."


@mcp.tool()
def clear_done() -> str:
    """Remove all completed todo items.

    Returns:
        Confirmation message with the number of items removed.
    """
    todos = _load()
    remaining = [t for t in todos if not t["done"]]
    removed = len(todos) - len(remaining)
    _save(remaining)
    return f"Removed {removed} completed todo item(s)."


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()


def main():
    mcp.run()
