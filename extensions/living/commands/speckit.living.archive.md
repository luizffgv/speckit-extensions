---
description: "Archive a delivered feature's derived artifacts (plan.md, tasks.md, checklists/, data-model.md, contracts/, quickstart.md) after moving their durable rationale into research.md, merge its deltas into other living specs, and mark its spec Living"
---

# Archive Derived Artifacts

This command supports **spec-anchored living specs**: `spec.md` is the contract for a feature's
current behavior, and `plan.md`, `tasks.md`, `checklists/`, `data-model.md`, `contracts/` and
`quickstart.md` are derivations that describe how it was built. Later features update only
`spec.md` (through deltas), never these. Once the feature is delivered they go stale and mislead later readers, so this command
removes them, after keeping whatever is worth keeping. If the feature changed other living specs,
its `spec.md` records those changes as deltas (`__SPECKIT_COMMAND_LIVING_DELTA__`), and this
command merges them into those specs.

It requires the implementation to be complete: step 1 stops unless every task is done or
waived. We recommend running it as the **last commit of a feature's PR**, after reviews, so the
PR still shows the plan and tasks while it is reviewed. Git history keeps every archived file.

It works on features created before this extension was installed: it needs only the core
artifacts, and a spec without a `## Changes to Living Specs` section simply has no deltas to
merge.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

Accepted input:

- A feature directory (`specs/002-config-cleanup`), its name, or its number (`002`).
- `--keep <list>`: comma-separated artifacts to keep even though they are archivable
  (`plan`, `tasks`, `checklists`, `data-model`, `contracts`, `quickstart`).
- `--dry-run`: report what would happen, change nothing.
- **Nothing**: fall back to context (see below).

## Resolve the Project and Feature

1. **Project root** (`PROJECT_ROOT`): the nearest ancestor of the current working directory that
   contains `.specify/`. In a repository with nested Spec Kit projects (for example one per module),
   that is the nested project's directory. All paths below are relative to `PROJECT_ROOT`.
2. **Feature directory** (`FEATURE_DIR`), first match wins:
   1. Explicit user input.
   2. The feature the conversation just worked on.
   3. `.specify/feature.json` → `feature_directory`, if that directory exists.
   4. Otherwise list `specs/*/` with each `spec.md`'s `**Status**` and ask which one. In a
      non-interactive run (no one to ask), stop and report the candidates instead.
3. State which resolution path was used.

## Pre-Execution Checks

**Check for extension hooks (before archiving)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_living_archive` key.
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue normally.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- Do not interpret hook `condition` expressions: a hook with no or an empty `condition` is executable; a hook with a non-empty `condition` is skipped and left to the HookExecutor.
- For each executable hook:  
  - **Optional** (`optional: true`): output
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **Mandatory** (`optional: false`): output
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    then actually invoke the hook the way you would run the command yourself in this session, and wait for it to finish before continuing.
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently.

**Preconditions** (stop and explain if any fails):

- `FEATURE_DIR/spec.md` exists. If its `**Status**` is `Retired` (the feature itself was removed
  from the product), stop: there is nothing to archive.
- At least one archivable artifact (`plan.md`, `tasks.md`, `checklists/`, `data-model.md`,
  `contracts/`, `quickstart.md`) exists. If none does, the feature is already archived (or never
  had them): skip steps 1–3, 5 and 6, but still merge any deltas (step 4) and update the header
  (step 7).
- The files under `FEATURE_DIR` have no uncommitted changes (`git status --porcelain -- FEATURE_DIR`).
  If they do, stop and ask the user to commit or discard them first, so the deletion is a clean,
  reviewable diff.
- If `FEATURE_DIR/spec.md` has a `## Changes to Living Specs` section with deltas, every target it
  names exists, has `**Status**: Living`, and has no uncommitted changes. If not, stop and explain.
  A target delivered before this extension was installed is not `Living` yet: recommend archiving
  it first (`__SPECKIT_COMMAND_LIVING_ARCHIVE__ <target>`), which marks it `Living`.
- If `FEATURE_DIR/spec.md` has **no** `## Changes to Living Specs` section (for example, it was
  written before this extension was installed) and other specs are `Living`, the feature may have
  changed their behavior without recording it. Compare this feature's spec (and, if they are
  quick to check, its tasks and the code it changed) with the `Living` specs. If anything this
  feature specifies or changed contradicts or changes what a `Living` spec states, stop: name the
  spec and the statement, and recommend `__SPECKIT_COMMAND_LIVING_DELTA__` first. Archiving now
  would leave that spec stale. If you find nothing, ask the user to confirm the feature changed no
  other living spec (in a non-interactive run, continue and say in the Completion Report that you
  checked and found none).

