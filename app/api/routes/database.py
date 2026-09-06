from fastapi import APIRouter, HTTPException

from app.services.schema_service import (
format_database_schema,
get_database_schema,
)

router = APIRouter(
prefix="/database",
tags=["Database"],
)

@router.get("/schema")
def database_schema():
    """
    Returns the current database schema.

    The schema is obtained from the same service used by
    the SQL generation pipeline.
    """
    try:
        schema = get_database_schema()

        return {
            "schema": schema,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve database schema: {exc}",
        ) from exc


@router.get("/schema/formatted")
def formatted_database_schema():
    """
    Returns the database schema in the formatted representation
    used by the AI SQL generation prompt.
    """
    try:
        schema = get_database_schema()

        formatted_schema = format_database_schema(
            schema
        )

        return {
            "schema": formatted_schema,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to format database schema: {exc}",
        ) from exc


@router.get("/status")
def database_status():
    """
    Basic database availability check.

    This endpoint verifies that the application can retrieve
    the database schema successfully.
    """
    try:
        schema = get_database_schema()

        return {
            "status": "connected",
            "tables": len(schema),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable: {exc}",
        ) from exc

