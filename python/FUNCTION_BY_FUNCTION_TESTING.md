# Function-by-Function Test Execution Guide

This document describes the function-by-function test execution system that runs each test individually and generates comprehensive reports.

## Overview

The function-by-function test system:
- Runs each test function individually
- Generates detailed reports for each test in a hierarchical structure
- Tracks progress against a master checklist
- Generates per-category and overall summary reports
- Sanitizes sensitive data (API keys, tokens) in all outputs

## Components

### 1. Test Checklist Generator (`generate_test_checklist.py`)

Generates a comprehensive checklist of all test functions organized by category, feature, and class.

**Usage:**
```bash
cd python
python generate_test_checklist.py
```

**Output:**
- `local/reports/TEST_CHECKLIST.md` - Markdown checklist table
- `local/reports/TEST_CHECKLIST.json` - JSON data for programmatic access

### 2. Function-by-Function Test Runner (`run_tests_function_by_function.py`)

Runs tests individually and generates detailed reports.

**Usage:**
```bash
cd python

# Run all tests in a directory
python run_tests_function_by_function.py tests/integration/sandbox

# Run specific test file
python run_tests_function_by_function.py tests/integration/sandbox/creation/sandbox_creation.py

# Filter by class
python run_tests_function_by_function.py tests/integration/sandbox --class TestSandboxCreation

# Filter by function
python run_tests_function_by_function.py tests/integration/sandbox --function test_create_from_template_name

# Update checklist and generate summaries
python run_tests_function_by_function.py tests/integration/sandbox \
    --update-checklist \
    --generate-summaries
```

**Options:**
- `-v, --verbose` - Verbose output
- `--class CLASS` - Filter by class name
- `--function FUNCTION` - Filter by function name
- `--update-checklist` - Update checklist status as tests run
- `--generate-summaries` - Generate per-category and overall summary reports

### 3. Category Test Runner (`run_tests_by_category.sh`)

Helper script to run all tests organized by category.

**Usage:**
```bash
cd python
./run_tests_by_category.sh
```

This script runs tests for all categories:
- Sandbox Integration
- AsyncSandbox Integration
- Desktop Integration
- Terminal Integration
- Template Integration
- Sandbox E2E
- AsyncSandbox E2E

## Report Structure

Reports are generated in a hierarchical structure:

```
local/reports/
├── TEST_CHECKLIST.md                    # Master checklist
├── TEST_CHECKLIST.json                  # Checklist data (JSON)
├── TEST_STATUS_REPORT.md                # Overall status report
├── CATEGORY_SUMMARY_*.md                # Per-category summaries
├── summary.json                         # Overall summary (JSON)
└── <class>/
    └── <feature>/
        └── <function-description>/
            ├── TEST_REPORT.md           # Individual test report
            ├── junit.xml                # JUnit XML results
            ├── pytest_output.txt        # Full pytest output (sanitized)
            └── result.json              # Structured test results
```

## Individual Test Reports

Each test generates a detailed report (`TEST_REPORT.md`) following the `individual_test_report.md` template with:

- Summary (status, description, duration)
- Test information (location, metadata)
- Test execution details (command, environment)
- Execution results (JUnit XML data)
- Test outcome (passed/failed/skipped/error with analysis)
- Test output (stdout, stderr - sanitized)
- Performance metrics
- Test dependencies
- Artifacts & references
- Recommendations

## Category Summaries

Per-category summary reports (`CATEGORY_SUMMARY_*.md`) include:

- Total tests, passed, failed, skipped
- Success rate
- Duration
- Test results organized by feature
- Status table with notes

## Overall Status Report

The overall status report (`TEST_STATUS_REPORT.md`) follows the `test_status_report.md` template with:

- Overall summary (totals, success rate)
- Test status summary by category
- Individual test results by category
- Failed tests analysis
- Detailed error information

## Checklist Tracking

The checklist tracks test execution status:

- ✅ = Test passed
- ❌ = Test failed
- ⚠️ = Test skipped
- ⏳ = Test in progress
- ⬜ = Test not yet executed

When using `--update-checklist`, the checklist JSON is updated with:
- Test status
- Last run timestamp

## Security

All reports automatically sanitize sensitive data:
- API keys
- Tokens
- Passwords
- Secrets
- Authorization headers

Sensitive values are redacted as `***REDACTED***` in all outputs.

## Running All Tests

To run all tests function-by-function:

```bash
cd python

# Option 1: Run by category (recommended)
./run_tests_by_category.sh

# Option 2: Run all integration tests
python run_tests_function_by_function.py tests/integration \
    --update-checklist \
    --generate-summaries

# Option 3: Run all tests (integration + e2e)
python run_tests_function_by_function.py tests \
    --update-checklist \
    --generate-summaries
```

**Note:** Running all 171 tests will take significant time (several hours) and requires:
- Valid `HOPX_API_KEY` environment variable
- Network connectivity to test API
- Sufficient time for execution

## Test Statistics

Current test suite:
- **Total Test Functions:** 171
- **Categories:** 7
  - Sandbox Integration: 71 tests
  - AsyncSandbox Integration: 43 tests
  - Desktop Integration: 34 tests
  - Template Integration: 13 tests
  - Terminal Integration: 4 tests
  - Sandbox E2E: 5 tests
  - AsyncSandbox E2E: 1 test
- **Features:** 27
- **Test Classes:** 49

## Troubleshooting

### Tests are skipped
- Check that `HOPX_API_KEY` is set
- Verify network connectivity
- Check that test templates exist

### Checklist not updating
- Ensure `--update-checklist` flag is used
- Check that `TEST_CHECKLIST.json` exists (generate it first)

### Reports not generated
- Ensure `--generate-summaries` flag is used
- Check write permissions in `local/reports/`

### Test discovery issues
- Verify test files follow naming conventions (classes start with `Test`, functions start with `test_`)
- Check that test files are in correct directory structure

## Integration with CI/CD

The function-by-function test system can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Function-by-Function Tests
  run: |
    cd python
    python run_tests_function_by_function.py tests/integration \
      --update-checklist \
      --generate-summaries
  env:
    HOPX_API_KEY: ${{ secrets.HOPX_API_KEY }}
```

## Next Steps

1. **Generate initial checklist:**
   ```bash
   python generate_test_checklist.py
   ```

2. **Run tests by category:**
   ```bash
   ./run_tests_by_category.sh
   ```

3. **Review reports:**
   - Check `local/reports/TEST_STATUS_REPORT.md` for overall status
   - Review category summaries in `local/reports/CATEGORY_SUMMARY_*.md`
   - Check individual test reports for detailed information

4. **Update checklist:**
   - The checklist is automatically updated when using `--update-checklist`
   - Review `local/reports/TEST_CHECKLIST.md` to see progress


