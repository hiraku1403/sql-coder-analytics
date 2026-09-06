from unittest.mock import Mock, patch

import pytest

from app.services.chart_service import (
    ChartPlanningError,
    generate_chart_plan,
)


def test_generate_chart_plan():

    provider = Mock()

    provider.generate_chart_plan.return_value = """
    {
        "chart_type": "bar",
        "x_axis": "region",
        "y_axis": "revenue",
        "title": "Revenue by Region",
        "reason": "Bar charts are appropriate for comparing regions."
    }
    """

    columns = [
        "region",
        "revenue",
    ]

    rows = [
        {
            "region": "North",
            "revenue": 1000,
        },
        {
            "region": "South",
            "revenue": 2000,
        },
    ]

    with patch(
        "app.services.chart_service.get_llm_provider",
        return_value=provider,
    ):

        plan = generate_chart_plan(
            question="Revenue by region",
            columns=columns,
            rows=rows,
        )

    assert plan.chart_type == "bar"
    assert plan.x_axis == "region"
    assert plan.y_axis == "revenue"
    assert plan.title == "Revenue by Region"


def test_invalid_chart_type():

    provider = Mock()

    provider.generate_chart_plan.return_value = """
    {
        "chart_type": "invalid_chart",
        "x_axis": "region",
        "y_axis": "revenue",
        "title": "Revenue",
        "reason": "Invalid chart."
    }
    """

    with patch(
        "app.services.chart_service.get_llm_provider",
        return_value=provider,
    ):

        with pytest.raises(
            ChartPlanningError
        ):

            generate_chart_plan(
                question="Revenue by region",
                columns=[
                    "region",
                    "revenue",
                ],
                rows=[],
            )


def test_invalid_column():

    provider = Mock()

    provider.generate_chart_plan.return_value = """
    {
        "chart_type": "bar",
        "x_axis": "secret_column",
        "y_axis": "revenue",
        "title": "Revenue",
        "reason": "Testing invalid column."
    }
    """

    with patch(
        "app.services.chart_service.get_llm_provider",
        return_value=provider,
    ):

        with pytest.raises(
            ChartPlanningError
        ):

            generate_chart_plan(
                question="Revenue",
                columns=[
                    "region",
                    "revenue",
                ],
                rows=[],
            )