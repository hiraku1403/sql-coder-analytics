from typing import Any

from app.database.connection import get_connection


def get_database_schema() -> list[dict[str, Any]]:
    connection = get_connection()

    try:
        tables = connection.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'main'
            ORDER BY table_name
            """
        ).fetchall()

        schema = []

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