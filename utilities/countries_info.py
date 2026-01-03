"""Countries information utility for LLM interactions.

This module reads the countries/countries.csv file and provides
query methods to retrieve information about continents, countries,
and LLM providers.

Example:
    >>> from utilities.countries_info import get_continents, get_llms
    >>> continents = get_continents()
    >>> "Africa" in continents
    True
"""

import csv
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CountryInfo:
    """Information about a country's LLM assignment."""

    country: str
    continent: str
    llm: str


@dataclass
class CountriesData:
    """Parsed countries data from CSV."""

    continents: list[str] = field(default_factory=list)
    llms: list[str] = field(default_factory=list)
    countries: list[str] = field(default_factory=list)
    continent_countries: dict[str, list[str]] = field(default_factory=dict)
    llm_countries: dict[str, list[str]] = field(default_factory=dict)
    country_info_map: dict[str, CountryInfo] = field(default_factory=dict)


# Module-level cache for parsed data
_cached_data: CountriesData | None = None


def _get_csv_path() -> Path:
    """Get path to countries.csv file."""
    # utilities/ is at project root, countries/ is also at project root
    return Path(__file__).parent.parent / "countries" / "countries.csv"


def _parse_csv() -> CountriesData:
    """Parse the countries CSV file and return structured data."""
    csv_path = _get_csv_path()

    if not csv_path.exists():
        raise FileNotFoundError(f"Countries CSV not found: {csv_path}")

    data = CountriesData()
    continent_set: set[str] = set()
    country_set: set[str] = set()

    # Read CSV with BOM handling
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)

        # Parse header row to get LLM names
        header = next(reader)
        data.llms = [llm.strip() for llm in header[2:] if llm.strip()]

        # Initialize llm_countries dict
        for llm in data.llms:
            data.llm_countries[llm] = []

        # Parse data rows
        for row in reader:
            if not row or not row[0].strip():
                continue

            continent = row[0].strip()
            continent_set.add(continent)

            # Initialize continent in dict if needed
            if continent not in data.continent_countries:
                data.continent_countries[continent] = []

            # Process each LLM column (columns 2-9)
            for i, llm in enumerate(data.llms):
                col_idx = i + 2  # LLM columns start at index 2
                if col_idx < len(row) and row[col_idx].strip():
                    country = row[col_idx].strip()
                    country_set.add(country)

                    # Add to continent mapping
                    if country not in data.continent_countries[continent]:
                        data.continent_countries[continent].append(country)

                    # Add to LLM mapping
                    if country not in data.llm_countries[llm]:
                        data.llm_countries[llm].append(country)

                    # Add to country info map
                    data.country_info_map[country.lower()] = CountryInfo(
                        country=country,
                        continent=continent,
                        llm=llm,
                    )

    # Sort results
    data.continents = sorted(continent_set)
    data.countries = sorted(country_set)

    return data


def _get_data() -> CountriesData:
    """Get cached parsed data, parsing if necessary."""
    global _cached_data
    if _cached_data is None:
        _cached_data = _parse_csv()
    return _cached_data


def reload_data() -> None:
    """Force reload of countries data from CSV.

    Example:
        >>> from utilities.countries_info import reload_data
        >>> reload_data()  # Force fresh read from CSV
    """
    global _cached_data
    _cached_data = None
    _get_data()


def get_continents() -> list[str]:
    """Return list of all continents.

    Returns:
        Sorted list of continent names.

    Example:
        >>> from utilities.countries_info import get_continents
        >>> continents = get_continents()
        >>> print("Africa" in continents)
        True
        >>> print(len(continents))
        7
    """
    return _get_data().continents.copy()


def get_llms() -> list[str]:
    """Return list of all LLM providers.

    Returns:
        List of LLM provider names in column order.

    Example:
        >>> from utilities.countries_info import get_llms
        >>> llms = get_llms()
        >>> print("OpenAI" in llms)
        True
        >>> print(len(llms))
        8
    """
    return _get_data().llms.copy()


def get_all_countries() -> list[str]:
    """Return list of all countries.

    Returns:
        Sorted list of all unique country names.

    Example:
        >>> from utilities.countries_info import get_all_countries
        >>> countries = get_all_countries()
        >>> print("Nigeria" in countries)
        True
    """
    return _get_data().countries.copy()


