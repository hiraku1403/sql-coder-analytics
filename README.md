# SQL-Coder & Analytics Agent

AI-powered analytics platform that transforms natural language questions into SQL queries, executes them safely against a relational analytics database, generates business insights, and recommends data visualizations.

The project combines **FastAPI, DuckDB, Gemini, SQLGlot, Pydantic and Next.js** into a complete Text-to-SQL analytics workflow.

---

## Overview

SQL-Coder & Analytics Agent allows users to interact with an e-commerce analytics database using natural language.

Instead of manually writing SQL, the user can ask questions such as:

> "Quais são os produtos mais vendidos?"

or:

> "Qual região possui o maior faturamento?"

The system processes the question through an AI-powered pipeline:

```text
Natural Language Question
          │
          ▼
    Schema Discovery
          │
          ▼
     SQL Generation
          │
          ▼
     SQL Validation
          │
          ▼
   Safe SQL Execution
          │
          ▼
   Self-Correction Loop
          │
          ▼
 Business Data Analysis
          │
          ▼
 Visualization Planning
          │
          ▼
      Final Result
```

---

## Features

### Natural Language → SQL

Users can ask analytical questions without knowing SQL.

The Gemini model generates SQL based on the database schema and the user's question.

### SQL Validation

Generated SQL is validated before execution.

The query engine enforces a read-only policy and protects the database from unsafe operations.

Current protections include:

* SELECT-only queries
* Multiple statement protection
* SQL syntax validation
* Query length limits
* Result row limits
* Read-only execution
* SQL parser-based validation

### Self-Correction

If the generated SQL fails during execution, the system sends the error back to the LLM and requests a corrected query.

The current agent supports a limited correction loop to avoid uncontrolled execution attempts.

```text
Generated SQL
     │
     ▼
  Execute
     │
 ┌───┴────┐
 │        │
Success   Error
 │        │
 ▼        ▼
Result   Correction
          │
          ▼
       New SQL
```

### Business Analysis

After obtaining the query results, the AI generates a business-oriented analysis containing:

* Summary
* Key insights
* Data interpretation

### Visualization Planning

The system analyzes the returned dataset and generates a visualization plan based on the available columns and values.

Supported chart planning includes analytical chart types such as:

* Bar charts
* Line charts
* Other compatible visualization structures

### Interactive Frontend

The project includes a modern Next.js interface with:

* Natural language query input
* Suggested questions
* Loading states
* Error handling
* KPI cards
* AI-generated analysis
* Data visualization
* Data explorer
* Generated SQL viewer
* Execution metadata
* Query history
* Responsive layout

---

# Architecture

```text
┌──────────────────────────────────────────────┐
│                  Next.js                     │
│                 Frontend                     │
│                                              │
│  Query Input → Results → Charts → Data      │
└──────────────────────┬───────────────────────┘
                       │
                       │ HTTP / REST
                       ▼
┌──────────────────────────────────────────────┐
│                  FastAPI                     │
│                   API                        │
│                                              │
│  Analytics │ Database │ Health              │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│             Analytics Services               │
│                                              │
│ SQL Generation                               │
│ SQL Validation                               │
│ Query Execution                              │
│ Self-Correction                              │
│ Analysis                                     │
│ Visualization Planning                      │
└──────────────┬───────────────────┬───────────┘
               │                   │
               ▼                   ▼
        ┌─────────────┐     ┌─────────────┐
        │   Gemini    │     │   DuckDB    │
        │     LLM     │     │  Analytics  │
        └─────────────┘     └─────────────┘
```

---

# Tech Stack

## Backend

* Python
* FastAPI
* Uvicorn
* Pydantic
* DuckDB
* SQLGlot
* Plotly
* Google Gemini API
* python-dotenv

## Frontend

* Next.js
* React
* TypeScript
* Recharts
* Tailwind CSS

## Infrastructure

* GitHub
* Render
* REST API

---

# Project Structure

```text
sql-coder-analytics/
│
├── app/
│   ├── ai/
│   │   ├── factory.py
│   │   ├── llm.py
│   │   ├── prompts.py
│   │   └── providers/
│   │       └── gemini_provider.py
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── analytics.py
│   │       ├── database.py
│   │       └── health.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   ├── models.py
│   │   └── seed.py
│   │
│   ├── schemas/
│   │   ├── ai.py
│   │   ├── analysis.py
│   │   └── chart.py
│   │
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── analysis_service.py
│   │   ├── chart_service.py
│   │   ├── query_executor.py
│   │   ├── schema_service.py
│   │   ├── sql_validator.py
│   │   └── visualization_service.py
│   │
│   └── main.py
│
├── data/
│   └── ecommerce.duckdb
│
├── frontend/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   │
│   ├── public/
│   ├── package.json
│   ├── package-lock.json
│   ├── next.config.ts
│   ├── postcss.config.mjs
│   └── ...
│
├── tests/
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── render.yaml
├── requirements.txt
└── README.md
```

