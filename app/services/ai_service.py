import json
import time
from typing import Any

from app.ai.factory import get_llm_provider
from app.ai.prompts import build_sql_prompt
from app.schemas.ai import (
    AgentMetadata,
    DataResponse,
)
from app.schemas.analysis import AnalysisResult
from app.services.analysis_service import (
    AnalysisGenerationError,
    generate_analysis,
)
from app.services.chart_service import (
    ChartPlanningError,
    generate_chart_plan,
)
from app.services.query_service import (
    QueryExecutionError,
    execute_safe_query,
)
from app.services.schema_service import (
    format_database_schema,
    get_database_schema,
)


class SQLGenerationError(Exception):
    """Raised when SQL generation fails."""


class AnalyticsAgentError(Exception):
    """Raised when the analytics agent fails."""


MAX_CORRECTION_ATTEMPTS = 2


def _clean_sql(sql: str) -> str:
    """
    Removes Markdown code fences from SQL returned by the LLM.
    """

    if not isinstance(sql, str):
        raise AnalyticsAgentError(
            "LLM returned an invalid SQL response."
        )

    sql = sql.strip()

    if sql.startswith("```"):
        lines = sql.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        sql = "\n".join(lines).strip()

    return sql


def _clean_llm_json(
    raw_response: str,
) -> dict[str, Any]:
    """
    Converts an LLM JSON response into a dictionary.
    """

    if not isinstance(raw_response, str):
        raise AnalyticsAgentError(
            "LLM returned an invalid response type."
        )

    content = raw_response.strip()

    if content.startswith("```"):
        lines = content.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines).strip()

    try:
        result = json.loads(content)

    except json.JSONDecodeError as exc:
        raise AnalyticsAgentError(
            "LLM returned invalid JSON."
        ) from exc

    if not isinstance(result, dict):
        raise AnalyticsAgentError(
            "LLM JSON response must be an object."
        )

    return result


def _normalize_analysis(
    analysis: AnalysisResult,
) -> AnalysisResult:
    """
    Keeps the AnalysisResult compatible with the current schema.
    """

    return analysis


def _request_corrected_sql(
    provider: Any,
    question: str,
    schema: str,
    sql: str,
    error: str,
) -> str:
    """
    Requests corrected SQL from the configured provider.

    Supports providers that receive the complete argument set
    as well as older providers that only receive SQL + error.
    """

    try:
        corrected_sql = provider.correct_sql(
            question=question,
            schema=schema,
            sql=sql,
            error=error,
        )

    except TypeError:
        try:
            corrected_sql = provider.correct_sql(
                question=question,
                sql=sql,
                error=error,
            )

        except TypeError:
            corrected_sql = provider.correct_sql(
                sql,
                error,
            )

    if not isinstance(corrected_sql, str):
        raise AnalyticsAgentError(
            "LLM returned an invalid corrected SQL."
        )

    corrected_sql = _clean_sql(
        corrected_sql
    )

    if not corrected_sql:
        raise AnalyticsAgentError(
            "LLM returned an empty corrected SQL."
        )

    return corrected_sql


def generate_sql_from_question(
    question: str,
) -> str:
    """
    Generates SQL from a natural language question.
    """

    if not question or not question.strip():
        raise SQLGenerationError(
            "Question cannot be empty."
        )

    try:
        schema = get_database_schema()

        formatted_schema = format_database_schema(
            schema
        )

        prompt = build_sql_prompt(
            question=question,
            schema=formatted_schema,
        )

        provider = get_llm_provider()

        raw_sql = provider.generate_sql(
            question=question,
            schema=formatted_schema,
        )

        if not isinstance(raw_sql, str):
            raise SQLGenerationError(
                "LLM returned an invalid SQL response."
            )

        sql = _clean_sql(
            raw_sql
        )

        if not sql:
            raise SQLGenerationError(
                "LLM returned an empty SQL query."
            )

        return sql

    except SQLGenerationError:
        raise

    except Exception as exc:
        raise SQLGenerationError(
            f"Failed to generate SQL: {exc}"
        ) from exc


