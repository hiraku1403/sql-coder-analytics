from time import perf_counter
from typing import Any

from app.core.config import (
    MAX_QUERY_LENGTH,
    MAX_RESULT_ROWS,
    QUERY_TIMEOUT_SECONDS,
)
from app.core.security import validate_sql
from app.database.connection import get_connection


class QueryExecutionError(Exception):
    """Raised when a SQL query cannot be executed safely."""


def execute_safe_query(
    sql: str,
    max_rows: int = MAX_RESULT_ROWS,
) -> dict[str, Any]:
    """
    Validate and execute a read-only SQL query.
    """

    if len(sql) > MAX_QUERY_LENGTH:
        raise QueryExecutionError(
            f"SQL query exceeds the maximum allowed length "
            f"of {MAX_QUERY_LENGTH} characters."
        )

    if max_rows < 1 or max_rows > MAX_RESULT_ROWS:
        raise QueryExecutionError(
            f"max_rows must be between 1 and {MAX_RESULT_ROWS}."
        )

    validation = validate_sql(sql)

    if not validation.is_valid:
        raise QueryExecutionError(
            validation.message
        )

    connection = get_connection()

    try:
        start_time = perf_counter()

        connection.execute(
            f"SET threads = 1"
        )

        connection.execute(
            f"SET max_expression_depth = 1000"
        )

        result = connection.execute(sql)

        columns = [
            column[0]
            for column in result.description
        ]

        rows = result.fetchmany(max_rows)

        execution_time_ms = round(
            (perf_counter() - start_time) * 1000,
            2,
        )

        data = [
            dict(zip(columns, row))
            for row in rows
        ]

        return {
            "columns": columns,
            "rows": data,
            "row_count": len(data),
            "execution_time_ms": execution_time_ms,
        }

    except Exception as exc:
        raise QueryExecutionError(
            f"Query execution failed: {exc}"
        ) from exc

    finally:
        connection.close()