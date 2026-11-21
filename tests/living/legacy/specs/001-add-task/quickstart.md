# Quickstart: Add Task

```bash
export TODO_FILE=$(mktemp -u)
python3 todo.py add "  Buy milk  "   # Added task 1.
python3 todo.py add ""               # Title must not be empty. (exit 2)
python3 -m unittest discover -s tests
```
