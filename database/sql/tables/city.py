"""Cities table operations."""

from pathlib import Path

from database.executor import execute_sql_file, table_exists

# Path to SQL scripts
SCRIPT_DIR = Path(__file__).parent


def create_table() -> bool:
    """
    Create the cities table.

    Prerequisite: countries table must exist.

    Returns:
        True if table was created successfully

    Example:
        >>> from database.sql.tables.city import create_table
        >>> create_table()
        True
    """
    script_path = SCRIPT_DIR / "city_create.sql"
    return execute_sql_file(script_path)


def cleanup_table() -> bool:
    """
    Drop the cities table.

    WARNING: This will permanently delete all data!

    Returns:
        True if table was dropped successfully

    Example:
        >>> from database.sql.tables.city import cleanup_table
        >>> cleanup_table()
        True
    """
    script_path = SCRIPT_DIR / "city_cleanup.sql"
    return execute_sql_file(script_path)


def exists() -> bool:
    """
    Check if the cities table exists.

    Returns:
        True if table exists

    Example:
        >>> from database.sql.tables.city import exists
        >>> exists()
        True
    """
    return table_exists("cities")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m database.sql.tables.city [create|cleanup|exists]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "create":
        success = create_table()
        sys.exit(0 if success else 1)
    elif command == "cleanup":
        success = cleanup_table()
        sys.exit(0 if success else 1)
    elif command == "exists":
        print(f"Table 'cities' exists: {exists()}")
        sys.exit(0)
    else:
        print(f"Unknown command: {command}")
        print("Usage: python -m database.sql.tables.city [create|cleanup|exists]")
        sys.exit(1)
