"""Tests for notes-server/server.py."""

import sys
import tempfile
from pathlib import Path
import unittest


def _load_server(notes_dir: str):
    """Import server module with a custom NOTES_DIR."""
    import os
    os.environ["NOTES_DIR"] = notes_dir
    # Force reimport so module-level NOTES_DIR is re-evaluated
    if "server" in sys.modules:
        del sys.modules["server"]
    sys.path.insert(0, str(Path(__file__).parent))
    import server  # noqa: PLC0415
    return server


class TestNotesServer(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.srv = _load_server(self.tmp)

    # ------------------------------------------------------------------
    def test_create_and_read(self):
        result = self.srv.create_note("Hello World", "This is the body.", "test,demo")
        import json
        data = json.loads(result)
        self.assertIn("id", data)
        note_id = data["id"]

        content = self.srv.read_note(note_id)
        self.assertIn("Hello World", content)
        self.assertIn("This is the body.", content)

    def test_list_notes_empty(self):
        import json
        result = json.loads(self.srv.list_notes())
        self.assertEqual(result, [])

    def test_list_notes_returns_created(self):
        import json
        self.srv.create_note("Note A", "Body A")
        self.srv.create_note("Note B", "Body B")
        notes = json.loads(self.srv.list_notes())
        self.assertEqual(len(notes), 2)

    def test_list_notes_filter_by_tag(self):
        import json
        self.srv.create_note("Tagged", "body", tags="work")
        self.srv.create_note("Untagged", "body", tags="personal")
        work_notes = json.loads(self.srv.list_notes(tag="work"))
        self.assertEqual(len(work_notes), 1)
        self.assertEqual(work_notes[0]["title"], "Tagged")

    def test_search_notes(self):
        import json
        self.srv.create_note("Searchable", "unique_keyword_xyz")
        self.srv.create_note("Other", "nothing special")
        results = json.loads(self.srv.search_notes("unique_keyword_xyz"))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Searchable")

    def test_update_note(self):
        import json
        note_id = json.loads(self.srv.create_note("Update Me", "old content"))["id"]
        msg = self.srv.update_note(note_id, "new content")
        self.assertIn("updated", msg)
        content = self.srv.read_note(note_id)
        self.assertIn("new content", content)
        self.assertNotIn("old content", content)

    def test_delete_note(self):
        import json
        note_id = json.loads(self.srv.create_note("Delete Me", "body"))["id"]
        msg = self.srv.delete_note(note_id)
        self.assertIn("deleted", msg)
        result = self.srv.read_note(note_id)
        self.assertIn("not found", result)

    def test_read_nonexistent(self):
        result = self.srv.read_note("does-not-exist")
        self.assertIn("not found", result)

    def test_delete_nonexistent(self):
        result = self.srv.delete_note("does-not-exist")
        self.assertIn("not found", result)

    def test_duplicate_title_gets_unique_id(self):
        import json
        id1 = json.loads(self.srv.create_note("Dupe", "a"))["id"]
        id2 = json.loads(self.srv.create_note("Dupe", "b"))["id"]
        self.assertNotEqual(id1, id2)


if __name__ == "__main__":
    unittest.main()
