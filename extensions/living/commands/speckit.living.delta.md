---
description: "Record how a new feature changes existing living specs, as deltas in its spec.md that archive later merges into those specs"
---

# Record Changes to Living Specs

A feature often changes behavior that other, already delivered features specify. Their `spec.md`
files are **living specs**: the contract for current behavior. This command finds the living specs
the current feature changes and records each change as a **delta** in the current feature's
`spec.md`. Nothing is written to the other specs now: the deltas are reviewed, planned, tasked and
implemented with the feature, and `__SPECKIT_COMMAND_LIVING_ARCHIVE__` merges them into the target
specs when the feature is delivered.

With this repository's `living` preset installed, `__SPECKIT_COMMAND_SPECIFY__` already writes
the deltas while it writes the spec; use this command to refresh them after the spec changes
(clarification, manual edits). Without the preset, run it after `__SPECKIT_COMMAND_SPECIFY__`,
before planning. It replaces its own section each time.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). It may name the feature
(directory, name or number) and may name living specs that are, or are not, affected.

## Resolve the Project and Feature

1. **Project root** (`PROJECT_ROOT`): the nearest ancestor of the current working directory that
   contains `.specify/`. All paths below are relative to it.
2. **Feature directory** (`FEATURE_DIR`), first match wins: explicit user input; the feature the
   conversation just worked on; `.specify/feature.json` → `feature_directory`, if that directory
   exists. Otherwise list `specs/*/` with each `spec.md`'s `**Status**` and ask which one; in a
   non-interactive run (no one to ask), stop and report the candidates instead.
3. State which resolution path was used.

## Execution

### 1. Find the living specs

List every `specs/*/spec.md` other than `FEATURE_DIR/spec.md` whose `**Status**` is `Living`.
Those are the possible **targets**. If there are none, go to step 4 and record that none are
affected.

Specs with any other status (`Draft`, in progress, `Retired`) are never targets: a feature still
being built is changed in its own directory, not through deltas. If the current feature would
change one of them, say so in the report and do not record a delta for it.

### 2. Decide which targets the feature changes

Read `FEATURE_DIR/spec.md`, then each target's `spec.md` (title, user stories, edge cases,
functional requirements, key entities, success criteria, assumptions). A target is **affected**
when, once the feature ships, some statement in it would be false, incomplete or contradicted:
behavior it specifies changes, gains a new case, or goes away.

A target is not affected merely because the feature uses it, touches the same code, or adds a
neighboring capability that leaves its statements true.

### 3. Keep each piece of behavior in one spec

The current spec owns the **new** capability; each target owns its **existing** behavior.

- If `FEATURE_DIR/spec.md` contains a requirement, scenario, edge case or success criterion that
  really changes or extends behavior a target owns, move it out of the current spec into that
  target's delta. If `FEATURE_DIR/plan.md` doesn't exist yet, renumber the current spec's
  remaining IDs to close the gaps (nothing refers to them yet); otherwise leave the gaps.
- If a delta needs a new requirement in the target, it goes in the delta, not in the current
  spec.

### 4. Write the deltas section

Replace any existing `## Changes to Living Specs` section in `FEATURE_DIR/spec.md`, or append it
at the end of the file. Format:

```markdown
## Changes to Living Specs

Deltas applied to other living specs when this feature is archived.

### specs/001-user-auth (User Authentication)

#### MODIFIED

- **FR-003** (Functional Requirements)
  - Was: System MUST lock an account after 5 failed sign-in attempts.
  - Now: System MUST lock an account after 3 failed sign-in attempts within 10 minutes.
  - Why: Brute-force protection for the new public API.

#### ADDED

- (Functional Requirements) System MUST let administrators unlock a locked account.
- (Edge Cases) What happens when an administrator unlocks an account that is not locked?

#### REMOVED

- **SC-004** (Success Criteria)
  - Was: 95% of locked users regain access within 1 hour without support.
  - Why: Unlocking now goes through administrators.
```

Rules:

- One `###` subsection per affected target, headed by its directory and title. Omit empty
  `MODIFIED`/`ADDED`/`REMOVED` blocks.
- **MODIFIED** and **REMOVED** name the target item by its ID (`FR-003`, `SC-004`) or, for items
  without IDs (stories, edge cases, assumptions, entities), by its heading or a short quote. `Was`
  quotes the target's **current text exactly**: archive uses it to detect that the target changed
  in the meantime.
- **ADDED** items carry no ID; archive assigns the next free ID in the target. Write them in the
  target's own style (`System MUST …`, `Given/When/Then`).
- `Now` and `ADDED` text is the complete new statement, never a diff or "same as before, plus …".
- Write behavior only (what, not how), as everywhere in a spec.
- If no target is affected, the section contains only the line
  `None: no living spec's behavior changes.`, so reviewers can see the check happened.

In a non-interactive run, when it is unclear whether a target is affected, record the delta and
mark its `Why` with `(unsure: <reason>)`; the spec review decides.

### 5. Leave the targets alone

Do not edit any target's `spec.md` or any other file outside `FEATURE_DIR`. Deltas are applied only
by `__SPECKIT_COMMAND_LIVING_ARCHIVE__`.

## Completion Report

Report:

- `FEATURE_DIR` and how it was resolved.
- Each affected target with the count of modified, added and removed items, and any marked unsure.
- Requirements moved out of the current spec into deltas.
- Non-living specs the feature would change (no delta recorded), if any.
- Next step: review the deltas with the spec, then `__SPECKIT_COMMAND_PLAN__`. Planning and tasks
  must cover the code changes the deltas describe.

## Guardrails

- Never edit a target spec, and never record deltas against a spec that is not `Living`.
- Never change the current spec beyond moving items into deltas and writing the deltas section.
- Never commit.
