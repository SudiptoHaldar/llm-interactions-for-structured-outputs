"""Shared country information prompts for all LLM providers.

This module centralizes country prompt definitions to ensure consistency
across all LLM providers and eliminate code duplication.
"""

from typing import Any

# System prompt for country queries
COUNTRY_SYSTEM_PROMPT = (
    "You are a helpful AI geography teacher knowledgeable on "
    "world geography, continents and countries. "
    "Always respond with valid JSON."
)

# Field definitions for country information
# Format: (field_name, json_type, description)
COUNTRY_FIELDS: list[tuple[str, str, str | None]] = [
    ("description", "string", "MUST be under 250 characters"),
    ("interesting_fact", "string", "MUST be under 250 characters"),
    ("area_sq_mile", "number", "area in square miles"),
    ("area_sq_km", "number", "area in square km"),
    ("population", "integer", None),
    ("ppp", "number", "purchasing power parity in $"),
    ("life_expectancy", "number", "in years"),
    ("travel_risk_level", "string", "US advisory level"),
    ("global_peace_index_score", "number", "IEP score"),
    ("global_peace_index_rank", "integer", "IEP rank"),
    ("happiness_index_score", "number", "Oxford score"),
    ("happiness_index_rank", "integer", "Oxford rank"),
    ("gdp", "number", "in $"),
    ("gdp_growth_rate", "number", "in %"),
    ("inflation_rate", "number", "in %"),
    ("unemployment_rate", "number", "in %"),
    ("govt_debt", "number", "in % of GDP"),
    ("credit_rating", "string", "S&P rating"),
    ("poverty_rate", "number", "in %"),
    ("gini_coefficient", "number", "income inequality"),
    ("military_spending", "number", "in % of GDP"),
    ("gdp_per_capita", "number", "GDP per capita in $"),
]


def get_country_user_prompt(country_name: str) -> str:
    """Generate the user prompt for country information.

    Args:
        country_name: Name of the country to query

    Returns:
        Formatted user prompt string
    """
    fields_text = "\n".join(
        f"- {name}: {type_}" + (f" ({desc})" if desc else "")
        for name, type_, desc in COUNTRY_FIELDS
    )
    return (
        f"Provide information about the country {country_name} "
        f"as a JSON object with these exact fields:\n{fields_text}"
    )


def get_country_json_schema(include_max_length: bool = True) -> dict[str, Any]:
    """Generate JSON schema for country info (used by Anthropic/Cohere).

    Args:
        include_max_length: Whether to include maxLength constraint.
            Set to False for providers that don't support it (e.g., Cohere).

    Returns:
        JSON schema dictionary with properties and required fields
    """
    properties: dict[str, dict[str, Any]] = {}
    for name, type_, desc in COUNTRY_FIELDS:
        prop: dict[str, Any] = {}
        if type_ == "integer":
            prop["type"] = "integer"
        elif type_ == "number":
            prop["type"] = "number"
        else:
            prop["type"] = "string"
            # Add maxLength for string fields that need character limits
            # (only if supported by the provider)
            if include_max_length and name in ("description", "interesting_fact"):
                prop["maxLength"] = 250
        if desc:
            prop["description"] = desc
        properties[name] = prop

    return {
        "type": "object",
        "properties": properties,
        "required": [f[0] for f in COUNTRY_FIELDS],
    }


def get_country_tool_schema() -> dict[str, Any]:
    """Generate tool schema for country info (used by Anthropic tool use).

    Returns:
        Tool definition dictionary for Anthropic's tool use API
    """
    properties: dict[str, dict[str, Any]] = {}
    for name, type_, desc in COUNTRY_FIELDS:
        prop: dict[str, Any] = {}
        if type_ == "integer":
            prop["type"] = "integer"
        elif type_ == "number":
            prop["type"] = "number"
        else:
            prop["type"] = "string"
            # Add maxLength for string fields that need character limits
            if name in ("description", "interesting_fact"):
                prop["maxLength"] = 250
        if desc:
            prop["description"] = desc
        properties[name] = prop

    return {
        "name": "record_country_info",
        "description": "Records structured information about a country",
        "input_schema": {
            "type": "object",
            "properties": properties,
            "required": [f[0] for f in COUNTRY_FIELDS],
        },
    }


# Template for string interpolation (e.g., for providers that need it)
COUNTRY_USER_PROMPT_TEMPLATE = get_country_user_prompt("{country_name}")

# Maximum character length for description and interesting_fact fields
MAX_STRING_LENGTH = 250


def truncate_country_strings(data: dict[str, Any]) -> dict[str, Any]:
    """Truncate string fields to enforce character limits.

    LLMs don't always follow character limit instructions, so this function
    provides a safety net by truncating fields before Pydantic validation.

    Args:
        data: Raw country data dictionary from LLM response

    Returns:
        Dictionary with truncated string fields
    """
    result = data.copy()
    for field in ("description", "interesting_fact"):
        if field in result and isinstance(result[field], str):
            if len(result[field]) > MAX_STRING_LENGTH:
                # Truncate and add ellipsis
                result[field] = result[field][: MAX_STRING_LENGTH - 3] + "..."
    return result
