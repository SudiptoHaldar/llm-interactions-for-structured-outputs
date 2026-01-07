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

### 4.4 Countries Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/countries` | GET | List all countries |
| `/api/v1/countries/{country_id}` | GET | Get country by ID |
| `/api/v1/countries/name/{country_name}` | GET | Get country by name (case-insensitive) |
| `/api/v1/countries/continent/{continent_id}` | GET | Get countries by continent ID |
| `/api/v1/countries/continent/name/{continent_name}` | GET | Get countries by continent name |
| `/api/v1/countries/model/{model_id}` | GET | Get countries by AI model ID |

**Example Response (GET /api/v1/countries):**
```json
{
  "countries": [
    {
      "country_id": 1,
      "name": "Spain",
      "description": "European country known for diverse landscapes",
      "interesting_fact": "Home to world's oldest restaurant",
      "area_sq_mile": 195000.0,
      "area_sq_km": 506000.0,
      "population": 47400000,
      "ppp": 47210.0,
      "life_expectancy": 82.1,
      "travel_risk_level": "Level 1",
      "global_peace_index_score": 1.54,
      "global_peace_index_rank": 23,
      "happiness_index_score": 6.93,
      "happiness_index_rank": 29,
      "gdp": 1400000000000.0,
      "gdp_growth_rate": 2.5,
      "inflation_rate": 3.2,
      "unemployment_rate": 12.5,
      "govt_debt": 118.0,
      "credit_rating": "A",
      "poverty_rate": 20.0,
      "gini_coefficient": 34.7,
      "military_spending": 1.2,
      "continent_id": 1,
      "ai_model_id": 1,
      "created_at": "2026-01-06T10:00:00Z",
      "updated_at": "2026-01-06T10:00:00Z"
    }
  ],
  "count": 1
}
```

### 4.5 Cities Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/cities` | GET | List all cities |
| `/api/v1/cities/{city_id}` | GET | Get city by ID |
| `/api/v1/cities/name/{city_name}` | GET | Get city by name (case-insensitive) |
| `/api/v1/cities/country/{country_id}` | GET | Get cities by country ID |
| `/api/v1/cities/country/name/{country_name}` | GET | Get cities by country name |

**Example Response (GET /api/v1/cities):**
```json
{
  "cities": [
    {
      "city_id": 1,
      "country_id": 1,
      "name": "Madrid",
      "is_capital": true,
      "description": "Capital and largest city of Spain",
      "interesting_fact": "Home to the world-famous Prado Museum",
      "area_sq_mile": 233.3,
      "area_sq_km": 604.3,
      "population": 3200000,
      "sci_score": 82.4,
      "sci_rank": 23,
      "numbeo_si": 86.8,
      "numbeo_ci": 27.2,
      "airport_code": "MAD",
      "created_at": "2026-01-06T15:00:00Z",
      "updated_at": "2026-01-06T15:00:00Z"
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

# 3. Create countries table (has FK to ai_models)
python -m database.sql.tables.country create

# 4. Create cities table (has FK to countries)
python -m database.sql.tables.city create
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

### 5.6 Countries Table

The `countries` table stores comprehensive country information including economic indicators, quality of life metrics, and geopolitical data.

**Using CLI:**

```bash
# Create countries table
python -m database.sql.tables.country create

# Check if exists
python -m database.sql.tables.country exists

# Add continent_id FK (for existing tables)
python -m database.sql.tables.country alter

# Rollback continent_id FK (WARNING: data loss!)
python -m database.sql.tables.country rollback

# Cleanup (drop table)
python -m database.sql.tables.country cleanup
```

**Using Python:**

```python
from database.sql.tables.country import (
    create_table, cleanup_table, exists, alter_table, rollback_alter
)

# Create the countries table
create_table()

# Check if table exists
print(f"Table exists: {exists()}")

# Add continent_id FK (for existing tables)
alter_table()

# Rollback continent_id FK (WARNING: data loss!)
rollback_alter()

