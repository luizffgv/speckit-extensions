## Living Specs

This project keeps **living specs**: `specs/living/<name>/spec.md` (`**Status**: Living`), one per
capability, listed in `specs/living/README.md`, state its **current behavior**. Feature
directories (`specs/NNN-*`) are **history**: each records one change as it was specified and
built, and may describe behavior later features changed. Retired living specs in
`specs/retired/` are history too.

- For what the product does now, read the living specs. Never read another feature's directory
  or `specs/retired/` as a statement of current behavior.
- Read history only to learn **why** something is the way it is: start from the feature
  directories a living spec's `**History**` line lists (newest last). Where history and a living
  spec or the code disagree, the living spec and the code win.

The current feature's `## Changes to Living Specs` section declares which living specs it
creates (`CREATE`, with their names), how it changes existing ones (`UPDATE`, as
`MODIFIED`/`ADDED`/`REMOVED` deltas) and which it retires (`RETIRE`).
`__SPECKIT_COMMAND_LIVING_SYNC__` applies it once the feature ships. Until then, nothing under
`specs/living/` or `specs/retired/` is edited.

Follow the implement instructions below with these additions. Where they conflict, these win.

1. **Read the living specs the feature touches.** Besides the feature's own artifacts, read the
   `## Changes to Living Specs` section and the `spec.md` of each `UPDATE` and `RETIRE` target in
   `specs/living/`. For behavior the feature doesn't change, the living specs are the reference;
   don't take it from other feature directories.
2. **Keep the rest of the living specs true.** Code changed for this feature must not break
   behavior a living spec states unless a delta or retirement in this feature changes it. If a
   task would, stop that task and report the conflict, recommending a delta
   (`__SPECKIT_COMMAND_LIVING_DELTA__`).
3. **Never edit `specs/living/` or `specs/retired/`.** `__SPECKIT_COMMAND_LIVING_SYNC__`
   applies the section after implementation.
4. **Completion report** also recommends `__SPECKIT_COMMAND_LIVING_SYNC__` once every task is
   done, as the last commit of the feature's PR.

{CORE_TEMPLATE}
