-- ============================================================================
-- Rollback: continents table - Remove ai_model_id FK
-- Description: Remove the ai_model_id column and related constraints
-- Version: 1.0.0
-- Created: 2026-01-03
-- WARNING: This will permanently remove ai_model_id data from continents!
-- ============================================================================

-- Drop index first (if exists)
DROP INDEX IF EXISTS idx_continents_ai_model_id;

-- Drop foreign key constraint (if exists)
ALTER TABLE continents
DROP CONSTRAINT IF EXISTS fk_continents_ai_models;

-- Drop column (if exists)
ALTER TABLE continents
DROP COLUMN IF EXISTS ai_model_id;
