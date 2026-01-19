"""Shared city information prompts for all LLM providers.

This module centralizes city prompt definitions to ensure consistency
across all LLM providers and eliminate code duplication.
"""

from typing import Any

# System prompt for city queries
CITY_SYSTEM_PROMPT = (
    "You are a helpful AI geography teacher knowledgeable on "
    "world geography, continents, countries, and cities. "
    "Always respond with valid JSON."
)

# Field definitions for city information
# Format: (field_name, json_type, description, is_required)
CITY_FIELDS: list[tuple[str, str, str | None, bool]] = [
    ("name", "string", None, True),
    ("is_capital", "boolean", None, True),
    ("description", "string", "MUST be under 250 characters", True),
    ("interesting_fact", "string", "MUST be under 250 characters", True),
    ("area_sq_mile", "number", None, True),
    ("area_sq_km", "number", None, True),
    ("population", "integer", None, True),
    ("sci_score", "number or null", "EIU Safe Cities Index", False),
    ("sci_rank", "integer or null", "EIU Safe Cities Index rank", False),
    ("numbeo_si", "number or null", "Numbeo Safety Index 0-100", False),
    ("numbeo_ci", "number or null", "Numbeo Crime Index 0-100", False),
    ("airport_code", "string", "3-letter IATA code", True),
]

# Maximum character length for description and interesting_fact fields
MAX_STRING_LENGTH = 250


def get_cities_user_prompt(country_name: str) -> str:
    """Generate the user prompt for cities information.

    Args:
        country_name: Name of the country to query cities for

    Returns:
        Formatted user prompt string
    """
    fields_text = "\n".join(
        f"- {name}: {type_}" + (f" ({desc})" if desc else "")
        for name, type_, desc, _ in CITY_FIELDS
    )
    return (
        f"List up to 5 most populous cities in {country_name}. "
        f"Return a JSON object with a 'cities' array. "
        f"Each city should have these fields:\n{fields_text}"
    )


def get_city_json_schema(include_max_length: bool = True) -> dict[str, Any]:
    """Generate JSON schema for a single city (used in arrays).

    Args:
        include_max_length: Whether to include maxLength constraint.
            Set to False for providers that don't support it (e.g., Cohere).

    Returns:
        JSON schema dictionary for a city object
    """
    properties: dict[str, Any] = {}
    required: list[str] = []

    for name, type_, desc, is_required in CITY_FIELDS:
        prop: dict[str, Any] = {}

        # Handle nullable types
        if "or null" in type_:
            base_type = type_.replace(" or null", "")
            prop["type"] = [base_type, "null"]
        elif type_ == "boolean":
            prop["type"] = "boolean"
        elif type_ == "integer":
            prop["type"] = "integer"
        elif type_ == "number":
            prop["type"] = "number"
        else:
            prop["type"] = "string"
            # Add maxLength for string fields that need character limits
            # (only if supported by the provider)
            if include_max_length and name in ("description", "interesting_fact"):
                prop["maxLength"] = MAX_STRING_LENGTH

        if desc:
            prop["description"] = desc

        properties[name] = prop

        if is_required:
            required.append(name)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def get_cities_json_schema(include_max_length: bool = True) -> dict[str, Any]:
    """Generate JSON schema for cities response (used by Cohere).

    Args:
        include_max_length: Whether to include maxLength constraint.
            Set to False for providers that don't support it (e.g., Cohere).

    Returns:
        JSON schema dictionary with cities array
    """
    return {
        "type": "object",
        "required": ["cities"],
        "properties": {
            "cities": {
                "type": "array",
                "items": get_city_json_schema(include_max_length),
            },
        },
    }


def get_cities_tool_schema() -> dict[str, Any]:
    """Generate tool schema for cities info (used by Anthropic tool use).

    Returns:
        Tool definition dictionary for Anthropic's tool use API
    """
    return {
        "name": "record_cities_info",
        "description": "Records structured information about cities in a country",
        "input_schema": {
            "type": "object",
            "properties": {
                "cities": {
                    "type": "array",
                    "items": get_city_json_schema(),
                    "description": "List of up to 5 most populous cities",
                },
            },
            "required": ["cities"],
        },
    }


# Template for string interpolation
CITY_USER_PROMPT_TEMPLATE = get_cities_user_prompt("{country_name}")


def truncate_city_strings(city_data: dict[str, Any]) -> dict[str, Any]:
    """Truncate string fields in city data to enforce character limits.

    LLMs don't always follow character limit instructions, so this function
    provides a safety net by truncating fields before Pydantic validation.

    Args:
        city_data: Raw city data dictionary from LLM response

    Returns:
        Dictionary with truncated string fields
    """
    result = city_data.copy()
    for field in ("description", "interesting_fact"):
        if field in result and isinstance(result[field], str):
            if len(result[field]) > MAX_STRING_LENGTH:
                # Truncate and add ellipsis
                result[field] = result[field][: MAX_STRING_LENGTH - 3] + "..."
    return result
