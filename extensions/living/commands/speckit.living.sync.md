---
description: "Sync a delivered feature into the living specs: create, update and retire specs/living/<name>/spec.md as its spec declares, and mark the feature directory as history"
---

# Sync Living Specs

This command supports **living specs**. The project's current behavior is specified in
`specs/living/<name>/spec.md` (`**Status**: Living`), one spec per capability, listed in
`specs/living/README.md`. Feature directories (`specs/NNN-*`) are **history**: each records one
change as it was specified, planned and built, and is never deleted. Retired living specs are moved
to `specs/retired/<name>/`.

A feature's `spec.md` declares, in its `## Changes to Living Specs` section, which living specs it
**creates** (`CREATE`), how it changes existing ones (`UPDATE`, with `MODIFIED`/`ADDED`/`REMOVED`
deltas) and which it **retires** (`RETIRE`). That section is written by `__SPECKIT_COMMAND_SPECIFY__`
(with the `living` preset) or `__SPECKIT_COMMAND_LIVING_DELTA__`. This command applies it once the
feature is delivered, then marks the feature `Synced`.

Sync only creates, edits, moves and indexes files under `specs/living/` and `specs/retired/`, and
updates the header of the feature's `spec.md`. It never deletes or edits any other artifact: the
feature's plan, tasks, research, data model, contracts, quickstart and checklists stay as history.

It requires the implementation to be complete: step 1 stops unless every task is done or waived
and no waiver leaves a synced statement untrue. We recommend running it as the **last commit of a
feature's PR**, after reviews.

It also works on features written before this extension was installed (no
`## Changes to Living Specs` section): see the preconditions.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

Accepted input:

- A feature directory (`specs/002-config-cleanup`), its name, or its number (`002`).
- `--dry-run`: report what would happen, change nothing.
- **Nothing**: fall back to context (see below).

## Resolve the Project and Feature

1. **Project root** (`PROJECT_ROOT`): the nearest ancestor of the current working directory that
   contains `.specify/`. In a repository with nested Spec Kit projects (for example one per module),
   that is the nested project's directory. All paths below are relative to `PROJECT_ROOT`.
2. **Feature directory** (`FEATURE_DIR`), first match wins:
   1. Explicit user input.
   2. The feature the conversation just worked on.
   3. `.specify/feature.json` → `feature_directory`, if that directory exists.
   4. Otherwise list the `specs/*/` directories other than `specs/living/` and `specs/retired/`,
      with each `spec.md`'s `**Status**`, and ask which one. In a non-interactive run (no one to
      ask), stop and report the candidates instead.
3. `FEATURE_DIR` is never `specs/living/…` or `specs/retired/…`: those are not features.
4. State which resolution path was used.

## Pre-Execution Checks

**Check for extension hooks (before syncing)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_living_sync` key.
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue normally.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- Do not interpret hook `condition` expressions: a hook with no or an empty `condition` is executable; a hook with a non-empty `condition` is skipped and left to the HookExecutor.
- For each executable hook:
  - **Optional** (`optional: true`): output
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **Mandatory** (`optional: false`): output
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    then actually invoke the hook the way you would run the command yourself in this session, and wait for it to finish before continuing.
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently.

**Preconditions** (stop and explain if any fails; change nothing):

- `FEATURE_DIR/spec.md` exists.
- Its `**Status**` is not `Synced`. A synced feature is history: further changes to the behavior
  it introduced are a new feature, with their own deltas. Say so and stop.
- `FEATURE_DIR`, `specs/living/` and `specs/retired/` have no uncommitted changes
  (`git status --porcelain -- FEATURE_DIR specs/living specs/retired`). If they do, stop and ask
  the user to commit or discard them first, so the sync is a clean, reviewable diff.
- **If the section `## Changes to Living Specs` exists**, it is well-formed:
  - Each `###` block is `CREATE`, `UPDATE` or `RETIRE` followed by `specs/living/<name>` and a
    title in parentheses. Names are lowercase kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`).
  - Every `CREATE` name is free: neither `specs/living/<name>/` nor `specs/retired/<name>/` exists.
    Names are never reused.
  - Every `UPDATE` and `RETIRE` target exists as `specs/living/<name>/spec.md` with
    `**Status**: Living`.
  - No name appears in more than one block.
  - When there are two or more `CREATE` blocks, each has an `Items:` line, and no item of this
    spec is listed in more than one.
  - Alternatively the section holds only `None: no living spec's behavior changes.`: then the
    feature has nothing to sync except its header (step 7); say so.
