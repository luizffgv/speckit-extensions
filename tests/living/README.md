# Living specs: end-to-end fixture

A tiny to-do CLI (`todo.py`, Python standard library only) that has been through three delivered,
synced features. Use it to try the `living` extension, the `living` preset and the
`living-speckit` workflow with a real agent.

| Path | Status | What it is |
| --- | --- | --- |
| `specs/living/add-task` | Living | Adding tasks: titles trimmed, 1–200 characters, sequential IDs never reused, "Added task <ID>." |
| `specs/living/list-tasks` | Living | Listing tasks in the order added as "<ID>. <title>", "No tasks." when empty |
| `specs/living/README.md` | | The index |
| `specs/001-add-task` | Synced | History, with every artifact (plan, tasks, research, data model, contracts, quickstart, checklists). It specified a **100**-character limit. |
| `specs/002-list-tasks` | Synced | History (spec only) |
| `specs/003-longer-titles` | Synced | History: raised the limit to 200 through a delta to `add-task` |

The code and `tests/` (10 tests) match the living specs, and `.specify/memory/constitution.md` is
a short real constitution, so analyze has no placeholders to flag.

The 100-character limit in `specs/001-add-task` is a trap: an agent that reads history as current
behavior will quote it. Nothing a scenario produces should mention a 100-character limit.

## Set up

```bash
tests/living/setup.sh
```

It prints the path of a new git repository (a temp dir, or the path you pass). That project has:
- Spec Kit initialised for Claude;
- the fixture files on top;
- this repository's extension, preset and workflow installed from the working tree (`--dev`);
- one baseline commit.

Re-run it after changing any of them. Requires `specify` and `git`.

## Scenarios

### A. One new living spec, two living specs changed

```bash
specify workflow run living-speckit -i spec="Let users give tasks a priority (high, normal or low) when adding them, and list higher-priority tasks first"
```

Expected:

- **specify**:
  - Either a `CREATE` naming a capability (e.g. `specs/living/task-priority`, not the change)
    for the priority behavior, or none, with priority recorded as `ADDED` items in `add-task`
    (both are valid; a run on 2026-11-22 chose the latter).
  - `UPDATE` blocks for `add-task` (priority on add) and `list-tasks` (its order `FR-001`
    MODIFIED).
  - Every `Was` is quoted exactly from `specs/living/`.
  - Nothing under `specs/living/` changes.
- **plan**: covers the changes to `add` and `list`, and how tasks stored without a priority are
  handled. It doesn't mention a 100-character limit.
- **tasks**:
  - Every delta item has a task ending in `(Δ <name>/<key>)`, e.g. `(Δ list-tasks/FR-001)`.
  - There are tasks to update the existing tests that assert the old order and format.
