"""Personal Notes MCP Server.

Provides tools to create, read, list, search, and delete plain-text / Markdown
notes stored as individual files in a local directory.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

NOTES_DIR = Path(os.environ.get("NOTES_DIR", Path.home() / ".mcps" / "notes"))
NOTES_DIR.mkdir(parents=True, exist_ok=True)

mcp = FastMCP("notes-server")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _slug(title: str) -> str:
    """Turn a title into a safe filename slug."""
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-")
    return slug or "note"


def _note_path(note_id: str) -> Path:
    return NOTES_DIR / f"{note_id}.md"


def _load_metadata(path: Path) -> dict:
    """Read the YAML-style front-matter comment block from a note file."""
    meta: dict = {"id": path.stem, "title": path.stem, "created_at": "", "tags": []}
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("<!--"):
            end = text.index("-->")
            raw = text[4:end].strip()
            for line in raw.splitlines():
                if ":" in line:
                    key, _, val = line.partition(":")
                    key = key.strip()
                    val = val.strip()
                    if key == "tags":
                        meta[key] = [t.strip() for t in val.split(",") if t.strip()]
                    else:
                        meta[key] = val
    except Exception:
        pass
    return meta


def _all_notes() -> list[dict]:
    return [_load_metadata(p) for p in sorted(NOTES_DIR.glob("*.md"))]


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def create_note(title: str, content: str, tags: str = "") -> str:
    """Create a new note.

    Args:
        title: The note title.
        content: The note body (Markdown supported).
        tags: Optional comma-separated tags.

    Returns:
        JSON object with the new note's id and path.
    """
    slug = _slug(title)
    # Make filename unique if needed
    base = slug
    counter = 1
    while _note_path(slug).exists():
        slug = f"{base}-{counter}"
        counter += 1

    created_at = datetime.now(timezone.utc).isoformat()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    front_matter = (
        f"<!-- title: {title}\n"
        f"created_at: {created_at}\n"
        f"tags: {', '.join(tag_list)}\n"
        "-->\n\n"
    )
    _note_path(slug).write_text(front_matter + content, encoding="utf-8")
    return json.dumps({"id": slug, "path": str(_note_path(slug))})


@mcp.tool()
def read_note(note_id: str) -> str:
    """Read the full content of a note by its id.

    Args:
        note_id: The note identifier (filename without .md extension).

    Returns:
        The raw Markdown content of the note, or an error message.
    """
    path = _note_path(note_id)
    if not path.exists():
        return f"Error: note '{note_id}' not found."
    return path.read_text(encoding="utf-8")


@mcp.tool()
def list_notes(tag: str = "") -> str:
    """List all notes, optionally filtered by tag.

    Args:
        tag: Optional tag to filter by. Leave empty to list all notes.

    Returns:
        JSON array of note metadata objects.
    """
    notes = _all_notes()
    if tag:
        notes = [n for n in notes if tag in n.get("tags", [])]
    return json.dumps(notes, indent=2)


@mcp.tool()
def search_notes(query: str) -> str:
    """Full-text search across all notes (title + body).

    Args:
        query: The search string (case-insensitive).

    Returns:
        JSON array of matching note metadata objects.
    """
    results = []
    q = query.lower()
    for path in sorted(NOTES_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8").lower()
        if q in text:
            results.append(_load_metadata(path))
    return json.dumps(results, indent=2)


@mcp.tool()
def update_note(note_id: str, content: str) -> str:
    """Replace the body of an existing note (front-matter is preserved).

    Args:
        note_id: The note identifier.
        content: The new Markdown body.

    Returns:
        Confirmation message or error.
    """
    path = _note_path(note_id)
    if not path.exists():
        return f"Error: note '{note_id}' not found."
    text = path.read_text(encoding="utf-8")
    if text.startswith("<!--"):
        end = text.index("-->") + 3
        front = text[:end]
    else:
        front = ""
    path.write_text(front + "\n\n" + content, encoding="utf-8")
    return f"Note '{note_id}' updated."


@mcp.tool()
def delete_note(note_id: str) -> str:
    """Permanently delete a note.

    Args:
        note_id: The note identifier.

    Returns:
        Confirmation message or error.
    """
    path = _note_path(note_id)
    if not path.exists():
        return f"Error: note '{note_id}' not found."
    path.unlink()
    return f"Note '{note_id}' deleted."


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()


def main():
    mcp.run()
