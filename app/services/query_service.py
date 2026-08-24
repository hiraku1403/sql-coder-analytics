from typing import Any

from app.core.security import validate_sql
from app.database.connection import get_connection


class QueryExecutionError(Exception):
    """Raised when a SQL query cannot be executed."""


def execute_safe_query(
    sql: str,
    max_rows: int = 1000,
) -> dict[str, Any]:
    """
    Validate and execute a read-only SQL query.
    """

    validation = validate_sql(sql)

    if not validation.is_valid:
        raise QueryExecutionError(
            validation.message
        )

    connection = get_connection()

    try:
        result = connection.execute(sql)

        columns = [
            column[0]
            for column in result.description
        ]

        rows = result.fetchmany(max_rows)

        data = [
            dict(zip(columns, row))
            for row in rows
        ]

        return {
            "columns": columns,
            "rows": data,
            "row_count": len(data),
        }

    except Exception as exc:
        raise QueryExecutionError(
            f"Query execution failed: {exc}"
        ) from exc

    finally:
        connection.close()