- **If the section is missing** (for example, the feature was written before this extension was
  installed, or its spec was marked `Living` by version 0.2 of this extension, which kept living
  specs in feature directories):
  - If `specs/living/` holds living specs, the feature may have changed their behavior without
    recording it. Compare this feature's spec (and, if they are quick to check, its tasks and the
    code it changed) with the living specs. If anything this feature specifies or changed
    contradicts or changes what a living spec states, stop: name the living spec and the
    statement, and recommend `__SPECKIT_COMMAND_LIVING_DELTA__` first. Syncing now would leave
    that spec stale.
  - Otherwise, treat the section as a single `CREATE` of all of the feature's own items, named
    after the feature directory without its number prefix (`specs/002-list-tasks` →
    `list-tasks`). In an interactive run, show the name and ask the user to confirm or choose
    another; in a non-interactive run, use it and say so in the Completion Report. If that name
    is taken, stop and recommend `__SPECKIT_COMMAND_LIVING_DELTA__`, which lets you name it.
  - A spec marked `Living` by version 0.2 may carry `**Last changed by**` and
    `**Updated living specs**` lines naming other feature directories: note them for the
    `**History**` line (step 4).

## Execution

Steps 1–3 only read and check. Change nothing until they all pass.

### 1. Check the work is done and the specs will be true

Read `FEATURE_DIR/tasks.md` (if it exists) and list every unchecked task (`- [ ]`).

- A task is **waived** if its own text says so (e.g. `**Waived by the owner** …`) or the user
  confirms it is waived when asked. In a non-interactive run, only the first counts.
- If any unchecked task is not waived, **stop**: the feature is not delivered. Suggest
  `__SPECKIT_COMMAND_IMPLEMENT__`.
- A waived task is acceptable only **if the living specs will still be true without it**. For
  each one, find the statements it served: the feature's own items being created and the delta
  items (`(Δ …)` keys in the task text name them). If the waived work implements behavior that a
  statement being synced requires (an `ADDED` or `Now` requirement, a created requirement or
  scenario, a `REMOVED` behavior that would still be in the code), **stop**: name the task and
  the statement, and recommend implementing it or changing the spec (or its deltas) so it no
  longer states that behavior. Work that leaves behavior only **unverified** (a skipped test, a
  manual check) does not make a statement untrue: allow it, and list what stays unverified in the
  PR notes.
- Waived tasks are **never written into any file**. Collect them (ID, one-line summary, who waived
  it and why, what stays unverified) for the PR notes in the Completion Report only.

Also scan `FEATURE_DIR/checklists/*.md` for unchecked items. Treat them like tasks: list them, and
stop unless the user confirms each is resolved or waived (waivers again go only to the PR notes).

### 2. Check that each piece of behavior lands in its living spec

Behavior an `UPDATE` target owns must be in that target's delta, or the target will not state it
once synced. Look for details of a target's **user-observable** behavior (accepted values and input
forms, defaults, matching rules, validation and its order, user-visible messages and output) that:

- this feature's own sections state (often Assumptions or Edge Cases) but its delta doesn't, or
- `plan.md`, `research.md`, `data-model.md`, `contracts/` or `tasks.md` decided in a way that
  contradicts what the target will state after the deltas.

