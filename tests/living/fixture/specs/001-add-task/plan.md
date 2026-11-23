# Implementation Plan: Add Task

**Branch**: `001-add-task` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

## Summary

A single-file Python CLI, `todo.py`, with an `add` command that validates and trims the title,
assigns the next sequential ID and stores the task in a JSON file.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: standard library only
**Storage**: one JSON file named by `TODO_FILE` (default `tasks.json`), see
[research.md](research.md)
**Testing**: `unittest`, running the CLI as a subprocess
**Target Platform**: any OS with Python 3
**Project Type**: single-file CLI
**Constraints**: no third-party packages (constitution, Principle I)

## Constitution Check

- I. Standard library only: pass.
- II. Every behavior has a test: pass (tests/test_todo.py).

## Project Structure

```text
todo.py
tests/test_todo.py
```

**Structure Decision**: one module is enough for two commands; split it only when a third
command needs shared helpers.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Atomic write through a temporary file (more code than a plain `open(..., "w")`) | A crash during a plain write truncates the whole list | A plain write loses every task if interrupted |
