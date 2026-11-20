#!/usr/bin/env python3
"""Minimal to-do list CLI.

Usage:
    todo.py add <title...>
    todo.py list

Tasks are stored as JSON in the file named by TODO_FILE (default: tasks.json).
"""

import json
import os
import sys
import tempfile

MAX_TITLE_LENGTH = 200


def store_path():
    return os.environ.get("TODO_FILE", "tasks.json")


def load():
    try:
        with open(store_path(), encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"next_id": 1, "tasks": []}


def save(data):
    path = store_path()
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tasks-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def fail(message):
    print(message, file=sys.stderr)
    return 2


def add(words):
    title = " ".join(words).strip()
    if not title:
        return fail("Title must not be empty.")
    if len(title) > MAX_TITLE_LENGTH:
        return fail(f"Title must be at most {MAX_TITLE_LENGTH} characters.")
    data = load()
    task_id = data["next_id"]
    data["tasks"].append({"id": task_id, "title": title})
    data["next_id"] = task_id + 1
    save(data)
    print(f"Added task {task_id}.")
    return 0


def list_tasks():
    tasks = load()["tasks"]
    if not tasks:
        print("No tasks.")
        return 0
    for task in tasks:
        print(f"{task['id']}. {task['title']}")
    return 0


def main(argv):
    if argv[:1] == ["add"]:
        return add(argv[1:])
    if argv == ["list"]:
        return list_tasks()
    return fail("Usage: todo.py add <title...> | todo.py list")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
