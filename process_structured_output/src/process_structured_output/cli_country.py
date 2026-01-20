"""CLI for country structured output processing."""

import argparse
import sys
from pathlib import Path

# Add project root to path for utilities import
# cli_country.py is at: process_structured_output/src/process_structured_output/
# Project root is 4 parents up: llm-interactions-for-structured-outputs/
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from process_structured_output.db.operations import (  # noqa: E402
    get_continent_id,
    upsert_ai_model,
    upsert_city,
    upsert_country,
)
from process_structured_output.providers.ai21_provider import (  # noqa: E402
    AI21Provider,
)
from process_structured_output.providers.anthropic_provider import (  # noqa: E402
    AnthropicProvider,
)
from process_structured_output.providers.cohere_provider import (  # noqa: E402
    CohereProvider,
)
from process_structured_output.providers.deepseek_provider import (  # noqa: E402
    DeepSeekProvider,
)
from process_structured_output.providers.google_provider import (  # noqa: E402
    GoogleProvider,
)
from process_structured_output.providers.groq_provider import (  # noqa: E402
    GroqProvider,
)
from process_structured_output.providers.mistral_provider import (  # noqa: E402
    MistralProvider,
)
from process_structured_output.providers.openai_provider import (  # noqa: E402
    OpenAIProvider,
)


def process_country(
    country_name: str,
    provider: str | None = None,
    skip_cities: bool = False,
) -> dict[str, int | list[int] | None]:
    """
    Process a single country and return results.

    Args:
        country_name: Name of the country to query
        provider: LLM provider to use (None = auto-detect from countries.csv)
        skip_cities: Whether to skip city retrieval

    Returns:
        Dictionary with ai_model_id, continent_id, country_id, city_ids

    Raises:
        ValueError: On processing errors
    """
    print(f"\n=== Processing: {country_name} ===\n")

    # Look up continent and assigned LLM from utilities
    from utilities.countries_info import get_country_info as get_country_lookup

    try:
        country_lookup = get_country_lookup(country_name)
        continent_name = country_lookup.continent
        assigned_llm = country_lookup.llm
        print(f"Continent lookup: {country_name} -> {continent_name}")

        # Auto-detect provider if not specified
        if provider is None:
            provider = assigned_llm.lower()
            print(f"Provider auto-detected: {assigned_llm}")
    except ValueError:
        continent_name = None
        print(f"Warning: Country '{country_name}' not in countries.csv")
        print("         Continent will be set to NULL in database")
        if provider is None:
            provider = "ai21"  # Default fallback
            print(f"         Using default provider: {provider}")

    # Initialize provider
    llm_provider: (
        AI21Provider | AnthropicProvider | CohereProvider | DeepSeekProvider
        | GoogleProvider | GroqProvider | MistralProvider | OpenAIProvider
    )
    if provider == "ai21":
        llm_provider = AI21Provider()
    elif provider == "anthropic":
        llm_provider = AnthropicProvider()
    elif provider == "cohere":
        llm_provider = CohereProvider()
    elif provider == "deepseek":
        llm_provider = DeepSeekProvider()
    elif provider == "google":
        llm_provider = GoogleProvider()
    elif provider == "groq":
        llm_provider = GroqProvider()
    elif provider == "mistral":
        llm_provider = MistralProvider()
    elif provider == "openai":
        llm_provider = OpenAIProvider()
    else:
        raise ValueError(f"Unknown provider: {provider}")

    # Q1: Get model identity
    print("\nQ1: Getting model identity...")
    model_identity = llm_provider.get_model_identity()
    print(f"    Model Provider: {model_identity.model_provider}")
    print(f"    Model Name: {model_identity.model_name}")

    # Q1 Action: Upsert ai_model
    print("\nQ1 Action: Upserting ai_model...")
    ai_model_id = upsert_ai_model(model_identity)

    # Look up continent_id if we have a continent
    continent_id: int | None = None
    if continent_name:
        continent_id = get_continent_id(continent_name)
        if continent_id:
            print(f"    Continent ID: {continent_id} ({continent_name})")
        else:
            print(f"    Warning: Continent '{continent_name}' not in database")

    # Q2: Get country info (with retry for transient LLM failures)
    print(f"\nQ2: Getting country info for {country_name}...")
    country_info = llm_provider.get_country_info_with_retry(country_name)
    print(f"    Description: {country_info.description[:50]}...")
    print(f"    Area (sq mi): {country_info.area_sq_mile:,.2f}")
    print(f"    Area (sq km): {country_info.area_sq_km:,.2f}")
    print(f"    Population: {country_info.population:,}")
    print(f"    GDP: ${country_info.gdp:,.0f}")
    print(f"    Life Expectancy: {country_info.life_expectancy:.1f} years")

    # Q2 Action: Upsert country
    print(f"\nQ2 Action: Upserting country {country_name}...")
    country_id = upsert_country(
        country_name, country_info, ai_model_id, continent_id
    )

    # Q3: Get cities info (unless skipped, with retry for transient LLM failures)
    city_ids: list[int] = []
    if not skip_cities:
        print(f"\nQ3: Getting cities info for {country_name}...")
        cities = llm_provider.get_cities_info_with_retry(country_name)
        print(f"    Retrieved {len(cities)} cities")

        for city in cities:
            capital_marker = " (capital)" if city.is_capital else ""
            print(f"    - {city.name}{capital_marker}: pop {city.population:,}")

        # Q3 Action: Upsert cities
        print(f"\nQ3 Action: Upserting {len(cities)} cities...")
        for city in cities:
            city_id = upsert_city(city, country_id)
            city_ids.append(city_id)
    else:
        print("\nQ3: Skipped (--skip-cities flag)")

    return {
        "ai_model_id": ai_model_id,
        "continent_id": continent_id,
        "country_id": country_id,
        "city_ids": city_ids,
    }


def main() -> int:
    """
    CLI entry point for country info retrieval.

    Usage:
        python -m process_structured_output.cli_country Nigeria
        country-info "United States" --skip-cities

    Returns:
        0 on success, 1 on error
    """
    parser = argparse.ArgumentParser(
        description="Get country information using LLM structured output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  country-info Nigeria
  country-info "South Africa" --skip-cities
  country-info Brazil --provider anthropic
  country-info China --provider ai21
  country-info Germany --provider cohere
  country-info Poland --provider deepseek
  country-info Kenya --provider google
  country-info Ghana --provider groq
  country-info Algeria --provider mistral
  country-info France --provider openai
        """,
    )
    parser.add_argument(
        "country_name",
        type=str,
        help="Name of the country to query",
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=[
            "ai21", "anthropic", "cohere", "deepseek", "google", "groq",
            "mistral", "openai"
        ],
        default=None,
        help="LLM provider to use (default: auto-detect from countries.csv)",
    )
    parser.add_argument(
        "--skip-cities",
        action="store_true",
        help="Skip retrieving city information",
    )

    args = parser.parse_args()

    try:
        result = process_country(
            country_name=args.country_name,
            provider=args.provider,
            skip_cities=args.skip_cities,
        )

        print("\n=== Complete ===")
        print(f"    ai_model_id: {result['ai_model_id']}")
        print(f"    continent_id: {result['continent_id']}")
        print(f"    country_id: {result['country_id']}")
        if result["city_ids"]:
            print(f"    city_ids: {result['city_ids']}")

        return 0

    except ValueError as e:
        print(f"\n[X] Error: {e}")
        return 1
    except Exception as e:
        print(f"\n[X] Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
