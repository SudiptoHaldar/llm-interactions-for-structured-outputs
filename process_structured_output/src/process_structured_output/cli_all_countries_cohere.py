"""CLI for batch processing all countries assigned to Cohere."""

import argparse
import sys
import time
from pathlib import Path

# Add project root to path for utilities import
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utilities.countries_info import get_countries_by_llm  # noqa: E402

from process_structured_output.cli_country import process_country  # noqa: E402


def main() -> int:
    """
    CLI entry point for processing all Cohere-assigned countries.

    Usage:
        python -m process_structured_output.cli_all_countries_cohere
        all-countries-cohere
        all-countries-cohere --skip-cities

    Returns:
        0 on success (all countries processed), 1 on any failure
    """
    parser = argparse.ArgumentParser(
        description="Process all countries assigned to Cohere",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  all-countries-cohere
  all-countries-cohere --skip-cities
  all-countries-cohere --dry-run
        """,
    )
    parser.add_argument(
        "--skip-cities",
        action="store_true",
        help="Skip retrieving city information for each country",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show countries to be processed without actually processing",
    )

    args = parser.parse_args()

    # Get list of Cohere countries from utilities
    try:
        countries = get_countries_by_llm("Cohere")
    except (ImportError, ValueError) as e:
        print(f"[X] Error loading countries list: {e}")
        return 1

    print(f"\n=== Processing {len(countries)} Cohere Countries ===\n")
    print("Countries to process:")
    for i, country in enumerate(countries, 1):
        print(f"  {i}. {country}")

    if args.dry_run:
        print("\n[DRY RUN] No countries processed.")
        return 0

    print("\n" + "=" * 50 + "\n")

    # Track results
    success_count = 0
    failure_count = 0
    results: dict[str, dict | str] = {}
    start_time = time.time()

    for i, country in enumerate(countries, 1):
        print(f"\n[{i}/{len(countries)}] Processing: {country}")
        print("-" * 40)

        try:
            result = process_country(
                country_name=country,
                provider="cohere",
                skip_cities=args.skip_cities,
            )
            results[country] = result
            success_count += 1
            print(f"[OK] {country} completed successfully")
        except Exception as e:
            results[country] = f"Error: {e}"
            failure_count += 1
            print(f"[X] {country} failed: {e}")

    # Summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 50)
    print("\n=== BATCH PROCESSING COMPLETE ===\n")
    print(f"Total countries: {len(countries)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failure_count}")
    print(f"Elapsed time: {elapsed:.1f} seconds")
    print(f"Average per country: {elapsed / len(countries):.1f} seconds")

    if failure_count > 0:
        print("\nFailed countries:")
        for country_name, country_result in results.items():
            if isinstance(country_result, str):  # Error message
                print(f"  - {country_name}: {country_result}")

    return 0 if failure_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
