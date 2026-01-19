"""Glossary table operations."""

from pathlib import Path

from database.executor import execute_sql_file, table_exists

# Path to SQL scripts
SCRIPT_DIR = Path(__file__).parent


def create_table() -> bool:
    """
    Create the glossary table.

    Returns:
        True if table was created successfully

    Example:
        >>> from database.sql.tables.glossary import create_table
        >>> create_table()
        True
    """
    script_path = SCRIPT_DIR / "glossary_create.sql"
    return execute_sql_file(script_path)


def cleanup_table() -> bool:
    """
    Drop the glossary table.

    WARNING: This will permanently delete all data!

    Returns:
        True if table was dropped successfully

    Example:
        >>> from database.sql.tables.glossary import cleanup_table
        >>> cleanup_table()
        True
    """
    script_path = SCRIPT_DIR / "glossary_cleanup.sql"
    return execute_sql_file(script_path)


def exists() -> bool:
    """
    Check if the glossary table exists.

    Returns:
        True if table exists

    Example:
        >>> from database.sql.tables.glossary import exists
        >>> exists()
        True
    """
    return table_exists("glossary")


if __name__ == "__main__":
    import sys

    usage = "Usage: python -m database.sql.tables.glossary <command>"
    commands = "Commands: create, cleanup, exists"

    if len(sys.argv) < 2:
        print(usage)
        print(commands)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "create":
        success = create_table()
        sys.exit(0 if success else 1)
    elif command == "cleanup":
        success = cleanup_table()
        sys.exit(0 if success else 1)
    elif command == "exists":
        print(f"Table 'glossary' exists: {exists()}")
        sys.exit(0)
    else:
        print(f"Unknown command: {command}")
        print(usage)
        print(commands)
        sys.exit(1)
