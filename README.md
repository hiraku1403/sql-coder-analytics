# SQL-Coder & Analytics Agent

**An AI-powered analytics platform that turns natural-language questions into validated SQL, executes them against an analytics database, and presents results with business insights and charts.**

[Live Demo](https://sql-coder-frontend.onrender.com/) · [API Documentation](https://sql-coder-api.onrender.com/docs) · [GitHub Repository](https://github.com/hiraku1403/sql-coder-analytics)

---

## Overview

SQL-Coder & Analytics Agent makes e-commerce data accessible to people who may not know SQL. Ask a question in plain language; the application generates a query, validates it, executes it against DuckDB, and returns the result with an AI-generated explanation and visualization when appropriate.

Example questions:
- Which products sold the most?
- Which region generated the highest revenue?
- What are the top-selling products?
- Show the products and their sales.

This project demonstrates an end-to-end full-stack workflow combining an LLM, SQL validation, database access, API design, automated tests, and a deployed web interface.

## Live application

- **Frontend:** https://sql-coder-frontend.onrender.com/
- **Backend API:** https://sql-coder-api.onrender.com/
- **Swagger UI:** https://sql-coder-api.onrender.com/docs
- **ReDoc:** https://sql-coder-api.onrender.com/redoc

> The application uses a sample e-commerce dataset. On a free hosting tier, the service may take a little while to wake up after inactivity.

## How it works

```text
Natural-language question
          |
          v
   Database schema discovery
          |
          v
      SQL generation <----> Gemini
          |
          v
      SQL validation
          |
          v
   Read-only query execution
          |
          +---- On error ----> AI-assisted correction
          |                         |
          +<------------------------+
          |
          v
      Business analysis
          |
          v
   Visualization planning
          |
          v
 Dashboard: KPIs, chart, data, SQL
```

## Features

### Natural language to SQL
- Ask analytical questions without writing SQL manually.
- Use database schema context to guide SQL generation.

### SQL validation and safer execution
- Validate generated SQL before execution.
- Restrict execution to read-only analytical queries.
- Protect against multiple statements.
- Enforce query-length and result-row limits.
- Parse SQL before it reaches the database.

These controls reduce risk but do not, by themselves, make an AI-generated query system production-ready.

### AI-assisted self-correction
When a generated query fails, the application can pass the error through a bounded correction flow and retry with corrected SQL.

### Business-oriented analysis
Receive a concise summary and key insights based on the query results.

### Data visualization
The backend prepares a visualization plan, and the frontend renders suitable results using Recharts.

### Analytics dashboard
- Suggested questions and loading/error states
- KPI cards
- AI-generated summary and insights
- Responsive chart visualization
- Tabular data explorer
- Generated SQL viewer
- Execution metadata
- Recent query history stored in the browser

## Architecture

```text
┌─────────────────────────────┐
│       Next.js Frontend      │
│  Question · KPIs · Charts   │
│  Data Explorer · SQL Viewer │
└──────────────┬──────────────┘
               │ HTTP / REST
               v
┌─────────────────────────────┐
│           FastAPI           │
│ Analytics · Database · Health│
└──────────────┬──────────────┘
               v
┌─────────────────────────────┐
│      Analytics Services     │
│ SQL generation and validation│
│ Execution and self-correction│
│ Analysis and chart planning │
└───────────┬─────────┬───────┘
            v         v
          Gemini    DuckDB
```

## Tech stack

| Area | Technologies |
|---|---|
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| AI | Google Gemini API |
| Data and SQL | DuckDB, SQLGlot |
| Frontend | Next.js, React, TypeScript |
| Charts and styling | Recharts, Tailwind CSS |
| Testing | pytest |
| Deployment | Render |
| Version control | Git, GitHub |

## Project structure

```text
sql-coder-analytics/
├── app/
│   ├── ai/
│   │   └── providers/
│   ├── api/
│   │   └── routes/
│   ├── core/
│   ├── database/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── data/
├── frontend/
│   ├── app/
│   ├── public/
│   ├── package.json
│   └── ...
├── tests/
├── .env.example
├── render.yaml
├── requirements.txt
└── README.md
```

## API endpoints

Explore the interactive API documentation at [Swagger UI](https://sql-coder-api.onrender.com/docs).

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health/` | Check API health |
| `GET` | `/analytics/schema` | Inspect the analytics schema |
| `POST` | `/analytics/generate-sql` | Generate SQL from a question |
| `POST` | `/analytics/query` | Execute a validated analytical query |
| `POST` | `/analytics/ask` | Run the complete analytics workflow |
| `GET` | `/database/schema` | Retrieve database schema information |
| `GET` | `/database/schema/formatted` | Retrieve formatted schema information |
| `GET` | `/database/status` | Check database status |

Example request to `POST /analytics/ask`:

```json
{
  "question": "Qual produto vendeu mais?"
}
```

The response includes the question, generated SQL, returned data, analysis, and visualization information when available.

## Run locally

### Requirements
- Python
- Node.js and npm
- A Google Gemini API key

### 1. Clone the repository

```bash
git clone https://github.com/hiraku1403/sql-coder-analytics.git
cd sql-coder-analytics
```

### 2. Set up the backend

Create and activate a virtual environment.

**Windows PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the repository root based on `.env.example`:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
DATABASE_PATH=data/ecommerce.duckdb
```

Keep your actual API key private. Never commit `.env` or real credentials.

Initialize the sample database:

```bash
python -m app.database.seed
```

Start the API from the repository root:

```bash
uvicorn app.main:app --reload
```

The backend is available at `http://127.0.0.1:8000`; interactive docs are at `http://127.0.0.1:8000/docs`.

### 3. Set up the frontend

Open a second terminal:

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Start the frontend:

```bash
npm run dev
```

Open `http://localhost:3000`.

> `NEXT_PUBLIC_API_URL` is embedded into the frontend at build time. Rebuild and redeploy the frontend after changing this variable in a deployment environment.

## Database

The application uses DuckDB with a sample e-commerce dataset containing customers, products, orders, order items, regions, and states.

Create or refresh the sample database:

```bash
python -m app.database.seed
```

Default database path: `data/ecommerce.duckdb`. It can be changed with the `DATABASE_PATH` environment variable.

The dataset is intended for demos, development, and portfolio evaluation. For a multi-user production workload, review persistence, concurrency, and database architecture requirements.

## Tests

Run the backend test suite from the repository root with the virtual environment activated:

```bash
pytest -v
```

Tests cover areas including analytics API behavior, SQL validation, query execution, self-correction, analysis, visualization/chart planning, and database functionality.

## Deployment on Render

The repository includes a Render Blueprint (`render.yaml`) for the backend and frontend services.

Configure these environment variables in Render:

**Backend (`sql-coder-api`)**
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
DATABASE_PATH=data/ecommerce.duckdb
ALLOWED_ORIGINS=https://sql-coder-frontend.onrender.com
```

Set `GEMINI_API_KEY` as a secret. `ALLOWED_ORIGINS` should contain the exact frontend origin, without a trailing slash. Add any additional origins as comma-separated values if needed.

**Frontend (`sql-coder-frontend`)**
```env
NEXT_PUBLIC_API_URL=https://sql-coder-api.onrender.com
```

Do not add a trailing slash to the API URL. Since the variable is embedded at build time, redeploy the frontend after changing it. The backend build process initializes the demo database using the seed command configured in `render.yaml`.

## Security notes and limitations

- SQL generated by the LLM is validated before execution; the model is not the authority for database access.
- Keep credentials in environment variables and out of version control.
- The current demo is not a substitute for a production security review.
- Query history is stored in browser local storage, not in a server-side user account.
- The sample DuckDB database is intended for a portfolio demo rather than a high-concurrency, multi-user production workload.
- Before using sensitive data, add the authentication, authorization, monitoring, privacy controls, and operational safeguards appropriate to that environment.

## Potential next steps

Possible extensions include authentication and role-based access, PostgreSQL support, persistent user-specific history, query caching, streaming responses, more chart types, observability, and CI/CD.

## Project status

The core portfolio workflow is implemented and deployed:

**Natural-language question → SQL generation → validation → execution → correction when needed → business analysis → visualization → dashboard.**

## License

This repository is a technical portfolio and educational project. No specific open-source license is declared here; add a `LICENSE` file if you intend to distribute the project under a particular license.
