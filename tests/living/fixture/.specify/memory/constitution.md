# Todo CLI Constitution

## Core Principles

### I. Standard Library Only

The tool is a single Python 3 script (`todo.py`) using only the standard library. No
third-party packages.

### II. Specified Messages Are Exact

User-facing messages and output formats that a spec quotes MUST be produced exactly as quoted.

### III. Tested Behavior

Every functional requirement MUST be covered by a test in `tests/` that runs the CLI as a
subprocess. `python3 -m unittest discover -s tests` MUST pass before a feature is done.

### IV. Safe Storage

Writes to the task file MUST be atomic (write a temporary file, then replace).

## Governance

This constitution supersedes other practices. Amendments are made by editing this file.

**Version**: 1.0.0 | **Ratified**: 2026-09-01 | **Last Amended**: 2026-09-01
