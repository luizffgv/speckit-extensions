# Feature Specification: Friendlier Empty List

**Feature Branch**: `003-friendly-empty-list`

**Created**: 2026-10-01

**Status**: Draft

**Input**: User description: "When the list is empty, tell people how to add a task"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Learn how to add a task from an empty list (Priority: P1)

A new user lists their tasks before adding any. Instead of a bare "No tasks.", they see how to
add one.

**Why this priority**: It is the first thing a new user sees.

**Independent Test**: List tasks with no task file and check the hint is shown.

**Acceptance Scenarios**:

1. **Given** no tasks, **When** the user lists tasks, **Then** the output is
   "No tasks yet. Add one with: todo.py add <title>".

---

### Edge Cases

- What happens when the task file doesn't exist yet? The same hint is shown.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST print "No tasks yet. Add one with: todo.py add <title>" instead of
  "No tasks." when there are no tasks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user who lists an empty list learns the add command without reading the docs.

## Assumptions

- The hint names the script as `todo.py`, the way users run it today.
