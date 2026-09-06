from pathlib import Path

import duckdb

from app.core.config import DATABASE_PATH as CONFIG_DATABASE_PATH


BASE_DIR = Path(__file__).resolve().parents[2]


def get_database_path() -> Path:
    """
    Returns the configured DuckDB database path.

    Relative paths are resolved from the project root.
    Absolute paths are used as provided.
    """

    configured_path = Path(CONFIG_DATABASE_PATH)

    if configured_path.is_absolute():
        return configured_path

    return BASE_DIR / configured_path


def get_connection():
    """
    Creates a DuckDB connection.

    The database directory is created automatically
    when necessary.
    """

    database_path = get_database_path()

    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return duckdb.connect(
        str(database_path)
    )