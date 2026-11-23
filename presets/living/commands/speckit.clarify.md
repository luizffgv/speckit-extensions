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

Follow the clarify instructions below with these additions. Where they conflict, these win.

1. **Read the living specs first.** Before the ambiguity scan, read `specs/living/README.md` and
   every `specs/living/*/spec.md`, not other feature directories. Treat what they state as
   settled: do not ask a question they already answer, unless this feature deliberately changes
   that behavior.
2. **Scan the section too.** Include the `## Changes to Living Specs` section in the ambiguity
   scan: unclear `Now`/`ADDED` text, deltas marked `(unsure: …)`, places where it is unclear
   whether this feature changes a living spec, and `CREATE` names or splits that don't fit the
   capability are candidate questions. Name the living spec in the question so the user knows
   what existing behavior is at stake.
3. **Record answers where the behavior belongs.** An answer about the new capability goes in
   this spec's own sections, as usual. An answer that changes behavior a living spec owns
   goes in that spec's `UPDATE` block (`MODIFIED` quoting its current text exactly in `Was`,
   `ADDED`, or `REMOVED`), creating the block if needed, never in this spec's own sections. An
   answer that keeps a living spec's behavior as it is needs no delta: log it in
   `## Clarifications` only. An answer that confirms an unsure delta removes its `(unsure: …)`
   marker; one that rejects it removes the delta. An answer about a name or split updates the
   `CREATE` blocks. Log every answer in the `## Clarifications` session as usual.
4. **Never edit a living spec.**
5. **Completion report** also lists the changes to the section. It is then current, so the
   optional delta refresh hook can be skipped.

{CORE_TEMPLATE}