Either is **spec drift**: stop, show it, and recommend moving it into the delta (with
`__SPECKIT_COMMAND_LIVING_DELTA__` or by editing the spec). Details decided only in the design
artifacts that leave every synced statement true are not drift; list them in the report as
"decided in design, not specified". Not drift either: internal choices a user cannot observe,
interface syntax and data shapes (the code is their reference), and incidental text no spec
specifies (usage or help text).

The same holds for `CREATE`: behavior of the new capability that only the design artifacts
state, and that contradicts the items being created, is drift.

Also check that nothing this feature specifies is lost: a statement of behavior in its own
sections that no `CREATE` receives (for example, with no `CREATE` at all) and no delta states is
drift too. Notes that only scope this feature ("out of scope", "not part of this change") are not
behavior and stay as history.

### 3. Check every delta against its target

For each `UPDATE` block:

- Every `MODIFIED` and `REMOVED` item exists in the target's `spec.md` and its current text
  matches `Was` (ignoring whitespace and line wrapping).
- Any `Why` marked `(unsure: …)` was resolved. In an interactive run, ask; in a non-interactive
  run, stop.

If any check fails, the target changed since the delta was written: stop, show each mismatch
(expected `Was` versus the current text), and recommend re-running
`__SPECKIT_COMMAND_LIVING_DELTA__`.

With `--dry-run`, stop here and report what steps 4–8 would do.

### 4. Create living specs (`CREATE`)

For each `CREATE specs/living/<name> (<Title>)` block, write `specs/living/<name>/spec.md`:

```markdown
# Living Specification: <Title>

**Status**: Living

**Last Updated**: <today>

**History**: specs/004-task-priority

<one or two sentences: what this capability covers>

## User Scenarios & Testing

### User Story 1 - … (Priority: P1)
…

### Edge Cases
…

## Requirements

### Functional Requirements

- **FR-001**: …

### Key Entities
…

## Success Criteria

### Measurable Outcomes

- **SC-001**: …

## Assumptions
…
```

- **Content**: the items the block's `Items:` line lists, or, with no `Items:` line, all of the
  feature's own user stories (with their acceptance scenarios), edge cases, functional
  requirements, key entities, success criteria and assumptions. `Items:` names stories (`US1`),
  IDs and ranges (`FR-001–FR-004`, `SC-002`), and sections (`Edge Cases`, `Key Entities`,
  `Assumptions`), optionally narrowed with a short quote.
- **Wording**: copy the statements as they are, apart from what follows. Number the items
  afresh in the living spec (`User Story 1…`, `FR-001…`, `SC-001…`, in their original order);
  rewrite references between them to the new numbers. Rewrite references to deltas or to this
  feature ("as changed below", "this feature") so each statement stands on its own. Do not copy
  this feature's header fields (Feature Branch, Created, Input), `## Clarifications` (their
  answers are already in the statements), the `*(mandatory)*` markers, or the
  `## Changes to Living Specs` section. Omit sections that end up empty.
- **History**: `**History**` lists, oldest first, every feature directory that created or
  changed the capability: this `FEATURE_DIR`, preceded, for a spec marked `Living` by version
  0.2 of this extension, by the directories its `**Last changed by**` line named.

### 5. Update living specs (`UPDATE`)

Apply each target's delta to `specs/living/<name>/spec.md`:

- **MODIFIED**: replace the item's text with `Now`, keeping its ID and position.
- **ADDED**: the section is named in parentheses before the text (`- (Functional Requirements)
  …`); also accept `- Functional Requirements: …`. Append the item to that section, giving it the
  next free ID of that kind (`FR-`, `SC-`, …) in the target; items without IDs (stories, edge
  cases, assumptions) go at the end of their section in the target's style. Never reuse a removed
  ID: the highest ID ever given is the highest ID in the target or in any `REMOVED` item of the
  feature directories its `**History**` lists.