# Drop the table (WARNING: deletes all data!)
cleanup_table()
```

**Table Schema:**

| Column | Type | Description |
|--------|------|-------------|
| country_id | INTEGER IDENTITY | Primary key |
| ai_model_id | INTEGER (FK) | Reference to ai_models |
| continent_id | INTEGER (FK) | Reference to continents |
| name | VARCHAR(100) | Country name (unique) |
| description | VARCHAR(250) | Brief description |
| interesting_fact | VARCHAR(250) | Notable fact |
| area_sq_mile | NUMERIC(15,2) | Area in square miles |
| area_sq_km | NUMERIC(15,2) | Area in sq km |
| population | BIGINT | Total population |
| ppp | NUMERIC(15,2) | Purchasing power parity ($) |
| life_expectancy | NUMERIC(5,2) | Life expectancy (years) |
| travel_risk_level | VARCHAR(50) | US travel advisory |
| global_peace_index_score | NUMERIC(5,3) | GPI score (IEP) |
| global_peace_index_rank | INTEGER | GPI rank |
| happiness_index_score | NUMERIC(5,3) | Happiness score |
| happiness_index_rank | INTEGER | Happiness rank |
| gdp | NUMERIC(18,2) | GDP in USD |
| gdp_growth_rate | NUMERIC(6,2) | GDP growth (%) |
| inflation_rate | NUMERIC(6,2) | Inflation (%) |
| unemployment_rate | NUMERIC(5,2) | Unemployment (%) |
| govt_debt | NUMERIC(6,2) | Govt debt (% GDP) |
| credit_rating | VARCHAR(10) | S&P rating |
| poverty_rate | NUMERIC(5,2) | Poverty (%) |
| gini_coefficient | NUMERIC(5,2) | Gini coefficient |
| military_spending | NUMERIC(5,2) | Military (% GDP) |
| created_at | TIMESTAMPTZ | Creation time |
| updated_at | TIMESTAMPTZ | Update time |

### 5.7 Cities Table

The `cities` table stores city information including safety indices, population data, and airport codes.

**Using CLI:**

```bash
# Create cities table
python -m database.sql.tables.city create

# Check if exists
python -m database.sql.tables.city exists

# Cleanup (drop table)
python -m database.sql.tables.city cleanup
```

**Using Python:**

```python
from database.sql.tables.city import create_table, cleanup_table, exists

# Create the cities table
create_table()

# Check if table exists
print(f"Table exists: {exists()}")

# Drop the table (WARNING: deletes all data!)
cleanup_table()
```

**Table Schema:**

| Column | Type | Description |
|--------|------|-------------|
| city_id | INTEGER IDENTITY | Primary key |
| country_id | INTEGER (FK) | Reference to countries |
| name | VARCHAR(100) | City name |
| is_capital | BOOLEAN | Capital city flag |
| description | VARCHAR(250) | Brief description |
| interesting_fact | VARCHAR(250) | Notable fact |
| area_sq_mile | NUMERIC(15,2) | Area in square miles |
| area_sq_km | NUMERIC(15,2) | Area in sq km |
| population | BIGINT | Total population |
| sci_score | NUMERIC(5,2) | EIU Safe Cities Index score |
| sci_rank | INTEGER | EIU Safe Cities Index rank |
| numbeo_si | NUMERIC(5,2) | Numbeo Safety Index |
| numbeo_ci | NUMERIC(5,2) | Numbeo Crime Index |
| airport_code | CHAR(3) | IATA airport code |
| created_at | TIMESTAMPTZ | Creation time |
| updated_at | TIMESTAMPTZ | Update time |

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
AI21_API_KEY=your_ai21_api_key_here
CO_API_KEY=your_cohere_api_key_here
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

### 6.4 Get Country Information (AI21 / Anthropic / Cohere / DeepSeek / Google / Groq / Mistral / OpenAI)

The `country-info` CLI retrieves comprehensive country and city data using supported LLM providers.

**Supported Providers:**
- `ai21` - AI21 Jamba model (default)
- `anthropic` - Anthropic Claude model (uses tool use for structured output)
- `cohere` - Cohere Command R+ model (uses JSON schema for structured output)
- `deepseek` - DeepSeek-V3 model (uses OpenAI-compatible API with JSON mode)
- `google` - Google Gemini model (uses response_mime_type with schema)
- `groq` - Groq Llama model (uses JSON mode, very fast inference)
- `mistral` - Mistral Large model (uses JSON mode)
- `openai` - OpenAI GPT-4o model (uses JSON mode)

**Usage:**

```bash
# Using AI21 (default)
uv run country-info Nigeria

