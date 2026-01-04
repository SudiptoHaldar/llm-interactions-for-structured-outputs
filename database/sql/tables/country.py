"""Countries table operations."""

from pathlib import Path

from database.executor import execute_sql_file, table_exists

# Path to SQL scripts
SCRIPT_DIR = Path(__file__).parent


def create_table() -> bool:
    """
    Create the countries table.

    Prerequisites: ai_models and continents tables must exist.

    Returns:
        True if table was created successfully

    Example:
        >>> from database.sql.tables.country import create_table
        >>> create_table()
        True
    """
    script_path = SCRIPT_DIR / "country_create.sql"
    return execute_sql_file(script_path)


def alter_table() -> bool:
    """
    Add continent_id FK column to existing countries table.

    This migration adds the continent_id column with FK reference
    to continents.continent_id. Use this for existing databases.

    Prerequisite: continents table must exist.

    Returns:
        True if migration was applied successfully

    Example:
        >>> from database.sql.tables.country import alter_table
        >>> alter_table()
        True
    """
    script_path = SCRIPT_DIR / "country_alter.sql"
    return execute_sql_file(script_path)


def rollback_alter() -> bool:
    """
    Remove continent_id FK column from countries table.

    WARNING: This will permanently delete the continent_id data!

    Returns:
        True if rollback was applied successfully

    Example:
        >>> from database.sql.tables.country import rollback_alter
        >>> rollback_alter()
        True
    """
    script_path = SCRIPT_DIR / "country_rollback.sql"
    return execute_sql_file(script_path)


def cleanup_table() -> bool:
    """
    Drop the countries table.

    WARNING: This will permanently delete all data!

    Returns:
        True if table was dropped successfully

    Example:
        >>> from database.sql.tables.country import cleanup_table
        >>> cleanup_table()
        True
    """
    script_path = SCRIPT_DIR / "country_cleanup.sql"
    return execute_sql_file(script_path)


def exists() -> bool:
    """
    Check if the countries table exists.

    Returns:
        True if table exists

    Example:
        >>> from database.sql.tables.country import exists
        >>> exists()
        True
    """
    return table_exists("countries")


if __name__ == "__main__":
    import sys

    usage = "Usage: python -m database.sql.tables.country <command>"
    commands = "Commands: create, alter, rollback, cleanup, exists"

    if len(sys.argv) < 2:
        print(usage)
        print(commands)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "create":
        success = create_table()
        sys.exit(0 if success else 1)
    elif command == "alter":
        success = alter_table()
        sys.exit(0 if success else 1)
    elif command == "rollback":
        success = rollback_alter()
        sys.exit(0 if success else 1)
    elif command == "cleanup":
        success = cleanup_table()
        sys.exit(0 if success else 1)
    elif command == "exists":
        print(f"Table 'countries' exists: {exists()}")
        sys.exit(0)
    else:
        print(f"Unknown command: {command}")
        print(usage)
        print(commands)
        sys.exit(1)
