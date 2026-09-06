from app.services.visualization_service import (
    create_visualization,
    detect_chart_type,
)


def test_detect_bar_chart():

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
        {
            "region": "East",
            "revenue": 1500,
        },
    ]

    chart_type = detect_chart_type(
        columns,
        rows,
    )

    assert chart_type == "bar"


def test_detect_line_chart():

    columns = [
        "month",
        "revenue",
    ]

    rows = [
        {
            "month": "2026-01",
            "revenue": 1000,
        },
        {
            "month": "2026-02",
            "revenue": 1500,
        },
        {
            "month": "2026-03",
            "revenue": 2000,
        },
    ]

    chart_type = detect_chart_type(
        columns,
        rows,
    )

    assert chart_type == "line"


def test_create_visualization():

    columns = [
        "category",
        "sales",
    ]

    rows = [
        {
            "category": "Electronics",
            "sales": 100,
        },
        {
            "category": "Furniture",
            "sales": 80,
        },
    ]

    result = create_visualization(
        columns,
        rows,
    )

    assert result["type"] == "bar"

    assert result["figure"] is not None