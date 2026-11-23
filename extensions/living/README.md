# Living Specs

For projects that keep **living specs**: a specification of the product's current behavior that
stays true as features change it. This extension keeps them apart from feature history:

```text
specs/
  living/
    README.md            index: one line per living spec
    add-task/spec.md     current behavior, one spec per capability (Status: Living)
    list-tasks/spec.md
  retired/
    legacy-export/spec.md  capabilities removed from the product (Status: Retired)
  001-add-task/          history: how each change was specified, planned and built
  002-list-tasks/
  004-task-priority/
```

- `speckit.living.delta` records, in a feature's `spec.md`, which living specs the feature
  **creates** (and their names), how it **updates** existing ones (deltas) and which it
  **retires**. With the companion [`living` preset](../../presets/living/), `/speckit.specify`
  and `/speckit.clarify` write that section themselves and this command only refreshes it.
- `speckit.living.sync` applies the section once the feature is delivered: it creates, updates
  and retires files under `specs/living/` and `specs/retired/`, updates the index, and marks the
  feature `Synced`. It never deletes or edits the feature's other artifacts.

## Install

```bash
specify extension add living
```

(Requires this repository's extension catalog; see the repository README.) Needs `git`.

## Commands

| Command | Description |
| --- | --- |
| `speckit.living.delta` | Reads the living specs, decides what the current feature creates, updates and retires, moves behavior existing living specs own out of the new spec into deltas, and writes a `## Changes to Living Specs` section. `MODIFIED` and `REMOVED` quote the target's current text (`Was`). Never edits the living specs. Re-run it after the spec changes. |
| `speckit.living.sync` | Checks every task is done or waived (and that no waiver leaves a synced statement untrue), checks every `Was` still matches, then creates, updates and retires the living specs, rewrites `specs/living/README.md`, marks the feature `Synced` and prints PR notes. |

Sync arguments: a feature directory, name or number; `--dry-run`.

Waived tasks are allowed only when the living specs stay true without them: a skipped test leaves
a statement unverified (listed in the PR notes), but skipped implementation of a synced
requirement makes sync stop. Waivers are reported only in the PR notes it prints, never written
into the repository. Sync leaves its changes in the working tree (retirements are staged by
`git mv`) and never commits: review the result and commit it yourself.

## The section a feature declares

```markdown
## Changes to Living Specs

### CREATE specs/living/account-unlock (Account Unlock)

### UPDATE specs/living/user-auth (User Authentication)

#### MODIFIED

- **FR-003** (Functional Requirements)
  - Was: System MUST lock an account after 5 failed sign-in attempts.
  - Now: System MUST lock an account after 3 failed sign-in attempts within 10 minutes.
  - Why: Brute-force protection for the new public API.

#### ADDED

- (Edge Cases) What happens when an administrator unlocks an account that is not locked?

### RETIRE specs/living/security-questions (Security Questions)

- Why: Account recovery no longer uses security questions.
```

- **CREATE** names a new living spec. With one `CREATE`, it receives all of the feature's own
  stories, requirements, success criteria, edge cases, entities and assumptions, renumbered in
  its own ID space. With several, each lists its share in an `Items:` line
  (`Items: US1, FR-001–FR-004, SC-001`). A feature that only changes existing behavior creates
  nothing.
- **UPDATE** holds deltas. Sync first checks that every `Was` still matches its target and stops
  on any mismatch without changing anything; then it applies them (added items get the next free
  ID; removed IDs are never reused) and appends the feature to the target's `**History**` line.
- **RETIRE** moves `specs/living/<name>/` to `specs/retired/<name>/` and marks it `Retired`.

Because the section sits in the feature's `spec.md`, plan, tasks, analyze and implement all see
it. It stays in the feature directory after sync as a record of what the feature changed.

### Naming living specs

Names are chosen **when the feature is specified**, not when it is synced: the name is a scope
decision (which spec owns which behavior), so it is reviewed with the spec, and plan, tasks and
analyze can refer to it. It may change until sync. Names are lowercase kebab-case and name the
capability, not the change (`task-priority`, not `add-priority-to-tasks`), and are never reused,
including names in `specs/retired/`. Sync never invents a name, except for a feature written
before the extension was installed (see below).

## Living specs and history

Agents should read **living specs for what the product does** and **feature directories for why**.
The preset tells every core command so, and three things help agents that land elsewhere:

- `specs/living/README.md`, the index agents start from;
- a banner sync adds to each synced feature's `spec.md`, pointing to the living specs it
  produced;
- each living spec's `**History**` line, listing the feature directories that created and changed
  it, oldest first: the place to look for rationale (their `research.md`, `plan.md`,
  `data-model.md`, `contracts/`).

For agent sessions that don't go through Spec Kit commands, add this to your `AGENTS.md` or
`CLAUDE.md`:

```markdown
Current behavior is specified in `specs/living/` (start at `specs/living/README.md`). Feature
directories (`specs/NNN-*`) and `specs/retired/` are history: read them only to learn why
something changed, never as a statement of current behavior.
```

## When to run them

Install the [`living` preset](../../presets/living/) too (`specify preset add living`), so
`/speckit.specify` writes the section in the same step as the spec, already knowing which
behavior the living specs own, `/speckit.clarify` keeps it current, and plan, tasks, analyze and
implement cover it (without it, tasks may generate nothing for the deltas).

`speckit.living.delta` refreshes the section after the spec changes, such as hand edits. The
extension registers it as an optional `after_clarify` hook, so the agent offers it after
`/speckit.clarify`. Without the preset, run it after `/speckit.specify`, before planning.

We recommend running `speckit.living.sync` as the last commit of a feature's PR, after reviews,
so reviewers see the living specs change together with the code.

## Adopting it in an existing project

Run `speckit.living.sync` on each delivered feature, oldest first. A feature written before the
extension was installed has no `## Changes to Living Specs` section, so sync:

- when no living spec exists yet, creates one from all of the feature's own items, named after
  the feature directory without its number (`specs/002-list-tasks` → `list-tasks`); it asks you to
  confirm the name, or, unattended, says it chose it;
- otherwise first compares the feature with the living specs, and stops if the feature changed
  behavior one of them states. Run `speckit.living.delta` on the feature (which names what it
  creates and records the deltas), commit, and sync again.

### From version 0.2

Version 0.2 kept living specs inside feature directories (`specs/NNN-*/spec.md` with
`**Status**: Living`) and deleted derived artifacts. To move to `specs/living/`, sync each
`Living` feature, oldest first. Their text is already current, so each becomes a living spec
named after its directory, and its `**Last changed by**` line moves into `**History**`. Rename a
living spec by moving its directory and fixing the index if the generated name doesn't fit.
Artifacts 0.2 deleted stay in git history.

## Assumptions about Spec Kit

Checked against Spec Kit 1.3.3. If a later release changes any of these, `specs/living/` and
`specs/retired/` could be mistaken for features:

- **Feature numbering** only counts directories in `specs/` whose names start with a number:
  `create-new-feature.sh` matches `^[0-9]{3,}-` (and skips timestamp prefixes
  `YYYYMMDD-HHMMSS-`), and `/speckit.specify` takes "the next available 3-digit number after
  scanning existing directories in `specs/`". `living` and `retired` match neither.
- **Feature resolution** never scans `specs/`: scripts use `SPECIFY_FEATURE_DIRECTORY`,
  `.specify/feature.json` or the branch name, so a non-numbered directory is never picked as the
  current feature.
- **Core commands read only the current feature's directory** (`spec.md`, `plan.md`,
  `tasks.md`, …), so they don't load living specs or history unless the preset tells them to.
- **The `agent-context` extension** looks for the most recently modified `specs/**/plan.md`.
  Living and retired specs have no `plan.md`.
- **Presets and extensions** can wrap core commands (`{CORE_TEMPLATE}`), append to
  `spec-template`, use `__SPECKIT_COMMAND_<NAME>__` placeholders, and register hooks in
  `.specify/extensions.yml`, which sync reads for its `before_living_sync` and
  `after_living_sync` events.

The `specs/living/` path is fixed.

## Hooks

Other extensions can run around sync with the `before_living_sync` and `after_living_sync` hook
events.
