from dataclasses import dataclass

import sqlglot
from sqlglot import exp


@dataclass
class SQLValidationResult:
    is_valid: bool
    message: str


FORBIDDEN_EXPRESSIONS = tuple(
    expression
    for expression in (
        getattr(exp, "Delete", None),
        getattr(exp, "Insert", None),
        getattr(exp, "Update", None),
        getattr(exp, "Drop", None),
        getattr(exp, "Alter", None),
        getattr(exp, "Create", None),
        getattr(exp, "TruncateTable", None),
        getattr(exp, "Merge", None),
        getattr(exp, "Grant", None),
        getattr(exp, "Revoke", None),
    )
    if expression is not None
)


def validate_sql(sql: str) -> SQLValidationResult:
    """
    Validate SQL before execution.

    The current policy allows only read-only SELECT queries.
    """

    if not sql or not sql.strip():
        return SQLValidationResult(
            is_valid=False,
            message="SQL query cannot be empty.",
        )

    try:
        statements = sqlglot.parse(
            sql,
            read="duckdb",
        )
    except Exception as exc:
        return SQLValidationResult(
            is_valid=False,
            message=f"Invalid SQL syntax: {exc}",
        )

    if len(statements) != 1:
        return SQLValidationResult(
            is_valid=False,
            message="Only one SQL statement is allowed.",
        )

    statement = statements[0]

    if not isinstance(statement, exp.Select):
        return SQLValidationResult(
            is_valid=False,
            message="Only SELECT statements are allowed.",
        )

    for node in statement.walk():
        if isinstance(node, FORBIDDEN_EXPRESSIONS):
            return SQLValidationResult(
                is_valid=False,
                message=(
                    f"Forbidden SQL operation: "
                    f"{node.__class__.__name__}"
                ),
            )

    return SQLValidationResult(
        is_valid=True,
        message="SQL query is valid and read-only.",
    )