def get_countries_by_continent(continent_name: str) -> list[str]:
    """Return list of countries in a specific continent.

    Args:
        continent_name: Name of the continent (case-insensitive).

    Returns:
        List of country names in the continent.

    Raises:
        ValueError: If continent_name is not found.

    Example:
        >>> from utilities.countries_info import get_countries_by_continent
        >>> african_countries = get_countries_by_continent("Africa")
        >>> print("Nigeria" in african_countries)
        True
        >>> print(len(african_countries))
        16
    """
    data = _get_data()

    # Case-insensitive lookup
    for continent in data.continents:
        if continent.lower() == continent_name.lower():
            return data.continent_countries[continent].copy()

    valid = ", ".join(data.continents)
    raise ValueError(f"Continent '{continent_name}' not found. Valid: {valid}")


def get_countries_by_llm(llm_name: str) -> list[str]:
    """Return list of countries assigned to a specific LLM provider.

    Args:
        llm_name: Name of the LLM provider (case-insensitive).

    Returns:
        List of country names assigned to the LLM.

    Raises:
        ValueError: If llm_name is not found.

    Example:
        >>> from utilities.countries_info import get_countries_by_llm
        >>> openai_countries = get_countries_by_llm("OpenAI")
        >>> print("Morocco" in openai_countries)
        True
    """
    data = _get_data()

    # Case-insensitive lookup
    for llm in data.llms:
        if llm.lower() == llm_name.lower():
            return data.llm_countries[llm].copy()

    valid = ", ".join(data.llms)
    raise ValueError(f"LLM '{llm_name}' not found. Valid: {valid}")


def get_country_info(country_name: str) -> CountryInfo:
    """Return the continent and LLM for a specific country.

    Args:
        country_name: Name of the country (case-insensitive).

    Returns:
        CountryInfo with country, continent, and llm fields.

    Raises:
        ValueError: If country_name is not found.

    Example:
        >>> from utilities.countries_info import get_country_info
        >>> info = get_country_info("Nigeria")
        >>> print(info.continent)
        Africa
        >>> print(info.llm)
        AI21
    """
    data = _get_data()
    key = country_name.lower()

    if key in data.country_info_map:
        return data.country_info_map[key]

    raise ValueError(f"Country '{country_name}' not found in countries data.")


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Query countries information for LLM interactions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m utilities.countries_info                    # Show summary
  python -m utilities.countries_info --continent Africa # List African countries
  python -m utilities.countries_info --llm OpenAI       # List OpenAI countries
  python -m utilities.countries_info Nigeria            # Get country info
        """,
    )
    parser.add_argument(
        "country",
        nargs="?",
        help="Country name to look up (returns continent and LLM)",
    )
    parser.add_argument(
        "--continent",
        "-c",
        metavar="NAME",
        help="List countries in specified continent",
    )
    parser.add_argument(
        "--llm",
        "-l",
        metavar="NAME",
        help="List countries assigned to specified LLM provider",
    )

    args = parser.parse_args()

    # Handle --continent and/or --llm flags
    if args.continent or args.llm:
        try:
            if args.continent and args.llm:
                # Both filters: intersection
                continent_countries = set(get_countries_by_continent(args.continent))
                llm_countries = set(get_countries_by_llm(args.llm))
                countries = list(continent_countries & llm_countries)
                label = f"{args.continent} for {args.llm}"
                print(f"Countries in {label} ({len(countries)}):")
            elif args.continent:
                # Continent only
                countries = get_countries_by_continent(args.continent)
                print(f"Countries in {args.continent} ({len(countries)}):")
            else:
                # LLM only
                countries = get_countries_by_llm(args.llm)
                print(f"Countries for {args.llm} ({len(countries)}):")

            for country in sorted(countries):
                print(f"  - {country}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
        sys.exit(0)

    # Handle country lookup
    if args.country:
        try:
            info = get_country_info(args.country)
            print(f"{info.country}: Continent={info.continent}, LLM={info.llm}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
        sys.exit(0)

    # Default: show summary
    print("=== Countries Info Utility ===\n")

    print("Continents:")
    for continent in get_continents():
        count = len(get_countries_by_continent(continent))
        print(f"  - {continent}: {count} countries")

    print("\nLLM Providers:")
    for llm in get_llms():
        count = len(get_countries_by_llm(llm))
        print(f"  - {llm}: {count} countries")

    print(f"\nTotal Countries: {len(get_all_countries())}")
