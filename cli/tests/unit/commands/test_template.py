"""Tests for template management commands.

Tests cover:
- Template table formatting
- Template details formatting
- Command help text
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

runner = CliRunner()


# =============================================================================
# Helper Function Tests
# =============================================================================


class TestFormatTemplateTable:
    """Tests for _format_template_table helper."""

    @pytest.mark.unit
    def test_creates_table_with_title(self) -> None:
        """Creates table with specified title."""
        from hopx_cli.commands.template import _format_template_table

        table = _format_template_table([], title="My Templates")
        assert table.title == "My Templates"

    @pytest.mark.unit
    def test_creates_table_with_columns(self) -> None:
        """Creates table with expected columns."""
        from hopx_cli.commands.template import _format_template_table

        table = _format_template_table([])

        # Check column headers
        column_headers = [col.header for col in table.columns]
        assert "Name" in column_headers
        assert "Display Name" in column_headers
        assert "Category" in column_headers
        assert "Language" in column_headers
        assert "Public" in column_headers
        assert "Resources" in column_headers

    @pytest.mark.unit
    def test_adds_template_rows(self) -> None:
        """Adds rows for each template."""
        from hopx_cli.commands.template import _format_template_table

        mock_template = MagicMock()
        mock_template.name = "python"
        mock_template.display_name = "Python 3.11"
        mock_template.category = "language"
        mock_template.language = "python"
        mock_template.is_public = True
        mock_template.default_resources = None

        table = _format_template_table([mock_template])

        assert table.row_count == 1

    @pytest.mark.unit
    def test_formats_resources(self) -> None:
        """Formats resource information."""
        from hopx_cli.commands.template import _format_template_table

        mock_resources = MagicMock()
        mock_resources.vcpu = 2
        mock_resources.memory_mb = 1024
        mock_resources.disk_gb = 10

        mock_template = MagicMock()
        mock_template.name = "custom"
        mock_template.display_name = "Custom Template"
        mock_template.category = "custom"
        mock_template.language = "python"
        mock_template.is_public = False
        mock_template.default_resources = mock_resources

        table = _format_template_table([mock_template])
        assert table.row_count == 1

    @pytest.mark.unit
    def test_handles_empty_list(self) -> None:
        """Handles empty template list."""
        from hopx_cli.commands.template import _format_template_table

        table = _format_template_table([])
        assert table.row_count == 0


class TestFormatTemplateDetails:
    """Tests for _format_template_details helper."""

    @pytest.mark.unit
    def test_json_format_calls_format_output(self) -> None:
        """JSON format calls format_output."""
        from hopx_cli.commands.template import _format_template_details
        from hopx_cli.core import CLIContext, OutputFormat

        mock_template = MagicMock()
        mock_template.model_dump.return_value = {"name": "python"}

        mock_ctx = MagicMock(spec=CLIContext)
        mock_ctx.output_format = OutputFormat.JSON

        with patch("hopx_cli.commands.template.format_output") as mock_format:
            _format_template_details(mock_template, mock_ctx)

            mock_format.assert_called_once()

    @pytest.mark.unit
    def test_plain_format_prints_lines(self) -> None:
        """Plain format prints key-value lines."""
        from hopx_cli.commands.template import _format_template_details
        from hopx_cli.core import CLIContext, OutputFormat

        mock_template = MagicMock()
        mock_template.id = "tpl_123"
        mock_template.name = "python"
        mock_template.display_name = "Python 3.11"
        mock_template.category = "language"
        mock_template.language = "python"
        mock_template.is_public = True
        mock_template.is_active = True
        mock_template.description = None
        mock_template.default_resources = None
        mock_template.features = None
        mock_template.tags = None
        mock_template.docs_url = None

        mock_ctx = MagicMock(spec=CLIContext)
        mock_ctx.output_format = OutputFormat.PLAIN

        with patch("hopx_cli.commands.template.console") as mock_console:
            _format_template_details(mock_template, mock_ctx)

            mock_console.print.assert_called_once()
            printed = mock_console.print.call_args[0][0]
            assert "python" in printed.lower()
            assert "tpl_123" in printed

    @pytest.mark.unit
    def test_table_format_creates_table(self) -> None:
        """Table format creates rich table."""
        from hopx_cli.commands.template import _format_template_details
        from hopx_cli.core import CLIContext, OutputFormat

        mock_template = MagicMock()
        mock_template.id = "tpl_123"
        mock_template.name = "python"
        mock_template.display_name = "Python 3.11"
        mock_template.category = "language"
        mock_template.language = "python"
        mock_template.is_public = True
        mock_template.is_active = True
        mock_template.description = "Python runtime"
        mock_template.default_resources = None
        mock_template.features = ["jupyter"]
        mock_template.tags = ["python", "data-science"]
        mock_template.docs_url = "https://docs.example.com"
        mock_template.icon = None  # Set icon to None to avoid render error

        mock_ctx = MagicMock(spec=CLIContext)
        mock_ctx.output_format = OutputFormat.TABLE

        with patch("hopx_cli.commands.template.console") as mock_console:
            _format_template_details(mock_template, mock_ctx)

            mock_console.print.assert_called()


# =============================================================================
# Command Help Tests
# =============================================================================


class TestTemplateCommandHelp:
    """Tests for template command help text."""

    @pytest.mark.unit
    def test_template_help(self) -> None:
        """Template command shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["template", "--help"])
        assert result.exit_code == 0
        assert "template" in result.output.lower() or "Manage" in result.output

    @pytest.mark.unit
    def test_template_alias_tpl_works(self) -> None:
        """tpl alias works for template."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["tpl", "--help"])
        assert result.exit_code == 0

    @pytest.mark.unit
    def test_template_list_help(self) -> None:
        """Template list subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["template", "list", "--help"])
        assert result.exit_code == 0
        assert "list" in result.output.lower() or "template" in result.output.lower()

    @pytest.mark.unit
    def test_template_info_help(self) -> None:
        """Template info subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["template", "info", "--help"])
        assert result.exit_code == 0
        assert "info" in result.output.lower() or "template" in result.output.lower()

    @pytest.mark.unit
    def test_template_delete_help(self) -> None:
        """Template delete subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["template", "delete", "--help"])
        assert result.exit_code == 0
        assert "delete" in result.output.lower() or "template" in result.output.lower()
