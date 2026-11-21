# Full SDD Cycle with Living Archive

Spec Kit's bundled `speckit` workflow (specify → plan → tasks → implement with review gates),
plus living-spec deltas, an analyze-and-fix loop after tasks, and a final step that archives the
feature's derived artifacts with `speckit.living.archive`, leaving `spec.md` as the living spec.

A feature can create one new living spec and change any number of existing ones: changes to
existing living specs are recorded as deltas in the new spec, planned and implemented with it,
and merged into those specs when the feature is archived.

## Requirements

The [`living` extension](../../extensions/living/) and [`living` preset](../../presets/living/),
from this repository's catalogs:

```bash
specify extension add living
```

```bash
specify preset add living
```

The preset makes `speckit.specify` also write the deltas, and makes plan, tasks and analyze cover
them; without it, the spec gets no deltas and existing living specs are never updated.

## Install

```bash
specify workflow add living-speckit
```

## Run

```bash
specify workflow run living-speckit -i spec="Describe what to build"
```

## Inputs

| Input | Required | Description |
| --- | --- | --- |
| `spec` | yes | Describe what to build |
| `integration` | no | Agent integration (default `auto`) |

## Steps

1. `speckit.specify` (wrapped by the `living` preset): writes the new spec for the new capability
   only, and records its changes to existing living specs in a `## Changes to Living Specs`
   section. Then a gate to review the spec and its deltas.
2. `speckit.plan` (wrapped): also designs the changes the deltas describe. Then a gate to review
   the plan.
3. `speckit.tasks` (wrapped): also generates tasks for every delta item.
4. `speckit.analyze` (wrapped): also checks every delta item has tasks and every `Was` still
   matches its target. If it reports CRITICAL or HIGH findings, the agent fixes `spec.md`,
   `plan.md` and `tasks.md` (no code) and analysis runs again, up to 3 fixes, each re-checked.
   MEDIUM and LOW findings don't block. Then:
   - still blocked: a gate shows the last report and the run stops;
   - clean after fixes: a gate shows the last report so you can review the fixes before
     implementing.

   The last report is saved to `.specify/workflows/runs/<run-id>/analysis-report.md`.
5. `speckit.implement`.
6. A gate to review the implementation. **Commit everything before approving**: archive refuses
   to run on uncommitted work. After you approve, the workflow checks `git status` (ignoring
   `.specify/workflows/runs/`); if anything is uncommitted, the gate comes back, up to 5 times,
   and then the run stops showing what is still uncommitted. Reject to stop and archive later by
   running `speckit.living.archive` yourself.
7. `speckit.living.archive`: moves durable rationale into `research.md`, merges the deltas into
   the existing living specs (stopping if one changed since its delta was written), deletes
   the derived artifacts (`plan.md`, `tasks.md`, `checklists/`, `data-model.md`, `contracts/`,
   `quickstart.md`) with `git rm`, and marks `spec.md` `Living`. It doesn't
   commit; changes to the other specs are left in the working tree with the rest. A final gate
   shows its report (PR notes, suggested commit message). If archive stopped without archiving,
   that gate shows why and the run ends as aborted, not completed.

## Side effects

Agent commands write and edit files in the project. The analyze loop's fix step edits the spec,
plan and tasks, which you review at a gate before implementing. The archive step deletes files
(staged, not committed) and edits the living specs named in the deltas. Uses `sh` to check `git status` before archiving and to save the analysis and archive reports
under `.specify/workflows/runs/<run-id>/`.
