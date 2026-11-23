# Full SDD Cycle with Living Specs

Spec Kit's bundled `speckit` workflow (specify → plan → tasks → implement with review gates),
plus living specs, an analyze-and-fix loop after tasks, and a final step that syncs
`specs/living/` with `speckit.living.sync`. The feature directory stays as history.

A feature can create living specs (named in its spec), change any number of existing ones and
retire others: changes to existing living specs are recorded as deltas in the new spec, planned
and implemented with it, and applied to `specs/living/` when the feature is synced.

## Requirements

The [`living` extension](../../extensions/living/) and [`living` preset](../../presets/living/),
from this repository's catalogs:

```bash
specify extension add living
```

```bash
specify preset add living
```

Extension 0.3.0 or later and preset 0.2.0 or later. The preset makes `speckit.specify` also name
the living specs the feature creates and write the deltas, and makes plan, tasks, analyze and
implement read current behavior from `specs/living/`; without it, the spec gets no deltas and
existing living specs are never updated.

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
   only, names the living spec(s) it will create, and records its changes to existing living
   specs in a `## Changes to Living Specs` section. Then a gate to review the spec, the names and
   the deltas.
2. `speckit.plan` (wrapped): also designs the changes the deltas describe. Then a gate to review
   the plan.
3. `speckit.tasks` (wrapped): also generates tasks for every delta item.
4. `speckit.analyze` (wrapped): also checks every delta item has tasks, every `Was` still
   matches its living spec, and every new name is valid and free. If it reports CRITICAL or HIGH findings, the agent fixes `spec.md`,
   `plan.md` and `tasks.md` (no code) and analysis runs again, up to 3 fixes, each re-checked.
   MEDIUM and LOW findings don't block. Then:
   - still blocked: a gate shows the last report and the run stops;
   - clean after fixes: a gate shows the last report so you can review the fixes before
     implementing.

   The last report is saved to `.specify/workflows/runs/<run-id>/analysis-report.md`.
5. `speckit.implement`.
6. A gate to review the implementation. **Commit everything before approving**: sync refuses
   to run on uncommitted work. After you approve, the workflow checks `git status` (ignoring
   `.specify/workflows/runs/`); if anything is uncommitted, the gate comes back, up to 5 times,
   and then the run stops showing what is still uncommitted. Reject to stop and sync later by
   running `speckit.living.sync` yourself.
7. `speckit.living.sync`: checks every task is done (or waived without leaving a synced statement
   untrue) and every `Was` still matches, then creates, updates and retires the living specs under
   `specs/living/` and `specs/retired/`, updates `specs/living/README.md`, and marks the feature
   `Synced`. It deletes nothing in the feature directory and doesn't commit. A final gate shows
   its report (PR notes, suggested commit message). If sync stopped, that gate shows why and the
   run ends as aborted, not completed.

## Side effects

Agent commands write and edit files in the project. The analyze loop's fix step edits the spec,
plan and tasks, which you review at a gate before implementing. The sync step creates and edits files under `specs/living/`, moves retired specs to
`specs/retired/` (staged by `git mv`, not committed) and edits the feature spec's header. Uses
`sh` to check `git status` before syncing and to save the analysis and sync reports
under `.specify/workflows/runs/<run-id>/`.
