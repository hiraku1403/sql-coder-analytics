import json
from typing import Any

from pydantic import ValidationError

from app.ai.factory import get_llm_provider
from app.schemas.chart import ChartPlan


class ChartPlanningError(Exception):
    """Raised when chart planning fails."""


def _clean_markdown_code_fence(
    content: str,
) -> str:
    """
    Removes Markdown code fences from an LLM response.
    """

    content = content.strip()

    if not content.startswith("```"):
        return content

    lines = content.splitlines()

    if lines:
        lines = lines[1:]

    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    return "\n".join(lines).strip()


def generate_chart_plan(
    question: str,
    columns: list[str],
    rows: list[dict[str, Any]],
    provider: Any | None = None,
) -> ChartPlan:
    """
    Generates and validates a chart plan using the LLM.

    The provider parameter is optional for backward compatibility.
    """

    # -------------------------------------------------
    # Validate data
    # -------------------------------------------------

    if not columns:

        raise ChartPlanningError(
            "No columns available for visualization."
        )

    if not rows:

        raise ChartPlanningError(
            "No rows available for visualization."
        )

    # -------------------------------------------------
    # Provider
    # -------------------------------------------------

    if provider is None:
        provider = get_llm_provider()

    # -------------------------------------------------
    # Generate chart plan
    # -------------------------------------------------

    try:

        raw_plan = provider.generate_chart_plan(
            question=question,
            columns=columns,
            rows=rows,
        )

    except Exception as exc:

        raise ChartPlanningError(
            f"Failed to generate chart plan: {exc}"
        ) from exc

    # -------------------------------------------------
    # Validate response type
    # -------------------------------------------------

    if not isinstance(
        raw_plan,
        str,
    ):

        raise ChartPlanningError(
            "LLM returned an invalid chart plan response."
        )

    raw_plan = (
        _clean_markdown_code_fence(
            raw_plan
        )
    )

    # -------------------------------------------------
    # Parse JSON
    # -------------------------------------------------

    try:

        data = json.loads(
            raw_plan
        )

    except (
        json.JSONDecodeError,
        TypeError,
    ) as exc:

        raise ChartPlanningError(
            "LLM returned invalid JSON."
        ) from exc

    # -------------------------------------------------
    # Validate object
    # -------------------------------------------------

    if not isinstance(
        data,
        dict,
    ):

        raise ChartPlanningError(
            "LLM chart plan JSON must be an object."
        )

    # -------------------------------------------------
    # Pydantic validation
    # -------------------------------------------------

    try:

        plan = ChartPlan.model_validate(
            data
        )

    except ValidationError as exc:

        raise ChartPlanningError(
            "LLM returned an invalid chart plan: "
            f"{exc}"
        ) from exc

    # -------------------------------------------------
    # Validate column references
    # -------------------------------------------------

    validate_chart_columns(
        plan=plan,
        columns=columns,
    )

    return plan


def validate_chart_columns(
    plan: ChartPlan,
    columns: list[str],
) -> None:
    """
    Ensures that the LLM only references
    columns returned by the database.
    """

    valid_columns = {
        str(column)
        for column in columns
    }

    # -------------------------------------------------
    # X axis
    # -------------------------------------------------

    if (
        plan.x_axis is not None
        and plan.x_axis not in valid_columns
    ):

        raise ChartPlanningError(
            f"Invalid x_axis: {plan.x_axis}"
        )

    # -------------------------------------------------
    # Y axis
    # -------------------------------------------------

    if (
        plan.y_axis is not None
        and plan.y_axis not in valid_columns
    ):

        raise ChartPlanningError(
            f"Invalid y_axis: {plan.y_axis}"
        )