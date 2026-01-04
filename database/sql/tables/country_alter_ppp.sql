-- ============================================================================
-- Table: countries
-- Description: Alter ppp column precision from NUMERIC(15,2) to NUMERIC(18,2)
-- Version: 1.2.0
-- Created: 2026-01-04
-- Issue: India's PPP ($13.5 trillion) exceeds NUMERIC(15,2) max of $10 trillion
-- ============================================================================

-- Increase ppp column precision to match gdp column
ALTER TABLE countries
    ALTER COLUMN ppp TYPE NUMERIC(18, 2);

-- Update column comment
COMMENT ON COLUMN countries.ppp IS 'Purchasing power parity in USD (increased precision for large economies)';

-- ============================================================================
-- Rollback script (if needed):
-- ALTER TABLE countries ALTER COLUMN ppp TYPE NUMERIC(15, 2);
-- ============================================================================
