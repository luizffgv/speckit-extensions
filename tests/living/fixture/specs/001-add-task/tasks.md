# Tasks: Add Task

**Input**: Design documents from `specs/001-add-task/`

## Phase 1: Setup

- [x] T001 Create `todo.py` with a `main(argv)` entry point and usage error
- [x] T002 [P] Create `tests/test_todo.py` with a subprocess test helper

## Phase 2: User Story 1 - Add a task (P1)

- [x] T003 [US1] Test: add confirms "Added task 1." and the task is stored
- [x] T004 [US1] Test: IDs are sequential and never reused
- [x] T005 [US1] Test: title is trimmed; empty and over-100 titles are rejected with exit code 2
- [x] T006 [US1] Implement JSON load and atomic save in `todo.py`
- [x] T007 [US1] Implement `add` with trimming, validation and ID assignment

## Phase 3: Polish

- [x] T008 Run quickstart.md
