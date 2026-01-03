"""SQL script executor utility for database operations."""

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


def get_database_url() -> str:
    """Get database URL from environment."""
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable not set")
    return url


def parse_database_url(url: str) -> dict[str, str]:
    """Parse PostgreSQL URL into connection parameters."""
    # postgresql://user:password@host:port/database
    url = url.replace("postgresql://", "").replace("postgresql+asyncpg://", "")

    # Split user:password from host:port/database
    if "@" in url:
        auth, rest = url.split("@", 1)
        user, password = auth.split(":", 1) if ":" in auth else (auth, "")
    else:
        user, password = "", ""
        rest = url

    # Split host:port from database
    if "/" in rest:
        host_port, database = rest.split("/", 1)
    else:
        host_port, database = rest, ""

    # Split host from port
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


def execute_sql_file(
    file_path: Path | str,
    database_url: str | None = None,
) -> bool:
    """
    Execute a SQL script file against the database.

    Args:
        file_path: Path to the SQL file
        database_url: Optional database URL (defaults to DATABASE_URL env var)

    Returns:
        True if execution succeeded, False otherwise

    Raises:
        FileNotFoundError: If the SQL file doesn't exist
        ValueError: If DATABASE_URL is not set
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"SQL file not found: {file_path}")

    url = database_url or get_database_url()
    params = parse_database_url(url)

    # Read SQL content
    sql_content = file_path.read_text(encoding="utf-8")

    # Execute
    conn = None
    try:
        conn = psycopg2.connect(
            host=params["host"],
            port=params["port"],
            user=params["user"],
            password=params["password"],
            database=params["database"],
        )
        conn.autocommit = True

        with conn.cursor() as cursor:
            cursor.execute(sql_content)

        print(f"✓ Executed: {file_path.name}")
        return True

    except psycopg2.Error as e:
        print(f"✗ Error executing {file_path.name}: {e}")
        return False

    finally:
        if conn:
            conn.close()


def execute_sql(
    sql: str,
    database_url: str | None = None,
) -> bool:
    """
    Execute raw SQL against the database.

    Args:
        sql: SQL statement to execute
        database_url: Optional database URL (defaults to DATABASE_URL env var)

    Returns:
        True if execution succeeded, False otherwise
    """
    url = database_url or get_database_url()
    params = parse_database_url(url)

    conn = None
    try:
        conn = psycopg2.connect(
            host=params["host"],
            port=params["port"],
            user=params["user"],
            password=params["password"],
            database=params["database"],
        )
        conn.autocommit = True

        with conn.cursor() as cursor:
            cursor.execute(sql)

        return True

    except psycopg2.Error as e:
        print(f"✗ Error executing SQL: {e}")
        return False

    finally:
        if conn:
            conn.close()


def table_exists(
    table_name: str,
    database_url: str | None = None,
) -> bool:
    """Check if a table exists in the database."""
    url = database_url or get_database_url()
    params = parse_database_url(url)

    conn = None
    try:
        conn = psycopg2.connect(
            host=params["host"],
            port=params["port"],
            user=params["user"],
            password=params["password"],
            database=params["database"],
        )

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = %s
                )
                """,
                (table_name,),
            )
            result = cursor.fetchone()
            return bool(result and result[0])

    except psycopg2.Error:
        return False

    finally:
        if conn:
            conn.close()
