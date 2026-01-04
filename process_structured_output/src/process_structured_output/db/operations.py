"""Database upsert operations for structured output data."""

import os
from typing import Any

import psycopg2
from dotenv import load_dotenv

from process_structured_output.models.continent import ContinentInfo, ModelIdentity
from process_structured_output.models.country import CityInfo, CountryInfo


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
            print(f"[OK] Upserted ai_model: {provider}/{model} (id={ai_model_id})")
            return ai_model_id
    except psycopg2.Error as e:
        conn.rollback()
        print(f"[X] Error upserting ai_model: {e}")
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
            print(f"[OK] Upserted continent: {continent_name} (id={continent_id})")
            return continent_id
    except psycopg2.Error as e:
        conn.rollback()
        print(f"[X] Error upserting continent: {e}")
        raise
    finally:
        conn.close()


def get_continent_id(
    continent_name: str,
    database_url: str | None = None,
) -> int | None:
    """
    Get continent_id by continent name.

    Args:
        continent_name: Name of the continent
        database_url: Optional database URL

    Returns:
        continent_id or None if not found
    """
    conn = get_connection(database_url)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT continent_id FROM continents WHERE name = %s",
                (continent_name,),
            )
            result = cursor.fetchone()
            return result[0] if result else None
    finally:
        conn.close()


def upsert_country(
    country_name: str,
    country_info: CountryInfo,
    ai_model_id: int,
    continent_id: int | None,
    database_url: str | None = None,
) -> int:
    """
    Upsert country into database and return country_id.

    Args:
        country_name: Name of the country
        country_info: CountryInfo with structured data
        ai_model_id: FK to ai_models table
        continent_id: FK to continents table (can be None)
        database_url: Optional database URL

    Returns:
        country_id of the upserted record

    Example:
        >>> info = CountryInfo(description="...", area_sq_mile=356669, ...)
        >>> country_id = upsert_country("Nigeria", info, 1, 1)
        >>> print(country_id)
        1
    """
    conn = get_connection(database_url)
    try:
        conn.autocommit = False
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO countries (
                    name, ai_model_id, continent_id,
                    description, interesting_fact,
                    area_sq_mile, area_sq_km, population, ppp, life_expectancy,
                    travel_risk_level, global_peace_index_score,
                    global_peace_index_rank, happiness_index_score,
                    happiness_index_rank, gdp, gdp_growth_rate, inflation_rate,
                    unemployment_rate, govt_debt, credit_rating, poverty_rate,
                    gini_coefficient, military_spending
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (name)
                DO UPDATE SET
                    ai_model_id = EXCLUDED.ai_model_id,
                    continent_id = EXCLUDED.continent_id,
                    description = EXCLUDED.description,
                    interesting_fact = EXCLUDED.interesting_fact,
                    area_sq_mile = EXCLUDED.area_sq_mile,
                    area_sq_km = EXCLUDED.area_sq_km,
                    population = EXCLUDED.population,
                    ppp = EXCLUDED.ppp,
                    life_expectancy = EXCLUDED.life_expectancy,
                    travel_risk_level = EXCLUDED.travel_risk_level,
                    global_peace_index_score = EXCLUDED.global_peace_index_score,
                    global_peace_index_rank = EXCLUDED.global_peace_index_rank,
                    happiness_index_score = EXCLUDED.happiness_index_score,
                    happiness_index_rank = EXCLUDED.happiness_index_rank,
                    gdp = EXCLUDED.gdp,
                    gdp_growth_rate = EXCLUDED.gdp_growth_rate,
                    inflation_rate = EXCLUDED.inflation_rate,
                    unemployment_rate = EXCLUDED.unemployment_rate,
                    govt_debt = EXCLUDED.govt_debt,
                    credit_rating = EXCLUDED.credit_rating,
                    poverty_rate = EXCLUDED.poverty_rate,
                    gini_coefficient = EXCLUDED.gini_coefficient,
                    military_spending = EXCLUDED.military_spending,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING country_id
                """,
                (
                    country_name,
                    ai_model_id,
                    continent_id,
                    country_info.description,
                    country_info.interesting_fact,
                    country_info.area_sq_mile,
                    country_info.area_sq_km,
                    country_info.population,
                    country_info.ppp,
                    country_info.life_expectancy,
                    country_info.travel_risk_level,
                    country_info.global_peace_index_score,
                    country_info.global_peace_index_rank,
                    country_info.happiness_index_score,
                    country_info.happiness_index_rank,
                    country_info.gdp,
                    country_info.gdp_growth_rate,
                    country_info.inflation_rate,
                    country_info.unemployment_rate,
                    country_info.govt_debt,
                    country_info.credit_rating,
                    country_info.poverty_rate,
                    country_info.gini_coefficient,
                    country_info.military_spending,
                ),
            )
            result = cursor.fetchone()
            conn.commit()

            if result is None:
                raise ValueError("Failed to upsert country - no ID returned")

            country_id: int = result[0]
            print(f"[OK] Upserted country: {country_name} (id={country_id})")
            return country_id
    except psycopg2.Error as e:
        conn.rollback()
        print(f"[X] Error upserting country: {e}")
        raise
    finally:
        conn.close()


def upsert_city(
    city_info: CityInfo,
    country_id: int,
    database_url: str | None = None,
) -> int:
    """
    Upsert city into database and return city_id.

    Args:
        city_info: CityInfo with structured data
        country_id: FK to countries table
        database_url: Optional database URL

    Returns:
        city_id of the upserted record

    Example:
        >>> info = CityInfo(name="Lagos", is_capital=False, ...)
        >>> city_id = upsert_city(info, 1)
        >>> print(city_id)
        1
    """
    conn = get_connection(database_url)
    try:
        conn.autocommit = False
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cities (
                    country_id, name, is_capital, description, interesting_fact,
                    area_sq_mile, area_sq_km, population,
                    sci_score, sci_rank, numbeo_si, numbeo_ci, airport_code
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (country_id, name)
                DO UPDATE SET
                    is_capital = EXCLUDED.is_capital,
                    description = EXCLUDED.description,
                    interesting_fact = EXCLUDED.interesting_fact,
                    area_sq_mile = EXCLUDED.area_sq_mile,
                    area_sq_km = EXCLUDED.area_sq_km,
                    population = EXCLUDED.population,
                    sci_score = EXCLUDED.sci_score,
                    sci_rank = EXCLUDED.sci_rank,
                    numbeo_si = EXCLUDED.numbeo_si,
                    numbeo_ci = EXCLUDED.numbeo_ci,
                    airport_code = EXCLUDED.airport_code,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING city_id
                """,
                (
                    country_id,
                    city_info.name,
                    city_info.is_capital,
                    city_info.description,
                    city_info.interesting_fact,
                    city_info.area_sq_mile,
                    city_info.area_sq_km,
                    city_info.population,
                    city_info.sci_score,
                    city_info.sci_rank,
                    city_info.numbeo_si,
                    city_info.numbeo_ci,
                    city_info.airport_code,
                ),
            )
            result = cursor.fetchone()
            conn.commit()

            if result is None:
                raise ValueError("Failed to upsert city - no ID returned")

            city_id: int = result[0]
            print(f"[OK] Upserted city: {city_info.name} (id={city_id})")
            return city_id
    except psycopg2.Error as e:
        conn.rollback()
        print(f"[X] Error upserting city: {e}")
        raise
    finally:
        conn.close()