## Execution

### 1. Check the work is done

Read `tasks.md` and list every unchecked task (`- [ ]`).

- A task is **waived** if its own text says so (e.g. `**Waived by the owner** …`) or the user
  confirms it is waived when asked. In a non-interactive run, only the first counts.
- If any unchecked task is not waived, **stop**: the feature is not delivered. Suggest
  `__SPECKIT_COMMAND_IMPLEMENT__`.
- Waived tasks are **never written into `spec.md`, `research.md` or any other file that persists
  after the work**. Collect them (ID, one-line summary, who waived it and why, any requirement or
  success criterion left unverified) for the PR notes in the Completion Report only.

Also scan `checklists/*.md` for unchecked items. Treat them like tasks: list them, and stop unless
the user confirms each is resolved or waived (waivers again go only to the PR notes).

### 2. Collect durable rationale

Read every artifact being archived, and pick out content that is still true and that a future
change would need, and that is not already in `spec.md`, `research.md` or the code and its own docs
(README, package docs, schemas, API docs):

- **Complexity Tracking** entries from `plan.md`: every justified constitution deviation that is
  still in the code. These MUST be kept, so the justification stays on record.
- Architectural or technology decisions and their reasons (Technical Context, Summary, structure
  decisions) not already in `research.md`.
- From `data-model.md` and `contracts/`: the reasons behind data and interface choices and any
  compatibility constraints still in force (e.g. how stored data from older versions is read),
  not the shapes or signatures themselves, which the code shows.
- Known limitations or deferred follow-ups that are still open and tracked nowhere else.

Do **not** keep: task lists, progress, phase plans, dates of work, waivers, checklist scaffolding,
copies of schemas, interfaces or setup steps, anything superseded by later changes, or anything the code or its README already says.

Content that describes *intended behavior* (a requirement, an edge case, an assumption about
behavior) belongs in `spec.md` (or, for behavior another living spec owns, in a delta), not
`research.md`; if you find any that neither `spec.md` nor its deltas cover, that is spec drift:
stop, show it to the user, and recommend correcting `spec.md` first (for changes to other living
specs, with `__SPECKIT_COMMAND_LIVING_DELTA__`).

The same holds for behavior a delta target owns that this feature's `spec.md` states only in its
own sections (often Assumptions or Edge Cases) and not in that target's delta: accepted values,
defaults, validation rules and their order, user-visible messages. Once the deltas are merged, the
target would not state its own behavior. Treat it as spec drift too: stop and recommend moving it
into the delta. (Interface syntax and data shapes need no delta: once `contracts/` and
`data-model.md` are archived, the code is their reference. Incidental text the target never
specified, such as usage text, needs no delta either.)

### 3. Write the rationale into `research.md`

- If there is anything to keep, append to `FEATURE_DIR/research.md` (create it with a
  `# Research: <feature name>` title if missing) a section:

  ```markdown
  ## Retained from archived plan

  ### Complexity Tracking
  | Deviation | Why needed | Simpler alternative rejected because |
  |---|---|---|
  | … | … | … |

  ### Decisions
  - **<decision>**: <reason>.
  ```

  Omit empty subsections. Write it as present-tense fact, not as a history of the work.
- If nothing qualifies, write nothing and say so.

### 4. Merge deltas into the living specs

Skip this step if `FEATURE_DIR/spec.md` has no `## Changes to Living Specs` section. If the section
says `None: …`, only remove it (last bullet below).

**Check every delta first, change nothing until all pass.** For each target subsection:

- Every `MODIFIED` and `REMOVED` item exists in the target's `spec.md` and its current text matches
  `Was` (ignoring whitespace and line wrapping).
- Any `Why` marked `(unsure: …)` was resolved. In an interactive run, ask; in a non-interactive
  run, stop.

If any check fails, the target changed since the delta was written: stop, show each mismatch
(expected `Was` versus the current text), and recommend re-running
`__SPECKIT_COMMAND_LIVING_DELTA__`. Do not delete anything.

Then, unless `--dry-run`, apply each target's delta to its `spec.md`:

- **MODIFIED**: replace the item's text with `Now`, keeping its ID and position.
- **ADDED**: the section is named in parentheses before the text (`- (Functional Requirements)
  …`); also accept `- Functional Requirements: …`. Append the item to that section, giving it the
  next free ID of that kind
  (`FR-`, `SC-`, …) in the target; items without IDs (stories, edge cases, assumptions) go at the
  end of their section in the target's style. Never reuse a removed ID.
