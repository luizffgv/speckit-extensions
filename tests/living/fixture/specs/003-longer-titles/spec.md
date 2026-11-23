# Feature Specification: Longer Titles

> **History.** This directory records how this feature was specified and built. For current
> behavior read the living specs under **Living specs** below; read this only for why things changed.

**Feature Branch**: `003-longer-titles`

**Created**: 2026-09-16

**Status**: Synced

**Synced**: 2026-09-20

**Living specs**: updated specs/living/add-task

**Input**: User description: "100 characters is too short for some of my task titles, allow 200"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add a task with a longer title (Priority: P1)

A user adds a task whose title is between 101 and 200 characters, and it is accepted. The
validation itself is specified in `specs/living/add-task` (see the deltas below).

**Why this priority**: It is the whole feature.

**Independent Test**: Add a task with a 200-character title and check it is stored.

**Acceptance Scenarios**:

1. **Given** any list, **When** the user adds a 150-character title, **Then** the task is added.

---

## Requirements *(mandatory)*

### Functional Requirements

The changed limit is recorded as deltas to `specs/living/add-task`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: No title of up to 200 characters is rejected for its length.

## Changes to Living Specs

Applied to `specs/living/` by sync once this feature ships.

### UPDATE specs/living/add-task (Add Task)

#### MODIFIED

- **FR-004** (Functional Requirements)
  - Was: System MUST reject a title longer than 100 characters, with the message
    "Title must be at most 100 characters.", and leave the stored tasks unchanged.
  - Now: System MUST reject a title longer than 200 characters, with the message
    "Title must be at most 200 characters.", and leave the stored tasks unchanged.
  - Why: Users need longer titles.
- **Edge Cases** ("longer than 100 characters")
  - Was: What happens when the title is longer than 100 characters? The task is rejected with
    "Title must be at most 100 characters." and the list is unchanged.
  - Now: What happens when the title is longer than 200 characters? The task is rejected with
    "Title must be at most 200 characters." and the list is unchanged.
  - Why: Same limit change.
- **Task** (Key Entities)
  - Was: **Task**: something the user needs to do. Has an ID (sequential, never reused) and a
    title (1–100 characters, trimmed).
  - Now: **Task**: something the user needs to do. Has an ID (sequential, never reused) and a
    title (1–200 characters, trimmed).
  - Why: Same limit change.
