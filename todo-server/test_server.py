"""Tests for todo-server/server.py."""

import json
import sys
import tempfile
from pathlib import Path
import unittest


def _load_server(todo_dir: str):
    """Import server module with a custom TODO_DIR."""
    import os
    os.environ["TODO_DIR"] = todo_dir
    if "server" in sys.modules:
        del sys.modules["server"]
    sys.path.insert(0, str(Path(__file__).parent))
    import server  # noqa: PLC0415
    return server


class TestTodoServer(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.srv = _load_server(self.tmp)

    # ------------------------------------------------------------------
    def test_add_and_list(self):
        item = json.loads(self.srv.add_todo("Buy milk"))
        self.assertEqual(item["title"], "Buy milk")
        self.assertFalse(item["done"])
        self.assertEqual(item["priority"], "medium")

        todos = json.loads(self.srv.list_todos())
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["id"], item["id"])

    def test_list_hides_done_by_default(self):
        item = json.loads(self.srv.add_todo("Task"))
        self.srv.complete_todo(item["id"])
        todos = json.loads(self.srv.list_todos())
        self.assertEqual(len(todos), 0)

    def test_list_show_done(self):
        item = json.loads(self.srv.add_todo("Task"))
        self.srv.complete_todo(item["id"])
        todos = json.loads(self.srv.list_todos(show_done="true"))
        self.assertEqual(len(todos), 1)
        self.assertTrue(todos[0]["done"])

    def test_complete_todo(self):
        item = json.loads(self.srv.add_todo("Complete me"))
        msg = self.srv.complete_todo(item["id"])
        self.assertIn("done", msg)
        todos = json.loads(self.srv.list_todos(show_done="true"))
        done_item = next(t for t in todos if t["id"] == item["id"])
        self.assertTrue(done_item["done"])
        self.assertNotEqual(done_item["completed_at"], "")

    def test_delete_todo(self):
        item = json.loads(self.srv.add_todo("Delete me"))
        msg = self.srv.delete_todo(item["id"])
        self.assertIn("deleted", msg)
        todos = json.loads(self.srv.list_todos(show_done="true"))
        self.assertEqual(len(todos), 0)

    def test_update_todo(self):
        item = json.loads(self.srv.add_todo("Old title", priority="low"))
        updated = json.loads(self.srv.update_todo(item["id"], title="New title", priority="high"))
        self.assertEqual(updated["title"], "New title")
        self.assertEqual(updated["priority"], "high")

    def test_clear_done(self):
        a = json.loads(self.srv.add_todo("A"))
        b = json.loads(self.srv.add_todo("B"))
        self.srv.complete_todo(a["id"])
        msg = self.srv.clear_done()
        self.assertIn("1", msg)
        todos = json.loads(self.srv.list_todos(show_done="true"))
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["id"], b["id"])

    def test_priority_filter(self):
        self.srv.add_todo("High task", priority="high")
        self.srv.add_todo("Low task", priority="low")
        high = json.loads(self.srv.list_todos(priority="high"))
        self.assertEqual(len(high), 1)
        self.assertEqual(high[0]["title"], "High task")

    def test_complete_nonexistent(self):
        msg = self.srv.complete_todo("no-such-id")
        self.assertIn("not found", msg)

    def test_delete_nonexistent(self):
        msg = self.srv.delete_todo("no-such-id")
        self.assertIn("not found", msg)

    def test_update_nonexistent(self):
        msg = self.srv.update_todo("no-such-id", title="x")
        self.assertIn("not found", msg)


if __name__ == "__main__":
    unittest.main()
