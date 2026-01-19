"""Shared prompts for LLM structured output queries.

This module provides centralized prompt definitions for all LLM providers,
ensuring consistency and eliminating code duplication across providers.
"""

from process_structured_output.prompts.city_prompts import (
    CITY_FIELDS,
    CITY_SYSTEM_PROMPT,
    CITY_USER_PROMPT_TEMPLATE,
    get_cities_json_schema,
    get_cities_tool_schema,
    get_cities_user_prompt,
    get_city_json_schema,
    truncate_city_strings,
)
from process_structured_output.prompts.country_prompts import (
    COUNTRY_FIELDS,
    COUNTRY_SYSTEM_PROMPT,
    COUNTRY_USER_PROMPT_TEMPLATE,
    get_country_json_schema,
    get_country_tool_schema,
    get_country_user_prompt,
    truncate_country_strings,
)

__all__ = [
    # Country prompts
    "COUNTRY_SYSTEM_PROMPT",
    "COUNTRY_USER_PROMPT_TEMPLATE",
    "COUNTRY_FIELDS",
    "get_country_user_prompt",
    "get_country_json_schema",
    "get_country_tool_schema",
    "truncate_country_strings",
    # City prompts
    "CITY_SYSTEM_PROMPT",
    "CITY_USER_PROMPT_TEMPLATE",
    "CITY_FIELDS",
    "get_cities_user_prompt",
    "get_city_json_schema",
    "get_cities_json_schema",
    "get_cities_tool_schema",
    "truncate_city_strings",
]
