-- ============================================================================
-- Migration: Add continent_id FK to countries table (with table recreation)
-- Description: Recreates table to position continent_id after ai_model_id
-- Version: 1.1.0
-- Created: 2026-01-03
-- Prerequisites: continents table must exist, cities table must NOT exist
-- WARNING: This migration recreates the table - backup data first!
-- ============================================================================

-- Check if continent_id column already exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'countries'
        AND column_name = 'continent_id'
    ) THEN
        RAISE NOTICE 'Column continent_id already exists in countries table';
        RETURN;
    END IF;

    -- Check if cities table exists (would block due to FK)
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'cities'
    ) THEN
        RAISE EXCEPTION 'Cannot recreate countries table: cities table exists with FK dependency. Drop cities table first.';
    END IF;

    -- Step 1: Create new table with correct column order
    CREATE TABLE countries_new (
        -- Primary key
        country_id      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

        -- Foreign key references (continent_id right after ai_model_id)
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
        ppp             NUMERIC(15, 2),
        life_expectancy NUMERIC(5, 2),

        -- Safety/Risk indicators
        travel_risk_level VARCHAR(50),

        -- Peace index
        global_peace_index_score NUMERIC(5, 3),
        global_peace_index_rank  INTEGER,

        -- Happiness index
        happiness_index_score NUMERIC(5, 3),
        happiness_index_rank  INTEGER,

        -- Economic indicators
        gdp                 NUMERIC(18, 2),
        gdp_growth_rate     NUMERIC(6, 2),
        inflation_rate      NUMERIC(6, 2),
        unemployment_rate   NUMERIC(5, 2),
        govt_debt           NUMERIC(6, 2),
        credit_rating       VARCHAR(10),
        poverty_rate        NUMERIC(5, 2),
        gini_coefficient    NUMERIC(5, 2),
        military_spending   NUMERIC(5, 2),

        -- Audit timestamps
        created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

        -- Foreign key constraints
        CONSTRAINT fk_countries_new_ai_models
            FOREIGN KEY (ai_model_id)
            REFERENCES ai_models (ai_model_id)
            ON DELETE SET NULL
            ON UPDATE CASCADE,

        CONSTRAINT fk_countries_new_continents
            FOREIGN KEY (continent_id)
            REFERENCES continents (continent_id)
            ON DELETE SET NULL
            ON UPDATE CASCADE
    );

    -- Step 2: Copy data from old table (continent_id will be NULL)
    INSERT INTO countries_new (
        country_id, ai_model_id, name, description, interesting_fact,
        area_sq_mile, area_sq_km, population, ppp, life_expectancy,
        travel_risk_level, global_peace_index_score, global_peace_index_rank,
        happiness_index_score, happiness_index_rank,
        gdp, gdp_growth_rate, inflation_rate, unemployment_rate,
        govt_debt, credit_rating, poverty_rate, gini_coefficient,
        military_spending, created_at, updated_at
    )
    OVERRIDING SYSTEM VALUE
    SELECT
        country_id, ai_model_id, name, description, interesting_fact,
        area_sq_mile, area_sq_km, population, ppp, life_expectancy,
        travel_risk_level, global_peace_index_score, global_peace_index_rank,
        happiness_index_score, happiness_index_rank,
        gdp, gdp_growth_rate, inflation_rate, unemployment_rate,
        govt_debt, credit_rating, poverty_rate, gini_coefficient,
        military_spending, created_at, updated_at
    FROM countries;

    -- Step 3: Reset identity sequence to max country_id + 1
    PERFORM setval(
        pg_get_serial_sequence('countries_new', 'country_id'),
        COALESCE((SELECT MAX(country_id) FROM countries_new), 0) + 1,
        false
    );

    -- Step 4: Drop old table
    DROP TABLE countries;

    -- Step 5: Rename new table
    ALTER TABLE countries_new RENAME TO countries;

    -- Step 6: Rename constraints
    ALTER TABLE countries
        RENAME CONSTRAINT fk_countries_new_ai_models TO fk_countries_ai_models;
    ALTER TABLE countries
        RENAME CONSTRAINT fk_countries_new_continents TO fk_countries_continents;

    -- Step 7: Create indexes
    CREATE INDEX idx_countries_name ON countries (name);
    CREATE INDEX idx_countries_ai_model_id ON countries (ai_model_id);
    CREATE INDEX idx_countries_continent_id ON countries (continent_id);

    -- Step 8: Add table comment
    COMMENT ON TABLE countries IS
        'Country information with economic and quality-of-life indicators from LLM structured outputs';

    -- Step 9: Add column comments
    COMMENT ON COLUMN countries.country_id IS 'Auto-generated identity primary key';
    COMMENT ON COLUMN countries.ai_model_id IS 'Foreign key to ai_models - tracks which AI model provided this data';
    COMMENT ON COLUMN countries.continent_id IS 'Foreign key to continents - the continent this country belongs to';
    COMMENT ON COLUMN countries.name IS 'Country name (unique)';

    RAISE NOTICE 'Successfully recreated countries table with continent_id column';
END $$;
