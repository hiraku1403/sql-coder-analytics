from app.core.security import validate_sql


def test_select_query_is_allowed():
    result = validate_sql(
        "SELECT * FROM products"
    )

    assert result.is_valid is True


def test_delete_query_is_blocked():
    result = validate_sql(
        "DELETE FROM products"
    )

    assert result.is_valid is False


def test_update_query_is_blocked():
    result = validate_sql(
        "UPDATE products SET selling_price = 0"
    )

    assert result.is_valid is False


def test_drop_query_is_blocked():
    result = validate_sql(
        "DROP TABLE products"
    )

    assert result.is_valid is False


def test_multiple_statements_are_blocked():
    result = validate_sql(
        "SELECT * FROM products; DROP TABLE products;"
    )

    assert result.is_valid is False


def test_empty_query_is_blocked():
    result = validate_sql("")

    assert result.is_valid is False