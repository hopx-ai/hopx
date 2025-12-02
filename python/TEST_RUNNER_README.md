# Test Runner Script

This directory contains test runner scripts for executing Hopx SDK tests and generating comprehensive reports.

## Quick Start

### Install Dependencies

First, install all test dependencies:

```bash
pip install -e '.[dev]'
```

Or install individually:
```bash
pip install pytest pytest-asyncio pytest-html pytest-cov
```

### Run Tests

```bash
# Run all tests
python run_tests.py

# Or use the shell script
./run_tests.sh
```

## Available Options

### Basic Usage

```bash
# Run all tests
python run_tests.py

# Run only integration tests
python run_tests.py --category integration

# Run only e2e tests
python run_tests.py --category e2e

# Run specific integration folder
python run_tests.py --integration-folder sandbox
python run_tests.py --integration-folder async_sandbox
python run_tests.py --integration-folder desktop
python run_tests.py --integration-folder template
python run_tests.py --integration-folder terminal

# Or use the short form
python run_tests.py --folder sandbox

# Run specific test file
python run_tests.py --file tests/integration/sandbox/creation/sandbox_creation.py

# Run with verbose output
python run_tests.py --verbose
```

### Coverage Reports

```bash
# Generate coverage report
python run_tests.py --coverage

# Note: Requires pytest-cov to be installed
```

### Filtering Tests

```bash
# Run tests with specific marker
python run_tests.py --marker slow

# Stop after N failures
python run_tests.py --maxfail 5

# Custom traceback style
python run_tests.py --tb long
```

### Additional Pytest Options

```bash
# Pass additional arguments to pytest
python run_tests.py --pytest-args -k "test_create" --tb=short
```

## Generated Reports

All reports are saved to `local/reports/` with timestamps:

- **JUnit XML**: `junit_<timestamp>.xml` - Always generated
- **HTML Report**: `report_<timestamp>.html` - Always generated (requires pytest-html)
- **Coverage HTML**: `coverage_<timestamp>.html` - Generated if `--coverage` is used
- **Coverage XML**: `coverage_<timestamp>.xml` - Generated if `--coverage` is used
- **Summary JSON**: `summary_<timestamp>.json` - Always generated
- **Summary Markdown**: `summary_<timestamp>.md` - Always generated

## Dependencies

All testing dependencies are **required** and are part of the dev dependencies:

- `pytest>=7.0.0` - Test framework
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-html>=3.0.0` - HTML test reports
- `pytest-cov>=4.0.0` - Coverage reports

All dependencies are listed in `pyproject.toml` under `[project.optional-dependencies]` -> `dev`.

**Note:** The test runner will check for all required dependencies and fail early with installation instructions if any are missing.

## Environment Variables

- `HOPX_API_KEY` - Required for most tests (some tests will be skipped if not set)
- `HOPX_TEST_BASE_URL` - Optional, defaults to `https://api-eu.hopx.dev`
- `HOPX_TEST_TEMPLATE` - Optional, defaults to `code-interpreter`

## Troubleshooting

### Missing Dependencies

If you see warnings about missing dependencies:

```bash
# Install all dev dependencies
pip install -e '.[dev]'
```

### Tests Skipped

If tests are being skipped, check:
1. `HOPX_API_KEY` environment variable is set
2. Network connectivity to the API
3. Test template exists

### Coverage Not Working

If coverage reports aren't generated:
1. Ensure all dev dependencies are installed: `pip install -e '.[dev]'`
2. Use the `--coverage` flag: `python run_tests.py --coverage`

## Examples

### Full Test Suite with Coverage

```bash
python run_tests.py --category all --coverage --verbose
```

### Quick Integration Test Run

```bash
python run_tests.py --category integration --maxfail 10
```

### Run Specific Integration Folder

```bash
# Test sandbox functionality
python run_tests.py --integration-folder sandbox

# Test async sandbox functionality
python run_tests.py --integration-folder async_sandbox

# Test desktop functionality
python run_tests.py --integration-folder desktop --verbose

# Test template functionality
python run_tests.py --integration-folder template --coverage
```

### Specific Feature Testing

```bash
python run_tests.py --file tests/integration/sandbox/creation/sandbox_creation.py --verbose
```

### Slow Tests Only

```bash
python run_tests.py --marker slow
```

