---
name: speckit-new-workflow
description: Create or edit a Spec Kit workflow (workflow.yml).
when_to_use: When asked to add a Spec Kit workflow, automate a sequence of speckit commands, or change a workflow's steps, inputs or gates.
---

# Create a Spec Kit workflow

A workflow is a YAML definition run by `specify workflow run <id>`. It is
installed with `specify workflow add <id>` from this repo's `workflows/catalog.json`.

## Workflow

1. **Pin down the design** with the user if unclear: the id (lowercase
   kebab-case), the inputs, the steps in order, and where a human should approve
   (gates). If a step needs custom behaviour that no built-in type covers, make a
   step type first with the `speckit-new-step` skill. If it needs a new agent
   command, put that in an extension (`speckit-new-extension` skill).
2. **Scaffold** from the repo root:
   ```bash
   uv run scripts/repo.py new workflow <id> --name "<Name>" --description "<one line>"
   ```
   This creates `workflows/<id>/` with `workflow.yml` (specify → gate → plan
   example), `README.md` and `CHANGELOG.md`.
3. **Write `workflow.yml`** (cheat sheet below).
4. **Document** in `README.md`: what it does, every input, which extensions or
   step types it needs (install those first), and any side effects (shell
   commands, files written, network).
5. **Validate and regenerate the catalog**:
   ```bash
   uv run scripts/repo.py validate workflows/<id>
   uv run scripts/repo.py catalog
   ```
   Validation loads this repo's `steps/` so custom step types resolve.
6. **Run it in a throwaway project** (never this repo). `run` validates and then
   really executes; there is no dry run:
   ```bash
   specify init <scratch>/proj --integration claude --ignore-agent-tools --script sh
   cd <scratch>/proj && specify workflow run <repo>/workflows/<id>/workflow.yml -i spec="..."
   ```
   Install any custom step types it uses first:
   `specify workflow step add <step> --dev <repo>/steps/<step>`.

For a version bump to an existing workflow, use the `speckit-release-item` skill.

## Keep it to one file

The catalog installs a workflow from the raw `workflow.yml` URL, which does not
download neighbouring files. So `workflows/<id>/` must contain only
`workflow.yml`, `README.md` and `CHANGELOG.md`, and validation rejects anything
else. Put scripts in an extension, or logic in a custom step type.

## `workflow.yml` cheat sheet

```yaml
schema_version: "1.0"
workflow:
  id: "my-flow"              # equals the directory name
  name: "My Flow"
  version: "0.1.0"           # X.Y.Z
  author: "luizffgv"
  description: "One line"
  integration: "auto"        # optional default for command/prompt steps
requires:                    # only these two keys are allowed; advisory, not enforced
  speckit_version: ">=1.3.0"
  integrations: {any: [claude, copilot]}
inputs:
  spec:   {type: string, required: true, prompt: "Describe what to build"}
  scope:  {type: string, default: "full", enum: ["full", "backend-only"]}
  count:  {type: number, default: 3}
  dry:    {type: boolean, default: false}
steps:                       # non-empty; ids unique, no ':' in ids
  - id: specify              # type omitted = command
    command: speckit.specify
    input: {args: "{{ inputs.spec }}"}
  - id: review
    type: gate
    message: "Review the spec."       # trusted text only, never raw agent output
    options: [approve, reject]
    on_reject: abort                  # abort | skip | retry
```

### Step types

| `type` | Key fields |
| --- | --- |
| `command` (default) | `command`, `input.args`, `integration`, `model`, `capture`, `timeout` |
| `prompt` | `prompt`, `integration`, `capture` |
| `shell` | `run`, `strict: true`, `env: {NAME: "{{ expr }}"}`, `timeout` (300 s), `output_format: json` |
| `gate` | `message`, `options`, `on_reject`, `show_file` |
| `if` | `condition`, `then: [...]`, `else: [...]` |
| `switch` | `expression`, `cases: {value: [...]}`, `default: [...]` |
| `while` / `do-while` | `condition`, `max_iterations`, `steps: [...]` |
| `fan-out` | `items`, `max_concurrency`, `step: {...}` (uses `{{ item }}`) |
| `fan-in` | `wait_for: [fan-out-id]` → `steps.<id>.output.results` |
| `workflow` | `workflow: <installed id>`, `input: {...}`; child returns declared `outputs` |
| `init`, `slot`, `github` | see the docs |
| custom | any `type_key` from `steps/` |

Any step: `continue_on_error: true` records a failure and continues;
`steps.<id>.output.exit_code` stays readable.

Output of a `command`/`prompt` step streams to the terminal; set `capture: true`
to read it later as `steps.<id>.output.stdout`.

### Expressions

`{{ ... }}` with `inputs.x`, `steps.<id>.output.x`, `item`, `fan_in`,
`context.run_id`, `context.workflow_dir`. Operators: `== != > < >= <=`,
`and or not`, `in`, `not in`. Filters: `default`, `join`, `contains`, `map`,
`from_json`, `to_json`, `upper`, `lower`, `split`, `length`. Not Jinja and no
arithmetic. Put filtered values in parentheses before comparing:
`{{ (inputs.items | length) > 0 }}`. A lone `{{ expr }}` keeps its type; mixed
text becomes a string.

### Shell safety

Interpolation is raw text substitution. Never put `inputs.*` or agent output
directly in a shell `run`. Use `strict: true` and pass values through `env`:

```yaml
- id: show
  type: shell
  strict: true
  env: {RESULT: "{{ steps.plan.output.stdout }}"}
  run: 'printf "%s\n" "$RESULT"'
```

Quoting is not a security boundary. For inputs that must reach a command,
restrict them with `enum`.

## Rules this repo enforces

- Directory name = `workflow.id`; `README.md` required; versions `X.Y.Z`.
- Must pass Spec Kit's `validate_workflow` (with this repo's step types loaded).
- A released version (tag `workflow-<id>-v<version>`) is immutable.

## Deeper reference

Spec Kit docs at the tag pinned in `pyproject.toml` (currently v1.3.3), e.g.
`gh api "repos/github/spec-kit/contents/docs/workflow-steps/types.md?ref=v1.3.3" --jq .content | base64 -d`.
Also `docs/workflows/api.md`, `docs/workflows/expressions.md`. Bundled examples:
`.venv/lib/python3*/site-packages/specify_cli/core_pack/workflows/` (run `uv sync` first).
