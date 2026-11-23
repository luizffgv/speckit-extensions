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

Follow the plan instructions below with these additions. Where they conflict, these win.

1. **Load the targets.** With FEATURE_SPEC, read the `## Changes to Living Specs` section and the
   `spec.md` of each `UPDATE` and `RETIRE` target in `specs/living/`. For the design behind a
   target, read the `research.md`, `data-model.md` and `contracts/` of the feature directories its
   `**History**` line lists, newest first, as background: they describe the code as it was when
   that feature shipped, and the code is the reference where they differ. Don't read other
   feature directories. If the section holds only `None: …`, skip items 2–4.
2. **Scope includes the deltas and retirements.** The Summary names each target and what changes
   in it. Locate the code that implements each `MODIFIED`/`REMOVED` item's `Was` behavior, and
   the code of each retired capability, and record it in the Project Structure section, so tasks
   can point at it.
3. **Design for the changes.** Research, data model and contracts cover the deltas and
   retirements as well as the new capability: changed or removed entities, fields and interfaces
   are documented in this feature's `data-model.md` and `contracts/` as changes, naming the
   living spec. Never edit another feature's files. A decision that keeps a recorded rationale
   in history from being true anymore is recorded in this feature's `research.md` and says which
   decision (and which feature directory) it supersedes.
4. **Migration and compatibility.** When a delta or retirement changes stored data, a public
   interface or behavior users rely on, the plan states how existing data and callers are
   handled.
5. **Constitution Check** also covers the delta changes.
6. **Never edit a living spec.** If planning shows a delta, name or retirement is wrong or
   missing, say so in the completion report and recommend fixing the spec (or
   `__SPECKIT_COMMAND_LIVING_DELTA__`) before tasks. That includes design decisions that settle
   user-visible behavior a target owns (accepted values, defaults, matching, validation order,
   messages) when its delta doesn't state them: list each one as missing from the delta.
   Incidental text the target never specified (usage or help text) and choices the target's
   unchanged text already settles are not missing; describe such text's new form, if it changes,
   in this feature's `contracts/`.

{CORE_TEMPLATE}
