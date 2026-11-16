"""__NAME__ workflow step type.

Used in a workflow as:

    - id: my-step
      type: __ID__
      message: "Hello {{ inputs.name }}"

Step instances are shared across concurrent fan-out iterations, so keep
``execute`` stateless: derive everything from ``config`` and ``context``.
"""

from __future__ import annotations

from typing import Any

from specify_cli.workflows.base import StepBase, StepContext, StepResult, StepStatus
from specify_cli.workflows.expressions import evaluate_expression


class __CLASS__Step(StepBase):
    """__DESCRIPTION__"""

    type_key = "__ID__"

    def execute(self, config: dict[str, Any], context: StepContext) -> StepResult:
        message = config.get("message", "")
        if isinstance(message, str) and "{{" in message:
            message = evaluate_expression(message, context)
        # ``output`` is exposed to later steps as ``steps.<id>.output``.
        return StepResult(status=StepStatus.COMPLETED, output={"message": message})

    def validate(self, config: dict[str, Any]) -> list[str]:
        errors = super().validate(config)
        if "message" in config and not isinstance(config["message"], str):
            errors.append(f"Step {config.get('id', '?')!r}: 'message' must be a string.")
        return errors
