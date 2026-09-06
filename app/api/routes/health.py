from fastapi import APIRouter

router = APIRouter(
prefix="/health",
tags=["Health"],
)

@router.get("/")
def health_check():
    """
    Health check endpoint.

    Used to verify that the API is running correctly.
    """
    return {
    "status": "healthy",
    "service": "SQL-Coder & Analytics Agent",
}

