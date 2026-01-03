-- ============================================================================
-- Table: ai_models
-- Description: AI/LLM model providers and their models for structured outputs
-- Version: 1.0.0
-- Created: 2026-01-03
-- ============================================================================

-- Create ai_models table if not exists
CREATE TABLE IF NOT EXISTS ai_models (
    -- Primary key (SQL-standard identity column)
    ai_model_id     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Core attributes
    model_provider  VARCHAR(50) NOT NULL,
    model_name      VARCHAR(100) NOT NULL,
    description     VARCHAR(250),

    -- Model capabilities/metadata
    supports_structured_output  BOOLEAN DEFAULT TRUE,
    is_active       BOOLEAN DEFAULT TRUE,

    -- Audit timestamps
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint on provider + model combination
    CONSTRAINT uq_ai_models_provider_model UNIQUE (model_provider, model_name)
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_ai_models_provider ON ai_models (model_provider);
CREATE INDEX IF NOT EXISTS idx_ai_models_name ON ai_models (model_name);
CREATE INDEX IF NOT EXISTS idx_ai_models_active ON ai_models (is_active) WHERE is_active = TRUE;

-- Add comment to table
COMMENT ON TABLE ai_models IS 'AI/LLM model providers and their models for structured output interactions';

-- Add comments to columns
COMMENT ON COLUMN ai_models.ai_model_id IS 'Auto-generated identity primary key';
COMMENT ON COLUMN ai_models.model_provider IS 'AI provider name (e.g., OpenAI, Anthropic, Google)';
COMMENT ON COLUMN ai_models.model_name IS 'Model identifier (e.g., gpt-4o, claude-3-opus, gemini-pro)';
COMMENT ON COLUMN ai_models.description IS 'Brief description of the model';
COMMENT ON COLUMN ai_models.supports_structured_output IS 'Whether the model supports structured output';
COMMENT ON COLUMN ai_models.is_active IS 'Whether the model is currently active/available';
COMMENT ON COLUMN ai_models.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN ai_models.updated_at IS 'Last update timestamp';
