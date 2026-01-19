-- ============================================================================
-- Migration: Increase precision of numeric fields in countries table
-- Description: Increases precision of NUMERIC(5,2) fields to handle LLM edge cases
-- Version: 1.4.0
-- Created: 2026-01-18
-- Issue: LLM sometimes returns values outside expected range (e.g., large gini values)
-- ============================================================================

BEGIN;

-- Increase precision for fields that might receive unexpected large values
-- Using NUMERIC(8, 2) to handle values up to 999,999.99

ALTER TABLE countries
    ALTER COLUMN life_expectancy TYPE NUMERIC(8, 2),
    ALTER COLUMN unemployment_rate TYPE NUMERIC(8, 2),
    ALTER COLUMN poverty_rate TYPE NUMERIC(8, 2),
    ALTER COLUMN gini_coefficient TYPE NUMERIC(8, 2),
    ALTER COLUMN military_spending TYPE NUMERIC(8, 2);

-- Also increase other economic fields for consistency
ALTER TABLE countries
    ALTER COLUMN govt_debt TYPE NUMERIC(8, 2),
    ALTER COLUMN gdp_growth_rate TYPE NUMERIC(8, 2),
    ALTER COLUMN inflation_rate TYPE NUMERIC(8, 2),
    ALTER COLUMN gdp_per_capita TYPE NUMERIC(12, 2);

-- Increase precision for index score fields (NUMERIC(5,3) -> NUMERIC(8,3))
-- LLMs sometimes return values >= 100 for these
ALTER TABLE countries
    ALTER COLUMN global_peace_index_score TYPE NUMERIC(8, 3),
    ALTER COLUMN happiness_index_score TYPE NUMERIC(8, 3);

-- Update column comments
COMMENT ON COLUMN countries.life_expectancy IS 'Life expectancy in years (increased precision for LLM compatibility)';
COMMENT ON COLUMN countries.unemployment_rate IS 'Unemployment rate percentage (increased precision for LLM compatibility)';
COMMENT ON COLUMN countries.poverty_rate IS 'Poverty rate percentage (increased precision for LLM compatibility)';
COMMENT ON COLUMN countries.gini_coefficient IS 'Gini coefficient - income inequality measure (increased precision for LLM compatibility)';
COMMENT ON COLUMN countries.military_spending IS 'Military spending as percentage of GDP (increased precision for LLM compatibility)';
COMMENT ON COLUMN countries.govt_debt IS 'Government debt as percentage of GDP (increased precision for LLM compatibility)';
COMMENT ON COLUMN countries.global_peace_index_score IS 'Global Peace Index score (increased precision for LLM compatibility)';
COMMENT ON COLUMN countries.happiness_index_score IS 'World Happiness Report score (increased precision for LLM compatibility)';

COMMIT;
