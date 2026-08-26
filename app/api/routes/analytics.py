from fastapi import APIRouter, HTTPException, Query

from app.services.schema_service import get_database_schema


from app.schemas.analytics import (
    ProductAnalytics,
    RegionAnalytics,
    SQLQueryRequest,
    SQLQueryResponse,
)
from app.services.analytics_service import (
    get_revenue_by_region,
    get_top_products,
)
from app.services.query_service import (
    QueryExecutionError,
    execute_safe_query,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "/top-products",
    response_model=list[ProductAnalytics],
)
def top_products(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
):
    rows = get_top_products(limit)

    return [
        ProductAnalytics(
            name=row[0],
            total_sold=row[1],
            revenue=float(row[2]),
        )
        for row in rows
    ]


@router.get(
    "/revenue-by-region",
    response_model=list[RegionAnalytics],
)
def revenue_by_region():
    rows = get_revenue_by_region()

    return [
        RegionAnalytics(
            region=row[0],
            revenue=float(row[1]),
        )
        for row in rows
    ]

@router.post(
    "/query",
    response_model=SQLQueryResponse,
)
def execute_query(request: SQLQueryRequest):
    try:
        return execute_safe_query(request.sql)

    except QueryExecutionError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    
@router.get("/schema")
def database_schema():
    return {
        "database": "ecommerce",
        "tables": get_database_schema(),
    }