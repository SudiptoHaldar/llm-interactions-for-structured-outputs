"""Glossary utility for reading and upserting glossary entries.

This module reads the glossary/glossary.csv file and provides
functions to upsert entries into the database.

Example:
    >>> from utilities.glossary import get_glossary_entries
    >>> entries = get_glossary_entries()
    >>> len(entries)
    4
"""

import csv
import os
from dataclasses import dataclass
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


@dataclass
class GlossaryEntry:
    """A glossary entry with its definition and interpretation."""

    entry: str
    meaning: str
    range: str | None
    interpretation: str | None


# Module-level cache for parsed data
_cached_entries: list[GlossaryEntry] | None = None


def _get_csv_path() -> Path:
    """Get path to glossary.csv file."""
    # utilities/ is at project root, glossary/ is also at project root
    return Path(__file__).parent.parent / "glossary" / "glossary.csv"


def _parse_csv() -> list[GlossaryEntry]:
    """Parse the glossary CSV file and return list of entries."""
    csv_path = _get_csv_path()

    if not csv_path.exists():
        raise FileNotFoundError(f"Glossary CSV not found: {csv_path}")

    entries: list[GlossaryEntry] = []

    # Read CSV with BOM handling
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            entry = GlossaryEntry(
                entry=row["Entry"].strip(),
                meaning=row["Meaning"].strip(),
                range=row.get("Range", "").strip() or None,
                interpretation=row.get("Interpretation", "").strip() or None,
            )
            entries.append(entry)

    return entries


def get_glossary_entries() -> list[GlossaryEntry]:
    """Get all glossary entries from CSV.

    Returns:
        List of GlossaryEntry objects.

    Example:
        >>> from utilities.glossary import get_glossary_entries
        >>> entries = get_glossary_entries()
        >>> entries[0].entry
        'Gini Coefficient'
    """
    global _cached_entries
    if _cached_entries is None:
        _cached_entries = _parse_csv()
    return _cached_entries.copy()


def reload_entries() -> None:
    """Force reload of glossary entries from CSV."""
    global _cached_entries
    _cached_entries = None
    get_glossary_entries()


def get_entry(entry_name: str) -> GlossaryEntry:
    """Get a specific glossary entry by name.

    Args:
        entry_name: Name of the entry (case-insensitive).

    Returns:
        GlossaryEntry if found.

    Raises:
        ValueError: If entry_name is not found.

    Example:
        >>> from utilities.glossary import get_entry
        >>> gini = get_entry("Gini Coefficient")
        >>> gini.interpretation
        'Lower is better'
    """
    entries = get_glossary_entries()
    for entry in entries:
        if entry.entry.lower() == entry_name.lower():
            return entry
    raise ValueError(f"Entry '{entry_name}' not found in glossary.")


def _get_database_url() -> str:
    """Get database URL from environment."""
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable not set")
    return url


def _parse_database_url(url: str) -> dict[str, str]:
    """Parse PostgreSQL URL into connection parameters."""
    url = url.replace("postgresql://", "").replace("postgresql+asyncpg://", "")

    if "@" in url:
        auth, rest = url.split("@", 1)
        user, password = auth.split(":", 1) if ":" in auth else (auth, "")
    else:
        user, password = "", ""
        rest = url

    if "/" in rest:
        host_port, database = rest.split("/", 1)
    else:
        host_port, database = rest, ""

    if ":" in host_port:
        host, port = host_port.split(":", 1)
    else:
        host, port = host_port, "5432"

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
    }


def upsert_glossary_entries(
    entries: list[GlossaryEntry] | None = None,
    dry_run: bool = False,
) -> int:
    """Upsert glossary entries into the database.

    Uses INSERT ... ON CONFLICT DO UPDATE to handle repeated ingestion.
    The 'entry' column is the unique key for conflict detection.

    Args:
        entries: List of entries to upsert (defaults to all from CSV).
        dry_run: If True, only print what would be done without DB writes.

    Returns:
        Number of entries processed.

    Example:
        >>> from utilities.glossary import upsert_glossary_entries
        >>> count = upsert_glossary_entries()
        >>> print(f"Upserted {count} entries")
        Upserted 4 entries
    """
    if entries is None:
        entries = get_glossary_entries()

    if not entries:
        print("No entries to upsert.")
        return 0

    if dry_run:
        print(f"[DRY RUN] Would upsert {len(entries)} entries:")
        for entry in entries:
            print(f"  - {entry.entry}: {entry.interpretation}")
        return len(entries)

    url = _get_database_url()
    params = _parse_database_url(url)

    upsert_sql = """
        INSERT INTO glossary (entry, meaning, range, interpretation, updated_at)
        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (entry) DO UPDATE SET
            meaning = EXCLUDED.meaning,
            range = EXCLUDED.range,
            interpretation = EXCLUDED.interpretation,
            updated_at = CURRENT_TIMESTAMP
    """

    conn = None
    count = 0
    try:
        conn = psycopg2.connect(
            host=params["host"],
            port=params["port"],
            user=params["user"],
            password=params["password"],
            database=params["database"],
        )

        with conn.cursor() as cursor:
            for entry in entries:
                cursor.execute(
                    upsert_sql,
                    (entry.entry, entry.meaning, entry.range, entry.interpretation),
                )
                count += 1

        conn.commit()
        print(f"Upserted {count} glossary entries")
        return count

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
        raise

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Glossary utility for reading and upserting entries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m utilities.glossary                  # Show all entries
  python -m utilities.glossary --upsert         # Upsert to database
  python -m utilities.glossary --upsert --dry-run  # Preview upsert
  python -m utilities.glossary "Gini Coefficient"  # Lookup entry
        """,
    )
    parser.add_argument(
        "entry",
        nargs="?",
        help="Entry name to look up",
    )
    parser.add_argument(
        "--upsert",
        action="store_true",
        help="Upsert entries from CSV to database",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be upserted without DB writes",
    )

    args = parser.parse_args()

    # Handle upsert
    if args.upsert:
        try:
            count = upsert_glossary_entries(dry_run=args.dry_run)
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    # Handle entry lookup
    if args.entry:
        try:
            entry = get_entry(args.entry)
            print(f"Entry: {entry.entry}")
            print(f"Meaning: {entry.meaning}")
            print(f"Range: {entry.range}")
            print(f"Interpretation: {entry.interpretation}")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
        sys.exit(0)

    # Default: show all entries
    print("=== Glossary Entries ===\n")
    entries = get_glossary_entries()
    for entry in entries:
        print(f"* {entry.entry}")
        print(f"  Range: {entry.range}")
        print(f"  Interpretation: {entry.interpretation}")
        print(f"  Meaning: {entry.meaning[:80]}...")
        print()
    print(f"Total Entries: {len(entries)}")
