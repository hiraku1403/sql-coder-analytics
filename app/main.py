from fastapi import FastAPI

from app.api.routes.analytics import router as analytics_router


app = FastAPI(
    title="SQL-Coder & Analytics Agent",
    description="AI-powered Text-to-SQL analytics platform",
    version="0.1.0",
)


app.include_router(analytics_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "sql-coder-analytics",
        "version": "0.1.0",
    }