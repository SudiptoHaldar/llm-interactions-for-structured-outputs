"""Tests for ai_model table operations."""

from unittest.mock import MagicMock, patch

from database.sql.tables.ai_model import SCRIPT_DIR


class TestSqlScripts:
    """Tests for SQL script files."""

    def test_create_script_exists(self) -> None:
        """Test that create script file exists."""
        script = SCRIPT_DIR / "ai_model_create.sql"
        assert script.exists(), f"Script not found: {script}"

    def test_cleanup_script_exists(self) -> None:
        """Test that cleanup script file exists."""
        script = SCRIPT_DIR / "ai_model_cleanup.sql"
        assert script.exists(), f"Script not found: {script}"

    def test_create_script_has_table_definition(self) -> None:
        """Test that create script contains table definition."""
        script = SCRIPT_DIR / "ai_model_create.sql"
        content = script.read_text()

        assert "CREATE TABLE" in content
        assert "ai_models" in content
        assert "ai_model_id" in content
        assert "model_provider" in content
        assert "model_name" in content
        assert "GENERATED ALWAYS AS IDENTITY" in content

    def test_cleanup_script_has_drop(self) -> None:
        """Test that cleanup script contains DROP statement."""
        script = SCRIPT_DIR / "ai_model_cleanup.sql"
        content = script.read_text()

        assert "DROP TABLE" in content
        assert "ai_models" in content

    def test_create_script_has_unique_constraint(self) -> None:
        """Test that create script has unique constraint on provider+model."""
        script = SCRIPT_DIR / "ai_model_create.sql"
        content = script.read_text()

        assert "UNIQUE" in content
        assert "model_provider" in content
        assert "model_name" in content


class TestAiModelFunctions:
    """Tests for ai_model module functions."""

    @patch("database.sql.tables.ai_model.execute_sql_file")
    def test_create_table_calls_executor(self, mock_execute: MagicMock) -> None:
        """Test create_table calls execute_sql_file with correct path."""
        from database.sql.tables.ai_model import create_table

        mock_execute.return_value = True
        result = create_table()

        assert result is True
        mock_execute.assert_called_once()
        call_path = mock_execute.call_args[0][0]
        assert call_path.name == "ai_model_create.sql"

    @patch("database.sql.tables.ai_model.execute_sql_file")
    def test_cleanup_table_calls_executor(self, mock_execute: MagicMock) -> None:
        """Test cleanup_table calls execute_sql_file with correct path."""
        from database.sql.tables.ai_model import cleanup_table

        mock_execute.return_value = True
        result = cleanup_table()

        assert result is True
        mock_execute.assert_called_once()
        call_path = mock_execute.call_args[0][0]
        assert call_path.name == "ai_model_cleanup.sql"

    @patch("database.sql.tables.ai_model.table_exists")
    def test_exists_calls_table_exists(self, mock_exists: MagicMock) -> None:
        """Test exists() calls table_exists with correct table name."""
        from database.sql.tables.ai_model import exists

        mock_exists.return_value = True
        result = exists()

        assert result is True
        mock_exists.assert_called_once_with("ai_models")
