from unittest.mock import Mock, patch

import pytest

from app.services.analysis_service import (
    AnalysisGenerationError,
    generate_analysis,
)


def test_generate_analysis():

    provider = Mock()

    provider.generate_analysis.return_value = """
    {
        "summary": "South generated the highest revenue.",
        "key_findings": [
            "South ranked first.",
            "North ranked second."
        ]
    }
    """

    columns = [
        "region",
        "revenue",
    ]

    rows = [
        {
            "region": "South",
            "revenue": 2000,
        },
        {
            "region": "North",
            "revenue": 1500,
        },
    ]

    with patch(
        "app.services.analysis_service.get_llm_provider",
        return_value=provider,
    ):

        result = generate_analysis(
            question="Which region generated the most revenue?",
            columns=columns,
            rows=rows,
        )

    assert (
        result.summary
        == "South generated the highest revenue."
    )

    assert len(result.key_findings) == 2


def test_invalid_analysis_json():

    provider = Mock()

    provider.generate_analysis.return_value = """
    INVALID JSON
    """

    with patch(
        "app.services.analysis_service.get_llm_provider",
        return_value=provider,
    ):

        with pytest.raises(
            AnalysisGenerationError
        ):

            generate_analysis(
                question="Revenue analysis",
                columns=[
                    "region",
                    "revenue",
                ],
                rows=[
                    {
                        "region": "South",
                        "revenue": 2000,
                    }
                ],
            )