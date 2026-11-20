## Living Specs

This project keeps **living specs**: each delivered feature's `specs/<feature>/spec.md` has
`**Status**: Living` and is the contract for that feature's current behavior. The current spec
owns only the feature's **new** capability; changes to behavior a living spec owns are
**deltas** in the current spec's `## Changes to Living Specs` section, merged into the owning
spec by `__SPECKIT_COMMAND_LIVING_ARCHIVE__` once the feature ships.

Follow the clarify instructions below with these additions. Where they conflict, these win.

1. **Read the living specs first.** Before the ambiguity scan, list every `specs/*/spec.md`
   other than the current one whose `**Status**` is `Living` and read them. Treat what they
   state as settled: do not ask a question they already answer, unless this feature
   deliberately changes that behavior.
2. **Scan the deltas too.** Include the `## Changes to Living Specs` section in the ambiguity
   scan: unclear `Now`/`ADDED` text, deltas marked `(unsure: …)`, and places where it is unclear
   whether this feature changes a living spec are candidate questions. Name the target spec in
   the question so the user knows what existing behavior is at stake.
3. **Record answers where the behavior belongs.** An answer about the new capability goes in
   this spec's own sections, as usual. An answer that changes behavior a living spec owns
   goes in that target's delta subsection (`MODIFIED` quoting the target's current text
   exactly in `Was`, `ADDED`, or `REMOVED`), creating the subsection if needed, never in this
   spec's own sections. An answer that keeps a target's behavior as it is needs no delta: log
   it in `## Clarifications` only. An answer that confirms an unsure delta removes its
   `(unsure: …)` marker; one that rejects it removes the delta. Log every answer in the
   `## Clarifications` session as usual.
4. **Never edit another spec.**
5. **Completion report** also lists the deltas added, changed or removed. The deltas are then
   current, so the optional delta refresh hook can be skipped.

{CORE_TEMPLATE}