- **REMOVED**: delete the item. Do not renumber the remaining items.
- Set `**Last Updated**` to today and append `FEATURE_DIR` to `**History**`.
- Change nothing else in the target.

### 6. Retire living specs (`RETIRE`)

For each `RETIRE specs/living/<name>` block:

- `git mv specs/living/<name> specs/retired/<name>` (create `specs/retired/` if needed).
- In the moved `spec.md`, set `**Status**: Retired`, set `**Last Updated**` to today, append
  `FEATURE_DIR` to `**History**`, and add `**Retired by**: <FEATURE_DIR>` after it. Change nothing
  else: the spec now records the behavior as it was when retired.
- Search the other living specs for references to `specs/living/<name>` and rewrite or remove
  each so no living spec points at retired behavior. Report every edit.

### 7. Index and mark the feature as history

Write `specs/living/README.md` (create it if missing):

```markdown
# Living Specs

The current behavior of this project, one spec per capability. Feature directories under
`specs/` (`specs/NNN-*`) and retired specs under `specs/retired/` are history: read them only to
learn why something changed. Updated by `speckit.living.sync`; edit a spec's text through a
feature's deltas, not by hand.

| Spec | Covers |
| --- | --- |
| [list-tasks](list-tasks/spec.md) | Listing tasks: order, line format, empty list. |
```

One row per directory in `specs/living/`, sorted by name; keep existing rows' wording unless the
spec's scope changed. Retired specs have no row.

Then update `FEATURE_DIR/spec.md`'s header only:

- Set `**Status**: Synced`.
- Add `**Synced**: <today>` after it.
- Add `**Living specs**: created specs/living/a; updated specs/living/b, specs/living/c; retired
  specs/living/d` (omit empty parts; `none` when nothing was synced).
- Right below the title, add:

  ```markdown
  > **History.** This directory records how this feature was specified and built. For current
  > behavior read the living specs under **Living specs** below; read this only for why things changed.
  ```

- For a spec marked `Living` by version 0.2, also remove its `**Last changed by**` and
  `**Updated living specs**` lines (they moved into `**History**`).

Change nothing else in `FEATURE_DIR`. Its `## Changes to Living Specs` section stays as a record
of what the feature changed.

### 8. Do not commit

Leave the changes in the working tree (the retire step's `git mv` stages its moves) for the user
to review and commit as part of the feature's PR.

## Post-Execution Checks

**Check for extension hooks (after syncing)**: same procedure as the pre-execution check, using
the `hooks.after_living_sync` key, with `**Automatic Hook**` / `**Optional Hook**` headings.

## Completion Report

Report:

- `PROJECT_ROOT`, `FEATURE_DIR` and how it was resolved.
- Living specs created (with the items each received), updated (with what changed in each) and
  retired, or "none".
- References rewritten in other living specs.
- Details decided in design but not specified (step 2), if any.
- A **PR notes** block, ready to paste into the PR description:

  ```markdown
  ### Living specs synced (<feature>)
  - Created: <specs/living/name — one line>, or "none"
  - Updated: <specs/living/name — one-line summary of its changes>, or "none"
  - Retired: <specs/living/name — why>, or "none"
  - Waived tasks: <ID — summary — waived by/why — what stays unverified>, or "none"
  ```

  The waived tasks live **only** here; tell the user they will not be recorded anywhere in the
  repository.
- A suggested commit message, e.g. `Sync living specs from <feature>`.

## Guardrails

- Never delete, move or edit any file outside `specs/living/` and `specs/retired/`, except the
  header of `FEATURE_DIR/spec.md`.
- Never apply a delta whose `Was` text no longer matches, and never reuse a living spec's name or
  a removed ID.
- Never sync a feature with unwaived open tasks, or with a waiver that leaves a synced statement
  untrue.
- Never record waived tasks or unchecked checklist items in a file that persists after the work.
- Never commit, push or rewrite history.