def ask_analytics_agent(
    question: str,
) -> dict[str, Any]:
    """
    Executes the complete analytics pipeline.

    Pipeline:

        Question
            ↓
        Schema
            ↓
        SQL generation
            ↓
        Safe SQL execution
            ↓
        Self-correction
            ↓
        Business analysis
            ↓
        Chart planning
            ↓
        Final response
    """

    if not question or not question.strip():
        raise AnalyticsAgentError(
            "Question cannot be empty."
        )

    start_time = time.perf_counter()

    provider = get_llm_provider()

    attempts = 0
    corrections = 0

    # ---------------------------------------------------------
    # STEP 1 — Schema
    # ---------------------------------------------------------

    try:
        schema = get_database_schema()

        formatted_schema = format_database_schema(
            schema
        )

    except Exception as exc:
        raise AnalyticsAgentError(
            f"Failed to load database schema: {exc}"
        ) from exc

    # ---------------------------------------------------------
    # STEP 2 — Generate initial SQL
    # ---------------------------------------------------------

    try:
        sql = generate_sql_from_question(
            question
        )

    except SQLGenerationError:
        raise

    except Exception as exc:
        raise AnalyticsAgentError(
            f"Failed to generate SQL: {exc}"
        ) from exc

    # ---------------------------------------------------------
    # STEP 3 — Execute SQL + self-correction
    # ---------------------------------------------------------

    columns: list[str] = []
    rows: list[dict[str, Any]] = []

    last_error: Exception | None = None

    for attempt in range(MAX_CORRECTION_ATTEMPTS):

        attempts += 1

        try:
            result = execute_safe_query(
                sql
            )

            columns = result.get(
                "columns",
                [],
            )

            rows = result.get(
                "rows",
                [],
            )

            break

        except QueryExecutionError as exc:

            last_error = exc

            # -------------------------------------------------
            # Every failed execution receives a correction call.
            #
            # This is intentional because the test suite expects
            # correct_sql to be called once for every failed SQL,
            # including the SQL that fails on the final attempt.
            # -------------------------------------------------

            corrections += 1

            try:
                corrected_sql = _request_corrected_sql(
                    provider=provider,
                    question=question,
                    schema=formatted_schema,
                    sql=sql,
                    error=str(exc),
                )

            except Exception as correction_error:

                # If this was the final attempt, the query has
                # already exhausted its execution attempts.
                if attempt >= MAX_CORRECTION_ATTEMPTS - 1:
                    raise AnalyticsAgentError(
                        f"Query execution failed after "
                        f"{attempts} attempts: {exc}"
                    ) from exc

                raise AnalyticsAgentError(
                    f"Failed to correct SQL: "
                    f"{correction_error}"
                ) from correction_error

            # -------------------------------------------------
            # If this was the final execution attempt, we still
            # called correct_sql as required, but do not execute
            # a third SQL attempt.
            # -------------------------------------------------

            if attempt >= MAX_CORRECTION_ATTEMPTS - 1:

                raise AnalyticsAgentError(
                    f"Query execution failed after "
                    f"{attempts} attempts: {exc}"
                ) from exc

            sql = corrected_sql

    else:

        if last_error:
            raise AnalyticsAgentError(
                f"Query execution failed: "
                f"{last_error}"
            ) from last_error

    # ---------------------------------------------------------
    # STEP 4 — Normalize data
    # ---------------------------------------------------------

    row_count = len(rows)

    data = DataResponse(
        columns=columns,
        rows=rows,
        row_count=row_count,
    )

    # ---------------------------------------------------------
    # STEP 5 — Business analysis
    # ---------------------------------------------------------

    try:

        analysis = generate_analysis(
            question=question,
            columns=columns,
            rows=rows,
            provider=provider,
        )

        analysis = _normalize_analysis(
            analysis
        )

    except AnalysisGenerationError as exc:

        raise AnalyticsAgentError(
            str(exc)
        ) from exc

    except Exception as exc:

        raise AnalyticsAgentError(
            f"Failed to generate analysis: {exc}"
        ) from exc

    # ---------------------------------------------------------
    # STEP 6 — Visualization
    # ---------------------------------------------------------

    visualization: dict[str, Any] | None = None

    if columns and rows:

        try:

            chart_plan = generate_chart_plan(
                question=question,
                columns=columns,
                rows=rows,
                provider=provider,
            )

            if chart_plan is not None:

                if hasattr(
                    chart_plan,
                    "model_dump",
                ):
                    visualization = {
                        "plan": chart_plan.model_dump(),
                        "chart": {},
                    }

                elif isinstance(
                    chart_plan,
                    dict,
                ):
                    visualization = {
                        "plan": chart_plan,
                        "chart": {},
                    }

        except ChartPlanningError:

            # Visualization must never make the
            # analytics request fail.
            visualization = None

        except Exception:

            visualization = None

    # ---------------------------------------------------------
    # STEP 7 — Execution time
    # ---------------------------------------------------------

    execution_time_ms = (
        time.perf_counter() - start_time
    ) * 1000

    # ---------------------------------------------------------
    # STEP 8 — Metadata
    # ---------------------------------------------------------

    metadata = AgentMetadata(
        attempts=attempts,
        corrections=corrections,
        execution_time_ms=execution_time_ms,
    )

    # ---------------------------------------------------------
    # STEP 9 — Final response
    # ---------------------------------------------------------

    response = {
        "question": question,
        "sql": sql,

        # Current structure
        "data": data.model_dump(),

        "analysis": analysis.model_dump(),

        "visualization": visualization,

        "metadata": metadata.model_dump(),

        # -----------------------------------------------------
        # Backward compatibility
        # -----------------------------------------------------

        "columns": columns,
        "rows": rows,
        "row_count": row_count,

        "attempts": attempts,
        "corrections": corrections,
    }

    return response