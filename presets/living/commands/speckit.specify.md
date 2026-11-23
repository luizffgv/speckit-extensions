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

Follow the specify instructions below with these additions. Where they conflict, these win.

1. **Read the living specs first.** Before extracting concepts (execution flow step 2), read
   `specs/living/README.md` and every `specs/living/*/spec.md`: user stories, edge cases,
   requirements, entities, success criteria and assumptions. Do not read other feature
   directories for this. A living spec is **affected** when, once this feature ships, some
   statement in it would be false, incomplete or contradicted. Merely using a capability, or
   touching the same code, does not affect its spec.
2. **Specify only the new capability** in the spec's own sections. Behavior an affected
   living spec owns (changing it, adding cases to it, removing it) goes **only** in that spec's
   `UPDATE` block, never in this spec's own stories, requirements, success criteria, edge cases
   or assumptions. That includes the details of that behavior: accepted values and input forms,
   defaults, matching rules (e.g. case-insensitive), validation and its order, user-visible
   messages. If you decide such a detail, write it into the target's delta (`MODIFIED` or
   `ADDED`), not as an assumption of this spec. Only behavior this feature adds or changes in the
   target needs a delta. Do not add delta items that restate what the target's unchanged text
   already guarantees (e.g. "MUST NOT show the priority" when the target already fixes the line
   format), or that pin incidental text the target never specified, such as usage or help text,
   unless the feature is about it. Prefer an `UPDATE` with `ADDED` items over a new living spec
   when the new behavior is one more case of an existing capability. Use what the living specs
   already state as settled context: do not mark `[NEEDS CLARIFICATION]` on anything they
   answer.
3. **Name the new living specs now.** What remains in this spec's own sections is a new
   capability: give it a `CREATE` block with a name, or several blocks with `Items:` lines when
   the feature adds clearly separate capabilities. The name is a scope decision, reviewed with
   the spec, and may change until sync. Use lowercase kebab-case naming the **capability**, not
   the change (`task-priority`, not `add-priority-to-tasks` or `004-task-priority`), and check it
   is unused in `specs/living/` and `specs/retired/`. A feature that only changes existing
   behavior has no `CREATE`. A capability the feature removes entirely is a `RETIRE`.
4. **Write the `## Changes to Living Specs` section** following the format and rules in the spec
   template's section of that name. Each `ADDED` item starts with its target section in
   parentheses: `- (Functional Requirements) System MUST …`, `- (Edge Cases) What happens when
   …?`. It is mandatory: when nothing is created, updated or retired, it holds only
   `None: no living spec's behavior changes.` In a non-interactive run, when it is unclear
   whether a spec is affected, record the delta and end its `Why` with `(unsure: <reason>)`.
5. **Features that mostly change existing behavior** still get a valid spec: keep the mandatory
   sections short, describe the user-visible outcome of the change, and point to the deltas
   instead of restating them. Do not fail with "Cannot determine user scenarios" when the
   scenarios live in the affected specs; reference them.
6. **Quality validation** also checks the section, adding these items to the checklist:
   - Every affected living spec has an `UPDATE` block, and every `UPDATE`/`RETIRE` target exists
     in `specs/living/`.
   - Every `CREATE` name is kebab-case, names a capability, and is unused in `specs/living/` and
     `specs/retired/`; with several `CREATE` blocks, every own item is in exactly one `Items:`.
   - Every `Was` quotes the living spec's current text exactly.
   - Every `Now` and `ADDED` item is a complete, testable statement.
   - Rules that can apply to the same input (validation, defaults, precedence), in deltas and in
     the target's unchanged requirements, agree on the outcome when an input triggers several of
     them at once.
   - No behavior appears both in this spec's own sections and in a delta, and no detail of a
     target's behavior (input forms, defaults, matching, messages) appears only in this spec's
     own sections, including Assumptions.
   - No delta item restates unchanged target behavior or pins text the target never specified
     (usage or help text).
7. **Never edit a living spec.** The section is applied only by
   `__SPECKIT_COMMAND_LIVING_SYNC__`.
8. **When updating an existing spec**, refresh the section too.
9. **Completion report**: also list the living specs to be created (with their names), each
   affected living spec with its count of modified, added and removed items, any deltas marked
   unsure, and any living spec to be retired.

{CORE_TEMPLATE}
