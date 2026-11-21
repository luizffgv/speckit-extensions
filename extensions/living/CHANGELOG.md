# Changelog

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