# Using Anthropic
uv run country-info Brazil --provider anthropic

# Using Cohere
uv run country-info Germany --provider cohere

# Using DeepSeek
uv run country-info Poland --provider deepseek

# Using Google
uv run country-info Kenya --provider google

# Using Groq
uv run country-info Ghana --provider groq

# Using Mistral
uv run country-info Algeria --provider mistral

# Using OpenAI
uv run country-info France --provider openai

# Skip city retrieval
uv run country-info "United States" --skip-cities
uv run country-info Canada --provider anthropic --skip-cities
uv run country-info Japan --provider cohere --skip-cities
uv run country-info "South Korea" --provider deepseek --skip-cities
uv run country-info Ireland --provider google --skip-cities
uv run country-info Morocco --provider openai --skip-cities

# Using module directly
python -m process_structured_output.cli_country Nigeria
python -m process_structured_output.cli_country Brazil --provider anthropic
python -m process_structured_output.cli_country Germany --provider cohere
python -m process_structured_output.cli_country Poland --provider deepseek
python -m process_structured_output.cli_country Kenya --provider google
python -m process_structured_output.cli_country Ghana --provider groq
python -m process_structured_output.cli_country Algeria --provider mistral
python -m process_structured_output.cli_country France --provider openai
```

**Anthropic Countries (10):**
Brazil, Canada, Denmark, Egypt, India, Italy, Nicaragua, Papua New Guinea, Singapore, Tanzania

**Cohere Countries (10):**
Bahamas, Chile, Germany, Japan, Mexico, New Zealand, Pakistan, South Africa, Sudan, Switzerland

**DeepSeek Countries (10):**
Bangladesh, Colombia, Costa Rica, Cuba, Ethiopia, Fiji, Hungary, Poland, South Korea, Uganda

**Google Countries (10):**
Kenya, Mozambique, Indonesia, Iran, Vanuatu, Malta, Ireland, Dominica, Trinidad and Tobago, Peru

**Groq Countries (10):**
Estonia, Ghana, Haiti, Israel, Kiribati, Madagascar, Saint Lucia, United Kingdom, Uruguay, Vietnam

**Mistral Countries (10):**
Algeria, Barbados, Belgium, Cote d'Ivoire, Jamaica, Portugal, Saudi Arabia, Suriname, Thailand, Tonga

**OpenAI Countries (10):**
Azerbaijan, Cameroon, Ecuador, Finland, France, Grenada, Guatemala, Morocco, Nauru, Philippines

**Note for Windows users:** Use `uv run country-info` instead of just `country-info`, or use the module directly.

**Expected output:**

```
=== Processing: Nigeria ===

Continent lookup: Nigeria -> Africa

Q1: Getting model identity...
    Model Provider: AI21
    Model Name: jamba-1.5-mini

Q1 Action: Upserting ai_model...
✓ Upserted ai_model: AI21/jamba-1.5-mini (id=2)
    Continent ID: 1 (Africa)

Q2: Getting country info for Nigeria...
    Description: West African nation known for...
    Area (sq mi): 356,669.00
    Area (sq km): 923,768.00
    Population: 220,000,000
    GDP: $450,000,000,000
    Life Expectancy: 55.0 years

Q2 Action: Upserting country Nigeria...
✓ Upserted country: Nigeria (id=1)

Q3: Getting cities info for Nigeria...
    Retrieved 5 cities
    - Lagos: pop 15,000,000
    - Kano: pop 4,000,000
    - Ibadan: pop 3,500,000
    - Abuja (capital): pop 3,200,000
    - Port Harcourt: pop 2,800,000

Q3 Action: Upserting 5 cities...
✓ Upserted city: Lagos (id=1)
✓ Upserted city: Kano (id=2)
✓ Upserted city: Ibadan (id=3)
✓ Upserted city: Abuja (id=4)
✓ Upserted city: Port Harcourt (id=5)

=== Complete ===
    ai_model_id: 2
    continent_id: 1
    country_id: 1
    city_ids: [1, 2, 3, 4, 5]
