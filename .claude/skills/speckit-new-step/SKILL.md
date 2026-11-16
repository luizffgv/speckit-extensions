---
name: speckit-new-step
description: Create or edit a custom workflow step type (Python).
when_to_use: When asked for a new workflow step type, when a workflow needs behaviour no built-in step (command, prompt, shell, gate, if, switch, loops, fan-out) provides, or to change a step type's config or outputs.
---

# Create a Spec Kit workflow step type

A step type is a small Python package. Workflows use it as `type: <type_key>`.
It is installed with `specify workflow step add <type_key>` from this repo's
`steps/catalog.json`, and loaded into the `specify` process with the user's
privileges.

First check that no built-in type does the job: `shell` with `strict: true` and
`output_format: json` covers most "run a program, read its result" needs. Make a
step type when you need typed config validation, structured outputs, or logic
that is awkward and unsafe in shell.

## Workflow

1. **Pin down the contract** with the user if unclear: the `type_key` (lowercase
   kebab-case, not a built-in name), the YAML config keys and their types, the
   output fields later steps read (`steps.<id>.output.*`), and when it fails.
2. **Scaffold** from the repo root:
   ```bash
   uv run scripts/repo.py new step <type_key> --name "<Name>" --description "<one line>"
   ```
   This creates `steps/<type_key>/` with `step.yml`, `__init__.py` (an example
   that renders a `message`), `README.md` and `CHANGELOG.md`.
3. **Implement `__init__.py`** (contract below). Helper modules and data files in
   the same directory ship too and can be imported relatively (`from .x import y`).
4. **Document** in `README.md`: a usage snippet, a table of config keys, the
   outputs, failure cases and side effects.
5. **Validate and regenerate the catalog**:
   ```bash
   uv run scripts/repo.py validate steps/<type_key>
   uv run scripts/repo.py catalog
   ```
   This runs Spec Kit's package validator and imports the module to check that the
   class exists.
6. **Exercise it** in a throwaway project with a small workflow that covers valid
   config, invalid config and each output:
   ```bash
   specify init <scratch>/proj --integration claude --ignore-agent-tools --script sh
   cd <scratch>/proj
   specify workflow step add <type_key> --dev <repo>/steps/<type_key>   # --force after edits
   specify workflow run ./test.yml
   ```

For a version bump to an existing step type, use the `speckit-release-item` skill.

## Package contract

`step.yml`:

```yaml
step:
  type_key: my-step        # equals the directory name
  name: "My Step"
  version: "0.1.0"         # X.Y.Z; the catalog version must match
  author: "luizffgv"
  description: "One line"
```

`__init__.py`:

```python
from __future__ import annotations
from typing import Any
from specify_cli.workflows.base import StepBase, StepContext, StepResult, StepStatus
from specify_cli.workflows.expressions import evaluate_expression


class MyStep(StepBase):
    type_key = "my-step"   # must equal step.yml type_key

    def validate(self, config: dict[str, Any]) -> list[str]:
        errors = super().validate(config)          # keeps the 'id' check
        if not isinstance(config.get("name"), str):
            errors.append("'name' must be a string.")
        return errors

    def execute(self, config: dict[str, Any], context: StepContext) -> StepResult:
        errors = self.validate(config)             # engine does NOT call validate first
        if errors:
            return StepResult(status=StepStatus.FAILED, error="; ".join(errors))
        name = config["name"]
        if "{{" in name:                           # config values arrive unevaluated
            name = evaluate_expression(name, context)
        return StepResult(output={"greeting": f"Hello, {name}!"})
```

- **Stateless:** one instance serves concurrent fan-out iterations. Never store
  per-run data on `self`.
- **Expressions:** evaluate `{{ }}` in config values yourself with
  `evaluate_expression(value, context)`.
- **Context:** `context.inputs`, `context.steps[<id>]["output"]`, `context.item`
  (in fan-out), `context.project_root`, `context.workflow_dir`, `context.run_id`,
  `context.is_resume`. Paths are `str`.
- **Results:** return `COMPLETED` (default), `FAILED` with `error=...` for
  expected failures (this lets `continue_on_error` apply), `SKIPPED`, or `PAUSED`
  to stop for `specify workflow resume`. An uncaught exception aborts the whole
  run, so catch expected errors and return `FAILED`.
- **Outputs** must be JSON-serializable; they are persisted for resume.
- **Side effects** can repeat after an interrupted run, so make them idempotent.
- `next_steps=[{...}]` expands nested step definitions (control-flow types).
- Only `specify_cli` and the standard library are available. Third-party
  packages can't be declared.

## Rules this repo enforces

- Directory name = `type_key`; it must not collide with a built-in type.
- `README.md` required; versions `X.Y.Z`.
- Every file except `README.md` and `CHANGELOG.md` ships as part of the package
  (listed in the catalog as `extra_files`, with checksums). Limits: 512 files,
  50 MiB, no symlinks.
- A released version (tag `step-<type_key>-v<version>`) is immutable.

## Deeper reference

Spec Kit docs at the tag pinned in `pyproject.toml` (currently v1.3.3):
`gh api "repos/github/spec-kit/contents/docs/workflow-steps/api.md?ref=v1.3.3" --jq .content | base64 -d`
(also `developing.md`). The built-in step types are good examples, one package
each: `.venv/lib/python3*/site-packages/specify_cli/workflows/step/<type>/__init__.py`
(e.g. `gate`, `shell`, `if_then`; run `uv sync` first).
