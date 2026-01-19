-- ============================================================================
-- Cleanup: glossary
-- Description: Drop glossary table and related objects
-- WARNING: This will permanently delete all data!
-- ============================================================================

-- Drop indexes first
DROP INDEX IF EXISTS idx_glossary_entry;

-- Drop table
DROP TABLE IF EXISTS glossary;
