# SQL-Coder & Analytics Agent

AI-powered Text-to-SQL analytics platform.

The system allows users to ask questions about relational
databases using natural language.

## Current Status

🚧 Project under development.

## Tech Stack

- Python
- FastAPI
- Pydantic

## Planned Features

- Natural Language → SQL
- SQL validation
- SQL injection protection
- DuckDB/PostgreSQL
- LLM integration
- Self-Correction Loop
- Data visualization
- AI-generated insights

## Current Features

- FastAPI backend
- DuckDB analytics database
- E-commerce sample dataset
- Product sales analytics
- Revenue by region analytics
- Automatic API documentation with Swagger
- Pydantic request/response validation

## Backend Architecture

The backend follows a layered architecture:

- API layer
- Service layer
- Database layer
- SQL validation layer

The SQL execution engine only allows read-only SELECT queries
and validates SQL statements before execution.

## Security

The query engine currently provides:

- SELECT-only policy
- Multiple statement protection
- SQL syntax validation
- Query length limits
- Result row limits
- Read-only execution
- SQL parser-based validation