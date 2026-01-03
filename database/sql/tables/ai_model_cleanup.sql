-- ============================================================================
-- Cleanup: ai_models table
-- Description: Drop ai_models table and related objects
-- Version: 1.0.0
-- Created: 2026-01-03
-- WARNING: This will permanently delete all data in the ai_models table!
-- ============================================================================

-- Drop indexes first (if exist)
DROP INDEX IF EXISTS idx_ai_models_provider;
DROP INDEX IF EXISTS idx_ai_models_name;
DROP INDEX IF EXISTS idx_ai_models_active;

-- Drop table
DROP TABLE IF EXISTS ai_models CASCADE;