---

# Database

The project uses DuckDB as the analytics database.

The included sample dataset represents an e-commerce environment containing entities such as:

* Customers
* Products
* Orders
* Order items
* Regions
* States

The seed process generates the sample data deterministically using a fixed random seed.

To recreate the database locally:

```bash
python -m app.database.seed
```

The default database location is:

```text
data/ecommerce.duckdb
```

The location can also be configured through:

```env
DATABASE_PATH=data/ecommerce.duckdb
```

---

# API

The FastAPI backend exposes the following main routes.

## Health

```http
GET /health/
```

Used to verify that the API is running.

---

## Analytics Schema

```http
GET /analytics/schema
```

Returns information about the analytics database schema.

---

## Generate SQL

```http
POST /analytics/generate-sql
```

Generates SQL from a natural language question.

Example request:

```json
{
  "question": "Quais são os produtos mais vendidos?"
}
```

---

## Execute Query

```http
POST /analytics/query
```

Executes a validated analytical SQL query.

---

## Complete Analytics Agent

```http
POST /analytics/ask
```

Runs the complete pipeline:

```text
Question
→ SQL
→ Validation
→ Execution
→ Self-Correction
→ Analysis
→ Visualization
```

Example:

```json
{
  "question": "Qual região possui o maior faturamento?"
}
```

---

## Database Schema

```http
GET /database/schema
```

Returns the database schema.

### Formatted Schema

```http
GET /database/schema/formatted
```

### Database Status

```http
GET /database/status
```

---

# API Documentation

When running locally, FastAPI automatically provides interactive documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# Local Development

## Backend

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the environment file:

```text
.env
```

Configure:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
DATABASE_PATH=data/ecommerce.duckdb
```

Initialize the database:

```bash
python -m app.database.seed
```

Start the API:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# Frontend

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Configure the API URL through the environment:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

The frontend will be available at:

```text
http://localhost:3000
```

---

# Testing

The backend includes automated tests covering important parts of the system.

Run the complete test suite:

```bash
pytest -v
```

Tests cover areas including:

* Analytics API
* Self-correction
* SQL validation
* Query execution
* Analysis generation
* Visualization
* Chart planning
* Database functionality

---

# Environment Variables

## Backend

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
DATABASE_PATH=data/ecommerce.duckdb
```

## Frontend

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Never commit real API keys or credentials to the repository.

---

# Deployment

The project is structured to be deployed as two Render Web Services:

```text
                    Render
                      │
             ┌────────┴────────┐
             │                 │
             ▼                 ▼
      sql-coder-api     sql-coder-frontend
          FastAPI              Next.js
             │                 │
             └───────┬─────────┘
                     │
                     ▼
                   User
```

The repository contains a `render.yaml` Blueprint for configuring both services.

The backend uses:

```text
Build:
pip install -r requirements.txt

Start:
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The frontend uses:

```text
Build:
npm ci && npm run build

Start:
npm start
```

The Render Blueprint also initializes the demo DuckDB database through the seed command before the backend starts.

---

# Render Environment Variables

The following values must be configured in Render.

## Backend

```text
GEMINI_API_KEY
```

The API key must be added as a secret environment variable.

## Frontend

```text
NEXT_PUBLIC_API_URL
```

Set this to the public URL of the deployed FastAPI backend.

Example:

```text
https://sql-coder-api.onrender.com
```

The exact URL depends on the service name assigned by Render.

---

# Important Deployment Note

The project currently uses DuckDB as a local analytics database.

This is ideal for:

* Portfolio demonstrations
* Prototypes
* Technical demonstrations
* Local development
* Small analytical workloads

For a production multi-user system, the database architecture should eventually be migrated to a persistent managed database such as PostgreSQL.

---

# Security Considerations

The analytics engine is designed around a read-only SQL execution model.

Current protections include:

* SELECT-only queries
* SQL parsing
* Multiple statement protection
* Query length limits
* Result size limits
* Read-only database execution
* Validation before execution

The LLM is never trusted as the final authority over database execution.

Generated SQL must pass through the application's validation and execution layers.

---

# Future Improvements

Potential future iterations include:

* PostgreSQL support
* Authentication
* User accounts
* Persistent query history
* Advanced chart generation
* Dashboard builder
* Query caching
* Streaming responses
* Better natural-language error recovery
* Multiple LLM providers
* AI-generated dashboards
* Role-based database permissions
* Production observability
* Automated CI/CD

---

# Project Status

The project currently provides a complete working prototype of an AI-powered analytics platform.

The core pipeline is implemented:

```text
Natural Language
       ↓
Schema
       ↓
Gemini
       ↓
SQL
       ↓
SQL Validation
       ↓
DuckDB
       ↓
Self-Correction
       ↓
Business Analysis
       ↓
Visualization
       ↓
Next.js Dashboard
```

---

# License

This project is intended as a technical portfolio and educational project.
