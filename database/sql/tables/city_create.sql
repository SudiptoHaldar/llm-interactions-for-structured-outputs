-- ============================================================================
-- Table: cities
-- Description: City information with safety indices and airport data
-- Version: 1.1.0
-- Created: 2026-01-03
-- Updated: 2026-01-04 - Added is_capital column
-- Prerequisite: countries table must be created first
-- ============================================================================

-- Create cities table if not exists
CREATE TABLE IF NOT EXISTS cities (
    -- Primary key (SQL-standard identity column)
    city_id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Foreign key to countries
    country_id      INTEGER,

    -- Core attributes
    name            VARCHAR(100) NOT NULL,
    is_capital      BOOLEAN DEFAULT FALSE,
    description     VARCHAR(250),
    interesting_fact VARCHAR(250),

    -- Geographic data
    area_sq_mile    NUMERIC(15, 2),
    area_sq_km      NUMERIC(15, 2),

    -- Demographic data
    population      BIGINT,

    -- Safety indices (Economist Intelligence Unit - Safe Cities Index)
    sci_score       NUMERIC(5, 2),
    sci_rank        INTEGER,

    -- Safety indices (Numbeo)
    numbeo_si       NUMERIC(5, 2),
    numbeo_ci       NUMERIC(5, 2),

    -- Travel data
    airport_code    CHAR(3),

    -- Audit timestamps
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint (countries must be created first)
    CONSTRAINT fk_cities_countries
        FOREIGN KEY (country_id)
        REFERENCES countries (country_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    -- Composite unique constraint (city name unique within a country)
    CONSTRAINT uq_cities_country_name UNIQUE (country_id, name)
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_cities_name ON cities (name);
CREATE INDEX IF NOT EXISTS idx_cities_country_id ON cities (country_id);
CREATE INDEX IF NOT EXISTS idx_cities_airport_code ON cities (airport_code);

-- Add comment to table
COMMENT ON TABLE cities IS 'City information with safety indices and airport data from LLM structured outputs';

-- Add comments to columns
COMMENT ON COLUMN cities.city_id IS 'Auto-generated identity primary key';
COMMENT ON COLUMN cities.country_id IS 'Foreign key to countries - the country this city belongs to';
COMMENT ON COLUMN cities.name IS 'City name (unique within country)';
COMMENT ON COLUMN cities.is_capital IS 'Whether this city is the capital of its country';
COMMENT ON COLUMN cities.description IS 'Brief description of the city (max 250 chars)';
COMMENT ON COLUMN cities.interesting_fact IS 'Notable fact about the city (max 250 chars)';
COMMENT ON COLUMN cities.area_sq_mile IS 'Total area in square miles';
COMMENT ON COLUMN cities.area_sq_km IS 'Total area in square kilometers';
COMMENT ON COLUMN cities.population IS 'Total population';
COMMENT ON COLUMN cities.sci_score IS 'Economist Intelligence Unit Safe Cities Index score (0-100)';
COMMENT ON COLUMN cities.sci_rank IS 'Economist Intelligence Unit Safe Cities Index rank';
COMMENT ON COLUMN cities.numbeo_si IS 'Numbeo Safety Index (0-100)';
COMMENT ON COLUMN cities.numbeo_ci IS 'Numbeo Crime Index (0-100)';
COMMENT ON COLUMN cities.airport_code IS 'IATA 3-letter airport code for nearest international airport';
COMMENT ON COLUMN cities.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN cities.updated_at IS 'Last update timestamp';
