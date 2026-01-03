# Process Structured Output

A Python package for processing structured outputs from LLM providers.

## Installation

```bash
cd process_structured_output
uv sync --all-extras
```

## Configuration

Set these environment variables in `.env`:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/llm_interactions_db
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

```bash
# Using module directly
python -m process_structured_output.cli Africa

# Using installed script
continent-info "North America"
```

## Valid Continents

- Africa
- Antarctica
- Asia
- Australia
- Europe
- North America
- South America

## Development

```bash
# Run tests
uv run pytest -v

# Linting
uv run ruff check .

# Type checking
uv run mypy .
```
