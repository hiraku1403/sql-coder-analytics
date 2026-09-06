from unittest.mock import Mock, patch

import pytest

from app.services.ai_service import (
    AnalyticsAgentError,
    ask_analytics_agent,
)


def test_self_correction():

    provider = Mock()

    provider.generate_sql.return_value = """
        SELECT
            nonexistent_column
        FROM products
    """

    provider.correct_sql.return_value = """
        SELECT
            name
        FROM products
        LIMIT 5
    """
    provider.generate_analysis.return_value = """
{
    "summary": "Foram encontrados alguns produtos disponíveis.",
    "key_findings": [
        "A consulta retornou produtos da tabela products."
    ]
}
"""

    with patch(
        "app.services.ai_service.get_llm_provider",
        return_value=provider,
    ):

        result = ask_analytics_agent(
            "Quais são alguns produtos?"
        )

    assert result["corrections"] == 1
    assert result["attempts"] == 2

    assert result["rows"]

    provider.generate_sql.assert_called_once()

    provider.correct_sql.assert_called_once()


def test_self_correction_max_attempts():

    provider = Mock()

    provider.generate_sql.return_value = """
        SELECT
            nonexistent_column
        FROM products
    """

    provider.correct_sql.return_value = """
        SELECT
            another_nonexistent_column
        FROM products
    """

    with patch(
        "app.services.ai_service.get_llm_provider",
        return_value=provider,
    ):

        with pytest.raises(
            AnalyticsAgentError
        ):

            ask_analytics_agent(
                "Faça uma consulta impossível"
            )

    assert (
        provider.correct_sql.call_count == 2
    )