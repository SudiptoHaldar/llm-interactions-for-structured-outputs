"""AI Models table operations."""

from pathlib import Path

from database.executor import execute_sql_file, table_exists

# Path to SQL scripts
SCRIPT_DIR = Path(__file__).parent


def create_table() -> bool:
    """
    Create the ai_models table.

    Returns:
        True if table was created successfully

    Example:
        >>> from database.sql.tables.ai_model import create_table
        >>> create_table()
        ✓ Executed: ai_model_create.sql
        True
    """
    script_path = SCRIPT_DIR / "ai_model_create.sql"
    return execute_sql_file(script_path)


def cleanup_table() -> bool:
    """
    Drop the ai_models table.

    WARNING: This will permanently delete all data!

    Returns:
        True if table was dropped successfully

    Example:
        >>> from database.sql.tables.ai_model import cleanup_table
        >>> cleanup_table()
        ✓ Executed: ai_model_cleanup.sql
        True
    """
    script_path = SCRIPT_DIR / "ai_model_cleanup.sql"
    return execute_sql_file(script_path)


def exists() -> bool:
    """
    Check if the ai_models table exists.

    Returns:
        True if table exists

    Example:
        >>> from database.sql.tables.ai_model import exists
        >>> exists()
        True
    """
    return table_exists("ai_models")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m database.sql.tables.ai_model [create|cleanup|exists]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "create":
        success = create_table()
        sys.exit(0 if success else 1)
    elif command == "cleanup":
        success = cleanup_table()
        sys.exit(0 if success else 1)
    elif command == "exists":
        print(f"Table 'ai_models' exists: {exists()}")
        sys.exit(0)
    else:
        print(f"Unknown command: {command}")
        print("Usage: python -m database.sql.tables.ai_model [create|cleanup|exists]")
        sys.exit(1)
