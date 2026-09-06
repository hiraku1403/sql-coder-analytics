from typing import Literal

from pydantic import BaseModel, Field


ChartType = Literal[
    "bar",
    "line",
    "pie",
    "scatter",
    "table",
]


class ChartPlan(BaseModel):
    chart_type: ChartType

    x_axis: str | None = None

    y_axis: str | None = None

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    reason: str = Field(
        min_length=1,
        max_length=500,
    )