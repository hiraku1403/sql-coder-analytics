import json
from typing import Any

from pydantic import ValidationError

from app.ai.factory import get_llm_provider
from app.schemas.analysis import AnalysisResult


class AnalysisGenerationError(Exception):
    """Raised when analysis generation fails."""


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


def generate_analysis(
    question: str,
    columns: list[str],
    rows: list[dict[str, Any]],
    provider: Any | None = None,
) -> AnalysisResult:
    """
    Generates and validates analytical insights using the LLM.

    The provider parameter is optional for backward compatibility.

    When omitted, the configured provider is created internally.

    When supplied, the existing provider instance is reused.
    """

    # -------------------------------------------------
    # No data
    # -------------------------------------------------

    if not columns or not rows:

        return AnalysisResult(
            summary="No data available for analysis.",
            insights=[],
        )

    # -------------------------------------------------
    # LLM provider
    # -------------------------------------------------

    if provider is None:
        provider = get_llm_provider()

    # -------------------------------------------------
    # Generate analysis
    # -------------------------------------------------

    try:

        raw_analysis = provider.generate_analysis(
            question=question,
            columns=columns,
            rows=rows,
        )

    except Exception as exc:

        raise AnalysisGenerationError(
            f"Failed to generate analysis: {exc}"
        ) from exc

    # -------------------------------------------------
    # Validate response type
    # -------------------------------------------------

    if not isinstance(
        raw_analysis,
        str,
    ):

        raise AnalysisGenerationError(
            "LLM returned an invalid analysis response."
        )

    raw_analysis = (
        _clean_markdown_code_fence(
            raw_analysis
        )
    )

    # -------------------------------------------------
    # Parse JSON
    # -------------------------------------------------

    try:

        data = json.loads(
            raw_analysis
        )

    except (
        json.JSONDecodeError,
        TypeError,
    ) as exc:

        raise AnalysisGenerationError(
            "LLM returned invalid analysis JSON."
        ) from exc

    # -------------------------------------------------
    # Validate object
    # -------------------------------------------------

    if not isinstance(
        data,
        dict,
    ):

        raise AnalysisGenerationError(
            "LLM analysis JSON must be an object."
        )

    # -------------------------------------------------
    # Backward compatibility
    # -------------------------------------------------
    #
    # Older prompts/providers may return:
    #
    #     key_findings
    #
    # The current schema uses:
    #
    #     insights
    #

    if (
        "insights" not in data
        and "key_findings" in data
    ):

        data["insights"] = data.pop(
            "key_findings"
        )

    # -------------------------------------------------
    # Validate with Pydantic
    # -------------------------------------------------

    try:

        analysis = AnalysisResult.model_validate(
            data
        )

    except ValidationError as exc:

        raise AnalysisGenerationError(
            "LLM returned an invalid analysis: "
            f"{exc}"
        ) from exc

    return analysis