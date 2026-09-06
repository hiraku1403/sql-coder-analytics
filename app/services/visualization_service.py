from typing import Any

import plotly.graph_objects as go

from app.schemas.chart import ChartPlan
from app.services.chart_service import (
    ChartPlanningError,
    generate_chart_plan,
)


def detect_chart_type(
    columns: list[str],
    rows: list[dict[str, Any]],
) -> str:
    """
    Detects a reasonable chart type based on the
    structure of the query result.

    This function is kept for backward compatibility
    with the original visualization pipeline.
    """

    if not columns or not rows:
        return "table"

    # -----------------------------------------
    # Detect numeric and categorical columns
    # -----------------------------------------

    numeric_columns: list[str] = []
    categorical_columns: list[str] = []

    for column in columns:

        values = [
            row.get(column)
            for row in rows
            if row.get(column) is not None
        ]

        if not values:
            continue

        if all(
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            for value in values
        ):
            numeric_columns.append(column)

        else:
            categorical_columns.append(column)

    # -----------------------------------------
    # Time-like columns
    # -----------------------------------------

    time_keywords = (
        "date",
        "time",
        "year",
        "month",
        "day",
        "datetime",
    )

    has_time_column = any(
        any(
            keyword in column.lower()
            for keyword in time_keywords
        )
        for column in columns
    )

    if has_time_column and numeric_columns:
        return "line"

    # -----------------------------------------
    # Category + numeric
    # -----------------------------------------

    if categorical_columns and numeric_columns:
        return "bar"

    # -----------------------------------------
    # Two numeric columns
    # -----------------------------------------

    if len(numeric_columns) >= 2:
        return "scatter"

    # -----------------------------------------
    # One category + one numeric
    # -----------------------------------------

    if len(categorical_columns) == 1 and len(
        numeric_columns
    ) == 1:

        if len(rows) <= 6:
            return "pie"

        return "bar"

    # -----------------------------------------
    # Fallback
    # -----------------------------------------

    return "table"


def generate_chart(
    plan: ChartPlan,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Generates a Plotly chart based on a validated
    chart plan.
    """

    # -----------------------------------------
    # Table
    # -----------------------------------------

    if plan.chart_type == "table":
        return {
            "type": "table",
            "figure": None,
        }

    if not plan.x_axis:
        raise ValueError(
            "Chart requires an x_axis."
        )

    x_values = [
        row.get(plan.x_axis)
        for row in rows
    ]

    # -----------------------------------------
    # Bar chart
    # -----------------------------------------

    if plan.chart_type == "bar":

        if not plan.y_axis:
            raise ValueError(
                "Bar chart requires a y_axis."
            )

        y_values = [
            row.get(plan.y_axis)
            for row in rows
        ]

        figure = go.Figure(
            data=[
                go.Bar(
                    x=x_values,
                    y=y_values,
                )
            ]
        )

    # -----------------------------------------
    # Line chart
    # -----------------------------------------

    elif plan.chart_type == "line":

        if not plan.y_axis:
            raise ValueError(
                "Line chart requires a y_axis."
            )

        y_values = [
            row.get(plan.y_axis)
            for row in rows
        ]

        figure = go.Figure(
            data=[
                go.Scatter(
                    x=x_values,
                    y=y_values,
                    mode="lines+markers",
                )
            ]
        )

    # -----------------------------------------
    # Pie chart
    # -----------------------------------------

    elif plan.chart_type == "pie":

        if not plan.y_axis:
            raise ValueError(
                "Pie chart requires a y_axis."
            )

        y_values = [
            row.get(plan.y_axis)
            for row in rows
        ]

        figure = go.Figure(
            data=[
                go.Pie(
                    labels=x_values,
                    values=y_values,
                )
            ]
        )

    # -----------------------------------------
    # Scatter chart
    # -----------------------------------------

    elif plan.chart_type == "scatter":

        if not plan.y_axis:
            raise ValueError(
                "Scatter chart requires a y_axis."
            )

        y_values = [
            row.get(plan.y_axis)
            for row in rows
        ]

        figure = go.Figure(
            data=[
                go.Scatter(
                    x=x_values,
                    y=y_values,
                    mode="markers",
                )
            ]
        )

    else:
        raise ValueError(
            f"Unsupported chart type: {plan.chart_type}"
        )

    # -----------------------------------------
    # Layout
    # -----------------------------------------

    figure.update_layout(
        title=plan.title,
        xaxis_title=plan.x_axis,
        yaxis_title=plan.y_axis,
        template="plotly_white",
    )

    return {
        "type": plan.chart_type,
        "figure": figure.to_plotly_json(),
    }



def create_visualization(
    columns: list[str],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Creates a visualization automatically based on
    the structure of the query result.

    This function preserves the original API used
    by the existing tests.

    Pipeline:

        columns + rows
              ↓
        detect_chart_type()
              ↓
          ChartPlan
              ↓
          generate_chart()
              ↓
            Plotly
    """

    if not columns or not rows:
        return {
            "type": "table",
            "figure": None,
        }

    chart_type = detect_chart_type(
        columns=columns,
        rows=rows,
    )

    # -----------------------------------------
    # Identify columns
    # -----------------------------------------

    numeric_columns: list[str] = []
    categorical_columns: list[str] = []

    for column in columns:

        values = [
            row.get(column)
            for row in rows
            if row.get(column) is not None
        ]

        if not values:
            continue

        if all(
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            for value in values
        ):
            numeric_columns.append(column)

        else:
            categorical_columns.append(column)

    # -----------------------------------------
    # Build ChartPlan
    # -----------------------------------------

    x_axis = (
        categorical_columns[0]
        if categorical_columns
        else columns[0]
    )

    y_axis = (
        numeric_columns[0]
        if numeric_columns
        else None
    )

    plan = ChartPlan(
        chart_type=chart_type,
        x_axis=x_axis,
        y_axis=y_axis,
        title=f"{y_axis or x_axis} by {x_axis}",
        reason=(
            "Chart type automatically detected "
            "from the query result structure."
        ),
    )

    # -----------------------------------------
    # Generate Plotly chart
    # -----------------------------------------

    return generate_chart(
        plan=plan,
        rows=rows,
    )



def create_ai_visualization(
    question: str,
    columns: list[str],
    rows: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Creates an AI-powered visualization.

    Pipeline:

        Question
           ↓
        Gemini
           ↓
        ChartPlan
           ↓
        Validation
           ↓
        Plotly

    Visualization failures are isolated from the
    main analytics pipeline.
    """

    try:

        plan = generate_chart_plan(
            question=question,
            columns=columns,
            rows=rows,
        )

        chart = generate_chart(
            plan=plan,
            rows=rows,
        )

        return {
            "plan": plan.model_dump(),
            "chart": chart,
        }

    except (
        ChartPlanningError,
        ValueError,
        KeyError,
        TypeError,
    ):

        # Visualization is optional.
        #
        # The SQL result and analysis should
        # still be returned to the user.

        return None

