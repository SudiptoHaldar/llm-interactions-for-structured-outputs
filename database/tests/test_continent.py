"""Tests for continent table operations."""

from unittest.mock import MagicMock, patch

from database.executor import parse_database_url, table_exists
from database.sql.tables.continent import SCRIPT_DIR


class TestParseUrl:
    """Tests for database URL parsing."""

    def test_parse_full_url(self) -> None:
        """Test parsing complete database URL."""
        url = "postgresql://user:password@localhost:5432/testdb"
        result = parse_database_url(url)

        assert result["host"] == "localhost"
        assert result["port"] == "5432"
        assert result["user"] == "user"
        assert result["password"] == "password"
        assert result["database"] == "testdb"

    def test_parse_asyncpg_url(self) -> None:
        """Test parsing asyncpg URL format."""
        url = "postgresql+asyncpg://user:pass@host:5433/db"
        result = parse_database_url(url)

        assert result["host"] == "host"
        assert result["port"] == "5433"
        assert result["user"] == "user"
        assert result["password"] == "pass"
        assert result["database"] == "db"

    def test_parse_url_default_port(self) -> None:
        """Test URL with default port."""
        url = "postgresql://user:pass@localhost/db"
        result = parse_database_url(url)

        assert result["port"] == "5432"


class TestSqlScripts:
    """Tests for SQL script files."""

    def test_create_script_exists(self) -> None:
        """Test that create script file exists."""
        script = SCRIPT_DIR / "continent_create.sql"
        assert script.exists(), f"Script not found: {script}"

    def test_cleanup_script_exists(self) -> None:
        """Test that cleanup script file exists."""
        script = SCRIPT_DIR / "continent_cleanup.sql"
        assert script.exists(), f"Script not found: {script}"

    def test_create_script_has_table_definition(self) -> None:
        """Test that create script contains table definition."""
        script = SCRIPT_DIR / "continent_create.sql"
        content = script.read_text()

        assert "CREATE TABLE" in content
        assert "continents" in content
        assert "continent_id" in content
        assert "name" in content
        assert "description" in content
        assert "area_sq_mile" in content
        assert "area_sq_km" in content
        assert "population" in content
        assert "num_country" in content

    def test_cleanup_script_has_drop(self) -> None:
        """Test that cleanup script contains DROP statement."""
        script = SCRIPT_DIR / "continent_cleanup.sql"
        content = script.read_text()

        assert "DROP TABLE" in content
        assert "continents" in content


class TestTableExists:
    """Tests for table_exists function."""

    @patch("database.executor.psycopg2.connect")
    def test_table_exists_returns_true(self, mock_connect: MagicMock) -> None:
        """Test table_exists returns True when table exists."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (True,)
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = table_exists("continents", "postgresql://u:p@h:5432/db")

        assert result is True

    @patch("database.executor.psycopg2.connect")
    def test_table_exists_returns_false(self, mock_connect: MagicMock) -> None:
        """Test table_exists returns False when table doesn't exist."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (False,)
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = table_exists("nonexistent", "postgresql://u:p@h:5432/db")

        assert result is False


class TestAlterScripts:
    """Tests for ALTER TABLE scripts."""

    def test_alter_script_exists(self) -> None:
        """Test that alter script file exists."""
        script = SCRIPT_DIR / "continent_alter_v1.sql"
        assert script.exists(), f"Script not found: {script}"

    def test_rollback_script_exists(self) -> None:
        """Test that rollback script file exists."""
        script = SCRIPT_DIR / "continent_alter_v1_rollback.sql"
        assert script.exists(), f"Script not found: {script}"

    def test_alter_script_adds_ai_model_id(self) -> None:
        """Test that alter script adds ai_model_id column."""
        script = SCRIPT_DIR / "continent_alter_v1.sql"
        content = script.read_text()

        assert "ai_model_id" in content
        assert "FOREIGN KEY" in content or "fk_continents_ai_models" in content
        assert "ai_models" in content

    def test_rollback_script_drops_column(self) -> None:
        """Test that rollback script drops ai_model_id column."""
        script = SCRIPT_DIR / "continent_alter_v1_rollback.sql"
        content = script.read_text()

        assert "DROP" in content
        assert "ai_model_id" in content

    def test_create_script_has_ai_model_id(self) -> None:
        """Test that create script includes ai_model_id for fresh installs."""
        script = SCRIPT_DIR / "continent_create.sql"
        content = script.read_text()

        assert "ai_model_id" in content


class TestAlterFunctions:
    """Tests for alter/rollback functions."""

    @patch("database.sql.tables.continent.execute_sql_file")
    def test_alter_table_calls_executor(self, mock_execute: MagicMock) -> None:
        """Test alter_table calls execute_sql_file with correct path."""
        from database.sql.tables.continent import alter_table

        mock_execute.return_value = True
        result = alter_table()

        assert result is True
        mock_execute.assert_called_once()
        call_path = mock_execute.call_args[0][0]
        assert call_path.name == "continent_alter_v1.sql"

    @patch("database.sql.tables.continent.execute_sql_file")
    def test_rollback_alter_calls_executor(self, mock_execute: MagicMock) -> None:
        """Test rollback_alter calls execute_sql_file with correct path."""
        from database.sql.tables.continent import rollback_alter

        mock_execute.return_value = True
        result = rollback_alter()

        assert result is True
        mock_execute.assert_called_once()
        call_path = mock_execute.call_args[0][0]
        assert call_path.name == "continent_alter_v1_rollback.sql"
