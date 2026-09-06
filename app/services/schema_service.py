from typing import Any

from app.database.connection import get_connection


def get_database_schema() -> list[dict[str, Any]]:
    """
    Returns the complete database schema.

    The schema contains:
    - table names
    - column names
    - column data types
    - nullable information
    """

    connection = get_connection()

    try:
        tables = connection.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'main'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
        ).fetchall()

        schema: list[dict[str, Any]] = []

        for (table_name,) in tables:
            columns = connection.execute(
                """
                SELECT
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'main'
                  AND table_name = ?
                ORDER BY ordinal_position
                """,
                [table_name],
            ).fetchall()

            schema.append(
                {
                    "table": table_name,
                    "columns": [
                        {
                            "name": column[0],
                            "type": column[1],
                            "nullable": column[2] == "YES",
                        }
                        for column in columns
                    ],
                }
            )

        return schema

    finally:
        connection.close()


def format_database_schema(
    schema: list[dict[str, Any]],
) -> str:
    """
    Converts the database schema into a text format
    optimized for sending to an LLM.
    """

    lines: list[str] = [
        "DATABASE SCHEMA",
        "",
    ]

    for table in schema:
        table_name = table["table"]

        lines.append(f"TABLE {table_name}")

        for column in table["columns"]:
            column_name = column["name"]
            column_type = column["type"]

            nullable = (
                "NULL"
                if column["nullable"]
                else "NOT NULL"
            )

            lines.append(
                f"- {column_name} "
                f"{column_type} "
                f"{nullable}"
            )

        lines.append("")

    return "\n".join(lines)