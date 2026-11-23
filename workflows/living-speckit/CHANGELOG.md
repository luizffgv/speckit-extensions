# Changelog

## 0.2.0

- Ends with `speckit.living.sync` instead of `speckit.living.archive` (living extension 0.3.0,
  preset 0.2.0): living specs are kept in `specs/living/` and the feature directory stays as
  history. The final step's marker is `SYNC: DONE` and its report is saved as `sync-report.md`.
- Renamed to "Full SDD Cycle with Living Specs". Gate messages mention the names of new living
  specs and retirements.

## 0.1.1

- Docs and the implementation review gate list every artifact archive deletes (living 0.2.0
  also archives `data-model.md`, `contracts/` and `quickstart.md`).

## 0.1.0

- Initial release.
