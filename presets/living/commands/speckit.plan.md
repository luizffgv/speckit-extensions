## Living Specs

This project keeps **living specs**: each delivered feature's `specs/<feature>/spec.md` has
`**Status**: Living` and is the contract for that feature's current behavior. The current spec's
`## Changes to Living Specs` section holds **deltas**: changes this feature makes to behavior
other living specs own. They are part of this feature's scope and need design like any user
story; `__SPECKIT_COMMAND_LIVING_ARCHIVE__` merges the spec text into the targets once the
feature ships.

Follow the plan instructions below with these additions. Where they conflict, these win.

1. **Load the targets.** With FEATURE_SPEC, read the `## Changes to Living Specs` section and
   each target's `spec.md`, plus its `research.md`, `data-model.md` and `contracts/` if present
   (a delivered feature's `plan.md` may have been archived; its retained rationale is in
   `research.md`). If the section holds only `None: …`, skip items 2–4.
2. **Scope includes the deltas.** The Summary names each target and what changes in it. Locate
   the code that implements each `MODIFIED`/`REMOVED` item's `Was` behavior and record it in
   the Project Structure section, so tasks can point at it.
3. **Design for the changes.** Research, data model and contracts cover the deltas as well as
   the new capability: changed or removed entities, fields and interfaces of the target features
   are documented in this feature's `data-model.md` and `contracts/` as changes, naming the
   target. Never edit the target's files. A decision that keeps the targets' recorded rationale
   from being true anymore is recorded in this feature's `research.md` and says which decision
   it supersedes.
4. **Migration and compatibility.** When a delta changes stored data, a public interface or
   behavior users rely on, the plan states how existing data and callers are handled.
5. **Constitution Check** also covers the delta changes.
6. **Never edit another spec.** If planning shows a delta is wrong or missing, say so in the
   completion report and recommend fixing the spec (or `__SPECKIT_COMMAND_LIVING_DELTA__`)
   before tasks.

{CORE_TEMPLATE}
