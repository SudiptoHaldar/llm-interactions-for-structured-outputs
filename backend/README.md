# LLM Interactions Backend

FastAPI backend for LLM interactions with structured outputs.

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL with pgvector extension
- uv package manager

### Installation

```bash
cd backend
uv sync
uv sync --all-extras  # Install dev dependencies
```

### Configuration

Copy the root `.env.sample` to `.env` and configure:

```bash
cp ../.env.sample ../.env
# Edit .env with your database credentials
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string (format: `postgresql+asyncpg://user:pass@host:port/db`)
- `WEB_HOST`: Server host (default: `0.0.0.0`)
- `WEB_PORT`: Server port (default: `8017`)

### Running

Development server:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8017
```

### Testing

```bash
uv run pytest -v
uv run pytest --cov=app tests/
```

### Linting

```bash
uv run ruff check .
uv run mypy app/
```

### API Documentation

- Swagger UI: http://localhost:8017/docs
- ReDoc: http://localhost:8017/redoc
- OpenAPI JSON: http://localhost:8017/api/v1/openapi.json

## Project Structure

```
backend/
├── app/
│   ├── main.py          # Application entry point
│   ├── config.py        # Configuration settings
│   ├── dependencies.py  # Shared dependencies
│   ├── api/v1/          # API version 1 routes
│   ├── core/            # Core utilities
│   ├── db/              # Database setup
│   ├── models/          # SQLAlchemy models
│   └── schemas/         # Pydantic schemas
└── tests/               # Test suite
```

## Adding New Features

1. Create router in `app/api/v1/{feature}.py`
2. Add Pydantic schemas in `app/schemas/{feature}.py`
3. Include router in `app/api/v1/router.py`
4. Add tests in `tests/api/test_{feature}.py`
