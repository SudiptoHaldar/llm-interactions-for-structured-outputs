# LLM Interactions - Operations Runbook

This document contains operational procedures for the LLM Interactions project.

---

## 1. Backend Setup

### 1.1 Prerequisites

- Python 3.11+
- PostgreSQL with pgvector extension
- uv package manager (https://docs.astral.sh/uv/)

### 1.2 Environment Configuration

1. Copy the environment template:
   ```bash
   cp .env.sample .env
   ```

2. Configure required environment variables in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/llm_interactions_db
   WEB_HOST=0.0.0.0
   WEB_PORT=8017
   LOG_LEVEL=INFO
   DEBUG_MODE=false
   ```

### 1.3 Install Dependencies

```bash
cd backend
uv sync                  # Production dependencies
uv sync --all-extras     # Include dev dependencies
```

### 1.4 Running the Development Server

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8017
```

**Verify the server is running:**
- Root endpoint: http://localhost:8017/
- Health check: http://localhost:8017/api/v1/health
- Liveness probe: http://localhost:8017/api/v1/health/live
- Swagger UI: http://localhost:8017/docs
- ReDoc: http://localhost:8017/redoc

---

## 2. Testing

### 2.1 Running Tests

```bash
cd backend
uv run pytest -v                    # Run all tests
uv run pytest --cov=app tests/      # Run with coverage
```

### 2.2 Linting

```bash
cd backend
uv run ruff check .                 # Check for linting issues
uv run ruff check . --fix           # Auto-fix issues
uv run mypy app/                    # Type checking
```

---

## 3. Troubleshooting

### 3.1 Database Connection Issues

**Symptom**: Health check returns `database: disconnected`

**Solutions**:
1. Verify PostgreSQL is running
2. Check DATABASE_URL format: `postgresql://user:pass@host:port/db`
3. Ensure database exists and user has permissions
4. Check firewall/network connectivity

### 3.2 Module Not Found Errors

**Symptom**: `ModuleNotFoundError: No module named 'app'`

**Solutions**:
1. Ensure you're running commands from the `backend/` directory
2. Run `uv sync` to install dependencies
3. Check `pyproject.toml` has `pythonpath = ["."]` in pytest config

### 3.3 Pydantic Validation Errors

**Symptom**: `Extra inputs are not permitted` errors on startup

**Solution**: The config.py should have `extra="ignore"` in SettingsConfigDict

---

## 4. API Endpoints

### 4.1 System Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint with welcome message |
| `/api/v1/health` | GET | Full health check with DB status |
| `/api/v1/health/live` | GET | Liveness probe for Kubernetes |
| `/docs` | GET | Swagger UI documentation |
| `/redoc` | GET | ReDoc documentation |
| `/api/v1/openapi.json` | GET | OpenAPI specification |

### 4.2 Continents Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/continents` | GET | List all continents |
| `/api/v1/continents/{continent_id}` | GET | Get continent by ID |
| `/api/v1/continents/name/{continent_name}` | GET | Get continent by name (case-insensitive) |

**Example Response (GET /api/v1/continents):**
```json
{
  "continents": [
    {
      "continent_id": 1,
      "continent_name": "Africa",
      "description": "Second largest continent by area and population",
      "area_sq_mile": 11668599.0,
      "area_sq_km": 30221532.0,
      "population": 1400000000,
      "num_country": 54,
      "ai_model_id": 1,
      "created_at": "2026-01-03T10:00:00Z",
      "updated_at": "2026-01-03T10:00:00Z"
    }
  ],
  "count": 1
}
```

### 4.3 AI Models Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/ai-models` | GET | List all AI models |
| `/api/v1/ai-models/{ai_model_id}` | GET | Get AI model by ID |

**Example Response (GET /api/v1/ai-models):**
```json
{
  "ai_models": [
    {
      "ai_model_id": 1,
      "model_provider": "OpenAI",
      "model_name": "gpt-4o",
      "description": null,
      "supports_structured_output": true,
      "is_active": true,
      "created_at": "2026-01-03T10:00:00Z",
      "updated_at": "2026-01-03T10:00:00Z"
    }
  ],
  "count": 1
}
```

---

## 5. Database Package

### 5.1 Installation

```bash
cd database
uv sync                  # Production dependencies
uv sync --all-extras     # Include dev dependencies
```

### 5.2 Creating Tables

**Using Python:**

```python
from database.sql.tables.continent import create_table, cleanup_table, exists

# Create the continents table
create_table()

# Check if table exists
print(f"Table exists: {exists()}")

# Drop the table (WARNING: deletes all data!)
cleanup_table()
```

**Using CLI:**

```bash
# Create table
python -m database.sql.tables.continent create

# Check if exists
python -m database.sql.tables.continent exists

# Cleanup (drop table)
python -m database.sql.tables.continent cleanup
```

**Using raw SQL (requires psql):**

```bash
# Connect to PostgreSQL
psql -h localhost -U llm_interactions -d llm_interactions_db

# Run create script
\i database/sql/tables/continent_create.sql

# Run cleanup script
\i database/sql/tables/continent_cleanup.sql
```

### 5.3 Running Database Tests

```bash
cd database
uv run pytest -v              # Run tests
uv run ruff check .           # Linting
```

### 5.4 AI Models Table

The `ai_models` table stores information about AI/LLM model providers and their models for structured output interactions.

**Using CLI:**

```bash
# Create ai_models table
python -m database.sql.tables.ai_model create

# Check if exists
python -m database.sql.tables.ai_model exists

# Cleanup (drop table)
python -m database.sql.tables.ai_model cleanup
```

**Using Python:**

```python
from database.sql.tables.ai_model import create_table, cleanup_table, exists

# Create the ai_models table
create_table()

# Check if table exists
print(f"Table exists: {exists()}")

# Drop the table (WARNING: deletes all data!)
cleanup_table()
```

**Table Schema:**

| Column | Type | Description |
|--------|------|-------------|
| ai_model_id | INTEGER IDENTITY | Primary key |
| model_provider | VARCHAR(50) | Provider name (e.g., OpenAI, Anthropic) |
| model_name | VARCHAR(100) | Model identifier (e.g., gpt-4o, claude-3-opus) |
| description | VARCHAR(250) | Brief description |
| supports_structured_output | BOOLEAN | Structured output support flag |
| is_active | BOOLEAN | Active status flag |
| created_at | TIMESTAMPTZ | Record creation time |
| updated_at | TIMESTAMPTZ | Last update time |

### 5.5 Database Migrations

#### Fresh Database Setup

For a fresh database, create tables in the correct order (foreign key dependencies):

```bash
# From project root

# 1. Create ai_models table first (referenced by FK)
python -m database.sql.tables.ai_model create

# 2. Create continents table (has FK to ai_models)
python -m database.sql.tables.continent create
```

#### Migrating Existing Databases

If you have an existing `continents` table without the `ai_model_id` column:

```bash
# From project root

# 1. Ensure ai_models table exists
python -m database.sql.tables.ai_model create

# 2. Apply the alter migration to add ai_model_id FK
python -m database.sql.tables.continent alter

# 3. Verify the column was added
psql -h localhost -U llm_interactions -d llm_interactions_db -c "\d continents"
```

#### Rolling Back Migrations

To remove the `ai_model_id` column (WARNING: data loss!):

```bash
python -m database.sql.tables.continent rollback
```

**Using Python:**

```python
from database.sql.tables.continent import alter_table, rollback_alter

# Apply migration
alter_table()

# Rollback (WARNING: removes ai_model_id data!)
rollback_alter()
```

---

## 6. Process Structured Output Package

The `process_structured_output` package provides CLI tools for retrieving structured data from LLM providers and storing it in the database.

### 6.1 Installation

```bash
cd process_structured_output
uv sync                  # Production dependencies
uv sync --all-extras     # Include dev dependencies
```

### 6.2 Configuration

Ensure these environment variables are set in `.env`:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/llm_interactions_db
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### 6.3 Using the CLI

**Get continent information:**

```bash
# Using OpenAI (default)
uv run continent-info Africa

# Using Google Gemini
uv run continent-info Africa --provider google

# Using module directly
python -m process_structured_output.cli "North America"

# Using module with Google provider
python -m process_structured_output.cli "North America" --provider google

# Skip continent name validation
python -m process_structured_output.cli "Atlantis" --skip-validation --provider google
```

**Note for Windows users:** Use `uv run continent-info` instead of just `continent-info`, or use the module directly with `python -m process_structured_output.cli`.

**Expected output:**

```
=== Processing: Africa ===

Q1: Getting model identity...
    Model Provider: OpenAI
    Model Name: gpt-4o

Q1 Action: Upserting ai_model...
✓ Upserted ai_model: OpenAI/gpt-4o (id=1)

Q2: Getting continent info for Africa...
    Description: Africa is the second-largest continent...
    Area (sq mi): 11,668,599.00
    Area (sq km): 30,221,532.00
    Population: 1,400,000,000
    Countries: 54

Q2 Action: Upserting continent Africa...
✓ Upserted continent: Africa (id=1)

=== Complete ===
    ai_model_id: 1
    continent_id: 1
```

### 6.4 Running Tests

```bash
cd process_structured_output
uv run pytest -v              # Run tests
uv run ruff check .           # Linting
uv run mypy src/              # Type checking
```

### 6.5 Valid Continents

The CLI accepts these continent names:
- Africa
- Antarctica
- Asia
- Europe
- North America
- Oceania
- South America

### 6.6 Prerequisites

Before running the CLI, ensure:
1. Database tables exist (see Section 5.5)
2. `OPENAI_API_KEY` is set in `.env` (for OpenAI provider)
3. `GOOGLE_API_KEY` is set in `.env` (for Google Gemini provider)
4. `DATABASE_URL` is correctly configured

---

## 7. Utilities Package

The `utilities` package provides helper functions for querying information about countries, continents, and LLM providers covered by the project.

### 7.1 Installation

```bash
cd utilities
uv sync                  # Production dependencies
uv sync --all-extras     # Include dev dependencies
```

### 7.2 Using the Countries Info Module

**Using Python:**

```python
from utilities.countries_info import (
    get_continents,
    get_llms,
    get_all_countries,
    get_countries_by_continent,
    get_countries_by_llm,
    get_country_info,
)

# Get all continents
continents = get_continents()
print(continents)  # ['Africa', 'Antarctica', 'Asia', ...]

# Get all LLM providers
llms = get_llms()
print(llms)  # ['AI21', 'Anthropic', 'Cohere', ...]

# Get all countries
countries = get_all_countries()
print(f"Total countries: {len(countries)}")

# Get countries in a continent
african_countries = get_countries_by_continent("Africa")
print(african_countries)

# Get countries assigned to an LLM
openai_countries = get_countries_by_llm("OpenAI")
print(openai_countries)

# Get info about a specific country
info = get_country_info("Nigeria")
print(f"Nigeria: {info.continent}, {info.llm}")
```

**Using CLI:**

```bash
# From project root

# Display all continents and LLM providers summary
python -m utilities.countries_info

# Query a specific country
python -m utilities.countries_info Nigeria
```

**Expected output:**

```
=== Countries Info Utility ===

Continents:
  - Africa: 16 countries
  - Antarctica: 0 countries
  - Asia: 16 countries
  - Europe: 16 countries
  - North America: 16 countries
  - Oceania: 8 countries
  - South America: 8 countries

LLM Providers:
  - AI21: 10 countries
  - Anthropic: 10 countries
  - Cohere: 10 countries
  - DeepSeek: 10 countries
  - Google: 10 countries
  - Groq: 10 countries
  - Mistral: 10 countries
  - OpenAI: 10 countries

Total Countries: 80

Nigeria: Continent=Africa, LLM=AI21
```

### 7.3 API Reference

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `get_continents()` | None | `list[str]` | Sorted list of all continents |
| `get_llms()` | None | `list[str]` | List of all 8 LLM providers |
| `get_all_countries()` | None | `list[str]` | Sorted list of all countries |
| `get_countries_by_continent()` | `continent_name: str` | `list[str]` | Countries in continent |
| `get_countries_by_llm()` | `llm_name: str` | `list[str]` | Countries for LLM |
| `get_country_info()` | `country_name: str` | `CountryInfo` | Country's continent & LLM |
| `reload_data()` | None | `None` | Force reload from CSV |

### 7.4 Running Tests

```bash
cd utilities
uv run pytest -v              # Run tests
uv run ruff check .           # Linting
uv run mypy .                 # Type checking
```

---

## 8. Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.8.0 | 2026-01-03 | Utilities package with countries_info module |
| 0.7.0 | 2026-01-03 | API endpoints for continents and AI models |
| 0.6.0 | 2026-01-03 | Added Google Gemini provider with --provider CLI flag |
| 0.5.0 | 2026-01-03 | Process Structured Output package with OpenAI CLI |
| 0.4.0 | 2026-01-03 | Continents table migration - added ai_model_id FK |
| 0.3.0 | 2026-01-03 | AI Models table for structured outputs |
| 0.2.0 | 2026-01-02 | Database package with continents table |
| 0.1.0 | 2026-01-02 | Initial FastAPI backend setup |
