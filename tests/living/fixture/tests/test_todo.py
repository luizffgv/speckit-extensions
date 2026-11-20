import os
import subprocess
import sys
import tempfile
import unittest

TODO = os.path.join(os.path.dirname(__file__), "..", "todo.py")


class TodoTestCase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.env = dict(os.environ, TODO_FILE=os.path.join(self.dir.name, "tasks.json"))

    def tearDown(self):
        self.dir.cleanup()

    def run_todo(self, *args):
        return subprocess.run(
            [sys.executable, TODO, *args], env=self.env, capture_output=True, text=True
        )


class AddTaskTests(TodoTestCase):
    def test_adds_task_and_confirms_id(self):
        result = self.run_todo("add", "Buy", "milk")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "Added task 1.\n")
        self.assertEqual(self.run_todo("list").stdout, "1. Buy milk\n")

    def test_ids_are_sequential(self):
        self.run_todo("add", "First")
        self.assertEqual(self.run_todo("add", "Second").stdout, "Added task 2.\n")

    def test_trims_whitespace(self):
        self.run_todo("add", "  Water plants  ")
        self.assertEqual(self.run_todo("list").stdout, "1. Water plants\n")

    def test_rejects_empty_title(self):
        result = self.run_todo("add", "   ")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, "Title must not be empty.\n")
        self.assertEqual(self.run_todo("list").stdout, "No tasks.\n")

    def test_rejects_long_title(self):
        result = self.run_todo("add", "x" * 201)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, "Title must be at most 200 characters.\n")

    def test_accepts_title_at_limit(self):
        self.assertEqual(self.run_todo("add", "x" * 200).returncode, 0)

    def test_tasks_persist_between_runs(self):
        self.run_todo("add", "Persisted")
        self.assertIn("Persisted", self.run_todo("list").stdout)


class ListTasksTests(TodoTestCase):
    def test_empty_list(self):
        result = self.run_todo("list")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "No tasks.\n")

    def test_lists_in_order_added(self):
        for title in ("Charlie", "Alpha", "Bravo"):
            self.run_todo("add", title)
        self.assertEqual(self.run_todo("list").stdout, "1. Charlie\n2. Alpha\n3. Bravo\n")

    def test_listing_does_not_change_tasks(self):
        self.run_todo("add", "Keep")
        with open(self.env["TODO_FILE"], encoding="utf-8") as f:
            before = f.read()
        self.run_todo("list")
        with open(self.env["TODO_FILE"], encoding="utf-8") as f:
            self.assertEqual(f.read(), before)


if __name__ == "__main__":
    unittest.main()
