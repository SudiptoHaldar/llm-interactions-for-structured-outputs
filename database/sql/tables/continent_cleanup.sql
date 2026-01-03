-- ============================================================================
-- Cleanup: continents table
-- Description: Drop continents table and related objects
-- Version: 1.0.0
-- Created: 2026-01-02
-- WARNING: This will permanently delete all data in the continents table!
-- ============================================================================

-- Drop index first (if exists)
DROP INDEX IF EXISTS idx_continents_name;

-- Drop table
DROP TABLE IF EXISTS continents CASCADE;
