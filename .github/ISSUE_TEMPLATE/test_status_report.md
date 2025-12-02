# Test Status Report - Individual Test Results

- **Date:** {{DATE}}
- **Commit:** `{{COMMIT_SHA}}`
- **Branch:** `{{BRANCH_NAME}}`
- **Environment:** {{ENV_NAME}} ({{ENV_TYPE}}: local/CI/staging/prod)
- **Trigger:** {{TRIGGER_TYPE}} (manual / push / PR #{{PR_NUMBER}})
- **Test Runner:** pytest (via `run_tests.sh`)

---

## Summary

- **Overall status:** ✅ PASSED / ❌ FAILED / ⚠️ UNSTABLE
- **Total tests:** {{TOTAL_TESTS}}
- **Passed:** {{PASSED_COUNT}} ✅
- **Failed:** {{FAILED_COUNT}} ❌
- **Skipped:** {{SKIPPED_COUNT}} ⏭️
- **Duration:** {{TOTAL_DURATION}}
- **Success rate:** {{SUCCESS_RATE}}%

---

## Test Execution Details

- **Command used:** `./run_tests.sh {{OPTIONS}}` or `pytest {{ARGS}}`
- **Environment variables:**
  - `HOPX_API_KEY`: {{SET/NOT_SET}}
  - `HOPX_TEST_BASE_URL`: {{VALUE}} (default: `https://api-eu.hopx.dev`)
  - `HOPX_TEST_TEMPLATE`: {{VALUE}} (default: `code-interpreter`)
  - `HOPX_DESKTOP_TEMPLATE`: {{VALUE}} (if used)
- **Pytest options:** {{PYTEST_OPTIONS}}

---

## Individual Test Results

### Integration Tests

#### Sandbox (Sync) Tests

| Status | Test Name | File | Duration | Notes |
|--------|-----------|------|----------|-------|
| ✅ | `{{TEST_NAME}}` | `tests/integration/sandbox/{{SUBDIR}}/{{FILE}}.py` | {{DURATION}} | {{NOTES}} |
| ❌ | `{{TEST_NAME}}` | `tests/integration/sandbox/{{SUBDIR}}/{{FILE}}.py` | {{DURATION}} | **Error:** {{ERROR_MESSAGE}} |
| ⏭️ | `{{TEST_NAME}}` | `tests/integration/sandbox/{{SUBDIR}}/{{FILE}}.py` | {{DURATION}} | **Reason:** {{SKIP_REASON}} |

**Detailed failures:**

1. **Test:** `{{FULL_TEST_PATH}}`
   - **File:** `tests/integration/sandbox/{{SUBDIR}}/{{FILE}}.py::{{TEST_CLASS}}::{{TEST_METHOD}}`
   - **Status:** ❌ FAILED
   - **Duration:** {{DURATION}}
   - **Error Type:** {{ERROR_TYPE}} (e.g., AssertionError, TimeoutError, APIError)
   - **Error Message:**
     ```
     {{ERROR_MESSAGE}}
     ```
   - **Traceback (key lines):**
     ```
     {{TRACEBACK_LINES}}
     ```
   - **Notes:** {{NOTES}} (e.g., FLAKY, ENV ISSUE, API ISSUE)

#### AsyncSandbox Tests

| Status | Test Name | File | Duration | Notes |
|--------|-----------|------|----------|-------|
| ✅ | `{{TEST_NAME}}` | `tests/integration/async_sandbox/{{SUBDIR}}/{{FILE}}.py` | {{DURATION}} | {{NOTES}} |
| ❌ | `{{TEST_NAME}}` | `tests/integration/async_sandbox/{{SUBDIR}}/{{FILE}}.py` | {{DURATION}} | **Error:** {{ERROR_MESSAGE}} |
| ⏭️ | `{{TEST_NAME}}` | `tests/integration/async_sandbox/{{SUBDIR}}/{{FILE}}.py` | {{DURATION}} | **Reason:** {{SKIP_REASON}} |

**Detailed failures:**

1. **Test:** `{{FULL_TEST_PATH}}`
   - **File:** `tests/integration/async_sandbox/{{SUBDIR}}/{{FILE}}.py::{{TEST_CLASS}}::{{TEST_METHOD}}`
   - **Status:** ❌ FAILED
   - **Duration:** {{DURATION}}
   - **Error Type:** {{ERROR_TYPE}}
   - **Error Message:**
     ```
     {{ERROR_MESSAGE}}
     ```
   - **Notes:** {{NOTES}}

#### Desktop Tests

| Status | Test Name | File | Duration | Notes |
|--------|-----------|------|----------|-------|
| ✅ | `{{TEST_NAME}}` | `tests/integration/desktop/{{FILE}}.py` | {{DURATION}} | {{NOTES}} |
| ❌ | `{{TEST_NAME}}` | `tests/integration/desktop/{{FILE}}.py` | {{DURATION}} | **Error:** {{ERROR_MESSAGE}} |
| ⏭️ | `{{TEST_NAME}}` | `tests/integration/desktop/{{FILE}}.py` | {{DURATION}} | **Reason:** {{SKIP_REASON}} (e.g., Desktop not available) |

**Detailed failures:**

1. **Test:** `{{FULL_TEST_PATH}}`
   - **File:** `tests/integration/desktop/{{FILE}}.py::{{TEST_CLASS}}::{{TEST_METHOD}}`
   - **Status:** ❌ FAILED / ⏭️ SKIPPED
   - **Duration:** {{DURATION}}
   - **Error Type:** {{ERROR_TYPE}} / **Skip Reason:** {{SKIP_REASON}}
   - **Notes:** {{NOTES}} (e.g., Template not available, Desktop not available)

#### Terminal Tests

| Status | Test Name | File | Duration | Notes |
|--------|-----------|------|----------|-------|
| ✅ | `{{TEST_NAME}}` | `tests/integration/terminal/{{FILE}}.py` | {{DURATION}} | {{NOTES}} |
| ❌ | `{{TEST_NAME}}` | `tests/integration/terminal/{{FILE}}.py` | {{DURATION}} | **Error:** {{ERROR_MESSAGE}} |

**Detailed failures:**

1. **Test:** `{{FULL_TEST_PATH}}`
   - **File:** `tests/integration/terminal/{{FILE}}.py::{{TEST_CLASS}}::{{TEST_METHOD}}`
   - **Status:** ❌ FAILED
   - **Duration:** {{DURATION}}
   - **Error Type:** {{ERROR_TYPE}}
   - **Error Message:**
     ```
     {{ERROR_MESSAGE}}
     ```

#### Template Building Tests

| Status | Test Name | File | Duration | Notes |
|--------|-----------|------|----------|-------|
| ✅ | `{{TEST_NAME}}` | `tests/integration/template/{{FILE}}.py` | {{DURATION}} | {{NOTES}} |
| ❌ | `{{TEST_NAME}}` | `tests/integration/template/{{FILE}}.py` | {{DURATION}} | **Error:** {{ERROR_MESSAGE}} |

**Detailed failures:**

1. **Test:** `{{FULL_TEST_PATH}}`
   - **File:** `tests/integration/template/{{FILE}}.py::{{TEST_CLASS}}::{{TEST_METHOD}}`
   - **Status:** ❌ FAILED
   - **Duration:** {{DURATION}}
   - **Error Type:** {{ERROR_TYPE}}
   - **Error Message:**
     ```
     {{ERROR_MESSAGE}}
     ```

### End-to-End Tests

#### Sandbox E2E Workflows

| Status | Test Name | File | Duration | Notes |
|--------|-----------|------|----------|-------|
| ✅ | `{{TEST_NAME}}` | `tests/e2e/sandbox/{{FILE}}.py` | {{DURATION}} | {{NOTES}} |
| ❌ | `{{TEST_NAME}}` | `tests/e2e/sandbox/{{FILE}}.py` | {{DURATION}} | **Error:** {{ERROR_MESSAGE}} |

**Detailed failures:**

1. **Test:** `{{FULL_TEST_PATH}}`
   - **File:** `tests/e2e/sandbox/{{FILE}}.py::{{TEST_FUNCTION}}`
   - **Status:** ❌ FAILED
   - **Duration:** {{DURATION}}
   - **Workflow:** {{BRIEF_FLOW_DESCRIPTION}}
   - **Break point:** {{WHERE_IT_FAILED}}
   - **Error Type:** {{ERROR_TYPE}}
   - **Error Message:**
     ```
     {{ERROR_MESSAGE}}
     ```

#### AsyncSandbox E2E Workflows

| Status | Test Name | File | Duration | Notes |
|--------|-----------|------|----------|-------|
| ✅ | `{{TEST_NAME}}` | `tests/e2e/async_sandbox/{{FILE}}.py` | {{DURATION}} | {{NOTES}} |
| ❌ | `{{TEST_NAME}}` | `tests/e2e/async_sandbox/{{FILE}}.py` | {{DURATION}} | **Error:** {{ERROR_MESSAGE}} |

**Detailed failures:**

1. **Test:** `{{FULL_TEST_PATH}}`
   - **File:** `tests/e2e/async_sandbox/{{FILE}}.py::{{TEST_FUNCTION}}`
   - **Status:** ❌ FAILED
   - **Duration:** {{DURATION}}
   - **Workflow:** {{BRIEF_FLOW_DESCRIPTION}}
   - **Break point:** {{WHERE_IT_FAILED}}
   - **Error Type:** {{ERROR_TYPE}}
   - **Error Message:**
     ```
     {{ERROR_MESSAGE}}
     ```

---

## Test Status Summary by Category

### Integration Tests Summary

| Category | Total | Passed | Failed | Skipped | Pass Rate |
|----------|-------|--------|--------|---------|-----------|
| Sandbox (Sync) | {{COUNT}} | {{PASSED}} | {{FAILED}} | {{SKIPPED}} | {{RATE}}% |
| AsyncSandbox | {{COUNT}} | {{PASSED}} | {{FAILED}} | {{SKIPPED}} | {{RATE}}% |
| Desktop | {{COUNT}} | {{PASSED}} | {{FAILED}} | {{SKIPPED}} | {{RATE}}% |
| Terminal | {{COUNT}} | {{PASSED}} | {{FAILED}} | {{SKIPPED}} | {{RATE}}% |
| Template | {{COUNT}} | {{PASSED}} | {{FAILED}} | {{SKIPPED}} | {{RATE}}% |
| **Total Integration** | **{{TOTAL}}** | **{{PASSED}}** | **{{FAILED}}** | **{{SKIPPED}}** | **{{RATE}}%** |

### E2E Tests Summary

| Category | Total | Passed | Failed | Skipped | Pass Rate |
|----------|-------|--------|--------|---------|-----------|
| Sandbox E2E | {{COUNT}} | {{PASSED}} | {{FAILED}} | {{SKIPPED}} | {{RATE}}% |
| AsyncSandbox E2E | {{COUNT}} | {{PASSED}} | {{FAILED}} | {{SKIPPED}} | {{RATE}}% |
| **Total E2E** | **{{TOTAL}}** | **{{PASSED}}** | **{{FAILED}}** | **{{SKIPPED}}** | **{{RATE}}%** |

---

## Failed Tests Analysis

### By Error Type

| Error Type | Count | Tests |
|------------|-------|-------|
| {{ERROR_TYPE}} | {{COUNT}} | `{{TEST_1}}`, `{{TEST_2}}` |
| {{ERROR_TYPE}} | {{COUNT}} | `{{TEST_1}}`, `{{TEST_2}}` |

### By Test File

| File | Failed | Tests |
|------|--------|-------|
| `{{FILE_PATH}}` | {{COUNT}} | `{{TEST_1}}`, `{{TEST_2}}` |
| `{{FILE_PATH}}` | {{COUNT}} | `{{TEST_1}}`, `{{TEST_2}}` |

---

## Skipped Tests

| Test Name | File | Reason |
|-----------|------|--------|
| `{{TEST_NAME}}` | `{{FILE_PATH}}` | {{SKIP_REASON}} (e.g., HOPX_API_KEY not set, Desktop not available) |
| `{{TEST_NAME}}` | `{{FILE_PATH}}` | {{SKIP_REASON}} |

---

## Slowest Tests

| Test Name | File | Duration | Status |
|-----------|------|----------|--------|
| `{{TEST_NAME}}` | `{{FILE_PATH}}` | {{DURATION}} | {{STATUS}} |
| `{{TEST_NAME}}` | `{{FILE_PATH}}` | {{DURATION}} | {{STATUS}} |

---

## Artifacts & References

- **Test reports location:** `local/reports/`
  - `junit.xml` - JUnit XML format
  - `test_results.json` - JSON format results
  - `pytest_output.txt` - Full pytest output
  - `test_summary.md` - Markdown summary
  - `passed_tests_report.txt` - List of passed tests
  - `failed_tests_report.txt` - List of failed tests with details
  - `all_tests_report.txt` - Combined report
- **CI job URL:** {{CI_JOB_URL}}
- **Coverage reports:**
  - HTML coverage report (if generated): `htmlcov/index.html`
  - Coverage summary: `python/tests/COVERAGE_REPORT.md`