```

**Country data retrieved (21 fields):**
- Basic: description, interesting_fact, area (sq mi/km), population
- Economy: GDP, GDP growth rate, inflation rate, unemployment rate, PPP
- Finance: government debt (% GDP), S&P credit rating
- Social: life expectancy, poverty rate, Gini coefficient
- Safety: travel risk level, Global Peace Index (score/rank), Happiness Index (score/rank)
- Military: military spending (% GDP)

**City data retrieved (13 fields):**
- Basic: name, is_capital, description, interesting_fact, area (sq mi/km), population
- Safety indices: EIU Safe Cities Index (score/rank), Numbeo Safety Index, Numbeo Crime Index
- Travel: IATA airport code

### 6.5 Batch Country Processing

#### 6.5.1 AI21 Batch Processing

The `all-countries-ai21` CLI processes all 10 countries assigned to AI21 in a single command.

**Usage:**

```bash
cd process_structured_output
uv run all-countries-ai21
uv run all-countries-ai21 --skip-cities
uv run all-countries-ai21 --dry-run

# Using module directly
python -m process_structured_output.cli_all_countries_ai21
```

**AI21 Countries (10):**
Angola, Argentina, Australia, China, Croatia, Malaysia, Nigeria, Panama, Spain, United States

#### 6.5.2 Anthropic Batch Processing

The `all-countries-anthropic` CLI processes all 10 countries assigned to Anthropic in a single command.

**Usage:**

```bash
cd process_structured_output
uv run all-countries-anthropic
uv run all-countries-anthropic --skip-cities
uv run all-countries-anthropic --dry-run

# Using module directly
python -m process_structured_output.cli_all_countries_anthropic
```

**Anthropic Countries (10):**
Brazil, Canada, Denmark, Egypt, India, Italy, Nicaragua, Papua New Guinea, Singapore, Tanzania

#### 6.5.3 Cohere Batch Processing

The `all-countries-cohere` CLI processes all 10 countries assigned to Cohere in a single command.

**Usage:**

```bash
cd process_structured_output
uv run all-countries-cohere
uv run all-countries-cohere --skip-cities
uv run all-countries-cohere --dry-run

# Using module directly
python -m process_structured_output.cli_all_countries_cohere
```

**Cohere Countries (10):**
South Africa, Sudan, Japan, Pakistan, New Zealand, Germany, Switzerland, Mexico, Bahamas, Chile

#### 6.5.4 DeepSeek Batch Processing

The `all-countries-deepseek` CLI processes all 10 countries assigned to DeepSeek in a single command.

**Usage:**

```bash
cd process_structured_output
uv run all-countries-deepseek
uv run all-countries-deepseek --skip-cities
uv run all-countries-deepseek --dry-run

# Using module directly
python -m process_structured_output.cli_all_countries_deepseek
```

**DeepSeek Countries (10):**
Bangladesh, Colombia, Costa Rica, Cuba, Ethiopia, Fiji, Hungary, Poland, South Korea, Uganda

#### 6.5.5 Google Batch Processing

The `all-countries-google` CLI processes all 10 countries assigned to Google in a single command.

**Usage:**

```bash
cd process_structured_output
uv run all-countries-google
uv run all-countries-google --skip-cities
uv run all-countries-google --dry-run

# Using module directly
python -m process_structured_output.cli_all_countries_google
```

**Google Countries (10):**
Kenya, Mozambique, Indonesia, Iran, Vanuatu, Malta, Ireland, Dominica, Trinidad and Tobago, Peru

**Expected output (all batch CLIs):**

```
=== Processing 10 [Provider] Countries ===

Countries to process:
  1. [Country 1]
  2. [Country 2]
  ...
  10. [Country 10]

==================================================

[1/10] Processing: [Country 1]
----------------------------------------
[OK] [Country 1] completed successfully

... (more countries) ...

==================================================

=== BATCH PROCESSING COMPLETE ===

Total countries: 10
Successful: 10
Failed: 0
Elapsed time: 120.5 seconds
Average per country: 12.0 seconds
```

#### 6.5.6 Groq Batch Processing

The `all-countries-groq` CLI processes all 10 countries assigned to Groq in a single command.

**Usage:**

```bash
cd process_structured_output
uv run all-countries-groq
uv run all-countries-groq --skip-cities
uv run all-countries-groq --dry-run

