from pathlib import Path

import duckdb


BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = BASE_DIR / "data"
DATABASE_PATH = DATABASE_DIR / "ecommerce.duckdb"


def get_connection():
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    return duckdb.connect(str(DATABASE_PATH))