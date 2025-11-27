"""Tests for authentication commands.

Tests cover:
- Auth command help text
- Login/logout subcommands
- Status display
- API key management commands
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

runner = CliRunner()


# =============================================================================
# Command Help Tests
# =============================================================================


class TestAuthCommandHelp:
    """Tests for auth command help text."""

    @pytest.mark.unit
    def test_auth_help(self) -> None:
        """Auth command shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["auth", "--help"])
        assert result.exit_code == 0
        assert "auth" in result.output.lower() or "Authentication" in result.output

    @pytest.mark.unit
    def test_auth_login_help(self) -> None:
        """Auth login subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["auth", "login", "--help"])
        assert result.exit_code == 0
        assert "login" in result.output.lower() or "authenticate" in result.output.lower()

    @pytest.mark.unit
    def test_auth_logout_help(self) -> None:
        """Auth logout subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["auth", "logout", "--help"])
        assert result.exit_code == 0
        assert "logout" in result.output.lower() or "clear" in result.output.lower()

    @pytest.mark.unit
    def test_auth_status_help(self) -> None:
        """Auth status subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["auth", "status", "--help"])
        assert result.exit_code == 0
        assert "status" in result.output.lower()

    @pytest.mark.unit
    def test_auth_keys_create_help(self) -> None:
        """Auth keys create subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["auth", "keys", "create", "--help"])
        assert result.exit_code == 0
        assert "create" in result.output.lower() or "key" in result.output.lower()


# =============================================================================
# API Keys Subcommand Help Tests
# =============================================================================


class TestApiKeysCommandHelp:
    """Tests for keys subcommand help text."""

    @pytest.mark.unit
    def test_keys_help(self) -> None:
        """Keys command shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["auth", "keys", "--help"])
        assert result.exit_code == 0
        assert "key" in result.output.lower() or "manage" in result.output.lower()

    @pytest.mark.unit
    def test_auth_refresh_help(self) -> None:
        """Auth refresh subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["auth", "refresh", "--help"])
        assert result.exit_code == 0
        assert "refresh" in result.output.lower() or "token" in result.output.lower()

    @pytest.mark.unit
    def test_auth_validate_help(self) -> None:
        """Auth validate subcommand shows help."""
        from hopx_cli.main import app as main_app

        result = runner.invoke(main_app, ["auth", "validate", "--help"])
        assert result.exit_code == 0
        assert "validate" in result.output.lower() or "test" in result.output.lower()
