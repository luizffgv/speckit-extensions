# Living Specs

Makes `/speckit.specify` declare, in the same step as the spec, which living specs a feature
creates (and their names), how it changes existing ones (deltas) and which it retires. Makes every
wrapped core command read current behavior from `specs/living/` and treat feature directories as
history. Companion to the [`living` extension](../../extensions/living/) (0.3.0 or later), whose
`speckit.living.sync` applies that section once the feature is delivered.

## Install

```bash
specify extension add living
```

```bash
specify preset add living
```

(Requires this repository's extension and preset catalogs; see the repository README.)

## What it changes

Every wrapped command starts with the same rule: `specs/living/` (index in
`specs/living/README.md`) is the current behavior; `specs/NNN-*` and `specs/retired/` are
history, read only to learn why, starting from the feature directories a living spec's
`**History**` line lists.

| Artifact | Type | Strategy | Change |
| --- | --- | --- | --- |
| `speckit.specify` | command | wrap | Reads the living specs before writing; specifies only the new capability and names the living spec(s) it creates; records changes to behavior existing living specs own as deltas and removed capabilities as retirements; adds checks for all of these to the quality checklist and the completion report. |
| `speckit.clarify` | command | wrap | Reads the living specs first and doesn't ask what they already answer; scans the section for ambiguity (including deltas marked unsure and names that don't fit); writes answers that change a living spec's behavior into its delta, not into the new spec. |
| `speckit.plan` | command | wrap | Reads each delta target in `specs/living/`, and the research, data model and contracts of the features in its `**History**` as background; puts the deltas and retirements in scope, locates the code behind each `Was`, and covers data, interface and migration changes. |
| `speckit.tasks` | command | wrap | Generates tasks for every delta item and retirement, in the story phase that needs it or in a "Changes to Living Specs" phase (`[LS]` label), each ending with its key, e.g. `(Δ user-auth/FR-003)`; adds tasks to update existing tests that assert the old behavior. |
| `speckit.analyze` | command | wrap | Keeps delta items in their own coverage keys (`user-auth/FR-003`) so they never collide with the new spec's IDs; reports delta items without tasks, `Was` text that no longer matches `specs/living/`, invalid or taken names, own requirements with no `CREATE`, plans relying on history, and conflicting or duplicated behavior. |
| `speckit.implement` | command | wrap | Reads the living specs the feature touches; stops a task that would break a living spec the feature doesn't change; never edits `specs/living/`; recommends sync when done. |
| `spec-template` | template | append | Adds the `## Changes to Living Specs` section with `CREATE`, `UPDATE` (`MODIFIED` / `ADDED` / `REMOVED`, with `Was` quoting the living spec's current text) and `RETIRE` blocks. |

Because the core commands are wrapped, not replaced, Spec Kit upgrades to them still apply. Other
presets that wrap or append to the same commands compose with this one.

## Notes

- No command edits `specs/living/` or `specs/retired/`; only `speckit.living.sync` applies the
  section.
- Clarify keeps the section current. After editing the spec by hand, refresh it with
  `speckit.living.delta`.
- The extension README lists the assumptions this layout makes about Spec Kit core.
