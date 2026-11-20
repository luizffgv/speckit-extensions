# Research: Add Task

Retained from archived plan.

## Decision: JSON file storage with atomic replace

- **Decision**: Store all tasks and the next ID in one JSON file (`TODO_FILE`, default
  `tasks.json`), written to a temporary file and moved into place.
- **Rationale**: No dependencies beyond the standard library; the atomic replace means a crash
  never leaves a half-written file.
- **Alternatives considered**: SQLite (more than a single-user list needs); one file per task
  (makes ordering and ID allocation harder).

## Decision: Keep `next_id` instead of deriving it

- **Decision**: Store the next ID explicitly.
- **Rationale**: FR-005 forbids reusing IDs; deriving `max(id) + 1` would reuse IDs once tasks
  can be deleted.
