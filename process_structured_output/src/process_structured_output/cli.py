"""CLI for continent structured output processing."""

import argparse
import sys

from process_structured_output.db.operations import upsert_ai_model, upsert_continent
from process_structured_output.providers.google_provider import GoogleProvider
from process_structured_output.providers.openai_provider import OpenAIProvider

VALID_CONTINENTS = [
    "Africa",
    "Antarctica",
    "Asia",
    "Europe",
    "North America",
    "Oceania",
    "South America",
]


def main() -> int:
    """
    CLI entry point for continent info retrieval.

    Usage:
        python -m process_structured_output.cli Africa
        continent-info "North America"

    Returns:
        0 on success, 1 on error
    """
    parser = argparse.ArgumentParser(
        description="Get continent information using OpenAI structured output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Valid continents: {', '.join(VALID_CONTINENTS)}",
    )
    parser.add_argument(
        "continent_name",
        type=str,
        help="Name of the continent to query",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip continent name validation",
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "google"],
        default="openai",
        help="LLM provider to use (default: openai)",
    )

    args = parser.parse_args()
    continent_name: str = args.continent_name

    # Validate continent name
    if not args.skip_validation:
        normalized = continent_name.strip().title()
        if normalized not in VALID_CONTINENTS:
            print(f"✗ Invalid continent: {continent_name}")
            print(f"  Valid continents: {', '.join(VALID_CONTINENTS)}")
            return 1

    print(f"\n=== Processing: {continent_name} ===\n")

    try:
        # Initialize provider
        provider: GoogleProvider | OpenAIProvider
        if args.provider == "google":
            provider = GoogleProvider()
        else:
            provider = OpenAIProvider()

        # Q1: Get model identity
        print("Q1: Getting model identity...")
        model_identity = provider.get_model_identity()
        print(f"    Model Provider: {model_identity.model_provider}")
        print(f"    Model Name: {model_identity.model_name}")

        # Q1 Action: Upsert ai_model
        print("\nQ1 Action: Upserting ai_model...")
        ai_model_id = upsert_ai_model(model_identity)

        # Q2: Get continent info
        print(f"\nQ2: Getting continent info for {continent_name}...")
        continent_info = provider.get_continent_info(continent_name)
        print(f"    Description: {continent_info.description[:50]}...")
        print(f"    Area (sq mi): {continent_info.area_sq_mile:,.2f}")
        print(f"    Area (sq km): {continent_info.area_sq_km:,.2f}")
        print(f"    Population: {continent_info.population:,}")
        print(f"    Countries: {continent_info.num_country}")

        # Q2 Action: Upsert continent
        print(f"\nQ2 Action: Upserting continent {continent_name}...")
        continent_id = upsert_continent(continent_name, continent_info, ai_model_id)

        print("\n=== Complete ===")
        print(f"    ai_model_id: {ai_model_id}")
        print(f"    continent_id: {continent_id}")

        return 0

    except ValueError as e:
        print(f"\n✗ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
