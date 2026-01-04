"""Tests for city table operations."""

from unittest.mock import MagicMock, patch

from database.sql.tables.city import SCRIPT_DIR


class TestSqlScripts:
    """Tests for SQL script files."""

    def test_create_script_exists(self) -> None:
        """Test that create script file exists."""
        script = SCRIPT_DIR / "city_create.sql"
        assert script.exists(), f"Script not found: {script}"

    def test_cleanup_script_exists(self) -> None:
        """Test that cleanup script file exists."""
        script = SCRIPT_DIR / "city_cleanup.sql"
        assert script.exists(), f"Script not found: {script}"

    def test_create_script_has_table_definition(self) -> None:
        """Test that create script contains table definition."""
        script = SCRIPT_DIR / "city_create.sql"
        content = script.read_text()

        assert "CREATE TABLE" in content
        assert "cities" in content
        assert "city_id" in content
        assert "country_id" in content
        assert "GENERATED ALWAYS AS IDENTITY" in content

    def test_create_script_has_all_required_columns(self) -> None:
        """Test that create script contains all required columns."""
        script = SCRIPT_DIR / "city_create.sql"
        content = script.read_text()

        required_columns = [
            "name",
            "description",
            "interesting_fact",
            "area_sq_mile",
            "area_sq_km",
            "population",
            "sci_score",
            "sci_rank",
            "numbeo_si",
            "numbeo_ci",
            "airport_code",
        ]

        for col in required_columns:
            assert col in content, f"Missing column: {col}"

    def test_create_script_has_foreign_key(self) -> None:
        """Test that create script has foreign key to countries."""
        script = SCRIPT_DIR / "city_create.sql"
        content = script.read_text()

        assert "FOREIGN KEY" in content or "fk_cities_countries" in content
        assert "countries" in content

    def test_create_script_has_indexes(self) -> None:
        """Test that create script creates indexes."""
        script = SCRIPT_DIR / "city_create.sql"
        content = script.read_text()

        assert "idx_cities_name" in content
        assert "idx_cities_country_id" in content

    def test_create_script_has_composite_unique(self) -> None:
        """Test that create script has composite unique constraint."""
        script = SCRIPT_DIR / "city_create.sql"
        content = script.read_text()

        assert "uq_cities_country_name" in content or "UNIQUE" in content

    def test_cleanup_script_has_drop(self) -> None:
        """Test that cleanup script contains DROP statement."""
        script = SCRIPT_DIR / "city_cleanup.sql"
        content = script.read_text()

        assert "DROP TABLE" in content
        assert "cities" in content


class TestCityFunctions:
    """Tests for city module functions."""

    @patch("database.sql.tables.city.execute_sql_file")
    def test_create_table_calls_executor(self, mock_execute: MagicMock) -> None:
        """Test create_table calls execute_sql_file with correct path."""
        from database.sql.tables.city import create_table

        mock_execute.return_value = True
        result = create_table()

        assert result is True
        mock_execute.assert_called_once()
        call_path = mock_execute.call_args[0][0]
        assert call_path.name == "city_create.sql"

    @patch("database.sql.tables.city.execute_sql_file")
    def test_cleanup_table_calls_executor(self, mock_execute: MagicMock) -> None:
        """Test cleanup_table calls execute_sql_file with correct path."""
        from database.sql.tables.city import cleanup_table

        mock_execute.return_value = True
        result = cleanup_table()

        assert result is True
        mock_execute.assert_called_once()
        call_path = mock_execute.call_args[0][0]
        assert call_path.name == "city_cleanup.sql"

    @patch("database.sql.tables.city.table_exists")
    def test_exists_calls_table_exists(self, mock_exists: MagicMock) -> None:
        """Test exists() calls table_exists with correct table name."""
        from database.sql.tables.city import exists

        mock_exists.return_value = True
        result = exists()

        assert result is True
        mock_exists.assert_called_once_with("cities")
