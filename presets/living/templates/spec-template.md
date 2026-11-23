## Changes to Living Specs *(mandatory)*

<!--
  ACTION REQUIRED: Living specs (specs/living/<name>/spec.md, **Status**: Living) state the
  project's current behavior, one per capability. Declare what this feature does to them. They
  are not edited now: speckit.living.sync applies this section once the feature ships.

  - CREATE names each new living spec this feature's own capability goes into: lowercase
    kebab-case, naming the capability, not the change (task-priority, not
    add-priority-to-tasks), unused in specs/living/ and specs/retired/. With one CREATE it
    receives all of this spec's own items; with several, each lists its share in an Items: line
    (Items: US1, FR-001–FR-004, SC-001, Edge Cases). A feature that only changes existing
    behavior has no CREATE.
  - UPDATE holds deltas to a living spec whose behavior this feature changes:
    - MODIFIED and REMOVED name the target item by ID (FR-003, SC-004) or, for items without
      IDs, by heading or short quote. "Was" quotes the target's current text exactly; sync uses
      it to detect that the target changed in the meantime.
    - ADDED items carry no ID (sync assigns the next free one) and start with the target section
      in parentheses, e.g. "- (Functional Requirements) System MUST ...", written in the
      target's own style. "Now" and ADDED text are complete statements, never diffs.
    - Details of a target's behavior (accepted values, defaults, matching, messages) go in its
      delta, never in this spec's own Assumptions or Edge Cases.
    - Record only what this feature adds or changes: no items restating unchanged target
      behavior, and no incidental text the target never specified (usage or help text).
    - Omit empty MODIFIED/ADDED/REMOVED blocks.
  - RETIRE a living spec whose capability this feature removes entirely, with a Why.
  - Blocks in the order CREATE, UPDATE, RETIRE; each living spec appears once.
  - If nothing is created, updated or retired, keep only the line
    "None: no living spec's behavior changes."
-->

Applied to `specs/living/` by sync once this feature ships.

### CREATE specs/living/[capability-name] ([Capability Title])

### UPDATE specs/living/[existing-name] ([Existing Title])

#### MODIFIED

- **FR-[###]** ([Section, e.g., Functional Requirements])
  - Was: [exact current text in the living spec]
  - Now: [complete new text]
  - Why: [reason]

#### ADDED

- ([Section]) [complete new statement, e.g., "System MUST let administrators unlock a locked account"]

#### REMOVED

- **SC-[###]** ([Section])
  - Was: [exact current text in the living spec]
  - Why: [reason]

### RETIRE specs/living/[retired-name] ([Retired Title])

- Why: [reason the capability is removed]
