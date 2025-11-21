# Hopx Python SDK Tests

This directory contains integration and end-to-end tests for the Hopx Python SDK.

## Quick Start

### Run All Tests
```bash
# From the python/ directory
./run_tests.sh
```

### Run Specific Test Types
```bash
# Integration tests only
./run_tests.sh -t integration

# E2E tests only
./run_tests.sh -t e2e
```

### Run Tests with Options
```bash
# Verbose output
./run_tests.sh -v

# With coverage report
./run_tests.sh -c

# Run in parallel
./run_tests.sh -p

# Run specific test file
./run_tests.sh tests/integration/sandbox/creation/sandbox_creation.py

# Run tests matching keyword
./run_tests.sh -k "creation"

# Run with specific marker
./run_tests.sh -m integration

# Generate reports
./run_tests.sh -r

# Stop on first failure
./run_tests.sh -f
```

## Test Organization

### Integration Tests
Located in `tests/integration/`, organized by feature:

- `sandbox/` - Sandbox operations (sync)
- `async_sandbox/` - AsyncSandbox operations
- `desktop/` - Desktop automation
- `terminal/` - Terminal operations
- `template/` - Template building

### E2E Tests
Located in `tests/e2e/`, covering complete workflows:

- `sandbox/` - Complete sandbox lifecycle workflows
- `async_sandbox/` - Complete async workflows

## Test Structure

Each test class is in its own file, organized by feature:

```
tests/integration/sandbox/
├── creation/
│   └── sandbox_creation.py
├── connection/
│   └── sandbox_connection.py
├── code_execution/
│   ├── code_execution.py
│   ├── code_execution_stream.py
│   └── background_execution.py
└── resources/
    └── files/
        ├── files_resource.py
        └── files_upload_download.py
```

## Configuration

### Environment Variables

- `HOPX_API_KEY` - Required for running tests
- `HOPX_TEST_BASE_URL` - Test API base URL (default: `https://api-eu.hopx.dev`)
- `HOPX_TEST_TEMPLATE` - Default template for tests (default: `code-interpreter`)
- `HOPX_DESKTOP_TEMPLATE` - Template for desktop tests

### Pytest Configuration

Pytest is configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
python_files = ["*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
testpaths = ["tests"]
```

## Running Tests Manually

### Using pytest directly

```bash
# Run all tests
pytest tests/

# Run specific directory
pytest tests/integration/sandbox/

# Run specific file
pytest tests/integration/sandbox/creation/sandbox_creation.py

# Run specific test class
pytest tests/integration/sandbox/creation/sandbox_creation.py::TestSandboxCreation

# Run specific test method
pytest tests/integration/sandbox/creation/sandbox_creation.py::TestSandboxCreation::test_create_from_template_name

# Run with markers
pytest -m integration

# Run with keyword filter
pytest -k "creation"

# Run in parallel
pytest -n auto

# Generate coverage
pytest --cov=hopx_ai --cov-report=html
```

## Test Reports

When using `-r` or `--report` flag, test reports are generated in `local/reports/`:

- `pytest_output.txt` - Full pytest output
- `junit.xml` - JUnit XML format
- `test_summary.md` - Markdown summary (if generate_reports.py exists)
- `passed_tests_report.txt` - List of passed tests
- `failed_tests_report.txt` - List of failed tests

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `api_key` - API key from environment
- `test_base_url` - Test base URL
- `test_template` - Test template name
- `sandbox_factory` - Factory for creating sandboxes

## Writing New Tests

1. **Follow the structure**: One test class per file, organized by feature
2. **Use fixtures**: Leverage existing fixtures from `conftest.py`
3. **Clean up**: Always clean up resources (sandboxes) in `finally` blocks
4. **Skip gracefully**: Use `pytest.skip()` for tests that require specific conditions
5. **Use markers**: Mark tests appropriately (`@pytest.mark.integration`, `@pytest.mark.e2e`)

### Example Test File

```python
"""
Integration tests for Feature X.

Tests cover:
- Operation 1
- Operation 2
"""

import os
import pytest
from hopx_ai import Sandbox

BASE_URL = os.getenv("HOPX_TEST_BASE_URL", "https://api-eu.hopx.dev")
TEST_TEMPLATE = os.getenv("HOPX_TEST_TEMPLATE", "code-interpreter")


@pytest.fixture
def api_key():
    """Get API key from environment."""
    key = os.getenv("HOPX_API_KEY")
    if not key:
        pytest.skip("HOPX_API_KEY environment variable not set")
    return key


@pytest.fixture
def sandbox(api_key):
    """Create a sandbox for testing and clean up after."""
    sandbox = Sandbox.create(
        template=TEST_TEMPLATE,
        api_key=api_key,
        base_url=BASE_URL,
    )
    yield sandbox
    try:
        sandbox.kill()
    except Exception:
        pass


class TestFeatureX:
    """Test Feature X operations."""

    def test_operation_one(self, sandbox):
        """Test operation one."""
        # Test implementation
        pass
```

## Troubleshooting

### Tests are skipped
- Check that `HOPX_API_KEY` is set
- Verify network connectivity to test API
- Check that test template exists

### Tests fail with import errors
- Ensure you're in the `python/` directory
- Install dependencies: `pip install -e .`
- Install test dependencies: `pip install pytest pytest-asyncio`

### Desktop tests fail
- Ensure you're using a template with desktop support
- Set `HOPX_DESKTOP_TEMPLATE` environment variable
- Tests will skip gracefully if desktop is not available

## Coverage

Current test coverage: **~90%** of documented SDK methods

See `COVERAGE_REPORT.md` for detailed coverage information and `INTENTIONALLY_UNTESTED.md` for methods that are intentionally not tested.
