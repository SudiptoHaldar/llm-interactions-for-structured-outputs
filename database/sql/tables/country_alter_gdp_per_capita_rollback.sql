-- ============================================================================
-- Rollback: Remove gdp_per_capita column from countries table
-- Description: Reverses the gdp_per_capita migration
-- Version: 1.3.0
-- Created: 2026-01-17
-- WARNING: This will remove the gdp_per_capita column and its data!
-- ============================================================================

BEGIN;

-- Check if column exists before removing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'countries' AND column_name = 'gdp_per_capita'
    ) THEN
        RAISE NOTICE 'Column gdp_per_capita does not exist. Skipping rollback.';
        RETURN;
    END IF;

    -- Simply drop the column (no need to recreate table for removal)
    ALTER TABLE countries DROP COLUMN gdp_per_capita;

    RAISE NOTICE 'Successfully removed gdp_per_capita column from countries table.';
END $$;

COMMIT;
