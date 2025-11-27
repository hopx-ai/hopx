"""Root conftest with shared fixtures for all test modules.

This file provides the core fixtures used across all tests including:
- Environment isolation
- Configuration mocks
- CLI context and runner
- SDK mocks
- Keyring mocks
"""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Pure unit tests (no I/O)")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Tests that take >1 second")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Auto-mark tests based on directory location."""
    for item in items:
        # Auto-mark based on path
        if "/unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "/integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


# =============================================================================
# Environment Isolation Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Ensure clean environment for each test.

    Automatically applied to all tests. Clears HOPX_* environment variables
    to ensure test isolation.
    """
    env_vars_to_clear = [
        "HOPX_API_KEY",
        "HOPX_BASE_URL",
        "HOPX_PROFILE",
        "HOPX_DEFAULT_TEMPLATE",
        "HOPX_DEFAULT_TIMEOUT",
        "HOPX_OUTPUT_FORMAT",
        "NO_COLOR",
    ]
    for var in env_vars_to_clear:
        monkeypatch.delenv(var, raising=False)
    yield


@pytest.fixture
def temp_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create temporary home directory for config/credentials.

    Creates a temp directory structure mimicking ~/.hopx/ for isolated
    config and credential testing.

    Returns:
        Path to the temporary home directory
    """
    home = tmp_path / "home"
    home.mkdir()
    hopx_dir = home / ".hopx"
    hopx_dir.mkdir()
    monkeypatch.setenv("HOME", str(home))
    return home


@pytest.fixture
def temp_hopx_dir(temp_home: Path) -> Path:
    """Get the .hopx directory within temp_home.

    Returns:
        Path to ~/.hopx/ in the temp home
    """
    return temp_home / ".hopx"


# =============================================================================
# Configuration Fixtures
# =============================================================================


@pytest.fixture
def mock_config() -> MagicMock:
    """Create a mock CLIConfig with sensible defaults.

    Returns:
        MagicMock configured to behave like CLIConfig
    """
    from hopx_cli.core.config import CLIConfig

    config = MagicMock(spec=CLIConfig)
    config.api_key = "hopx_live_test123.testsecret"
    config.base_url = "https://api.hopx.dev"
    config.default_template = "code-interpreter"
    config.default_timeout = 3600
    config.output_format = "table"
    config.profile = "default"
    config.get_api_key.return_value = "hopx_live_test123.testsecret"
    return config


@pytest.fixture
def real_config(temp_hopx_dir: Path) -> Any:
    """Create a real CLIConfig instance with temp directory.

    Use this when testing actual config loading/saving behavior.

    Returns:
        Real CLIConfig instance using temp directory
    """
    from hopx_cli.core.config import CLIConfig

    return CLIConfig.load(profile="default")


# =============================================================================
# CLI Context Fixtures
# =============================================================================


@pytest.fixture
def cli_context(mock_config: MagicMock) -> MagicMock:
    """Create a mock CLIContext.

    Returns:
        MagicMock configured to behave like CLIContext
    """
    from hopx_cli.core.context import CLIContext, OutputFormat

    ctx = MagicMock(spec=CLIContext)
    ctx.config = mock_config
    ctx.output_format = OutputFormat.TABLE
    ctx.verbose = False
    ctx.quiet = False
    ctx.no_color = False
    ctx.is_json_output.return_value = False
    ctx.is_table_output.return_value = True
    ctx.is_plain_output.return_value = False
    ctx._state = {}
    ctx.get_state.side_effect = lambda key, default=None: ctx._state.get(key, default)
    ctx.set_state.side_effect = lambda key, value: ctx._state.__setitem__(key, value)
    return ctx


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create Typer CLI test runner.

    Returns:
        CliRunner for invoking CLI commands in tests
    """
    return CliRunner(mix_stderr=False)


# =============================================================================
# SDK Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_sandbox() -> MagicMock:
    """Create a mock Sandbox instance with common methods.

    Returns:
        MagicMock configured to behave like hopx_ai.Sandbox
    """
    sandbox = MagicMock()
    sandbox.sandbox_id = "sb_test123"

    # Mock sandbox info
    info = MagicMock()
    info.sandbox_id = "sb_test123"
    info.status = "running"
    info.template_name = "python"
    info.region = "us-east-1"
    info.public_host = "https://sb_test123.vms.hopx.dev"
    info.timeout_seconds = 3600
    info.expires_at = None
    info.created_at = None
    info.resources = None
    info.internet_access = True
    info.model_dump = lambda: {
        "sandbox_id": "sb_test123",
        "status": "running",
        "template_name": "python",
        "region": "us-east-1",
    }

    sandbox.get_info.return_value = info
    sandbox.is_healthy.return_value = True
    sandbox.get_preview_url.side_effect = lambda port: f"https://{port}-sb_test123.vms.hopx.dev"

    # Mock resource managers
    sandbox.files = MagicMock()
    sandbox.commands = MagicMock()
    sandbox.env = MagicMock()

    return sandbox


