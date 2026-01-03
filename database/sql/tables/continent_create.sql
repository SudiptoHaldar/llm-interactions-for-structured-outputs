-- ============================================================================
-- Table: continents
-- Description: Geographic continents with area and population data
-- Version: 1.1.0
-- Created: 2026-01-02
-- Updated: 2026-01-03 - Added ai_model_id FK
-- Prerequisite: ai_models table must be created first
-- ============================================================================

-- Create continents table if not exists
CREATE TABLE IF NOT EXISTS continents (
    -- Primary key (SQL-standard identity column)
    continent_id    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Core attributes
    name            VARCHAR(100) NOT NULL UNIQUE,
    description     VARCHAR(250),

    -- Geographic data
    area_sq_mile    NUMERIC(15, 2),
    area_sq_km      NUMERIC(15, 2),

    -- Demographic data
    population      BIGINT,
    num_country     INTEGER,

    -- Source tracking
    ai_model_id     INTEGER,

    -- Audit timestamps
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint (ai_models must be created first)
    CONSTRAINT fk_continents_ai_models
        FOREIGN KEY (ai_model_id)
        REFERENCES ai_models (ai_model_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- Create index on name for faster lookups
CREATE INDEX IF NOT EXISTS idx_continents_name ON continents (name);

-- Create index on ai_model_id for faster joins
CREATE INDEX IF NOT EXISTS idx_continents_ai_model_id ON continents (ai_model_id);

-- Add comment to table
COMMENT ON TABLE continents IS 'Geographic continents with area and population statistics';

-- Add comments to columns
COMMENT ON COLUMN continents.continent_id IS 'Auto-generated identity primary key';
COMMENT ON COLUMN continents.name IS 'Continent name (unique)';
COMMENT ON COLUMN continents.description IS 'Brief description of the continent';
COMMENT ON COLUMN continents.area_sq_mile IS 'Total area in square miles';
COMMENT ON COLUMN continents.area_sq_km IS 'Total area in square kilometers';
COMMENT ON COLUMN continents.population IS 'Total population';
COMMENT ON COLUMN continents.num_country IS 'Number of countries in the continent';
COMMENT ON COLUMN continents.ai_model_id IS 'Foreign key to ai_models - tracks which AI model provided this data';
COMMENT ON COLUMN continents.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN continents.updated_at IS 'Last update timestamp';
