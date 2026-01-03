-- ============================================================================
-- Migration: continents table - Add ai_model_id FK
-- Description: Add foreign key to track which AI model provided the data
-- Version: 1.0.0
-- Created: 2026-01-03
-- Prerequisite: ai_models table must exist
-- ============================================================================

-- Add ai_model_id column if it doesn't exist
-- Note: Column is nullable to allow existing rows without values
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'continents'
        AND column_name = 'ai_model_id'
    ) THEN
        ALTER TABLE continents
        ADD COLUMN ai_model_id INTEGER;
    END IF;
END $$;

-- Add foreign key constraint if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_continents_ai_models'
        AND table_name = 'continents'
    ) THEN
        ALTER TABLE continents
        ADD CONSTRAINT fk_continents_ai_models
        FOREIGN KEY (ai_model_id)
        REFERENCES ai_models (ai_model_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;
    END IF;
END $$;

-- Create index on ai_model_id for faster joins (if not exists)
CREATE INDEX IF NOT EXISTS idx_continents_ai_model_id ON continents (ai_model_id);

-- Add column comment
COMMENT ON COLUMN continents.ai_model_id IS 'Foreign key to ai_models - tracks which AI model provided this data';