# Using module directly
python -m process_structured_output.cli_all_countries_groq
```

**Groq Countries (10):**
Estonia, Ghana, Haiti, Israel, Kiribati, Madagascar, Saint Lucia, United Kingdom, Uruguay, Vietnam

#### 6.5.7 Mistral Batch Processing

The `all-countries-mistral` CLI processes all 10 countries assigned to Mistral in a single command.

**Usage:**

```bash
cd process_structured_output
uv run all-countries-mistral
uv run all-countries-mistral --skip-cities
uv run all-countries-mistral --dry-run

# Using module directly
python -m process_structured_output.cli_all_countries_mistral
```

**Mistral Countries (10):**
Algeria, Barbados, Belgium, Cote d'Ivoire, Jamaica, Portugal, Saudi Arabia, Suriname, Thailand, Tonga

#### 6.5.8 OpenAI Batch Processing

The `all-countries-openai` CLI processes all 10 countries assigned to OpenAI in a single command.

**Usage:**

```bash
cd process_structured_output
uv run all-countries-openai
uv run all-countries-openai --skip-cities
uv run all-countries-openai --dry-run

# Using module directly
python -m process_structured_output.cli_all_countries_openai
```

**OpenAI Countries (10):**
Azerbaijan, Cameroon, Ecuador, Finland, France, Grenada, Guatemala, Morocco, Nauru, Philippines

### 6.6 Running Tests

```bash
cd process_structured_output
uv run pytest -v              # Run tests
uv run ruff check .           # Linting
uv run mypy src/              # Type checking
```

### 6.7 Valid Continents

The CLI accepts these continent names:
- Africa
- Antarctica
- Asia
- Europe
- North America
- Oceania
- South America

### 6.8 Prerequisites

Before running the CLI, ensure:
1. Database tables exist (see Section 5.5)
2. `OPENAI_API_KEY` is set in `.env` (for OpenAI provider)
3. `GOOGLE_API_KEY` is set in `.env` (for Google Gemini provider)
4. `AI21_API_KEY` is set in `.env` (for AI21 Jamba provider)
5. `ANTHROPIC_API_KEY` is set in `.env` (for Anthropic Claude provider)
6. `CO_API_KEY` is set in `.env` (for Cohere Command R+ provider)
7. `DEEPSEEK_API_KEY` is set in `.env` (for DeepSeek provider)
8. `GROQ_API_KEY` is set in `.env` (for Groq provider)
9. `MISTRAL_API_KEY` is set in `.env` (for Mistral provider)
10. `DATABASE_URL` is correctly configured

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

## 8. Flutter App

### 8.1 Prerequisites

- Flutter SDK 3.10+ (https://flutter.dev/docs/get-started/install)
- Android Studio (for Android emulator) or Chrome (for web)

### 8.2 Installation

```bash
cd flutter_app
flutter pub get
```

### 8.3 Running the App

```bash
cd flutter_app

# Run on connected device or emulator
flutter run

# Run on Chrome (web)
flutter run -d chrome

# Run on Android emulator
flutter run -d android
```

### 8.4 Running Tests

```bash
cd flutter_app

# Run all tests
flutter test

# Run with verbose output
flutter test -v

# Run specific test file
flutter test test/widgets/continent_carousel_test.dart
flutter test test/screens/landing_screen_test.dart
```

### 8.5 Analyzing Code

```bash
cd flutter_app
flutter analyze
```

### 8.6 Landing Screen

The app launches with the Landing Screen featuring:

1. **Continent Carousel** (top): Horizontal scrollable list of 7 continent images
   - Africa, Antarctica, Asia, Europe, North America, Oceania, South America
   - Tapping a continent shows a snackbar with the selected continent name
   - Images located in `assets/images/continents/`

2. **Globetrotter Hero** (bottom): Full-width image with title overlay
   - "The Virtual Globetrotter" title
   - Image located in `assets/images/globetrotter.png`

### 8.7 Asset Structure

```
flutter_app/assets/images/
├── globetrotter.png          # Hero image for landing screen
└── continents/
    ├── africa.png
    ├── antarctica.png
    ├── asia.png
    ├── europe.png
    ├── north_america.png
    ├── oceania.png
    └── south_america.png
