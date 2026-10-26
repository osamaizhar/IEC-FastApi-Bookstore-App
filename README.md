# IEC FastAPI Bookstore App

A simple Bookstore REST API built with **FastAPI**, **SQLAlchemy** and **PostgreSQL** (Neon) for the IEC Agentic AI bootcamp.
It covers the FastAPI basics: routes, request validation with Pydantic, database access with an ORM, and dependency injection.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| FastAPI | Web framework for building the API |
| Uvicorn | ASGI server that runs the app |
| SQLAlchemy | ORM: maps Python classes to database tables |
| Pydantic | Validates request data and shapes responses |
| psycopg2-binary | PostgreSQL driver used by SQLAlchemy |
| python-dotenv | Loads secrets from the `.env` file |
| Neon | Hosted (cloud) PostgreSQL database |

---

## Project Structure

```
IEC-FastApi-Bookstore-App/
├── main.py           # FastAPI app and API endpoints (routes)
├── services.py       # Business logic: CRUD operations on the database
├── models.py         # SQLAlchemy ORM models (database tables)
├── schemas.py        # Pydantic schemas (request/response shapes)
├── db.py             # DB engine, session, Base class, get_db(), create_table()
├── requirements.txt  # Python dependencies
├── .env.example      # Template for environment variables
└── .env              # Your real secrets (NOT committed to git)
```

### How a request flows

```
Client  ->  main.py (route)  ->  services.py (logic)  ->  models.py (ORM)  ->  PostgreSQL
               |                                                               |
          schemas.py validates input                     schemas.py shapes the response
```

1. **`main.py`** receives the HTTP request. FastAPI validates the body using a schema from **`schemas.py`**.
2. **`get_db()`** in **`db.py`** opens a database session for that request and closes it afterwards.
3. **`services.py`** does the actual database work using the **`Book`** model from **`models.py`**.
4. The result is converted to JSON using the response schema and sent back.

---

## Setup

### 1. Clone and enter the project
```bash
git clone <repo-url>
cd IEC-FastApi-Bookstore-App
```

### 2. Install dependencies

