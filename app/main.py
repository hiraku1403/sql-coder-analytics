from fastapi import FastAPI

app = FastAPI(
    title="SQL-Coder & Analytics Agent",
    description="AI-powered Text-to-SQL analytics platform",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "sql-coder-analytics",
        "version": "0.1.0",
    }