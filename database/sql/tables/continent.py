"""Continent table operations."""

from pathlib import Path

from database.executor import execute_sql_file, table_exists

# Path to SQL scripts
SCRIPT_DIR = Path(__file__).parent


def create_table() -> bool:
    """
    Create the continents table.

    Returns:
        True if table was created successfully

    Example:
        >>> from database.sql.tables.continent import create_table
        >>> create_table()
        ✓ Executed: continent_create.sql
        True
    """
    script_path = SCRIPT_DIR / "continent_create.sql"
    return execute_sql_file(script_path)


def cleanup_table() -> bool:
    """
    Drop the continents table.

    WARNING: This will permanently delete all data!

    Returns:
        True if table was dropped successfully

    Example:
        >>> from database.sql.tables.continent import cleanup_table
        >>> cleanup_table()
        ✓ Executed: continent_cleanup.sql
        True
    """
    script_path = SCRIPT_DIR / "continent_cleanup.sql"
    return execute_sql_file(script_path)


def exists() -> bool:
    """
    Check if the continents table exists.

    Returns:
        True if table exists

    Example:
        >>> from database.sql.tables.continent import exists
        >>> exists()
        True
    """
    return table_exists("continents")


def alter_table() -> bool:
    """
    Apply alter migration v1 to add ai_model_id column.

    Prerequisite: ai_models table must exist.

    Returns:
        True if migration was applied successfully

    Example:
        >>> from database.sql.tables.continent import alter_table
        >>> alter_table()
        ✓ Executed: continent_alter_v1.sql
        True
    """
    script_path = SCRIPT_DIR / "continent_alter_v1.sql"
    return execute_sql_file(script_path)


def rollback_alter() -> bool:
    """
    Rollback alter migration v1 - remove ai_model_id column.

    WARNING: This will permanently delete ai_model_id data!

    Returns:
        True if rollback was applied successfully

    Example:
        >>> from database.sql.tables.continent import rollback_alter
        >>> rollback_alter()
        ✓ Executed: continent_alter_v1_rollback.sql
        True
    """
    script_path = SCRIPT_DIR / "continent_alter_v1_rollback.sql"
    return execute_sql_file(script_path)


if __name__ == "__main__":
    import sys

    usage = (
        "Usage: python -m database.sql.tables.continent "
        "[create|cleanup|exists|alter|rollback]"
    )

    if len(sys.argv) < 2:
        print(usage)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "create":
        success = create_table()
        sys.exit(0 if success else 1)
    elif command == "cleanup":
        success = cleanup_table()
        sys.exit(0 if success else 1)
    elif command == "exists":
        print(f"Table 'continents' exists: {exists()}")
        sys.exit(0)
    elif command == "alter":
        success = alter_table()
        sys.exit(0 if success else 1)
    elif command == "rollback":
        success = rollback_alter()
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown command: {command}")
        print(usage)
        sys.exit(1)
