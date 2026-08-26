import pytest

from app.services.query_service import (
    QueryExecutionError,
    execute_safe_query,
)


def test_select_query_returns_data():
    result = execute_safe_query(
        "SELECT name FROM products LIMIT 3"
    )

    assert result["row_count"] == 3
    assert "name" in result["columns"]


def test_query_result_has_execution_time():
    result = execute_safe_query(
        "SELECT * FROM products LIMIT 1"
    )

    assert "execution_time_ms" in result
    assert result["execution_time_ms"] >= 0


def test_delete_query_is_rejected():
    with pytest.raises(QueryExecutionError):
        execute_safe_query(
            "DELETE FROM products"
        )


def test_drop_query_is_rejected():
    with pytest.raises(QueryExecutionError):
        execute_safe_query(
            "DROP TABLE products"
        )


def test_multiple_statements_are_rejected():
    with pytest.raises(QueryExecutionError):
        execute_safe_query(
            "SELECT * FROM products; "
            "DROP TABLE products;"
        )


def test_empty_query_is_rejected():
    with pytest.raises(QueryExecutionError):
        execute_safe_query("")


def test_query_length_is_limited():
    huge_query = "SELECT " + ("a" * 20_000)

    with pytest.raises(QueryExecutionError):
        execute_safe_query(huge_query)