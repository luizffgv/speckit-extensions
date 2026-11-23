# Changelog

## 0.2.0

Breaking: needs `living` extension 0.3.0, which keeps living specs in `specs/living/`.

- Every wrapped command reads current behavior from `specs/living/` and treats feature
  directories and `specs/retired/` as history, read only for rationale through a living spec's
  `**History**` line.
- Specify names the living specs a feature creates (`CREATE`), next to its deltas (`UPDATE`) and
  retirements (`RETIRE`); the spec template's section has all three.
- Tasks and analyze key deltas by living spec name (`user-auth/FR-003`) and cover retirements.
  Analyze checks names and flags plans that rely on history instead of living specs.
- New `speckit.implement` wrapper: keeps the living specs the feature doesn't change true and
  never edits `specs/living/`.

## 0.1.0

- Initial release.
