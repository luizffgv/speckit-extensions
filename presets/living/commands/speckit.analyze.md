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

Follow the analyze instructions below with these additions. Where they conflict, these win. The
analysis stays read-only.

1. **Load the section** with spec.md, and the `spec.md` of each `UPDATE` and `RETIRE` target in
   `specs/living/`. If the section holds only `None: …`, skip items 2–4 except the `CREATE`
   checks.
2. **Separate inventory.** Delta items are not this spec's requirements, even when they share
   an ID: key them as `<name>/<ID>` (`user-auth/FR-003`), `<name>/ADDED-<n>` for the n-th
   `ADDED` item of that living spec, or `<name>/<short quote>` for items without IDs, and each
   retirement as `<name>/RETIRE`. Never merge them with this spec's `FR-###`/`SC-###` keys. List
   them in the coverage table under these keys. Tasks reference them as `(Δ <key>)`.
3. **Additional detection passes** (category **Living Specs**):
   - Delta item or retirement with no task: **HIGH** (CRITICAL if it removes or changes
     security, data-integrity or other baseline behavior).
   - `Was` text that does not match the living spec's current text, or an `UPDATE`/`RETIRE`
     target missing from `specs/living/`: **HIGH**, since sync will refuse to apply it. A `Was`
     quoted from a feature directory or `specs/retired/` instead of `specs/living/` is the usual
     cause.
   - A `CREATE` name that is not lowercase kebab-case or is already used in `specs/living/` or
     `specs/retired/`: **HIGH**. With several `CREATE` blocks, an own item in no `Items:` line or
     in more than one: **HIGH**. Own requirements but no `CREATE`, so they would be synced
     nowhere: **HIGH**. A name that describes the change rather than the capability: **LOW**.
   - A delta that conflicts with this spec's own requirements, with the target's requirements
     that stay unchanged, or with another delta: **HIGH**. Check rules that apply to the same
     input together: for every pair of validation, default or precedence rules, consider an input
     that triggers both (e.g. an empty title together with a missing option value) and report
     any pair that gives different outcomes for it.
   - Behavior specified both in this spec's own sections and in a delta, or behavior a living
     spec owns that this spec changes without a delta: **HIGH**.
   - A detail of a target's **user-observable** behavior (accepted values or input forms,
     defaults, matching rules, validation and its order, user-visible messages and output)
     missing from that target's delta, **even when a delta for that item exists but its
     `Now`/`ADDED` text omits it**:
     - stated in this spec's own sections (including Assumptions and Edge Cases): **HIGH**,
       since sync would apply an incomplete delta and stop on the leftover. Remedy: move it
       into the target's delta and remove it from this spec's own sections;
     - decided only in plan.md, research.md or tasks.md: **MEDIUM**, unless it contradicts the
       spec or a delta (then it is a conflict, **HIGH**). Remedy: add it to the delta.

     Not findings: internal choices a user cannot observe (how data is stored or read, whether
     files are rewritten, robustness against hand-edited data), interface syntax and data shapes
     in `contracts/` and `data-model.md`, and incidental text the target never specified (usage
     or help text). Not pinning such text in a delta does not mean it must stay unchanged: the
     feature's own `contracts/` may describe its new form.
   - Plan, research or tasks that rely on another feature directory's description of behavior
     that its living spec states differently: **HIGH**. The living spec is current.
   - A delta item that only restates what the target's unchanged text already guarantees, or that
     pins incidental text the target never specified (usage or help text) when the feature is not
     about it: **MEDIUM**. Remedy: remove the item.
   - A delta whose `Why` is marked `(unsure: …)`: **MEDIUM**, to be confirmed or dropped.
   - `Now`/`ADDED` text that is incomplete, a diff, or untestable: as for requirements.
   - An `ADDED` item that does not start with its target section in parentheses
     (`- (Functional Requirements) …`): **LOW**.
4. **Metrics** also report delta items, delta coverage % and the count of `Was` mismatches.
5. If the `## Changes to Living Specs` section is missing entirely, report one **MEDIUM**
   finding: run `__SPECKIT_COMMAND_LIVING_DELTA__` to record what the feature creates, updates
   and retires.

{CORE_TEMPLATE}
