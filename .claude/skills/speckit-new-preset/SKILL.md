---
name: speckit-new-preset
description: Create or edit a Spec Kit preset (changes to core commands and templates).
when_to_use: When asked to change what a core Spec Kit command (speckit.specify, plan, tasks, ...) or core template (spec-template, plan-template, ...) does, to add a section to a core template, or to add or change a preset.
---

# Create a Spec Kit preset

A preset changes core commands, templates or scripts in a project, by replacing them or by
composing with them. It is installed with `specify preset add <id>` from this repo's
`presets/catalog.json`. To add **new** commands, write an extension instead
(`speckit-new-extension` skill); a preset is for changing existing ones.

## Workflow

1. **Pin down the design** with the user if unclear: which core artifacts change, and how. Prefer
   composing over replacing (see strategies below).
2. **Scaffold** from the repo root:
   ```bash
   uv run scripts/repo.py new preset <id> --name "<Name>" --description "<one line>"
   ```
   This creates `presets/<id>/` with `preset.yml`, an example `wrap` of `speckit.specify`,
   `README.md` and `CHANGELOG.md`. Replace or delete the example.
3. **Write the contributions** and list each under `provides.templates`.
4. **Document** in `README.md`: a table of every artifact changed (type, strategy, what changes)
   and any extensions it depends on.
5. **Validate and regenerate the catalog**:
   ```bash
   uv run scripts/repo.py validate presets/<id>
   uv run scripts/repo.py catalog
   ```
6. **Check the composed result** in a throwaway project (never this repo):
   ```bash
   specify init <scratch>/proj --integration claude --ignore-agent-tools --script sh
   cd <scratch>/proj && specify preset add --dev <repo>/presets/<id>
   specify preset resolve spec-template          # shows the composition stack
   ```
   Read the rendered command, e.g. `.claude/skills/speckit-specify/SKILL.md`, and the composed
   template (`bash .specify/scripts/bash/resolve-template.sh spec-template --json`). Reinstall
   with `specify preset remove <id>` then `add` after edits.

For a version bump to an existing preset, use the `speckit-release-item` skill.

## Manifest cheat sheet (`preset.yml`)

```yaml
schema_version: "1.0"
preset:
  id: "my-preset"            # [a-z0-9-]+, equals the directory name
  name: "My Preset"
  version: "0.1.0"           # X.Y.Z, quoted
  description: "One line"
  author: "luizffgv"
  repository: "https://github.com/luizffgv/speckit-extensions"
  license: "Unlicense"
requires:
  speckit_version: ">=1.3.0"
  extensions: ["some-ext"]   # optional; advisory: warned about after install, never installed
provides:
  templates:                 # non-empty; commands and scripts are listed here too
    - type: "command"        # command | template | script
      name: "speckit.specify"  # logical name: speckit.<cmd>, spec-template, plan-template, ...
      file: "commands/speckit.specify.md"
      description: "..."
      strategy: "wrap"       # replace (default) | prepend | append | wrap
tags: ["my-preset"]
```

## Strategies

| Strategy | Effect | Use for |
| --- | --- | --- |
| `replace` | This file wins entirely | Rarely: you then own every future core change |
| `prepend` / `append` | Added before/after the lower layer, blank line between | Extra template sections, extra guidance |
| `wrap` | Lower layer inserted at `{CORE_TEMPLATE}` (`$CORE_SCRIPT` for scripts) | Instructions around a core command |

- Scripts support only `replace` and `wrap`.
- Composition applies over the nearest `replace` layer below, so wraps from several presets stack.
- A composed command uses the highest-priority frontmatter it finds and inherits `scripts`,
  `agent_scripts` and `argument-hint` from the base. A wrapper with **no frontmatter** keeps the
  core command's frontmatter unchanged, which is usually what you want.
- Wrapper text placed before `{CORE_TEMPLATE}` is read first: state there what the additions are
  and that they win where they conflict with the core instructions. Refer to core steps by name
  or number only loosely; they change between Spec Kit versions.
- Commands from extensions can be referenced as `__SPECKIT_COMMAND_<EXT>_<NAME>__`.

## Rules this repo enforces

- Directory name = `preset.id`; `README.md` required; versions `X.Y.Z`.
- Must pass Spec Kit's `PresetManifest` validation; every `file` must exist; `wrap` files must
  contain their placeholder; scripts can't `prepend`/`append`.
- Everything tracked in `presets/<id>/` ships in the release zip.
- A released version (tag `preset-<id>-v<version>`) is immutable.
- A preset may share its id with an extension; `repo.py package` then needs `presets/<id>`.

## Deeper reference

Spec Kit docs at the tag pinned in `pyproject.toml` (currently v1.3.3):
`gh api "repos/github/spec-kit/contents/docs/presets/api.md?ref=v1.3.3" --jq .content | base64 -d`
(also `developing.md`, `catalogs.md`). Bundled examples:
`.venv/lib/python3*/site-packages/specify_cli/core_pack/presets/` (`constitution-sync` wraps a
command; `lean` replaces several). Core commands and templates to compose with:
`.venv/lib/python3*/site-packages/specify_cli/core_pack/{commands,templates}/`.
