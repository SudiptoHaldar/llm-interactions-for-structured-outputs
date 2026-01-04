-- ============================================================================
-- Cleanup: countries table
-- Description: Drop countries table and related objects
-- Version: 1.0.0
-- Created: 2026-01-03
-- WARNING: This will permanently delete all data in the countries table!
-- ============================================================================

-- Drop indexes first (if exist)
DROP INDEX IF EXISTS idx_countries_name;
DROP INDEX IF EXISTS idx_countries_ai_model_id;

-- Drop table
DROP TABLE IF EXISTS countries CASCADE;
