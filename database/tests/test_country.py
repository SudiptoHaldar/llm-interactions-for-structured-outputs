"""Tests for country table operations."""

from unittest.mock import MagicMock, patch

from database.sql.tables.country import SCRIPT_DIR


class TestSqlScripts:
    """Tests for SQL script files."""

    def test_create_script_exists(self) -> None:
        """Test that create script file exists."""
        script = SCRIPT_DIR / "country_create.sql"
        assert script.exists(), f"Script not found: {script}"

    def test_cleanup_script_exists(self) -> None:
        """Test that cleanup script file exists."""
        script = SCRIPT_DIR / "country_cleanup.sql"
        assert script.exists(), f"Script not found: {script}"

    def test_create_script_has_table_definition(self) -> None:
        """Test that create script contains table definition."""
        script = SCRIPT_DIR / "country_create.sql"
        content = script.read_text()

        assert "CREATE TABLE" in content
        assert "countries" in content
        assert "country_id" in content
        assert "ai_model_id" in content
        assert "GENERATED ALWAYS AS IDENTITY" in content

    def test_create_script_has_all_required_columns(self) -> None:
        """Test that create script contains all required columns."""
        script = SCRIPT_DIR / "country_create.sql"
        content = script.read_text()

        required_columns = [
            "name",
            "description",
            "interesting_fact",
            "area_sq_mile",
            "area_sq_km",
            "population",
            "ppp",
            "life_expectancy",
            "travel_risk_level",
            "global_peace_index_score",
            "global_peace_index_rank",
            "happiness_index_score",
            "happiness_index_rank",
            "gdp",
            "gdp_growth_rate",
            "inflation_rate",
            "unemployment_rate",
            "govt_debt",
            "credit_rating",
            "poverty_rate",
            "gini_coefficient",
            "military_spending",
        ]

        for col in required_columns:
            assert col in content, f"Missing column: {col}"

    def test_create_script_has_foreign_key(self) -> None:
        """Test that create script has foreign key to ai_models."""
        script = SCRIPT_DIR / "country_create.sql"
        content = script.read_text()

        assert "FOREIGN KEY" in content or "fk_countries_ai_models" in content
        assert "ai_models" in content

    def test_create_script_has_indexes(self) -> None:
        """Test that create script creates indexes."""
        script = SCRIPT_DIR / "country_create.sql"
        content = script.read_text()

        assert "idx_countries_name" in content
        assert "idx_countries_ai_model_id" in content

    def test_cleanup_script_has_drop(self) -> None:
        """Test that cleanup script contains DROP statement."""
        script = SCRIPT_DIR / "country_cleanup.sql"
        content = script.read_text()

        assert "DROP TABLE" in content
        assert "countries" in content


class TestCountryFunctions:
    """Tests for country module functions."""

    @patch("database.sql.tables.country.execute_sql_file")
    def test_create_table_calls_executor(self, mock_execute: MagicMock) -> None:
        """Test create_table calls execute_sql_file with correct path."""
        from database.sql.tables.country import create_table

        mock_execute.return_value = True
        result = create_table()

        assert result is True
        mock_execute.assert_called_once()
        call_path = mock_execute.call_args[0][0]
        assert call_path.name == "country_create.sql"

    @patch("database.sql.tables.country.execute_sql_file")
    def test_cleanup_table_calls_executor(self, mock_execute: MagicMock) -> None:
        """Test cleanup_table calls execute_sql_file with correct path."""
        from database.sql.tables.country import cleanup_table

        mock_execute.return_value = True
        result = cleanup_table()

        assert result is True
        mock_execute.assert_called_once()
        call_path = mock_execute.call_args[0][0]
        assert call_path.name == "country_cleanup.sql"

    @patch("database.sql.tables.country.table_exists")
    def test_exists_calls_table_exists(self, mock_exists: MagicMock) -> None:
        """Test exists() calls table_exists with correct table name."""
        from database.sql.tables.country import exists

        mock_exists.return_value = True
        result = exists()

        assert result is True
        mock_exists.assert_called_once_with("countries")
