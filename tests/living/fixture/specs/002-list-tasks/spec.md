# Feature Specification: List Tasks

**Feature Branch**: `002-list-tasks`

**Created**: 2026-09-10

**Status**: Living

**Last Updated**: 2026-09-15

**Archived artifacts**: plan.md, tasks.md, checklists/ (recover with
`git log --diff-filter=D --name-only -- specs/002-list-tasks`)

**Input**: User description: "Show me my tasks"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See all tasks (Priority: P1)

A user wants to see everything on their to-do list, in the order they added it.

**Why this priority**: Tasks are useless if the user can't see them.

**Independent Test**: Add three tasks, list them, and check they appear in the order added.

**Acceptance Scenarios**:

1. **Given** tasks "Charlie", "Alpha" and "Bravo" added in that order, **When** the user lists
   tasks, **Then** the output is "1. Charlie", "2. Alpha", "3. Bravo", one per line.
2. **Given** no tasks, **When** the user lists tasks, **Then** the output is "No tasks.".

---

### Edge Cases

- What happens when the task file doesn't exist yet? The list is treated as empty.
- What happens to the stored tasks when listing? Nothing; listing never changes them.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST list all tasks in the order they were added.
- **FR-002**: System MUST show each task on its own line as "<ID>. <title>".
- **FR-003**: System MUST print "No tasks." when there are no tasks.
- **FR-004**: Listing MUST NOT change the stored tasks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can see every task with a single command.
- **SC-002**: The listed order always matches the order tasks were added.

## Assumptions

- Lists are short enough to print in full; there is no paging or filtering.
