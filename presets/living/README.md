# Living Specs

Makes `/speckit.specify` write the new living spec and its deltas to existing living specs in one
step, and makes clarify, plan, tasks and analyze treat those deltas as part of the feature.
Companion to the [`living` extension](../../extensions/living/), whose
`speckit.living.archive` merges the deltas into their target specs once the feature is delivered.

## Install

```bash
specify extension add living
```

```bash
specify preset add living
```

(Requires this repository's extension and preset catalogs; see the repository README.)

## What it changes

| Artifact | Type | Strategy | Change |
| --- | --- | --- | --- |
| `speckit.specify` | command | wrap | Before writing, reads every spec with `**Status**: Living`; specifies only the new capability; records changes to behavior those specs own as deltas; adds delta checks to the quality checklist and the completion report. The core instructions are kept unchanged inside the wrapper. |
| `speckit.clarify` | command | wrap | Reads the living specs first and doesn't ask what they already answer; scans the deltas for ambiguity (including deltas marked unsure); writes answers that change a living spec's behavior into that spec's delta, not into the new spec. |
| `speckit.plan` | command | wrap | Reads each delta target's spec, `research.md`, `data-model.md` and `contracts/`; puts the delta changes in scope, locates the code behind each `Was`, and covers data, interface and migration changes to the target features. |
| `speckit.tasks` | command | wrap | Generates tasks for every delta item, in the story phase that needs it or in a "Changes to Living Specs" phase (`[LS]` label), each ending with its key, e.g. `(Δ 001-user-auth/FR-003)`; adds tasks to update existing tests that assert the old behavior. |
| `speckit.analyze` | command | wrap | Keeps delta items in their own coverage keys (`001-user-auth/FR-003`) so they never collide with the new spec's IDs; reports delta items without tasks, `Was` text that no longer matches its target, and conflicting or duplicated behavior as HIGH, and unsure deltas as MEDIUM. |
| `spec-template` | template | append | Adds the `## Changes to Living Specs` section with the delta format (`MODIFIED` / `ADDED` / `REMOVED`, with `Was` quoting the target's current text). |

Because the core commands are wrapped, not replaced, Spec Kit upgrades to them still apply. Other
presets that wrap or append to the same commands compose with this one.

## Notes

- No command edits the other specs; only `speckit.living.archive` applies deltas.
- Clarify keeps the deltas current. After editing the spec by hand, refresh them with
  `speckit.living.delta`.
- Implement needs no change: it follows tasks, which now cover the deltas.
