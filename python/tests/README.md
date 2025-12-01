# Hopx Python SDK Test Suite

This directory contains the complete test suite for the Hopx Python SDK, including integration tests and end-to-end (E2E) tests.

## Overview

The test suite is organized into two main categories:

- **Integration Tests** (`integration/`) - Test individual SDK methods and features against the real API
- **End-to-End Tests** (`e2e/`) - Test complete user workflows and scenarios

## Directory Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared pytest fixtures and configuration
├── README.md                   # This file
├── INTERACTIVE_TEST_RUNNER.md  # Interactive test runner documentation
├── TEST_COMMANDS.md            # Detailed test execution commands
├── COVERAGE_REPORT.md          # Test coverage information
├── INTENTIONALLY_UNTESTED.md   # Documentation of intentionally untested features
├── integration/                # Integration tests
│   ├── README.md              # Integration tests documentation
│   ├── sandbox/               # Sandbox class tests
│   ├── async_sandbox/         # AsyncSandbox class tests
│   ├── desktop/               # Desktop automation tests
│   ├── template/              # Template building tests
│   └── terminal/              # Terminal/WebSocket tests
├── e2e/                        # End-to-end tests
│   ├── sandbox/               # Complete sandbox workflows
│   └── async_sandbox/         # Complete async sandbox workflows
└── reports/                    # Test execution reports
    ├── index.html             # Report index page
    ├── manifest.json          # Report manifest
    └── generate_manifest.py   # Manifest generator script
```

## Integration Tests

Integration tests verify that individual SDK methods and features work correctly against the real Hopx API. These tests are organized by SDK class and feature area.

### Organization

Integration tests follow a feature-based organization structure:

- **One class per file** - Each test class is in its own file for easier navigation
- **Feature-based folders** - Tests are grouped into folders by functionality
- **Clear naming** - Files follow the pattern `<feature_name>.py` (without `test_` prefix)
- **Self-contained** - Each test file includes necessary setup and fixtures

### Test Categories

#### Sandbox Tests (`integration/sandbox/`)
Tests for the synchronous `Sandbox` class:
- **creation/** - Sandbox creation and configuration
- **connection/** - Connecting to existing sandboxes
- **info/** - Retrieving sandbox information
- **lifecycle/** - Pause, resume, timeout, and destruction
- **listing/** - Listing and filtering sandboxes
- **templates/** - Template operations
- **code_execution/** - Code execution features
  - Basic execution
  - Rich output capture
  - Background execution
  - Streaming execution
  - Webhook callbacks
- **resources/** - Resource access
  - **files/** - File operations (read, write, list, upload, download, watch)
  - **commands/** - Shell command execution
  - **env_vars/** - Environment variable management
  - **cache/** - Cache operations
  - **agent_info/** - Agent information and metrics

#### AsyncSandbox Tests (`integration/async_sandbox/`)
Tests for the asynchronous `AsyncSandbox` class, mirroring the structure of Sandbox tests:
- **auth/** - Token management
- **creation/** - Async sandbox creation
- **connection/** - Async connection operations
- **lifecycle/** - Async lifecycle operations
- **listing/** - Async sandbox listing
- **code_execution/** - Async code execution
- **resources/** - Async resource operations

#### Desktop Tests (`integration/desktop/`)
**Status:** ⚠️ **Pending** - Desktop tests are blocked pending availability of a desktop-enabled template/image.

Tests for desktop automation features:
- Screenshots (full screen, region, window)
- Window management
- Input simulation
- UI automation
- VNC operations
- Recordings
- Debug operations

#### Template Tests (`integration/template/`)
Tests for template building and management:
- Template builder methods
- Template building workflows
- Template ready checks

#### Terminal Tests (`integration/terminal/`)
**Status:** ⚠️ **Postponed** - Terminal tests have been postponed for future implementation.

Tests for terminal and WebSocket features:
- WebSocket terminal connections
- Terminal operations

### Running Integration Tests

#### Run All Integration Tests
```bash
cd python
pytest tests/integration/
```

#### Run Tests by Category
```bash
# All sandbox tests
pytest tests/integration/sandbox/

# All async sandbox tests
pytest tests/integration/async_sandbox/

# All desktop tests
pytest tests/integration/desktop/

# All template tests
pytest tests/integration/template/
```

#### Run Tests by File
```bash
# Specific test file
pytest tests/integration/sandbox/code_execution/code_execution.py
```

#### Run Tests by Class or Method
```bash
# Specific test class
pytest tests/integration/sandbox/code_execution/code_execution.py::TestCodeExecution

# Specific test method
pytest tests/integration/sandbox/code_execution/code_execution.py::TestCodeExecution::test_run_simple_code
```

#### With Reports
```bash
# Generate HTML and JUnit XML reports
pytest tests/integration/ \
  -v \
  --showlocals \
  --html=tests/reports/integration/report.html \
  --self-contained-html \
  --junitxml=tests/reports/integration/junit.xml
