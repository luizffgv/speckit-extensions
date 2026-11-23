# CLI Contract: add

```text
todo.py add <title...>
```

The words after `add` are joined with single spaces to form the title.

| Case | stdout | stderr | Exit code |
|------|--------|--------|-----------|
| Added | `Added task <ID>.` | | 0 |
| Empty title | | `Title must not be empty.` | 2 |
| Title over 100 characters | | `Title must be at most 100 characters.` | 2 |
| Unknown command | | usage line | 2 |
