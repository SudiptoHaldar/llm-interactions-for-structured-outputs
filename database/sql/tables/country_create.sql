-- ============================================================================
-- Table: countries
-- Description: Country information with economic and quality-of-life indicators
-- Version: 1.4.0
-- Created: 2026-01-03
-- Updated: 2026-01-04 - Increased ppp precision to NUMERIC(18,2) for large economies
-- Updated: 2026-01-17 - Added gdp_per_capita column
-- Updated: 2026-01-18 - Increased precision of percentage fields to NUMERIC(8,2)
-- Prerequisites: ai_models and continents tables must be created first
-- ============================================================================

-- Create countries table if not exists
CREATE TABLE IF NOT EXISTS countries (
    -- Primary key (SQL-standard identity column)
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

    -- Peace index (Institute for Economics & Peace)
    global_peace_index_score NUMERIC(8, 3),
    global_peace_index_rank  INTEGER,

    -- Happiness index (Oxford Wellbeing Research Centre)
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
    gdp_per_capita      NUMERIC(12, 2),

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

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_countries_name ON countries (name);
CREATE INDEX IF NOT EXISTS idx_countries_ai_model_id ON countries (ai_model_id);
CREATE INDEX IF NOT EXISTS idx_countries_continent_id ON countries (continent_id);

-- Add comment to table
COMMENT ON TABLE countries IS 'Country information with economic and quality-of-life indicators from LLM structured outputs';

-- Add comments to columns
COMMENT ON COLUMN countries.country_id IS 'Auto-generated identity primary key';
COMMENT ON COLUMN countries.ai_model_id IS 'Foreign key to ai_models - tracks which AI model provided this data';
COMMENT ON COLUMN countries.continent_id IS 'Foreign key to continents - the continent this country belongs to';
COMMENT ON COLUMN countries.name IS 'Country name (unique)';
COMMENT ON COLUMN countries.description IS 'Brief description of the country (max 250 chars)';
COMMENT ON COLUMN countries.interesting_fact IS 'Notable fact about the country (max 250 chars)';
COMMENT ON COLUMN countries.area_sq_mile IS 'Total area in square miles';
COMMENT ON COLUMN countries.area_sq_km IS 'Total area in square kilometers';
COMMENT ON COLUMN countries.population IS 'Total population';
COMMENT ON COLUMN countries.ppp IS 'Purchasing power parity in USD';
COMMENT ON COLUMN countries.life_expectancy IS 'Life expectancy in years';
COMMENT ON COLUMN countries.travel_risk_level IS 'US State Dept travel advisory level';
COMMENT ON COLUMN countries.global_peace_index_score IS 'Global Peace Index score (IEP)';
COMMENT ON COLUMN countries.global_peace_index_rank IS 'Global Peace Index rank (IEP)';
COMMENT ON COLUMN countries.happiness_index_score IS 'World Happiness Report score (Oxford)';
COMMENT ON COLUMN countries.happiness_index_rank IS 'World Happiness Report rank (Oxford)';
COMMENT ON COLUMN countries.gdp IS 'Gross Domestic Product in USD';
COMMENT ON COLUMN countries.gdp_growth_rate IS 'GDP growth rate percentage';
COMMENT ON COLUMN countries.inflation_rate IS 'Inflation rate percentage';
COMMENT ON COLUMN countries.unemployment_rate IS 'Unemployment rate percentage';
COMMENT ON COLUMN countries.govt_debt IS 'Government debt as percentage of GDP';
COMMENT ON COLUMN countries.credit_rating IS 'S&P credit rating';
COMMENT ON COLUMN countries.poverty_rate IS 'Poverty rate percentage';
COMMENT ON COLUMN countries.gini_coefficient IS 'Gini coefficient (income inequality measure)';
COMMENT ON COLUMN countries.military_spending IS 'Military spending as percentage of GDP';
COMMENT ON COLUMN countries.gdp_per_capita IS 'Gross Domestic Product per capita in USD';
COMMENT ON COLUMN countries.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN countries.updated_at IS 'Last update timestamp';
