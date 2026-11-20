# Living Specs

For projects that keep **spec-anchored living specs**: once a feature is delivered, its
`spec.md` stays as the contract for current behavior, while `plan.md`, `tasks.md` and
`checklists/` describe how it was built and go stale.

- `speckit.living.delta` records how a new feature changes existing living specs, as deltas in
  the new feature's `spec.md`. With the companion [`living` preset](../../presets/living/),
  `/speckit.specify` and `/speckit.clarify` write the deltas themselves and this command only
  refreshes them.
- `speckit.living.archive` removes the derived artifacts once the feature is delivered, after
  keeping whatever is still worth knowing, and merges the deltas into the specs they target.

So one feature can add a new living spec and update several existing ones.

## Install

```bash
specify extension add living
```

(Requires this repository's extension catalog; see the repository README.) Needs `git`.

## Commands

| Command | Description |
| --- | --- |
| `speckit.living.delta` | Finds the `Living` specs the current feature changes, moves any of their behavior out of the new spec, and writes a `## Changes to Living Specs` section with `MODIFIED`/`ADDED`/`REMOVED` items per target. `MODIFIED` and `REMOVED` quote the target's current text (`Was`). Never edits the targets. Re-run it after the spec changes. |
| `speckit.living.archive` | Checks every task is done or waived, moves still-true rationale (Complexity Tracking, decisions) from `plan.md` into `research.md`, merges deltas into their target specs, fixes links to the archived files, deletes them with `git rm`, marks `spec.md` `Living`, and prints PR notes. |

Archive arguments: a feature directory, name or number; `--keep plan,tasks,checklists` to keep
some; `--also quickstart,contracts,data-model` to archive more; `--dry-run`.

Waived tasks are reported only in the PR notes it prints, never written into the repository.
It never commits.

The name follows OpenSpec's `archive`. Unlike OpenSpec, nothing is moved to an archive folder:
the files are deleted, and git history keeps them (the spec header records how to recover them).

## Deltas

```markdown
## Changes to Living Specs

### specs/001-user-auth (User Authentication)

#### MODIFIED

- **FR-003** (Functional Requirements)
  - Was: System MUST lock an account after 5 failed sign-in attempts.
  - Now: System MUST lock an account after 3 failed sign-in attempts within 10 minutes.
  - Why: Brute-force protection for the new public API.

#### ADDED

- (Functional Requirements) System MUST let administrators unlock a locked account.
```

Because the deltas sit in the feature's `spec.md`, plan, tasks, analyze and implement all see
them. Archive first checks that every `Was` still matches its target and stops on any mismatch
without changing anything; then it applies the deltas (added items get the next free ID; removed
IDs are never reused), stamps each target's `**Last Updated**` and `**Last changed by**`, removes
the section, and records `**Updated living specs**` in the feature's header. Only specs with
`**Status**: Living` can be targets.

## When to run them

Install the [`living` preset](../../presets/living/) too (`specify preset add living`), so
`/speckit.specify` writes the deltas in the same step as the spec, already knowing which
behavior the living specs own, `/speckit.clarify` keeps them current, and plan, tasks and
analyze cover them (without it, tasks may generate nothing for the deltas).

`speckit.living.delta` refreshes the deltas after the spec changes, such as hand edits. The
extension registers it as an optional `after_clarify` hook, so the agent offers it after
`/speckit.clarify`. Without the preset, run it after `/speckit.specify`, before planning.

`speckit.living.archive` as the last commit of a feature's PR, after reviews and once
implementation is complete. A later change to the feature regenerates `plan.md` and `tasks.md`
from `spec.md` (`/speckit.plan`, `/speckit.tasks`) before implementing.

## Hooks

Other extensions can run around archive with the `before_living_archive` and
`after_living_archive` hook events.
