## Changes to Living Specs *(mandatory when existing living specs are affected)*

<!--
  ACTION REQUIRED: Record how this feature changes behavior that other living specs
  (specs/*/spec.md with **Status**: Living) own. Those specs are not edited now: these
  deltas are applied to them when this feature is archived (speckit.living.archive).

  - One ### subsection per affected spec, headed by its directory and title.
  - MODIFIED and REMOVED name the target item by ID (FR-003, SC-004) or, for items
    without IDs, by heading or short quote. "Was" quotes the target's current text
    exactly; archive uses it to detect that the target changed in the meantime.
  - ADDED items carry no ID (archive assigns the next free one) and start with the
    target section in parentheses, e.g. "- (Functional Requirements) System MUST ...",
    written in the target's own style. "Now" and ADDED text are complete statements,
    never diffs.
  - Details of a target's behavior (accepted values, defaults, matching, messages) go in
    its delta, never in this spec's own Assumptions or Edge Cases.
  - Record only what this feature adds or changes: no items restating unchanged target
    behavior (e.g. "MUST NOT show X" when the target's format is unchanged), and no
    incidental text the target never specified (usage or help text).
  - Omit empty MODIFIED/ADDED/REMOVED blocks.
  - If no living spec is affected, keep only the line "None: no living spec's behavior changes."
-->

Deltas applied to other living specs when this feature is archived.

### specs/[###-feature-name] ([Feature Title])

#### MODIFIED

- **FR-[###]** ([Section, e.g., Functional Requirements])
  - Was: [exact current text in the target spec]
  - Now: [complete new text]
  - Why: [reason]

#### ADDED

- ([Section]) [complete new statement, e.g., "System MUST let administrators unlock a locked account"]

#### REMOVED

- **SC-[###]** ([Section])
  - Was: [exact current text in the target spec]
  - Why: [reason]
