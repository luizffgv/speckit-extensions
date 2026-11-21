# Living specs: end-to-end fixture

A tiny to-do CLI (`todo.py`, Python standard library only) that has been through two delivered,
archived features. Use it to try the `living` extension, the `living` preset and the
`living-speckit` workflow with a real agent.

| Spec | Status | Owns |
| --- | --- | --- |
| `specs/001-add-task` | Living (has `research.md`) | Adding tasks: titles trimmed, 1–200 characters, sequential IDs never reused, "Added task <ID>." |
| `specs/002-list-tasks` | Living | Listing tasks in the order added as "<ID>. <title>", "No tasks." when empty |

The code and `tests/` (10 tests) match both specs, and `.specify/memory/constitution.md` is a short
real constitution, so analyze has no placeholders to flag.

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

### A. One new spec, two living specs changed

```bash
specify workflow run living-speckit -i spec="Let users give tasks a priority (high, normal or low) when adding them, and list higher-priority tasks first"
```

Expected:

- **specify**:
  - `specs/003-*/spec.md` owns priorities.
  - Its `## Changes to Living Specs` section has deltas for both 001 and 002. 001 gains the priority on add. 002 has its order (`FR-001`) and line format (`FR-002`) MODIFIED.
  - Every `Was` is quoted exactly from the target.
  - 001 and 002 are unchanged.
- **plan**: covers the changes to `add` and `list`, and how tasks stored without a priority are handled.
- **tasks**:
  - Every delta item has a task ending in `(Δ <target>/<key>)`.
  - There are tasks to update the existing tests that assert the old order and format.
- **analyze**: ends `ANALYSIS: CLEAN`, possibly after fixes.
- **implement**: tests pass.
- **archive**:
  - 001 and 002 contain the new text.
  - ADDED items get the next free ID, e.g. 001's `FR-008`.
  - Both targets get `**Last changed by**: specs/003-…`.
  - 003 is `Living` with `**Updated living specs**`, and has no deltas section.
  - `plan.md`, `tasks.md`, `checklists/`, `data-model.md`, `contracts/` and `quickstart.md` are
    deleted; `spec.md` and `research.md` remain.

### B. No living spec changed

```bash
specify workflow run living-speckit -i spec="Add an export command that prints all tasks as CSV with id and title columns"
```

Expected: the deltas section is only `None: no living spec's behavior changes.`; archive
updates no other spec. Using the task list does not affect 001 or 002.

### C. Target changed before archiving

Run scenario A up to the implementation review gate, then edit the `FR-002` line in
`specs/002-list-tasks/spec.md` and commit. Approve the gate. Expected: archive stops before
changing anything, names the `Was` mismatch, and recommends `/speckit-living-delta`.

### D. Clarify

Run `/speckit-specify` with scenario A's prompt, then `/speckit-clarify`. Expected:
- It asks nothing that 001 or 002 already answer, such as the title limit or the empty-list message.
- An answer that changes listing goes into 002's delta, not into 003's own requirements.

### E. Adopting the extension in an existing codebase

```bash
tests/living/setup.sh --legacy
```

This sets up the same project as it was before the extension was installed: 001 and 002 are
`Draft` specs that were never archived. 001 still has `plan.md` (with a Complexity Tracking
entry), `tasks.md`, `checklists/`, `data-model.md`, `contracts/` and `quickstart.md`, all done;
002 has only its spec. A third feature, `003-friendly-empty-list`, was delivered with the core
commands: it changed the empty-list message, which 002 owns, without recording a delta.

Run `/speckit-living-archive specs/001-add-task`, commit, then `/speckit-living-archive
specs/002-list-tasks`. Expected:
- 001:
  - all six derived artifacts are deleted, leaving `spec.md` and `research.md`;
  - the Complexity Tracking entry and the reason for storing `next_id` (from `data-model.md`)
    move into `research.md`;
  - the spec is `Living` with an `**Archived artifacts**` line.
- 002: archive reports nothing to delete and only marks the spec `Living`. 001 is now
  `Living` and 002 has no deltas section, so archive asks whether 002 changed 001; unattended,
  it flags this in the report.

### F. A feature from before the extension, with an unrecorded change

Continue from E (both 001 and 002 `Living`).

1. Run `/speckit-living-archive specs/003-friendly-empty-list`. Expected: archive stops before
   changing anything, names 002's `FR-003` (003 changed the empty-list message 002 owns), and
   recommends `/speckit-living-delta`.
2. Instead, run `/speckit-living-delta specs/003-friendly-empty-list` first, commit, then
   archive. Expected:
   - the delta modifies 002's `FR-003` and its empty-list acceptance scenario;
   - after archive, 002 states the new message and has `**Last changed by**:
     specs/003-friendly-empty-list`;
   - 003 is `Living` with `**Updated living specs**: specs/002-list-tasks`.
3. Recovery: if 003 was archived without deltas (for example by hand), running
   `/speckit-living-delta` and then archive again still merges the deltas into 002.

## Unattended runs

```bash
tests/living/run.sh "$(tests/living/setup.sh)" "Add an export command that prints all tasks as CSV with id and title columns"
```

`run.sh` runs the workflow and approves every gate. It commits all work just before the
implementation review gate, then prints the final `Status:`. It writes the gate log and answers
to `.specify/workflows/driver/` in the project. A full run takes about 20–40 minutes and 7–11
agent sessions. Check the results against the expectations below.

## Single commands without a TTY

To run one command non-interactively, e.g. archive on a hand-made feature, allow the shell tools
it needs. Otherwise it can't run `git` or Spec Kit's scripts:

```bash
claude -p "/speckit-living-archive specs/003-… This is an automated run: do not ask questions." --permission-mode acceptEdits --allowedTools "Bash(git:*)" "Bash(ls:*)" "Bash(.specify/scripts/bash/*)"
```

## Interactive runs

To step through commands yourself, open Claude Code in the project and run `/speckit-specify …`,
`/speckit-clarify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-analyze`,
`/speckit-implement` and `/speckit-living-archive` in turn.
