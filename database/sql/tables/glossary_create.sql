-- ============================================================================
-- Table: glossary
-- Description: Economic and quality-of-life indicator definitions
-- Version: 1.0.0
-- Created: 2026-01-10
-- ============================================================================

-- Create glossary table if not exists
CREATE TABLE IF NOT EXISTS glossary (
    -- Primary key (SQL-standard identity column)
    glossary_id     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Core attributes
    entry           VARCHAR(50) NOT NULL UNIQUE,
    meaning         TEXT NOT NULL,
    range           VARCHAR(25),
    interpretation  VARCHAR(25),

    -- Audit timestamps
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster lookups by entry
CREATE INDEX IF NOT EXISTS idx_glossary_entry ON glossary (entry);

-- Add comment to table
COMMENT ON TABLE glossary IS 'Economic and quality-of-life indicator definitions';

-- Add comments to columns
COMMENT ON COLUMN glossary.glossary_id IS 'Auto-generated identity primary key';
COMMENT ON COLUMN glossary.entry IS 'Indicator name (unique identifier)';
COMMENT ON COLUMN glossary.meaning IS 'Full description of the indicator';
COMMENT ON COLUMN glossary.range IS 'Valid value range (e.g., "0 - 100", "Numeric")';
COMMENT ON COLUMN glossary.interpretation IS 'How to interpret values (e.g., "Lower is better")';
COMMENT ON COLUMN glossary.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN glossary.updated_at IS 'Last update timestamp';
