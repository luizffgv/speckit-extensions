# Feature Specification: Add Task

> **History.** This directory records how this feature was specified and built. For current
> behavior read the living specs under **Living specs** below; read this only for why things changed.

**Feature Branch**: `001-add-task`

**Created**: 2026-09-02

**Status**: Synced

**Synced**: 2026-09-09

**Living specs**: created specs/living/add-task

**Input**: User description: "Let me add tasks to a to-do list from the command line"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add a task (Priority: P1)

A user records something they need to do by giving it a title. The task is kept so it is still
there the next time they use the tool.

**Why this priority**: Without adding tasks there is no to-do list.

**Independent Test**: Add a task, then run the tool again and see the task is still stored.

**Acceptance Scenarios**:

1. **Given** an empty list, **When** the user adds "Buy milk", **Then** the tool confirms
   "Added task 1." and the list contains "Buy milk".
2. **Given** a list with one task, **When** the user adds another, **Then** the new task gets
   ID 2.
3. **Given** any list, **When** the user adds "  Water plants  ", **Then** the task is stored as
   "Water plants".

---

### Edge Cases

- What happens when the title is empty or only whitespace? The task is rejected with
  "Title must not be empty." and the list is unchanged.
- What happens when the title is longer than 100 characters? The task is rejected with
  "Title must be at most 100 characters." and the list is unchanged.
- What happens when no task file exists yet? It is created on the first add.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST let users add a task by giving its title.
- **FR-002**: System MUST remove leading and trailing whitespace from the title before storing
  it.
- **FR-003**: System MUST reject a title that is empty after trimming, with the message
  "Title must not be empty.", and leave the stored tasks unchanged.
- **FR-004**: System MUST reject a title longer than 100 characters, with the message
  "Title must be at most 100 characters.", and leave the stored tasks unchanged.
- **FR-005**: System MUST give each new task the next sequential ID, starting at 1. IDs MUST
  never be reused.
- **FR-006**: System MUST keep added tasks across runs.
- **FR-007**: System MUST confirm a successful add with "Added task <ID>.".

### Key Entities

- **Task**: something the user needs to do. Has an ID (sequential, never reused) and a title
  (1–100 characters, trimmed).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can add a task with a single command.
- **SC-002**: Every added task is still listed after the tool is run again.
- **SC-003**: Invalid titles never change the stored tasks.

## Assumptions

- A single user uses the list; there is no concurrent access.
- Tasks are stored in a local file named by `TODO_FILE` (default `tasks.json`).
