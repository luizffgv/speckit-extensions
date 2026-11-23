---
description: "Record which living specs a feature creates, updates (as deltas) and retires, in its spec.md, for sync to apply once the feature ships"
---

# Record Changes to Living Specs

The project's current behavior is specified in **living specs**: `specs/living/<name>/spec.md`
(`**Status**: Living`), one per capability, listed in `specs/living/README.md`. Feature
directories (`specs/NNN-*`) are history. This command decides, for the current feature:

- which **new living specs** it creates, and their names (`CREATE`);
- how it changes behavior existing living specs own (`UPDATE`, as `MODIFIED`/`ADDED`/`REMOVED`
  deltas);
- which living specs it removes from the product entirely (`RETIRE`);

and records them in the feature's `spec.md`. Nothing under `specs/living/` is written now: the
section is reviewed, planned, tasked and implemented with the feature, and
`__SPECKIT_COMMAND_LIVING_SYNC__` applies it once the feature is delivered.

With this repository's `living` preset installed, `__SPECKIT_COMMAND_SPECIFY__` already writes
this section while it writes the spec; use this command to refresh it after the spec changes
(clarification, manual edits). Without the preset, run it after `__SPECKIT_COMMAND_SPECIFY__`,
before planning. It replaces its own section each time.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). It may name the feature
(directory, name or number), name living specs that are or are not affected, or propose names for
new living specs.

## Resolve the Project and Feature

1. **Project root** (`PROJECT_ROOT`): the nearest ancestor of the current working directory that
   contains `.specify/`. All paths below are relative to it.
2. **Feature directory** (`FEATURE_DIR`), first match wins: explicit user input; the feature the
   conversation just worked on; `.specify/feature.json` → `feature_directory`, if that directory
   exists. Otherwise list the `specs/*/` directories other than `specs/living/` and
   `specs/retired/`, with each `spec.md`'s `**Status**`, and ask which one; in a non-interactive
   run (no one to ask), stop and report the candidates instead.
3. If `FEATURE_DIR/spec.md` has `**Status**: Synced`, stop: the feature is history. Changes to
   what it introduced belong to a new feature.
4. State which resolution path was used.

## Execution

### 1. Read the living specs, not history

Read `specs/living/README.md` (if present), then every `specs/living/*/spec.md` (title, user
stories, edge cases, functional requirements, key entities, success criteria, assumptions). Those
are the possible `UPDATE` and `RETIRE` targets.

Do not read other feature directories or `specs/retired/` to learn current behavior: they may
describe behavior later features changed. If `specs/living/` doesn't exist or is empty, there are
no targets: skip to step 3.

### 2. Decide which living specs the feature changes

Read `FEATURE_DIR/spec.md`. A living spec is **affected** when, once the feature ships, some
statement in it would be false, incomplete or contradicted: behavior it specifies changes, gains a
new case, or goes away. A living spec is not affected merely because the feature uses it, touches
the same code, or adds a neighboring capability that leaves its statements true.

- When **every** statement of a living spec stops being true because the feature removes the
  capability, it is a `RETIRE`, not a delta that removes everything.
- When the feature's new behavior is a new case of an existing capability (one more option, one
  more rule for the same command), prefer an `UPDATE` with `ADDED` items over a new living spec.

### 3. Decide which living specs the feature creates, and name them

Whatever the feature specifies in its own sections, once behavior owned by existing living specs
has moved into deltas (step 4), is a **new capability** and needs a home: one `CREATE` block,
or several when the feature adds clearly separate capabilities.

Name each one now, so the name is reviewed with the spec and plan and tasks can refer to it:

