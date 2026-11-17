# Living Specs

For projects that keep **spec-anchored living specs**: once a feature is delivered, its
`spec.md` stays as the contract for current behavior, while `plan.md`, `tasks.md` and
`checklists/` describe how it was built and go stale. `speckit.living.archive` removes those
derived artifacts after keeping whatever is still worth knowing.

## Install

```bash
specify extension add living
```

(Requires this repository's extension catalog; see the repository README.) Needs `git`.

## Commands

| Command | Description |
| --- | --- |
| `speckit.living.archive` | Checks every task is done or waived, moves still-true rationale (Complexity Tracking, decisions) from `plan.md` into `research.md`, fixes links to the archived files, deletes them with `git rm`, marks `spec.md` `Living`, and prints PR notes. |

Arguments: a feature directory, name or number; `--keep plan,tasks,checklists` to keep some;
`--also quickstart,contracts,data-model` to archive more; `--dry-run`.

Waived tasks are reported only in the PR notes it prints, never written into the repository.
It never commits.

The name follows OpenSpec's `archive`. Unlike OpenSpec, nothing is moved to an archive folder:
the files are deleted, and git history keeps them (the spec header records how to recover them).

## When to run it

As the last commit of a feature's PR, after reviews and once implementation is complete. A later
change to the feature regenerates `plan.md` and `tasks.md` from `spec.md` (`/speckit.plan`,
`/speckit.tasks`) before implementing.

## Hooks

Other extensions can run around it with the `before_living_archive` and `after_living_archive`
hook events.
