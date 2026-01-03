"""Database upsert operations for structured output data."""

import os
from typing import Any

import psycopg2
from dotenv import load_dotenv

from process_structured_output.models.continent import ContinentInfo, ModelIdentity


def get_database_url() -> str:
    """Get database URL from environment."""
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable not set")
    return url


def parse_database_url(url: str) -> dict[str, str]:
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


def get_connection(database_url: str | None = None) -> Any:
    """Get database connection."""
    url = database_url or get_database_url()
    params = parse_database_url(url)
    return psycopg2.connect(
        host=params["host"],
        port=params["port"],
        user=params["user"],
        password=params["password"],
        database=params["database"],
    )


def upsert_ai_model(
    model_identity: ModelIdentity,
    database_url: str | None = None,
) -> int:
    """
    Upsert AI model into database and return ai_model_id.

    Args:
        model_identity: ModelIdentity with provider and model name
        database_url: Optional database URL

    Returns:
        ai_model_id of the upserted record

    Example:
        >>> identity = ModelIdentity(model_provider="OpenAI", model_name="gpt-4o")
        >>> ai_model_id = upsert_ai_model(identity)
        >>> print(ai_model_id)
        1
    """
    conn = get_connection(database_url)
    try:
        conn.autocommit = False
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ai_models (model_provider, model_name)
                VALUES (%s, %s)
                ON CONFLICT (model_provider, model_name)
                DO UPDATE SET updated_at = CURRENT_TIMESTAMP
                RETURNING ai_model_id
                """,
                (model_identity.model_provider, model_identity.model_name),
            )
            result = cursor.fetchone()
            conn.commit()

            if result is None:
                raise ValueError("Failed to upsert ai_model - no ID returned")

            ai_model_id: int = result[0]
            provider = model_identity.model_provider
            model = model_identity.model_name
            print(f"✓ Upserted ai_model: {provider}/{model} (id={ai_model_id})")
            return ai_model_id
    except psycopg2.Error as e:
        conn.rollback()
        print(f"✗ Error upserting ai_model: {e}")
        raise
    finally:
        conn.close()


def upsert_continent(
    continent_name: str,
    continent_info: ContinentInfo,
    ai_model_id: int,
    database_url: str | None = None,
) -> int:
    """
    Upsert continent into database and return continent_id.

    Args:
        continent_name: Name of the continent
        continent_info: ContinentInfo with structured data
        ai_model_id: FK to ai_models table
        database_url: Optional database URL

    Returns:
        continent_id of the upserted record

    Example:
        >>> info = ContinentInfo(description="...", area_sq_mile=11668000, ...)
        >>> continent_id = upsert_continent("Africa", info, 1)
        >>> print(continent_id)
        1
    """
    conn = get_connection(database_url)
    try:
        conn.autocommit = False
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO continents (
                    name, description, area_sq_mile, area_sq_km,
                    population, num_country, ai_model_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (name)
                DO UPDATE SET
                    description = EXCLUDED.description,
                    area_sq_mile = EXCLUDED.area_sq_mile,
                    area_sq_km = EXCLUDED.area_sq_km,
                    population = EXCLUDED.population,
                    num_country = EXCLUDED.num_country,
                    ai_model_id = EXCLUDED.ai_model_id,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING continent_id
                """,
                (
                    continent_name,
                    continent_info.description,
                    continent_info.area_sq_mile,
                    continent_info.area_sq_km,
                    continent_info.population,
                    continent_info.num_country,
                    ai_model_id,
                ),
            )
            result = cursor.fetchone()
            conn.commit()

            if result is None:
                raise ValueError("Failed to upsert continent - no ID returned")

            continent_id: int = result[0]
            print(f"✓ Upserted continent: {continent_name} (id={continent_id})")
            return continent_id
    except psycopg2.Error as e:
        conn.rollback()
        print(f"✗ Error upserting continent: {e}")
        raise
    finally:
        conn.close()
