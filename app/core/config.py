import os

from dotenv import load_dotenv


load_dotenv()


DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "data/ecommerce.duckdb",
)


MAX_QUERY_LENGTH = 10_000

MAX_RESULT_ROWS = 1_000

QUERY_TIMEOUT_SECONDS = 5


LLM_PROVIDER = os.getenv(
    "LLM_PROVIDER",
    "gemini",
)


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
)


def _get_allowed_origins() -> list[str]:
    """
    Returns the list of allowed CORS origins.

    Local development origins are always available.
    Additional production origins can be provided through
    the ALLOWED_ORIGINS environment variable.

    Example:

        ALLOWED_ORIGINS=https://sql-coder-frontend.onrender.com/
    """

    local_origins = [
        "https://sql-coder-frontend.onrender.com/",
        "https://sql-coder-frontend.onrender.com/",
    ]

    configured_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "",
    )

    production_origins = [
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    ]

    return list(
        dict.fromkeys(
            local_origins + production_origins
        )
    )


ALLOWED_ORIGINS = _get_allowed_origins()