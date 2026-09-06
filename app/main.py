from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analytics import router as analytics_router
from app.api.routes.database import router as database_router
from app.api.routes.health import router as health_router
from app.core.config import ALLOWED_ORIGINS


app = FastAPI(
    title="SQL-Coder & Analytics Agent",
    description=(
        "AI-powered analytics API for natural language "
        "to SQL, data analysis and visualization."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(analytics_router)
app.include_router(database_router)


@app.get("/")
def root():
    return {
        "name": "SQL-Coder & Analytics Agent",
        "version": "1.0.0",
        "status": "running",
    }