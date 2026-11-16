# __NAME__

__DESCRIPTION__

## Install

```bash
specify workflow step add __ID__
```

## Usage

```yaml
steps:
  - id: greet
    type: __ID__
    message: "Hello {{ inputs.name }}"
```

## Config

| Key | Type | Description |
| --- | --- | --- |
| `message` | string | Text to emit; supports `{{ }}` expressions |

## Output

`steps.<id>.output.message`: the rendered message.