```

### 8.8 Troubleshooting

**Symptom**: Images not loading / "Unable to load asset"

**Solutions**:
1. Verify `pubspec.yaml` includes asset paths:
   ```yaml
   flutter:
     assets:
       - assets/images/
       - assets/images/continents/
   ```
2. Run `flutter pub get` to refresh asset cache
3. Restart the app with `flutter run`

**Symptom**: Tests failing with hit test warnings

**Solution**: Tests that tap widgets should tap text labels instead of widget types:
```dart
// Instead of:
await tester.tap(find.byType(ContinentCard));

// Use:
await tester.tap(find.text('Africa'));
```

### 8.9 Interactive Features (v2)

The landing page includes interactive enhancements:

1. **Selection Animation**
   - Tap a continent to select it
   - Selected card shows primary color border, scales up 1.1x, and text becomes bold
   - Hero image changes to show the selected continent at 30% opacity
   - Hero title updates to show continent name

2. **Ripple Effect**
   - Material Design ripple animation on tap
   - Uses InkWell widget wrapped in Material

3. **Hover Animation (Web/Desktop)**
   - Cards scale up 1.05x on hover
   - Image opacity reduces to 80% on hover

4. **Auto-Centering (Mobile)**
   - Selected continent scrolls to center of viewport
   - First and last continents scroll to edges (can't fully center)

5. **Toggle Selection**
   - Tap the same continent again to deselect
   - Returns to showing globetrotter image and title

---

## 9. Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.29.0 | 2026-01-06 | Landing page enhancements: selection, ripple, hover, dynamic hero, auto-center |
| 0.28.0 | 2026-01-06 | Flutter landing page with continent carousel and hero image |
| 0.27.0 | 2026-01-05 | Batch processing CLI for all OpenAI countries |
| 0.26.0 | 2026-01-05 | OpenAI GPT-4o provider for country-info CLI |
| 0.25.0 | 2026-01-05 | Batch processing CLI for all Mistral countries |
| 0.24.0 | 2026-01-05 | Mistral Large provider for country-info CLI |
| 0.23.0 | 2026-01-05 | Batch processing CLI for all Groq countries |
| 0.22.0 | 2026-01-05 | Groq Llama provider for country-info CLI |
| 0.21.0 | 2026-01-05 | Batch processing CLI for all Google countries |
| 0.20.0 | 2026-01-05 | Google Gemini provider for country-info CLI |
| 0.19.0 | 2026-01-05 | Batch processing CLI for all DeepSeek countries |
| 0.18.0 | 2026-01-05 | DeepSeek provider for country-info CLI (OpenAI-compatible API) |
| 0.17.0 | 2026-01-04 | Batch processing CLI for all Cohere countries |
| 0.16.0 | 2026-01-04 | Cohere Command R+ provider for country-info CLI |
| 0.15.0 | 2026-01-04 | Batch processing CLI for all Anthropic countries |
| 0.14.0 | 2026-01-04 | Anthropic Claude provider for country-info CLI |
| 0.13.0 | 2026-01-04 | Batch processing CLI for all AI21 countries |
| 0.12.0 | 2026-01-04 | AI21 Jamba country-info CLI with 21 country and 13 city fields |
| 0.11.0 | 2026-01-04 | Cities table - added is_capital column |
| 0.10.0 | 2026-01-03 | Cities table with safety indices and airport codes |
| 0.9.0 | 2026-01-03 | Countries table with 25 columns for country data |
| 0.8.0 | 2026-01-03 | Utilities package with countries_info module |
| 0.7.0 | 2026-01-03 | API endpoints for continents and AI models |
| 0.6.0 | 2026-01-03 | Added Google Gemini provider with --provider CLI flag |
| 0.5.0 | 2026-01-03 | Process Structured Output package with OpenAI CLI |
| 0.4.0 | 2026-01-03 | Continents table migration - added ai_model_id FK |
| 0.3.0 | 2026-01-03 | AI Models table for structured outputs |
| 0.2.0 | 2026-01-02 | Database package with continents table |
| 0.1.0 | 2026-01-02 | Initial FastAPI backend setup |
