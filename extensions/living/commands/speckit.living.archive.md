---
description: "Archive a delivered feature's derived artifacts (plan.md, tasks.md, checklists/) after moving their durable rationale into research.md, and mark its spec Living"
---

# Archive Derived Artifacts

This command supports **spec-anchored living specs**: `spec.md` is the contract for a feature's
current behavior, and `plan.md`, `tasks.md` and `checklists/` are derivations that describe how it
was built. Once the feature is delivered they go stale and mislead later readers, so this command
removes them, after keeping whatever is worth keeping.

Run it as the **last commit of a feature's PR**, after reviews and once implementation is complete
(`__SPECKIT_COMMAND_IMPLEMENT__` finished, and any verification command you use reports no
remaining work). Git history keeps every archived file.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

Accepted input:

- A feature directory (`specs/002-config-cleanup`), its name, or its number (`002`).
- `--keep <list>`: comma-separated artifacts to keep even though they are archivable
  (`plan`, `tasks`, `checklists`).
- `--also <list>`: comma-separated artifacts kept by default that should also be archived
  (`quickstart`, `contracts`, `data-model`). Use only when they hold nothing durable.
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
- At least one archivable artifact (`plan.md`, `tasks.md`, `checklists/`) exists. If none does,
  report that the feature is already archived and only check the spec header (step 6).
- The files under `FEATURE_DIR` have no uncommitted changes (`git status --porcelain -- FEATURE_DIR`).
  If they do, stop and ask the user to commit or discard them first, so the deletion is a clean,
  reviewable diff.

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

Read `plan.md`, `tasks.md` and `checklists/`, and pick out content that is still true and that a
future change would need, and that is not already in `spec.md`, `research.md`, `data-model.md`,
`contracts/` or the code's own docs (README, package docs):

- **Complexity Tracking** entries from `plan.md`: every justified constitution deviation that is
  still in the code. These MUST be kept, so the justification stays on record.
- Architectural or technology decisions and their reasons (Technical Context, Summary, structure
  decisions) not already in `research.md`.
- Known limitations or deferred follow-ups that are still open and tracked nowhere else.

Do **not** keep: task lists, progress, phase plans, dates of work, waivers, checklist scaffolding,
anything superseded by later changes, or anything the code or its README already says.

Content that describes *intended behavior* (a requirement, an edge case, an assumption about
behavior) belongs in `spec.md`, not `research.md`; if you find any that `spec.md` lacks, that is
spec drift: stop, show it to the user, and recommend correcting `spec.md` first.

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

### 4. Check references to the files being archived

Search the whole repository (excluding `node_modules/`, `.git/` and `FEATURE_DIR` itself) for links
or mentions of each file to be deleted, e.g. `<feature-name>/plan.md`, `<feature-name>/tasks.md`,
`<feature-name>/checklists/`. For each hit, either rewrite it to point at `spec.md` / `research.md`
or drop the mention. Report every edit. Do the same for any `--also` artifacts.

### 5. Delete the archived artifacts

Unless `--dry-run`, delete (with `git rm`) the artifacts being archived. By default:

| Artifact | Default | Why |
|---|---|---|
| `plan.md` | archive | derived build plan |
| `tasks.md` | archive | derived task list |
| `checklists/` | archive | derived validation scaffolding |
| `spec.md` | **keep** | the living contract |
| `research.md` | **keep** | durable rationale |
| `data-model.md` | keep | may be archived with `--also` |
| `contracts/` | keep | often linked from docs; may be archived with `--also` |
| `quickstart.md` | keep | verification steps; may be archived with `--also` |

Apply `--keep` and `--also`. Never delete `spec.md` or `research.md`.

### 6. Update the spec header

In `FEATURE_DIR/spec.md`:

- Set `**Status**: Living` (unless it already is).
- Set `**Last Updated**` to today's date, adding the line after `**Status**` if missing.
- Add or update, right after `**Last Updated**`:

  ```markdown
  **Archived artifacts**: plan.md, tasks.md, checklists/ (recover with
  `git log --diff-filter=D --name-only -- <FEATURE_DIR>`)
  ```

  listing the artifacts actually archived. Change nothing else in `spec.md`.

### 7. Do not commit

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
- References rewritten in other files.
- A **PR notes** block, ready to paste into the PR description:

  ```markdown
  ### Archived derived artifacts (<feature>)
  - Archived: plan.md, tasks.md, checklists/
  - Rationale kept in research.md: <one line, or "none needed">
  - Waived tasks: <ID — summary — waived by/why — what stays unverified>, or "none"
  ```

  The waived tasks live **only** here; tell the user they will not be recorded anywhere in the
  repository.
- A suggested commit message, e.g. `Archive derived artifacts of <feature>`.

## Guardrails

- Never delete `spec.md` or `research.md`, and never edit `spec.md` beyond its header lines.
- Never record waived tasks or unchecked checklist items in a file that persists after the work.
- Never touch files outside `PROJECT_ROOT`, except rewriting references found in step 4.
- Never run on a feature with unwaived open tasks.
- Never commit, push or rewrite history.
