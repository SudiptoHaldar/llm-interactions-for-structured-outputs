# Database Package

SQL scripts and utilities for the LLM Interactions database.

## Structure

```
database/
├── executor.py           # SQL script execution utility
├── sql/
│   └── tables/
│       ├── continent_create.sql   # CREATE TABLE script
│       ├── continent_cleanup.sql  # DROP TABLE script
│       └── continent.py           # Python wrapper
└── tests/
    └── test_continent.py  # Tests
```

## Usage

### Prerequisites

Ensure `DATABASE_URL` is set in your `.env` file:

```bash
DATABASE_URL=postgresql://llm_interactions:password@localhost:5432/llm_interactions_db
```

### Creating Tables

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

**Using raw SQL:**

```bash
# Connect to PostgreSQL
psql -h localhost -U llm_interactions -d llm_interactions_db

# Run create script
\i database/sql/tables/continent_create.sql

# Run cleanup script
\i database/sql/tables/continent_cleanup.sql
```

## Continent Table Schema

| Column | Type | Description |
|--------|------|-------------|
| continent_id | SERIAL | Primary key (auto-increment) |
| name | VARCHAR(100) | Continent name (unique) |
| description | VARCHAR(250) | Brief description |
| area_sq_mile | NUMERIC(15,2) | Area in square miles |
| area_sq_km | NUMERIC(15,2) | Area in square kilometers |
| population | BIGINT | Total population |
| num_country | INTEGER | Number of countries |
| created_at | TIMESTAMPTZ | Record creation time |
| updated_at | TIMESTAMPTZ | Last update time |

## Testing

```bash
cd database
uv sync --all-extras
uv run pytest -v
```

## Adding New Tables

1. Create `{table}_create.sql` in `sql/tables/`
2. Create `{table}_cleanup.sql` in `sql/tables/`
3. Create `{table}.py` wrapper with `create_table()`, `cleanup_table()`, `exists()`
4. Add tests in `tests/test_{table}.py`
