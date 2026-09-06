from typing import Any

from pydantic import BaseModel, Field

from app.schemas.analysis import AnalysisResult
from app.schemas.chart import ChartPlan


class SQLGenerationRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=1000,
    )


class SQLGenerationResponse(BaseModel):
    question: str
    sql: str


class SQLExecutionRequest(BaseModel):
    sql: str = Field(
        min_length=1,
        max_length=10000,
    )


class AnalyticsAskRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=1000,
    )


class VisualizationResponse(BaseModel):
    plan: ChartPlan
    chart: dict[str, Any]


class DataResponse(BaseModel):
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int


class AgentMetadata(BaseModel):
    attempts: int
    corrections: int
    execution_time_ms: float


class AnalyticsAskResponse(BaseModel):
    question: str
    sql: str

    data: DataResponse

    analysis: AnalysisResult

    visualization: VisualizationResponse | None = None

    metadata: AgentMetadata

    # -----------------------------------------
    # Backward compatibility
    # -----------------------------------------

    attempts: int
    corrections: int