- **analyze**: ends `ANALYSIS: CLEAN`, possibly after fixes.
- **implement**: tests pass.
- **sync**:
  - If the section has a `CREATE`, `specs/living/<new name>/spec.md` exists with the feature's
    own items, `**Status**: Living` and `**History**: specs/004-…`, without the feature's header
    fields or deltas, and the index has a row for it.
  - `add-task` and `list-tasks` contain the new text. ADDED items get the next free ID (e.g.
    `add-task`'s `FR-008`), and `specs/004-…` is appended to their `**History**`.
  - 004 is `Synced` with the history banner and a `**Living specs**` line, and keeps every
    artifact (`plan.md`, `tasks.md`, `research.md`, …) and its deltas section.
  - `specs/001-*` to `specs/003-*` are unchanged.

### B. Only a new living spec

```bash
specify workflow run living-speckit -i spec="Add an export command that prints all tasks as CSV with id and title columns"
```

Expected: the section has one `CREATE` (e.g. `specs/living/task-export`) and no `UPDATE`: using
the task list doesn't affect `add-task` or `list-tasks`. Sync creates the spec and the index row
and changes no other living spec.

### C. Living spec changed before syncing

Run scenario A up to the implementation review gate, then edit the `FR-002` line in
`specs/living/list-tasks/spec.md` and commit. Approve the gate. Expected: sync stops before
changing anything, names the `Was` mismatch, and recommends `/speckit-living-delta`.

### D. Clarify

Run `/speckit-specify` with scenario A's prompt, then `/speckit-clarify`. Expected:
- It asks nothing that the living specs already answer, such as the title limit or the empty-list
  message, and never cites the 100-character limit.
- An answer that changes listing goes into the `list-tasks` delta, not into 004's own
  requirements.

### E. Retiring a living spec

```bash
specify workflow run living-speckit -i spec="Remove the list command. Instead, after each successful add, print every task as '<ID>. <title>', one per line, in the order added"
```

Expected:
- The section `RETIRE`s `specs/living/list-tasks` and `UPDATE`s `add-task` (probably no
  `CREATE`).
- Tasks remove the list command and its tests (`(Δ list-tasks/RETIRE)`).
- Sync moves the spec to `specs/retired/list-tasks/` with `**Status**: Retired` and
  `**Retired by**: specs/004-…`, and removes its row from the index.

### F. Waived tasks

After scenario A's implement step, before syncing:
1. Mark a test-only task unchecked with `**Waived by the owner** – manual check only`. Expected:
   sync runs and lists the task, and what stays unverified, only in the PR notes.
2. Instead, mark an implementation task waived and revert its code. Expected: sync stops, naming
   the task and the living spec statement that would be untrue.

### G. Adopting the extension in an existing codebase

```bash
tests/living/setup.sh --legacy
```

This sets up the same project as it was before the extension was installed: there is no
`specs/living/`, and 001 and 002 are `Draft` specs. 001 has every artifact, all tasks done; 002
has only its spec. A third feature, `003-friendly-empty-list`, was delivered with the core
commands: it changed the empty-list message, which 002 owns, without recording a delta.

Run `/speckit-living-sync specs/001-add-task`, commit, then `/speckit-living-sync
specs/002-list-tasks`. Expected:
- 001: no living spec exists, so sync creates `specs/living/add-task` from all of 001's items and,
  unattended, says it chose the name. Every file in `specs/001-add-task/` stays; `spec.md` is
  `Synced` with the banner.
- 002: sync compares 002 with `add-task`, finds no change to it (unattended, it says so) and
  creates `specs/living/list-tasks`.
- The index lists both.

### H. A feature from before the extension, with an unrecorded change

Continue from G.

1. Run `/speckit-living-sync specs/003-friendly-empty-list`. Expected: sync stops before
   changing anything, names `list-tasks`'s `FR-003` (003 changed the empty-list message), and
   recommends `/speckit-living-delta`.
2. Run `/speckit-living-delta specs/003-friendly-empty-list`, commit, then sync. Expected:
   - the section `UPDATE`s `list-tasks` (`FR-003` and its empty-list acceptance scenario) and
     creates nothing, since 003 has no capability of its own;
   - delta recommends sync, not planning, because every task is done;
   - after sync, `list-tasks` states the new message and its `**History**` is
     `specs/002-list-tasks, specs/003-friendly-empty-list`;
   - 003 is `Synced` with `**Living specs**: updated specs/living/list-tasks`.

## Unattended runs

```bash
tests/living/run.sh "$(tests/living/setup.sh)" "Add an export command that prints all tasks as CSV with id and title columns"
```

`run.sh` runs the workflow and approves every gate. It commits all work just before the
implementation review gate, then prints the final `Status:`. It writes the gate log and answers
to `.specify/workflows/driver/` in the project. A full run takes about 20–40 minutes and 7–11
agent sessions. Check the results against the scenarios above.

## Single commands without a TTY

To run one command non-interactively, e.g. sync on a hand-made feature, allow Bash. Narrower
patterns such as `Bash(git:*)` miss compound commands, so the agent can't run `git status` or
list directories and skips those checks. The project is a throwaway, so this is safe:

```bash
claude -p "/speckit-living-sync specs/003-… This is an automated run: do not ask questions." --permission-mode acceptEdits --allowedTools Bash
```

## Interactive runs

To step through commands yourself, open Claude Code in the project and run `/speckit-specify …`,
`/speckit-clarify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-analyze`,
`/speckit-implement` and `/speckit-living-sync` in turn.
