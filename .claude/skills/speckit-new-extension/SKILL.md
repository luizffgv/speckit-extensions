---
name: speckit-new-extension
description: Create or edit a Spec Kit extension (commands, hooks, scripts).
when_to_use: When asked to add a Spec Kit extension, add or change an extension's commands or hooks, or turn a prompt or skill into a Spec Kit command.
---

# Create a Spec Kit extension

An extension adds agent commands (`speckit.<ext-id>.<name>`), and optionally hooks
around core commands, helper scripts, templates and config files. It is installed
with `specify extension add <id>` from this repo's `extensions/catalog.json`.

## Workflow

1. **Pin down the design** with the user if unclear: the id (lowercase kebab-case,
   e.g. `living-specs`), which commands it provides, and whether any should run
   automatically as hooks (`before_plan`, `after_tasks`, ...).
2. **Scaffold** from the repo root:
   ```bash
   uv run scripts/repo.py new extension <id> --name "<Name>" --description "<one line>"
   ```
   This creates `extensions/<id>/` with `extension.yml`, an example command,
   `README.md` and `CHANGELOG.md`. Rename or delete the example command.
3. **Write the commands** (see below). One file per command in `commands/`,
   named `speckit.<id>.<name>.md`, each listed under `provides.commands`.
4. **Fill in `extension.yml`**: description, `tags`, `requires.tools` for CLIs the
   commands need, `hooks` if any.
5. **Document**: in `README.md`, list every command and hook, any config, and
   required tools. Keep the `0.1.0` entry in `CHANGELOG.md` for a new extension.
6. **Validate and regenerate the catalog**:
   ```bash
   uv run scripts/repo.py validate extensions/<id>
   uv run scripts/repo.py catalog
   ```
7. **Try it in a throwaway project** when the commands are non-trivial. Use a
   scratch directory, never this repo:
   ```bash
   specify init <scratch>/proj --integration claude --ignore-agent-tools --script sh
   cd <scratch>/proj && specify extension add --dev <repo>/extensions/<id>
   ```
   The rendered commands appear under `.claude/skills/speckit-<id>-<name>/`.

For a version bump to an existing extension, use the `speckit-release-item` skill.

## Manifest cheat sheet (`extension.yml`)

```yaml
schema_version: "1.0"
extension:
  id: my-ext                 # ^[a-z0-9-]+$, equals the directory name
  name: "My Extension"
  version: "0.1.0"           # X.Y.Z (repo rule; Spec Kit itself accepts PEP 440)
  description: "One line"
  author: luizffgv
  repository: https://github.com/luizffgv/speckit-extensions
  license: Unlicense
requires:
  speckit_version: ">=1.3.0"
  tools:                     # optional
    - name: gh
      version: ">=2.0"       # optional
      required: false
provides:                    # at least one of commands/templates/scripts
  commands:
    - name: speckit.my-ext.do-thing    # ^speckit\.[a-z0-9-]+\.[a-z0-9-]+$, namespace = id
      file: commands/speckit.my-ext.do-thing.md
      description: "..."
  templates:                 # optional; name ^[a-z0-9-]+$; no `strategy` key
    - name: my-template
      file: templates/my-template.md
  scripts:                   # optional
    - name: collect
      file: scripts/collect.sh
      runtimes: [bash]       # informational only
  config:                    # optional; user copies template to <name>
    - name: my-ext-config.yml
      template: my-ext-config.template.yml
      description: "..."
      required: false
hooks:                       # optional; value is a mapping or a list of mappings
  after_tasks:
    command: speckit.my-ext.do-thing
    optional: true           # true: user is asked with `prompt`; false: runs automatically
    prompt: "Run do-thing?"
    description: "..."
tags: [my-ext]
```

Hook events: `before_`/`after_` + `specify`, `clarify`, `plan`, `tasks`,
`implement`, `analyze`, `checklist`, `constitution`. Extensions installed in the
project can add more (the bundled `bug` extension adds `before_bug_assess`, ...).
Hook `condition` is not evaluated by current command templates; hooks with a
non-empty condition are skipped, so don't rely on it.

## Command file format

~~~markdown
---
description: "Shown in the agent's command list"
scripts:                      # optional; then call it with {SCRIPT} in the body
  sh: scripts/collect.sh      # bare path = this extension's own scripts/
  ps: scripts/collect.ps1
---

# Do Thing

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. ...
~~~

- `$ARGUMENTS`: what the user typed after the command.
- `{SCRIPT}`: the resolved path of the `scripts` entry for the user's shell.
  A path with two or more `../` (e.g. `../../scripts/bash/x.sh`) points at the
  project's core scripts in `.specify/scripts/`.
- `__SPECKIT_COMMAND_<NAME>__`: reference to another command, rendered with each
  agent's syntax. Drop `speckit.`, uppercase, dots become `_`, hyphens stay:
  `speckit.plan` → `__SPECKIT_COMMAND_PLAN__`, `speckit.my-ext.do-thing` →
  `__SPECKIT_COMMAND_MY-EXT_DO-THING__`. Never hard-code `/speckit.plan`.
- Commands are prompts for the coding agent: write them as clear, ordered
  instructions; state prerequisites, files read and written, and what to report.
  Handle both interactive use and automated runs (workflows), where the agent
  can't ask questions: say what to do instead (stop with an error, pick a default).
- Per-project settings live in `.specify/extensions/<id>/`. Secrets come from
  env vars, never committed config.

## Rules this repo enforces

- Directory name = `extension.id`; `README.md` required; versions `X.Y.Z`.
- Every file named in `provides` must exist.
- A released version (tag `extension-<id>-v<version>`) is immutable: any change
  needs a version bump.
- Everything tracked in `extensions/<id>/` ships in the release zip.

## Deeper reference

Spec Kit docs at the tag pinned in `pyproject.toml` (currently v1.3.3):
`gh api "repos/github/spec-kit/contents/docs/extensions/developing.md?ref=v1.3.3" --jq .content | base64 -d`
(also `docs/extensions/api.md`). The bundled extensions are good examples:
`.venv/lib/python3*/site-packages/specify_cli/core_pack/extensions/` (run `uv sync` first).
