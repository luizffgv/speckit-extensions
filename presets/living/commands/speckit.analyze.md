## Living Specs

This project keeps **living specs**: each delivered feature's `specs/<feature>/spec.md` has
`**Status**: Living` and is the contract for that feature's current behavior. The current spec's
`## Changes to Living Specs` section holds **deltas**: changes this feature makes to behavior
other living specs own. They are part of this feature's scope;
`__SPECKIT_COMMAND_LIVING_ARCHIVE__` merges them into the targets once the feature ships.

Follow the analyze instructions below with these additions. Where they conflict, these win. The
analysis stays read-only.

1. **Load the deltas** with spec.md, and each target's `spec.md`. If the section holds only
   `None: …`, skip items 2–4.
2. **Separate inventory.** Delta items are not this spec's requirements, even when they share
   an ID: key them as `<target dir>/<ID>` (`001-user-auth/FR-003`), `<target dir>/ADDED-<n>`
   for the n-th `ADDED` item of that target, or `<target dir>/<short quote>` for items without
   IDs. Never merge them with this spec's `FR-###`/`SC-###` keys. List them in the coverage
   table under these keys. Tasks reference them as `(Δ <key>)`.
3. **Additional detection passes** (category **Living Specs**):
   - Delta item with no task: **HIGH** (CRITICAL if it removes or changes security,
     data-integrity or other baseline behavior).
   - `Was` text that does not match the target's current text, or a target that is missing or
     not `Living`: **HIGH**, since archive will refuse to merge.
   - A delta that conflicts with this spec's own requirements, or two deltas that conflict:
     **HIGH**.
   - Behavior specified both in this spec's own sections and in a delta, or behavior a living
     spec owns that this spec changes without a delta: **HIGH**.
   - A delta whose `Why` is marked `(unsure: …)`: **MEDIUM**, to be confirmed or dropped.
   - `Now`/`ADDED` text that is incomplete, a diff, or untestable: as for requirements.
4. **Metrics** also report delta items, delta coverage % and the count of `Was` mismatches.
5. If the `## Changes to Living Specs` section is missing entirely, report one **MEDIUM**
   finding: run `__SPECKIT_COMMAND_LIVING_DELTA__` to record whether living specs change.

{CORE_TEMPLATE}
