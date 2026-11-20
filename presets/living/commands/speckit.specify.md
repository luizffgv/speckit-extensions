## Living Specs

This project keeps **living specs**: each delivered feature's `specs/<feature>/spec.md` has
`**Status**: Living` and is the contract for that feature's current behavior. A new feature owns
only its **new** capability; when it changes behavior an existing living spec owns, that change
is recorded as a **delta** in the new spec and merged into the owning spec when the feature is
archived (`__SPECKIT_COMMAND_LIVING_ARCHIVE__`).

Follow the specify instructions below with these additions. Where they conflict, these win.

1. **Read the living specs first.** Before extracting concepts (execution flow step 2), list
   every `specs/*/spec.md` other than the one being written whose `**Status**` is `Living`, and
   read their user stories, edge cases, requirements, entities, success criteria and assumptions.
   A living spec is **affected** when, once this feature ships, some statement in it would be
   false, incomplete or contradicted. Merely using a feature, or touching the same code, does
   not affect its spec. Specs with any other status are never affected through deltas; if the
   feature would change one, say so in the completion report.
2. **Specify only the new capability** in the spec's own sections. Behavior an affected living
   spec owns (changing it, adding cases to it, removing it) goes **only** in the
   `## Changes to Living Specs` section, never in this spec's own stories, requirements or
   success criteria. Use what the living specs already state as settled context: do not mark
   `[NEEDS CLARIFICATION]` on anything they answer.
3. **Write the `## Changes to Living Specs` section** following the format and rules in the spec
   template's section of that name. It is mandatory: when no living spec is affected, it holds
   only `None: no living spec's behavior changes.` In a non-interactive run, when it is unclear
   whether a spec is affected, record the delta and end its `Why` with `(unsure: <reason>)`.
4. **Features that mostly change existing behavior** still get a valid spec: keep the mandatory
   sections short, describe the user-visible outcome of the change, and point to the deltas
   instead of restating them. Do not fail with "Cannot determine user scenarios" when the
   scenarios live in the affected specs; reference them.
5. **Quality validation** also checks the deltas, adding these items to the checklist:
   - Every affected living spec has a delta subsection, and every target is `Living`.
   - Every `Was` quotes the target's current text exactly.
   - Every `Now` and `ADDED` item is a complete, testable statement.
   - No behavior appears both in this spec's own sections and in a delta.
6. **Never edit another spec.** Deltas are applied only by
   `__SPECKIT_COMMAND_LIVING_ARCHIVE__`.
7. **When updating an existing spec**, refresh the deltas section too.
8. **Completion report**: also list each affected living spec with its count of modified, added
   and removed items, any deltas marked unsure, and any non-living spec the feature would change.

{CORE_TEMPLATE}
