# Changelog

## 0.3.0

Breaking: living specs move out of feature directories.

- Living specs now live in `specs/living/<name>/spec.md`, one per capability, with an index in
  `specs/living/README.md`. Feature directories (`specs/NNN-*`) are history and are never
  deleted or rewritten.
- `speckit.living.archive` is replaced by `speckit.living.sync`. Sync creates, updates and
  retires living specs as the feature's spec declares, marks the feature `Synced` and adds a
  history banner to its `spec.md`. It no longer deletes plan, tasks or other artifacts, and no
  longer moves rationale into `research.md`; `--keep` is gone.
- The `## Changes to Living Specs` section has `CREATE`, `UPDATE` and `RETIRE` blocks. A feature
  names the living specs it creates when it is specified; `UPDATE` holds the same
  `MODIFIED`/`ADDED`/`REMOVED` deltas as before, now targeting `specs/living/<name>`.
- Retired living specs move to `specs/retired/<name>/`.
- Waived tasks no longer block sync unless the waived work leaves a synced statement untrue.
- Hook events are renamed `before_living_sync` and `after_living_sync`.
- README: the layout, naming, how agents tell living specs from history, migrating from 0.2, and
  the assumptions this makes about Spec Kit 1.3.3.

## 0.2.0

- Archive now deletes every derived artifact by default: `data-model.md`, `contracts/` and
  `quickstart.md` as well as `plan.md`, `tasks.md` and `checklists/`. Reasons behind data and
  interface choices move into `research.md`. `--also` is removed; use `--keep` to keep any of them.
- When a spec has no deltas section (for example, a feature written before the extension was
  installed), archive compares it with the living specs and stops if the feature changed one,
  recommending `speckit.living.delta`. It recommends archiving a target that isn't `Living` yet.
- Archive merges deltas even when the feature has no derived artifacts left to delete.
- Delta recommends archive, not planning, as the next step for a feature that is already
  delivered.
- README: adopting the extension in an existing project, which artifacts stay current, and what
  archive leaves uncommitted.

## 0.1.0

- Initial release.