```

For detailed commands for every test file, class, and method, see [TEST_COMMANDS.md](./TEST_COMMANDS.md).

## End-to-End Tests

**Status:** ⚠️ **Postponed** - E2E tests have been postponed for future implementation alongside terminal tests.

E2E tests verify complete user workflows and scenarios using the SDK. These tests ensure that multiple features work together correctly.

### Test Files

- **`e2e/sandbox/sandbox_complete_lifecycle_e2e.py`** - Complete sandbox lifecycle workflow
- **`e2e/async_sandbox/async_sandbox_complete_workflow_e2e.py`** - Complete async sandbox workflow

### Running E2E Tests

```bash
# All E2E tests
cd python
pytest tests/e2e/

# Specific E2E test file
pytest tests/e2e/sandbox/sandbox_complete_lifecycle_e2e.py
```

## Test Status

Most tests in the test suite have been run and tested. The following test categories are pending or postponed:

### Desktop Tests - Pending

**Status:** Blocked - Pending desktop image availability

The desktop automation tests (`integration/desktop/`) are currently pending due to a blocking requirement. These tests require a desktop-enabled template/image to properly test desktop automation features such as:

- Screenshot capture (full screen, region, window)
- Window management operations
- Input simulation
- UI automation
- VNC operations
- Desktop recordings

**Blocking Requirement:** A desktop-enabled template/image is needed to execute these tests. Once a suitable desktop template becomes available, the desktop tests can be fully validated.

**Note:** The desktop test files are present and ready to run once the desktop image requirement is met.

### Terminal Tests - Postponed

**Status:** Postponed for future implementation

The terminal/WebSocket tests (`integration/terminal/`) have been postponed for a later time. These tests cover:

- WebSocket terminal connections
- Terminal operations and interactions

**Reason:** Terminal testing functionality is planned for future development cycles.

### E2E Tests - Postponed

**Status:** Postponed for future implementation

The end-to-end tests (`e2e/`) have been postponed along with terminal tests. These tests are designed to verify complete user workflows and scenarios:

- Complete sandbox lifecycle workflows
- Complete async sandbox workflows
- Multi-feature integration scenarios

**Reason:** E2E testing functionality is planned for future development cycles alongside terminal testing.

### All Other Tests - Complete

All other test categories have been fully implemented, run, and validated:

- ✅ **Sandbox Tests** - All integration tests for synchronous `Sandbox` class
- ✅ **AsyncSandbox Tests** - All integration tests for asynchronous `AsyncSandbox` class
- ✅ **Template Tests** - Template building and management tests

## Setup

### Prerequisites

1. **Python 3.8+** - Required Python version
2. **API Key** - You need a valid Hopx API key to run tests
3. **Dependencies** - Install test dependencies

### Installation

1. Navigate to the `python/` directory:
```bash
cd python
```

2. Install dependencies (including dev dependencies):
```bash
# Using pip
pip install -e ".[dev]"

# Using uv (recommended)
uv pip install -e ".[dev]"
```

3. Set up environment variables:
```bash
# Create .env file in tests/integration/ directory
cp tests/.env.sample tests/integration/.env

# Edit tests/integration/.env and add your API key
# HOPX_API_KEY=your_api_key_here
```

### Environment Variables

Tests use the following environment variables (with defaults):

- **`HOPX_API_KEY`** (required) - Your Hopx API key
- **`HOPX_TEST_BASE_URL`** (optional) - API base URL (default: `https://api-eu.hopx.dev`)
- **`HOPX_TEST_TEMPLATE`** (optional) - Default template for tests (default: `code-interpreter`)
- **`HOPX_DESKTOP_TEMPLATE`** (optional) - Template for desktop tests (default: `code-interpreter`)
- **`HOPX_TEST_DEBUG`** (optional) - Enable debug logging (set to `1` or `true`)

You can set these in:
1. `tests/integration/.env` file (loaded automatically)
2. System environment variables
3. Shell session before running tests

## Running Tests

### Quick Start

```bash
cd python

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test category
pytest tests/integration/
pytest tests/e2e/
```

### Interactive Test Runner

For an interactive, hierarchical test runner that lets you navigate and run tests at any level:

```bash
cd python
python tests/run_tests_interactive.py
```

See [INTERACTIVE_TEST_RUNNER.md](./INTERACTIVE_TEST_RUNNER.md) for detailed usage.

### Common Options

