-- ============================================================================
-- Migration: Add gdp_per_capita column to countries table
-- Description: Adds gdp_per_capita column between military_spending and created_at
-- Version: 1.3.0
-- Created: 2026-01-17
-- Note: PostgreSQL doesn't support ADD COLUMN ... AFTER, so we recreate the table
-- ============================================================================

BEGIN;

-- Step 1: Check if column already exists (idempotency)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'countries' AND column_name = 'gdp_per_capita'
    ) THEN
        RAISE NOTICE 'Column gdp_per_capita already exists. Skipping migration.';
        RETURN;
    END IF;

    -- Step 2: Create temp table with existing data
    CREATE TEMP TABLE countries_backup AS SELECT * FROM countries;

    -- Step 3: Drop cities FK constraint temporarily
    ALTER TABLE cities DROP CONSTRAINT IF EXISTS fk_cities_countries;

    -- Step 4: Drop existing indexes
    DROP INDEX IF EXISTS idx_countries_name;
    DROP INDEX IF EXISTS idx_countries_ai_model_id;
    DROP INDEX IF EXISTS idx_countries_continent_id;

    -- Step 5: Drop original table
    DROP TABLE countries;

    -- Step 6: Recreate table with gdp_per_capita in correct position
    CREATE TABLE countries (
        -- Primary key
        country_id      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

        -- Foreign key references
        ai_model_id     INTEGER,
        continent_id    INTEGER,

        -- Core attributes
        name            VARCHAR(100) NOT NULL UNIQUE,
        description     VARCHAR(250),
        interesting_fact VARCHAR(250),

        -- Geographic data
        area_sq_mile    NUMERIC(15, 2),
        area_sq_km      NUMERIC(15, 2),

        -- Demographic data
        population      BIGINT,
        ppp             NUMERIC(18, 2),
        life_expectancy NUMERIC(8, 2),

        -- Safety/Risk indicators
        travel_risk_level VARCHAR(50),

        -- Peace index
        global_peace_index_score NUMERIC(8, 3),
        global_peace_index_rank  INTEGER,

        -- Happiness index
        happiness_index_score NUMERIC(8, 3),
        happiness_index_rank  INTEGER,

        -- Economic indicators
        gdp                 NUMERIC(18, 2),
        gdp_growth_rate     NUMERIC(8, 2),
        inflation_rate      NUMERIC(8, 2),
        unemployment_rate   NUMERIC(8, 2),
        govt_debt           NUMERIC(8, 2),
        credit_rating       VARCHAR(10),
        poverty_rate        NUMERIC(8, 2),
        gini_coefficient    NUMERIC(8, 2),
        military_spending   NUMERIC(8, 2),
        gdp_per_capita      NUMERIC(12, 2),  -- NEW COLUMN

        -- Audit timestamps
        created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

        -- Foreign key constraints
        CONSTRAINT fk_countries_ai_models
            FOREIGN KEY (ai_model_id)
            REFERENCES ai_models (ai_model_id)
            ON DELETE SET NULL
            ON UPDATE CASCADE,

        CONSTRAINT fk_countries_continents
            FOREIGN KEY (continent_id)
            REFERENCES continents (continent_id)
            ON DELETE SET NULL
            ON UPDATE CASCADE
    );

    -- Step 7: Restore data from backup (use OVERRIDING SYSTEM VALUE for identity column)
    INSERT INTO countries (
        country_id, ai_model_id, continent_id, name, description, interesting_fact,
        area_sq_mile, area_sq_km, population, ppp, life_expectancy, travel_risk_level,
        global_peace_index_score, global_peace_index_rank,
        happiness_index_score, happiness_index_rank,
        gdp, gdp_growth_rate, inflation_rate, unemployment_rate,
        govt_debt, credit_rating, poverty_rate, gini_coefficient, military_spending,
        gdp_per_capita, created_at, updated_at
    )
    OVERRIDING SYSTEM VALUE
    SELECT
        country_id, ai_model_id, continent_id, name, description, interesting_fact,
        area_sq_mile, area_sq_km, population, ppp, life_expectancy, travel_risk_level,
        global_peace_index_score, global_peace_index_rank,
        happiness_index_score, happiness_index_rank,
        gdp, gdp_growth_rate, inflation_rate, unemployment_rate,
        govt_debt, credit_rating, poverty_rate, gini_coefficient, military_spending,
        NULL,  -- gdp_per_capita (new column, NULL for existing rows)
        created_at, updated_at
    FROM countries_backup;

    -- Step 8: Reset identity sequence to max value
    PERFORM setval(
        pg_get_serial_sequence('countries', 'country_id'),
        COALESCE((SELECT MAX(country_id) FROM countries), 0) + 1,
        false
    );

    -- Step 9: Recreate indexes
    CREATE INDEX idx_countries_name ON countries (name);
    CREATE INDEX idx_countries_ai_model_id ON countries (ai_model_id);
    CREATE INDEX idx_countries_continent_id ON countries (continent_id);

    -- Step 10: Recreate cities FK constraint
    ALTER TABLE cities
        ADD CONSTRAINT fk_cities_countries
        FOREIGN KEY (country_id)
        REFERENCES countries (country_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE;

    -- Step 11: Add table and column comments
    COMMENT ON TABLE countries IS 'Country information with economic and quality-of-life indicators from LLM structured outputs';
    COMMENT ON COLUMN countries.gdp_per_capita IS 'Gross Domestic Product per capita in USD';

    -- Step 12: Cleanup temp table
    DROP TABLE countries_backup;

    RAISE NOTICE 'Successfully added gdp_per_capita column to countries table.';
END $$;

COMMIT;