- **REMOVED**: delete the item. Do not renumber the remaining items.
- Update the target's header: `**Last Updated**` to today's date (add it after `**Status**` if
  missing), and add or update `**Last changed by**: <FEATURE_DIR>` after it.
- Change nothing else in the target.

Finally, remove the `## Changes to Living Specs` section from `FEATURE_DIR/spec.md`; step 7
records which specs were updated. Then find every mention of that section or its deltas in the
files kept in `FEATURE_DIR` (`spec.md`, `research.md`, and anything kept with `--keep`), e.g. with `grep -rniE 'delta|changes to living specs|Δ' FEATURE_DIR`, and rewrite
each to name the target spec instead ("specified in the deltas below" → "specified in
`specs/001-user-auth`"; "the 001 delta's edge case" → "the edge case in `specs/001-user-auth`").
Repeat the search until it finds none. Report every edit.

### 5. Check references to the files being archived

Search the whole repository (excluding `node_modules/`, `.git/` and `FEATURE_DIR` itself) for links
or mentions of each file to be deleted, e.g. `<feature-name>/plan.md`, `<feature-name>/tasks.md`,
`<feature-name>/checklists/`, `<feature-name>/contracts/`. For each hit, either rewrite it to point
at `spec.md` / `research.md` (or the code that now documents the interface) or drop the mention.
Report every edit.

### 6. Delete the archived artifacts

Unless `--dry-run`, delete (with `git rm`) the artifacts being archived. By default:

| Artifact | Default | Why |
|---|---|---|
| `plan.md` | archive | derived build plan |
| `tasks.md` | archive | derived task list |
| `checklists/` | archive | derived validation scaffolding |
| `data-model.md` | archive | derived design; the code is the reference |
| `contracts/` | archive | derived interface design; the code is the reference |
| `quickstart.md` | archive | derived verification steps |
| `spec.md` | **keep** | the living contract |
| `research.md` | **keep** | durable rationale |

Apply `--keep`. Never delete `spec.md` or `research.md`.

### 7. Update the spec header

In `FEATURE_DIR/spec.md`:

- Set `**Status**: Living` (unless it already is).
- Set `**Last Updated**` to today's date, adding the line after `**Status**` if missing.
- Add or update, right after `**Last Updated**`:

  ```markdown
  **Archived artifacts**: plan.md, tasks.md, checklists/, contracts/ (recover with
  `git log --diff-filter=D --name-only -- <FEATURE_DIR>`)
  ```

  listing the artifacts actually archived.
- If step 4 merged deltas, add or update, right after `**Archived artifacts**`:
  `**Updated living specs**: specs/001-user-auth, specs/004-billing` (the targets).

Change nothing else in `spec.md` (step 4 already removed its deltas section and rewrote mentions
of it).

### 8. Do not commit

Leave the changes staged or in the working tree for the user to review and commit as part of the
feature's PR.

## Post-Execution Checks

**Check for extension hooks (after archiving)**: same procedure as the pre-execution check, using
the `hooks.after_living_archive` key, with `**Automatic Hook**` / `**Optional Hook**` headings.

## Completion Report

Report:

- `PROJECT_ROOT`, `FEATURE_DIR` and how it was resolved.
- Artifacts archived and artifacts kept.
- What was moved into `research.md` (or "nothing").
- Living specs updated from deltas, with what changed in each (or "none").
- References rewritten in other files.
- A **PR notes** block, ready to paste into the PR description:

  ```markdown
  ### Archived derived artifacts (<feature>)
  - Archived: <artifacts archived>
  - Living specs updated: <target — one-line summary of its changes>, or "none"
  - Rationale kept in research.md: <one line, or "none needed">
  - Waived tasks: <ID — summary — waived by/why — what stays unverified>, or "none"
  ```

  The waived tasks live **only** here; tell the user they will not be recorded anywhere in the
  repository.
- A suggested commit message, e.g. `Archive derived artifacts of <feature>`.

## Guardrails

- Never delete `spec.md` or `research.md`, and never edit `spec.md` beyond its header lines,
  removing its merged deltas section and rewriting mentions of it.
- Never edit another living spec except to apply this feature's deltas (and its header lines), and
  never apply a delta whose `Was` text no longer matches.
- Never record waived tasks or unchecked checklist items in a file that persists after the work.
- Never touch files outside `PROJECT_ROOT`, except rewriting references found in step 5.
- Never run on a feature with unwaived open tasks.
- Never commit, push or rewrite history.