@pytest.fixture
def mock_sandbox_list(mock_sandbox: MagicMock) -> list[MagicMock]:
    """Create a list of mock sandboxes for list operations.

    Returns:
        List containing the mock sandbox
    """
    return [mock_sandbox]


@pytest.fixture
def mock_template() -> MagicMock:
    """Create a mock Template instance.

    Returns:
        MagicMock configured to behave like hopx_ai.Template
    """
    template = MagicMock()
    template.name = "custom-template"
    template.status = "active"
    template.created_at = None
    template.model_dump = lambda: {
        "name": "custom-template",
        "status": "active",
    }
    return template


# =============================================================================
# Keyring Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_keyring() -> Generator[MagicMock, None, None]:
    """Mock keyring module for credential tests.

    Yields:
        MagicMock replacing the keyring module
    """
    with patch("hopx_cli.auth.credentials.keyring") as mock:
        mock.get_password.return_value = None
        mock.set_password.return_value = None
        mock.delete_password.return_value = None
        yield mock


@pytest.fixture
def mock_keyring_with_api_key() -> Generator[MagicMock, None, None]:
    """Mock keyring with a stored API key.

    Yields:
        MagicMock with pre-stored API key
    """
    with patch("hopx_cli.auth.credentials.keyring") as mock:

        def get_password(service: str, key: str) -> str | None:
            if key == "default:api_key":
                return "hopx_live_stored.secret"
            return None

        mock.get_password.side_effect = get_password
        mock.set_password.return_value = None
        mock.delete_password.return_value = None
        yield mock


@pytest.fixture
def mock_keyring_unavailable() -> Generator[MagicMock, None, None]:
    """Mock keyring that raises exceptions (simulating unavailable backend).

    Yields:
        MagicMock that raises Exception on all operations
    """
    with patch("hopx_cli.auth.credentials.keyring") as mock:
        mock.get_password.side_effect = Exception("Keyring backend not available")
        mock.set_password.side_effect = Exception("Keyring backend not available")
        mock.delete_password.side_effect = Exception("Keyring backend not available")
        yield mock


# =============================================================================
# SDK Error Fixtures
# =============================================================================


@pytest.fixture
def sdk_auth_error() -> Any:
    """Create an SDK AuthenticationError.

    Returns:
        hopx_ai.errors.AuthenticationError instance
    """
    import hopx_ai.errors as sdk_errors

    return sdk_errors.AuthenticationError(
        message="Invalid API key",
        status_code=401,
        request_id="req_auth123",
    )


@pytest.fixture
def sdk_not_found_error() -> Any:
    """Create an SDK NotFoundError.

    Returns:
        hopx_ai.errors.NotFoundError instance
    """
    import hopx_ai.errors as sdk_errors

    return sdk_errors.NotFoundError(
        message="Sandbox not found",
        status_code=404,
        request_id="req_notfound456",
    )


@pytest.fixture
def sdk_template_not_found_error() -> Any:
    """Create an SDK TemplateNotFoundError with suggestions.

    Returns:
        hopx_ai.errors.TemplateNotFoundError instance
    """
    import hopx_ai.errors as sdk_errors

    error = sdk_errors.TemplateNotFoundError(
        template_name="pythn",
        available_templates=["python", "nodejs", "code-interpreter"],
    )
    # Manually set suggested_template for testing (some SDK versions may not have this)
    error.suggested_template = "python"
    return error


@pytest.fixture
def sdk_rate_limit_error() -> Any:
    """Create an SDK RateLimitError.

    Returns:
        hopx_ai.errors.RateLimitError instance
    """
    import hopx_ai.errors as sdk_errors

    return sdk_errors.RateLimitError(
        message="Rate limit exceeded",
        status_code=429,
        request_id="req_rate789",
        retry_after=60,
    )


@pytest.fixture
def sdk_timeout_error() -> Any:
    """Create an SDK TimeoutError.

    Returns:
        hopx_ai.errors.TimeoutError instance
    """
    import hopx_ai.errors as sdk_errors

    return sdk_errors.TimeoutError(
        message="Operation timed out after 30 seconds",
    )


@pytest.fixture
def sdk_network_error() -> Any:
    """Create an SDK NetworkError.

    Returns:
        hopx_ai.errors.NetworkError instance
    """
    import hopx_ai.errors as sdk_errors

    return sdk_errors.NetworkError(
        message="Connection refused",
    )


@pytest.fixture
def sdk_validation_error() -> Any:
    """Create an SDK ValidationError.

    Returns:
        hopx_ai.errors.ValidationError instance
    """
    import hopx_ai.errors as sdk_errors

    return sdk_errors.ValidationError(
        message="Invalid template name",
        field="template",
    )


# =============================================================================
# Console and Output Fixtures
# =============================================================================


@pytest.fixture
def mock_console() -> MagicMock:
    """Create a mock Rich console that captures output.

    Returns:
        MagicMock replacing the console
    """
    from rich.console import Console

    console = MagicMock(spec=Console)
    console.print = MagicMock()
    return console
