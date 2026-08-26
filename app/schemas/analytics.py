from typing import Any

from pydantic import BaseModel, Field


class ProductAnalytics(BaseModel):
    name: str
    total_sold: int
    revenue: float


class RegionAnalytics(BaseModel):
    region: str
    revenue: float


class SQLQueryRequest(BaseModel):
    sql: str = Field(
        min_length=1,
        max_length=10000,
    )


class SQLQueryResponse(BaseModel):
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    execution_time_ms: float