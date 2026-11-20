## Living Specs

This project keeps **living specs**: each delivered feature's `specs/<feature>/spec.md` has
`**Status**: Living` and is the contract for that feature's current behavior. The current spec's
`## Changes to Living Specs` section holds **deltas**: changes this feature makes to behavior
other living specs own. They are part of this feature's scope and need code like any user story;
`__SPECKIT_COMMAND_LIVING_ARCHIVE__` merges the spec text into the targets once the feature ships.

Follow the tasks instructions below with these additions. Where they conflict, these win.

1. **Load the deltas.** Besides the user stories, read the `## Changes to Living Specs` section
   of spec.md. Each `MODIFIED`, `ADDED` and `REMOVED` item is a **delta item**, keyed as
   `<target dir>/<ID>` (`001-user-auth/FR-003`), `<target dir>/ADDED-<n>` for the n-th `ADDED`
   item of that target, or `<target dir>/<short quote>` for items without IDs. If the section
   holds only `None: …` or does not exist, skip the rest of this list.
2. **Every delta item gets tasks.** Read each target's `spec.md` for context and find the code
   that implements the `Was` behavior. Generate the tasks that make the code match `Now` (or
   add the `ADDED` behavior, or remove the `REMOVED` behavior). End each such task's
   description with the delta key in parentheses: `(Δ 001-user-auth/FR-003)`.
3. **Placement.** A delta item a user story depends on goes in that story's phase with the
   story label. All other delta tasks go in a **Changes to Living Specs** phase after the last
   user story phase and before Polish, labeled `[LS]` in place of a story label
   (`- [ ] T030 [LS] Lower lockout threshold in src/auth/lockout.py (Δ 001-user-auth/FR-003)`).
   Show its dependencies in the Dependencies section like a story's.
4. **Existing tests.** Whether or not tests were requested, when existing tests assert the
   `Was` behavior of a modified or removed item, add a task to update or remove them.
5. **Validation** also checks that every delta item has at least one task.
6. **Completion report** also lists the task count per delta target and any delta item without
   tasks (there should be none).

{CORE_TEMPLATE}
