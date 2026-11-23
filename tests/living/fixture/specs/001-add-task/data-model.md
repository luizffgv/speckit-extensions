# Data Model: Add Task

## Task

| Field | Type | Rules |
|-------|------|-------|
| `id` | integer | assigned from `next_id`; never reused |
| `title` | string | trimmed, 1–100 characters |

## Store (`tasks.json`)

```json
{"next_id": 3, "tasks": [{"id": 1, "title": "Buy milk"}, {"id": 2, "title": "Water plants"}]}
```

`next_id` is stored instead of derived from the highest ID: deriving `max(id) + 1` would reuse
IDs once tasks can be deleted, which FR-005 forbids. A missing file means an empty store with
`next_id` 1.