- Lowercase kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`), naming the **capability**, not the change:
  `task-priority`, not `add-priority-to-tasks` or `004-task-priority`. The feature directory's
  short name is often a good start but not always the right name.
- Not already used in `specs/living/` or `specs/retired/` (names are never reused).
- With one `CREATE`, no `Items:` line is needed: it receives all of the feature's own items. With
  several, each gets an `Items:` line listing its stories, IDs or ranges and sections
  (`Items: US1, US2, FR-001–FR-004, SC-001, Edge Cases`), and every own item belongs to exactly
  one.

A feature that only changes existing behavior has no `CREATE`: its own sections then only
describe the change's outcome and point to the deltas.

If the user input proposes names, use them unless they break the rules above (then say why).

### 4. Keep each piece of behavior in one spec

The current spec owns the **new** capability; each living spec owns its **existing** behavior.

- If `FEATURE_DIR/spec.md` contains a requirement, scenario, edge case or success criterion that
  really changes or extends behavior a living spec owns, move it out of the current spec into
  that target's delta. If `FEATURE_DIR/plan.md` doesn't exist yet, renumber the current spec's
  remaining IDs to close the gaps (nothing refers to them yet); otherwise leave the gaps.
- If a delta needs a new requirement in the target, it goes in the delta, not in the current
  spec.
- The same goes for details of a target's behavior stated anywhere in the current spec,
  including Assumptions and Edge Cases: accepted values and input forms, defaults, matching
  rules, validation and its order, user-visible messages. Move them into the target's delta.
- Record only what the feature adds or changes. Do not add items that restate what the target's
  unchanged text already guarantees (e.g. "MUST NOT show the priority" when the target's line
  format stays as it is), or that pin incidental text the target never specified (usage or help
  text) unless the feature is about it. When refreshing, remove existing items of either kind.

### 5. Write the section

Replace any existing `## Changes to Living Specs` section in `FEATURE_DIR/spec.md`, or append it
at the end of the file. Format:

```markdown
## Changes to Living Specs

Applied to `specs/living/` by sync once this feature ships.

### CREATE specs/living/account-unlock (Account Unlock)

### UPDATE specs/living/user-auth (User Authentication)

#### MODIFIED

- **FR-003** (Functional Requirements)
  - Was: System MUST lock an account after 5 failed sign-in attempts.
  - Now: System MUST lock an account after 3 failed sign-in attempts within 10 minutes.
  - Why: Brute-force protection for the new public API.

#### ADDED

- (Edge Cases) What happens when an administrator unlocks an account that is not locked?

#### REMOVED

- **SC-004** (Success Criteria)
  - Was: 95% of locked users regain access within 1 hour without support.
  - Why: Unlocking now goes through administrators.

### RETIRE specs/living/security-questions (Security Questions)

- Why: Account recovery no longer uses security questions.
```

Rules:

- Blocks in the order `CREATE`, `UPDATE`, `RETIRE`; each name appears in one block only.
- **MODIFIED** and **REMOVED** name the target item by its ID (`FR-003`, `SC-004`) or, for items
  without IDs (stories, edge cases, assumptions, entities), by its heading or a short quote. `Was`
  quotes the target's **current text exactly**, from `specs/living/`: sync uses it to detect that
  the target changed in the meantime.
- **ADDED** items carry no ID; sync assigns the next free ID in the target. Start each with its
  target section in parentheses (`- (Functional Requirements) …`) and write it in the target's
  own style (`System MUST …`, `Given/When/Then`).
- `Now` and `ADDED` text is the complete new statement, never a diff or "same as before, plus …".
  Omit empty `MODIFIED`/`ADDED`/`REMOVED` blocks.
- Write behavior only (what, not how), as everywhere in a spec.
- If the feature creates, updates and retires nothing, the section contains only the line
  `None: no living spec's behavior changes.`, so reviewers can see the check happened. (Every
  feature that adds behavior of its own creates or updates something.)

In a non-interactive run, when it is unclear whether a target is affected, record the delta and
mark its `Why` with `(unsure: <reason>)`; the spec review decides.

### 6. Leave the living specs alone

Do not edit anything under `specs/living/` or `specs/retired/`, or any file outside `FEATURE_DIR`.
Only `__SPECKIT_COMMAND_LIVING_SYNC__` applies the section.

## Completion Report

Report:

- `FEATURE_DIR` and how it was resolved.
- Living specs to be created, with their names and (with several) items; each affected target
  with the count of modified, added and removed items, and any marked unsure; living specs to be
  retired.
- Requirements moved out of the current spec into deltas.
- Next step: review the section with the spec, then `__SPECKIT_COMMAND_PLAN__`. Planning and tasks
  must cover the code changes the deltas and retirements describe. If the feature was already
  implemented, recommend `__SPECKIT_COMMAND_LIVING_SYNC__` instead of planning. It was if
  `tasks.md` exists and `grep -c '^\s*- \[ \]' FEATURE_DIR/tasks.md` prints 0, or if its spec is
  `Living` (marked by version 0.2 of this extension); run that command, don't guess.

## Guardrails

- Never edit a living spec, and never record deltas against anything outside `specs/living/`.
- Never change the current spec beyond moving items into deltas and writing the section.
- Never commit.
