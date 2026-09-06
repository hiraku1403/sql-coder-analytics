from fastapi import APIRouter, HTTPException

from app.schemas.ai import (
    AnalyticsAskRequest,
    AnalyticsAskResponse,
    SQLExecutionRequest,
    SQLGenerationRequest,
    SQLGenerationResponse,
)
from app.services.ai_service import (
    AnalyticsAgentError,
    SQLGenerationError,
    ask_analytics_agent,
    generate_sql_from_question,
)
from app.services.query_service import (
    QueryExecutionError,
    execute_safe_query,
)
from app.services.schema_service import (
    get_database_schema,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/schema")
def database_schema():
    """
    Returns the current database schema.
    """

    try:
        schema = get_database_schema()

        return {
            "database": "ecommerce",
            "tables": schema,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve database schema: {exc}",
        ) from exc


@router.post(
    "/generate-sql",
    response_model=SQLGenerationResponse,
)
def generate_sql(
    request: SQLGenerationRequest,
):
    """
    Generates validated SQL from a natural language question.
    """

    try:
        sql = generate_sql_from_question(
            request.question
        )

        return {
            "question": request.question,
            "sql": sql,
        }

    except SQLGenerationError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate SQL: {exc}",
        ) from exc


@router.post("/query")
def execute_query(
    request: SQLExecutionRequest,
):
    """
    Executes a validated SQL query.
    """

    try:
        return execute_safe_query(
            request.sql
        )

    except QueryExecutionError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected query error: {exc}",
        ) from exc


@router.post(
    "/ask",
    response_model=AnalyticsAskResponse,
)
def ask_analytics(
    request: AnalyticsAskRequest,
):
    """
    Ask a natural language analytics question.

    The agent generates SQL, validates it,
    executes it against DuckDB and returns
    the result.
    """

    try:
        result = ask_analytics_agent(
            request.question
        )

        return result

    except SQLGenerationError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except AnalyticsAgentError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected agent error: {exc}",
        ) from exc