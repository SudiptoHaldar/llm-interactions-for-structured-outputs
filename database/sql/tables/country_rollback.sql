-- ============================================================================
-- Rollback: Remove continent_id FK from countries table
-- Description: Removes continent_id column and FK constraint
-- WARNING: This will permanently delete the continent_id data!
-- Version: 1.1.0
-- Created: 2026-01-03
-- ============================================================================

-- Remove continent_id column if it exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'countries'
        AND column_name = 'continent_id'
    ) THEN
        -- Drop the index first
        DROP INDEX IF EXISTS idx_countries_continent_id;

        -- Drop the foreign key constraint
        ALTER TABLE countries DROP CONSTRAINT IF EXISTS fk_countries_continents;

        -- Drop the column
        ALTER TABLE countries DROP COLUMN continent_id;

        RAISE NOTICE 'Removed continent_id column from countries table';
    ELSE
        RAISE NOTICE 'Column continent_id does not exist in countries table';
    END IF;
END $$;
