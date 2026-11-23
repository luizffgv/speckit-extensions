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

Follow the tasks instructions below with these additions. Where they conflict, these win.

1. **Load the section.** Besides the user stories, read the `## Changes to Living Specs` section
   of spec.md. Each `MODIFIED`, `ADDED` and `REMOVED` item of an `UPDATE` block is a **delta
   item**, keyed as `<name>/<ID>` (`user-auth/FR-003`), `<name>/ADDED-<n>` for the n-th `ADDED`
   item of that living spec, or `<name>/<short quote>` for items without IDs. Each `RETIRE` block
   is keyed `<name>/RETIRE`. `CREATE` blocks need no keys: their content is this spec's own
   stories. If the section holds only `None: …` or does not exist, skip the rest of this list.
2. **Every delta item and retirement gets tasks.** Read each target's `specs/living/<name>/spec.md`
   for context and find the code that implements the `Was` behavior (or the retired capability).
   Generate the tasks that make the code match `Now` (or add the `ADDED` behavior, or remove the
   `REMOVED` behavior or retired capability). End each such task's description with the key in
   parentheses: `(Δ user-auth/FR-003)`.
3. **Placement.** A delta item a user story depends on goes in that story's phase with the
   story label. All other delta and retirement tasks go in a **Changes to Living Specs** phase
   after the last user story phase and before Polish, labeled `[LS]` in place of a story label
   (`- [ ] T030 [LS] Lower lockout threshold in src/auth/lockout.py (Δ user-auth/FR-003)`).
   Show its dependencies in the Dependencies section like a story's.
4. **Existing tests.** Whether or not tests were requested, when existing tests assert the
   `Was` behavior of a modified or removed item, or a retired capability, add a task to update
   or remove them.
5. **No tasks edit living specs.** Sync applies the section after implementation; tasks never
   touch `specs/living/` or `specs/retired/`.
6. **Validation** also checks that every delta item and retirement has at least one task.
7. **Completion report** also lists the task count per living spec and any delta item or
   retirement without tasks (there should be none).

{CORE_TEMPLATE}
