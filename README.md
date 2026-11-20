# speckit-extensions

Spec Kit add-ons, published as installable catalogs:

| Kind | Source | Catalog |
| --- | --- | --- |
| Extensions (commands, hooks, templates) | [`extensions/`](extensions/) | [`extensions/catalog.json`](extensions/catalog.json) |
| Presets (changes to core commands and templates) | [`presets/`](presets/) | [`presets/catalog.json`](presets/catalog.json) |
| Workflows | [`workflows/`](workflows/) | [`workflows/catalog.json`](workflows/catalog.json) |
| Workflow step types | [`steps/`](steps/) | [`steps/catalog.json`](steps/catalog.json) |

Built and checked against [Spec Kit](https://github.com/github/spec-kit) 1.3.3.

These items are **not** submitted to Spec Kit's official community catalogs, so they
won't appear in `specify ... search` by default. To use them, add this repository's
catalogs or install an item directly from its URL, as described below.

## Using these catalogs

Run these inside a Spec Kit project (`specify init` first):

```bash
specify extension catalog add https://raw.githubusercontent.com/luizffgv/speckit-extensions/main/extensions/catalog.json --name luizffgv --install-allowed
```

```bash
specify preset catalog add https://raw.githubusercontent.com/luizffgv/speckit-extensions/main/presets/catalog.json --name luizffgv --install-allowed
```

```bash
specify workflow catalog add https://raw.githubusercontent.com/luizffgv/speckit-extensions/main/workflows/catalog.json --name luizffgv
```

```bash
specify workflow step catalog add https://raw.githubusercontent.com/luizffgv/speckit-extensions/main/steps/catalog.json --name luizffgv
```

Then install by id:

```bash
specify extension add <id>
```

```bash
specify preset add <id>
```

```bash
specify workflow step add <id>
```

```bash
specify workflow add <id>
```

Install a workflow's extensions, presets and custom step types before the workflow; its README
lists them.

> **Note:** a project catalog file (`.specify/*-catalogs.yml`) replaces Spec Kit's
> built-in catalog list. If you still want the official catalogs, add them back too,
> for example `https://raw.githubusercontent.com/github/spec-kit/main/extensions/catalog.json`
> (or `presets/catalog.json` for the official presets).

To try one item without adding a catalog:

```bash
specify workflow add https://raw.githubusercontent.com/luizffgv/speckit-extensions/main/workflows/<id>/workflow.yml
```

## Authoring

Requires [uv](https://docs.astral.sh/uv/). All tooling is in [`scripts/repo.py`](scripts/repo.py).

```bash
uv run scripts/repo.py new extension my-ext
```

```bash
uv run scripts/repo.py new preset my-preset
```

```bash
uv run scripts/repo.py new workflow my-flow
```

```bash
uv run scripts/repo.py new step my-step
```

With [Claude Code](https://claude.com/claude-code) in this repo, you can also just
ask for what you want: the project skills in [`.claude/skills/`](.claude/skills/)
(`speckit-new-extension`, `speckit-new-preset`, `speckit-new-workflow`, `speckit-new-step`,
`speckit-release-item`) walk through scaffolding, writing, validating and versioning.

The `new` command copies [`templates/`](templates/) into `extensions/<id>/`, `presets/<id>/`,
`workflows/<id>/` or `steps/<id>/`. Ids are lowercase kebab-case and must match the directory name.

Each item's layout:

- **Extension**: `extension.yml`, `commands/speckit.<id>.<name>.md`, optional
  `templates/`, `scripts/`, config templates. Commands must be named `speckit.<id>.*`.
- **Preset**: `preset.yml` and the files it provides (`commands/`, `templates/`, `scripts/`).
  Prefer `wrap`, `prepend` or `append` over `replace` for core commands, so Spec Kit upgrades
  still apply. An extension and a preset may share an id.
- **Workflow**: `workflow.yml`. It can use built-in step types (`command`, `gate`,
  `shell`, `if`, `fan-out`, ...) and any step type from `steps/`. Only
  `workflow.yml`, `README.md` and `CHANGELOG.md` are allowed, because catalog
  installs fetch `workflow.yml` alone; put scripts in an extension or step type.
- **Step type**: `step.yml` (`step.type_key` = id) and `__init__.py` with a `StepBase`
  subclass whose `type_key` matches. Other files (helper modules, data) ship as extra
  files; `README.md` and `CHANGELOG.md` don't ship.

All of them also need a `README.md`; keep a `CHANGELOG.md` too.

### Checking your work

```bash
uv run scripts/repo.py validate
```

This runs Spec Kit's own manifest, workflow and step-package validators, and checks that preset
`wrap` files contain their placeholder. Workflows
are checked with this repo's step types loaded. It also fails if an item has
changed since its released version was tagged.

To try an item in a real project:

```bash
specify extension add --dev /path/to/speckit-extensions/extensions/<id>
```

```bash
specify preset add --dev /path/to/speckit-extensions/presets/<id>
```

```bash
specify workflow step add <id> --dev /path/to/speckit-extensions/steps/<id>
```

```bash
specify workflow add --dev /path/to/speckit-extensions/workflows/<id>
```

```bash
specify workflow run /path/to/speckit-extensions/workflows/<id>/workflow.yml
```

## Releasing

Versions are released by merging to `main`; there is no manual tagging.

1. Bump `version` in the item's manifest and add a `CHANGELOG.md` entry.
2. Run `uv run scripts/repo.py catalog` and commit the updated `catalog.json`.
3. Merge to `main`. CI validates, then `repo.py release` creates a GitHub release
   tagged `<kind>-<id>-v<version>` (for example `extension-my-ext-v1.2.0`) for every
   version without a tag. Extension and preset releases include the `<id>-<version>.zip` asset.

Catalog entries point at those tags, so an installed version never changes after
release. Checksums are computed from the source. Extension and preset zips are built
reproducibly, so `catalog.json` can be generated before the release exists.
CI fails if a catalog is stale or a released item changed without a version bump.

To validate against a newer Spec Kit, bump the `specify-cli` tag in
[`pyproject.toml`](pyproject.toml). Repository-wide settings (GitHub slug, default
author, license, minimum Spec Kit version) are in [`repo.toml`](repo.toml).

## License

[Unlicense](LICENSE).