#### Option A: uv (recommended)
[uv](https://docs.astral.sh/uv/) is a fast Python package and project manager (10–100x faster than pip). It creates the virtual environment and installs packages in one tool.

**Install uv (once per machine):**
```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Create the virtual environment and install dependencies:**
```bash
uv venv
uv pip install -r requirements.txt
```
No activation needed if you use `uv run` (step 4). It runs commands inside `.venv` automatically.

#### Option B: pip
```powershell
# Windows (PowerShell)
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure the database URL
Copy `.env.example` to `.env` and add your Neon connection string:
```
SQLALCHEMY_DATABASE_URL=postgresql+psycopg2://<user>:<password>@<host>/<dbname>?sslmode=require
```
> Note the `+psycopg2` in the URL. It tells SQLAlchemy which driver to use (see [Common Issues](#common-issues-and-fixes)).
> **Never** commit `.env` or share your real password.

### 4. Run the app
```bash
# with uv (no activation needed)
uv run uvicorn main:app --reload

# with pip (venv activated)
uvicorn main:app --reload
```
The `Books` table is created automatically on startup (if it doesn't exist).

Open the interactive API docs: **http://127.0.0.1:8000/docs**

---

## API Endpoints

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/books/` | List all books | — |
| GET | `/books/{id}` | Get one book by id | — |
| POST | `/books/` | Create a book | `BookCreate` |
| PUT | `/books/{id}` | Update a book | `BookCreate` |
| DELETE | `/books/{id}` | Delete a book | — |

Missing ids return **404 Not Found**.

### Example request body (`BookCreate`)
```json
{
  "title": "Sherlock Holmes",
  "description": "Detective stories",
  "author": "Arthur Conan Doyle",
  "year": 1892
}
```

### Example response (`Book`)
```json
{
  "id": 1,
  "title": "Sherlock Holmes",
  "description": "Detective stories",
  "author": "Arthur Conan Doyle",
  "year": 1892
}
```

---

## Common Issues and Fixes

### 1. `ImportError: no pq wrapper available`
**Cause:** The URL starts with a bare `postgresql://`. In SQLAlchemy 2.1+ that defaults to the **psycopg 3** driver, but we installed **psycopg2-binary**.
**Fix:** Name the driver in `.env`:
```
postgresql+psycopg2://...
```
(Alternative: `pip install "psycopg[binary]"` and use `postgresql+psycopg://...`.)

### 2. `relation "Books" does not exist`
**Cause:** `create_table()` (`Base.metadata.create_all()`) only creates tables for models that have been **imported**. Running `python db.py` alone never imports `models.py`, so no tables are created, even if it prints "Tables created".
**Fix:** Import the models before calling `create_table()`. This is done in `main.py`:
```python
import models  # registers Book on Base
create_table()
```

### 3. `FastAPIError: Response not awaited`
**Cause:** A dependency with `yield` (like `get_db()`) has an `except Exception` block that catches the error but **does not re-raise it**. FastAPI loses the real error.
**Fix:** Don't swallow exceptions in dependencies. Either remove the `except` block (the `finally` still closes the session) or add `raise` after logging.

### 4. `[WinError 10013] An attempt was made to access a socket in a way forbidden`
**Cause:** Port 8000 is already in use, or reserved by Windows (Hyper-V / WSL / Docker).
**Fix:** Use another port:
```bash
uvicorn main:app --reload --port 8080
```
To check what is using the port: `netstat -ano | findstr :8000`

### 5. `Activate.ps1 cannot be loaded because running scripts is disabled`
**Cause:** PowerShell's execution policy blocks scripts.
**Fix:** Allow scripts for the current session only:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### 6. `ArgumentError: Expected string or URL object, got None`
**Cause:** `SQLALCHEMY_DATABASE_URL` is not set. The `.env` file is missing, misnamed, or the app is started from a different folder.
**Fix:** Make sure `.env` exists in the project root and run `uvicorn` from that folder.

### 7. `ModuleNotFoundError` (e.g. `No module named 'fastapi'`)
**Cause:** The virtual environment is not activated, so the global Python is used.
**Fix:** Activate `.venv` (see Setup step 2), then `pip install -r requirements.txt`. With uv, use `uv run ...` so the right environment is always used.

### 8. `307 Temporary Redirect`
**Cause:** Routes are defined as `/books/` (with a trailing slash) and you called `/books`. FastAPI redirects to the slash version.
**Fix:** Call the exact path shown in `/docs`, and keep one style for all routes.

### 9. Columns missing from the table / `Mapper could not assemble any primary key columns`
**Cause:** Model fields written as type hints (`id: Column(...)`) instead of assignments.
**Fix:** Use `=`:
```python
id = Column(Integer, primary_key=True, index=True)
```

### 10. Changed a model but the table didn't update
**Cause:** `create_all()` only creates **missing** tables. It never alters existing ones.
**Fix:** For learning: drop the table in Neon and restart the app. For real projects: use **Alembic** migrations.

---

## How a Best-Practices Project Would Differ

This project is intentionally simple for learning. A production project would usually change these things:

| Area | This project | Best practice |
|------|-------------|---------------|
| **Folder structure** | All files in the root | Package layout: `app/api/routes/`, `app/models/`, `app/schemas/`, `app/services/`, `app/core/config.py` |
| **Configuration** | `os.getenv()` + `load_dotenv()` | `pydantic-settings` `BaseSettings` class: typed, validated, fails fast if a variable is missing |
| **Creating tables** | `create_all()` on startup | **Alembic** migrations: versioned schema changes, safe upgrades/rollbacks |
| **Startup logic** | Runs at import time in `main.py` | FastAPI `lifespan` handler |
| **Sync vs async** | `async def` routes calling a sync DB session (blocks the event loop) | Plain `def` routes with a sync session, **or** a fully async stack (`create_async_engine` + `AsyncSession` + `asyncpg`/`psycopg`) |
| **Pydantic config** | `class config: orm_mode = True` (v1 style) | `model_config = ConfigDict(from_attributes=True)` (v2) |
| **SQLAlchemy style** | `Column(...)`, `db.query(...)` (legacy 1.x style) | `Mapped[int] = mapped_column(...)` and `db.execute(select(Book))` (2.0 style, type-safe) |
| **Error handling** | No rollback on failed commits | `try/except` with `db.rollback()`, custom exception handlers |
| **Updates** | `PUT` replaces all fields | Also a `PATCH` endpoint with a `BookUpdate` schema (optional fields) for partial updates |
| **Listing data** | Returns every row | Pagination (`skip`/`limit`) and filtering |
| **Validation** | Basic types only | Field constraints, e.g. `Field(min_length=1, max_length=200)`, `year: int = Field(ge=0, le=2100)` |
| **Dependencies** | Unpinned `requirements.txt` (`fastapi`) | uv project: `pyproject.toml` + `uv.lock` for exact, reproducible installs (`uv init`, `uv add fastapi`, `uv sync`) |
| **Table names** | `"Books"` (capitalized) | `"books"`: lowercase avoids quoting issues in PostgreSQL |
| **Logging** | `print()` | `logging` module with levels and structured logs |
| **Testing** | None | `pytest` + FastAPI `TestClient` with a separate test database |
| **Security** | Open API | Authentication (JWT/OAuth2), CORS settings, rate limiting |
| **Deployment** | `uvicorn --reload` locally | Docker image, CI/CD pipeline, `uvicorn`/`gunicorn` workers without `--reload` |
| **Code quality** | Manual | `ruff` (lint + format), `mypy` (type checking), pre-commit hooks |

> Start simple, then add these as the project grows. Each one solves a real problem you'll hit at scale.
