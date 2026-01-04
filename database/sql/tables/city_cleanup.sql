-- ============================================================================
-- Cleanup: cities table
-- Description: Drop cities table and related objects
-- Version: 1.0.0
-- Created: 2026-01-03
-- WARNING: This will permanently delete all data in the cities table!
-- ============================================================================

-- Drop indexes first (if exist)
DROP INDEX IF EXISTS idx_cities_name;
DROP INDEX IF EXISTS idx_cities_country_id;
DROP INDEX IF EXISTS idx_cities_airport_code;

-- Drop table
DROP TABLE IF EXISTS cities CASCADE;