```bash
# Verbose output with local variables on failure
pytest tests/ -v --showlocals

# Generate HTML report
pytest tests/ --html=tests/reports/report.html --self-contained-html

# Generate JUnit XML report
pytest tests/ --junitxml=tests/reports/junit.xml

# Run only tests matching a pattern
pytest tests/ -k "code_execution"

# Run tests in parallel (requires pytest-xdist)
pytest tests/ -n auto

# Stop on first failure
pytest tests/ -x

# Show print statements
pytest tests/ -s
```

## Test Configuration

### Pytest Configuration

Pytest is configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
python_files = ["*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
testpaths = ["tests"]
asyncio_default_fixture_loop_scope = "function"
```

### Test Discovery

- **Test files**: Any `.py` file in the `tests/` directory
- **Test classes**: Classes starting with `Test` (e.g., `TestCodeExecution`)
- **Test methods**: Methods starting with `test_` (e.g., `test_run_simple_code`)

### Fixtures

Common fixtures are defined in `conftest.py`:

- **`api_key`** - Provides API key from environment
- **`sandbox`** - Creates and cleans up a standard sandbox
- **`async_sandbox`** - Creates and cleans up a standard async sandbox
- **`sandbox_factory`** - Factory for creating custom sandboxes
- **`cleanup_sandbox`** - Helper for manual sandbox cleanup
- **`cleanup_async_sandbox`** - Helper for async sandbox cleanup
- **`test_base_url`** - Test API base URL
- **`test_template`** - Default test template

### Markers

Custom pytest markers are available:

- **`@pytest.mark.integration`** - Marks tests as integration tests
- **`@pytest.mark.e2e`** - Marks tests as end-to-end tests
- **`@pytest.mark.slow`** - Marks tests as slow running

Use markers to filter tests:

```bash
# Run only integration tests
pytest tests/ -m integration

# Run only E2E tests
pytest tests/ -m e2e

# Skip slow tests
pytest tests/ -m "not slow"
```

## Test Reports

### HTML Reports

HTML reports are generated using `pytest-html`:

```bash
pytest tests/ --html=tests/reports/report.html --self-contained-html
```

### JUnit XML Reports

JUnit XML reports for CI/CD integration:

```bash
pytest tests/ --junitxml=tests/reports/junit.xml
```

### Report Index

The test suite includes a report index page at `tests/reports/index.html` that provides a navigable view of all generated reports.

Generate the manifest for the report index:

```bash
cd python/tests/reports
python generate_manifest.py
```

## Test Coverage

See [COVERAGE_REPORT.md](./COVERAGE_REPORT.md) for information about test coverage.

To generate coverage reports:

```bash
cd python
pytest tests/ --cov=hopx_ai --cov-report=html --cov-report=term
```

## Intentionally Untested Features

Some features are intentionally not tested. See [INTENTIONALLY_UNTESTED.md](./INTENTIONALLY_UNTESTED.md) for details.

## Debugging Tests

### Debug Mode

Enable debug logging by setting the `HOPX_TEST_DEBUG` environment variable:

```bash
export HOPX_TEST_DEBUG=1
pytest tests/ -v
```

This enables:
- Test timing information
- Progress indicators
- Detailed operation logging

### Debug Utilities

Debug utilities are available in `tests/integration/debug_utils.py`:
- `timed_operation()` - Time operations
- `ProgressIndicator` - Show progress
- `log_test_start()` / `log_test_complete()` - Test lifecycle logging

### Common Issues

1. **Missing API Key**
   - Error: `pytest.skip("HOPX_API_KEY environment variable not set")`
   - Solution: Set `HOPX_API_KEY` in environment or `.env` file

2. **Sandbox Creation Fails**
   - Check API key is valid
   - Check network connectivity
   - Verify base URL is correct

3. **Tests Timeout**
   - Some tests may take longer than expected
   - Check sandbox status in Hopx dashboard
   - Increase timeout if needed

4. **Import Errors**
   - Ensure all dependencies are installed: `pip install -e ".[dev]"`
   - Check Python version is 3.8+

## Contributing

When adding new tests:

1. **Follow the organization structure** - Place tests in appropriate directories
2. **Use descriptive names** - Test classes and methods should clearly describe what they test
3. **Use fixtures** - Leverage existing fixtures from `conftest.py`
4. **Clean up resources** - Ensure sandboxes are cleaned up (use fixtures)
5. **Add documentation** - Document any special setup or requirements
6. **Update TEST_COMMANDS.md** - Run the command generator to update test commands

## Additional Resources

- [Integration Tests README](./integration/README.md) - Detailed integration test documentation
- [Interactive Test Runner](./INTERACTIVE_TEST_RUNNER.md) - Interactive test runner guide
- [Test Commands](./TEST_COMMANDS.md) - Detailed test execution commands
- [Coverage Report](./COVERAGE_REPORT.md) - Test coverage information
- [Intentionally Untested](./INTENTIONALLY_UNTESTED.md) - Untested features documentation

