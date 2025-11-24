# Individual Test Function Report

- **Date:** {{DATE}}
- **Commit:** `{{COMMIT_SHA}}`
- **Branch:** `{{BRANCH_NAME}}`
- **Environment:** {{ENV_NAME}} ({{ENV_TYPE}}: local/CI/staging/prod)
- **Trigger:** {{TRIGGER_TYPE}} (manual / push / PR #{{PR_NUMBER}})
- **Test Runner:** pytest (function-by-function)

---

## Summary

- **Status:** ✅ PASSED / ❌ FAILED / ⚠️ SKIPPED / ❌ ERROR
- **Test Function:** `{{TEST_CLASS}}::{{TEST_FUNCTION}}`
- **Test Description:** {{TEST_DESCRIPTION}}
- **Duration:** {{DURATION}}s
- **Exit Code:** {{EXIT_CODE}}

---

## Test Information

### Test Location

- **File:** `{{TEST_FILE_PATH}}`
- **Class:** `{{TEST_CLASS}}`
- **Function:** `{{TEST_FUNCTION}}`
- **Full Test Path:** `{{FULL_TEST_PATH}}`
- **Feature Category:** `{{FEATURE}}` (e.g., template, sandbox, async_sandbox)

### Test Metadata

- **Test Type:** {{TEST_TYPE}} (integration / e2e / unit)
- **Test Markers:** {{TEST_MARKERS}} (e.g., asyncio, integration, slow)
- **Fixtures Used:** {{FIXTURES}} (e.g., api_key, sandbox, template_name)

---

## Test Execution Details

### Command Used

```bash
pytest {{FULL_TEST_PATH}} -v --tb=short --junitxml={{JUNIT_XML_PATH}}`
```

### Environment Variables

**Note:** Sensitive values (API keys, tokens, passwords) are redacted for security.

- `HOPX_API_KEY`: {{SET/NOT_SET}} (value redacted)
- `HOPX_TEST_BASE_URL`: {{VALUE}} (default: `https://api-eu.hopx.dev`)
- `HOPX_TEST_TEMPLATE`: {{VALUE}} (default: `code-interpreter`)
- `HOPX_DESKTOP_TEMPLATE`: {{VALUE}} (if used)
- Other relevant env vars: {{OTHER_ENV_VARS}} (sensitive values redacted)

### Pytest Configuration

- **Pytest version:** {{PYTEST_VERSION}}
- **Python version:** {{PYTHON_VERSION}}
- **Working directory:** `{{WORKING_DIRECTORY}}`
- **Pytest options:** {{PYTEST_OPTIONS}}

---

## Execution Results

### Status Details

- **Status:** {{STATUS}} (passed / failed / skipped / error)
- **Duration:** {{DURATION}}s
- **Start Time:** {{START_TIME}}
- **End Time:** {{END_TIME}}
- **Exit Code:** {{EXIT_CODE}}

### JUnit XML Results

- **Tests:** {{JUNIT_TESTS}}
- **Errors:** {{JUNIT_ERRORS}}
- **Failures:** {{JUNIT_FAILURES}}
- **Skipped:** {{JUNIT_SKIPPED}}
- **Time:** {{JUNIT_TIME}}s

---

## Test Outcome

### ✅ Test Passed

The test executed successfully and all assertions passed.

**Key Validations:**
- {{VALIDATION_1}}
- {{VALIDATION_2}}
- {{VALIDATION_3}}

---

### ❌ Test Failed

**Error Type:** `{{ERROR_TYPE}}` (e.g., AssertionError, TimeoutError, APIError)

**Error Message:**
```
{{ERROR_MESSAGE}}
```

**Traceback:**
```
{{TRACEBACK}}
```

**Failure Location:**
- **File:** `{{FAILURE_FILE}}`
- **Line:** {{FAILURE_LINE}}
- **Function:** `{{FAILURE_FUNCTION}}`

**Failure Analysis:**
- **Root Cause:** {{ROOT_CAUSE}}
- **Impact:** {{IMPACT}}
- **Likely Fix:** {{LIKELY_FIX}}

---

### ⚠️ Test Skipped

**Skip Reason:** {{SKIP_REASON}}

**Skip Details:**
- **Skip Type:** {{SKIP_TYPE}} (e.g., pytest.skip, conditional skip, missing dependency)
- **Skip Condition:** {{SKIP_CONDITION}}
- **Required for Execution:** {{REQUIREMENTS}}

**Notes:**
{{SKIP_NOTES}}

---

### ❌ Test Error

**Error Type:** `{{ERROR_TYPE}}` (e.g., ImportError, SetupError, TeardownError)

**Error Message:**
```
{{ERROR_MESSAGE}}
```

**Error Location:**
- **Phase:** {{ERROR_PHASE}} (setup / execution / teardown)
- **File:** `{{ERROR_FILE}}`
- **Line:** {{ERROR_LINE}}

**Error Analysis:**
- **Root Cause:** {{ROOT_CAUSE}}
- **Impact:** {{IMPACT}}
- **Likely Fix:** {{LIKELY_FIX}}

---

## Test Output

**Note:** Sensitive data (API keys, tokens, passwords) has been automatically redacted.

### Standard Output

```
{{STDOUT}}
```

### Standard Error

```
{{STDERR}}
```

### Pytest Output

```
{{PYTEST_OUTPUT}}
```

**Security:** All output is sanitized before inclusion in reports. Long outputs may be truncated.

---

## Performance Metrics

- **Execution Time:** {{DURATION}}s
- **Setup Time:** {{SETUP_TIME}}s (if available)
- **Teardown Time:** {{TEARDOWN_TIME}}s (if available)
- **Test Time:** {{TEST_TIME}}s (if available)

**Performance Notes:**
- {{PERFORMANCE_NOTES}} (e.g., "Test execution time is within acceptable range", "Test is slower than expected")

---

## Test Dependencies

### Required Resources

- **API Access:** {{REQUIRED}} (yes / no)
- **Network Access:** {{REQUIRED}} (yes / no)
- **External Services:** {{SERVICES}} (e.g., API endpoints, databases)
- **Templates:** {{TEMPLATES}} (if applicable)
- **Sandboxes:** {{SANDBOXES}} (if applicable)

### Cleanup Actions

- **Resources Created:** {{RESOURCES_CREATED}}
- **Resources Cleaned Up:** {{RESOURCES_CLEANED}}
- **Cleanup Status:** {{CLEANUP_STATUS}} (success / failed / skipped)

---

## Related Tests

### Tests in Same Class

| Test Function | Status | Duration | Notes |
|--------------|--------|----------|-------|
| `{{TEST_1}}` | {{STATUS}} | {{DURATION}} | {{NOTES}} |
| `{{TEST_2}}` | {{STATUS}} | {{DURATION}} | {{NOTES}} |

### Tests in Same Feature

| Test Function | Status | Duration | Notes |
|--------------|--------|----------|-------|
| `{{TEST_1}}` | {{STATUS}} | {{DURATION}} | {{NOTES}} |
| `{{TEST_2}}` | {{STATUS}} | {{DURATION}} | {{NOTES}} |

---

## Artifacts & References

### Report Artifacts

- **Report Directory:** `{{REPORT_DIRECTORY}}`
- **JUnit XML:** `junit.xml`
- **Pytest Output:** `pytest_output.txt`
- **Result JSON:** `result.json`
- **This Report:** `TEST_REPORT.md`

### Related Reports

- **Class Summary:** `../../{{CLASS}}_summary.md` (if available)
- **Feature Summary:** `../{{FEATURE}}_summary.md` (if available)
- **Overall Test Run:** `../../../../summary.json` (if available)

### CI/CD References

- **CI Job URL:** {{CI_JOB_URL}}
- **Build Number:** {{BUILD_NUMBER}}
- **Run ID:** {{RUN_ID}}

---

## Recommendations

### ✅ Test Passed

- Test is functioning correctly
- Consider adding additional edge case coverage if applicable

### ❌ Test Failed

- 🔧 **Immediate Actions:**
  - {{ACTION_1}}
  - {{ACTION_2}}
  
- 📋 **Investigation Steps:**
  1. {{STEP_1}}
  2. {{STEP_2}}
  3. {{STEP_3}}
  
- 🐛 **Bug Report:** {{BUG_REPORT_LINK}} (if applicable)

### ⚠️ Test Skipped

- ⚠️ **To Enable This Test:**
  - {{REQUIREMENT_1}}
  - {{REQUIREMENT_2}}
  
- 📝 **Notes:** {{ADDITIONAL_NOTES}}

---

*Report generated on {{TIMESTAMP}}*
*Report location: `local/reports/{{CLASS}}/{{FEATURE}}/{{FUNCTION_DESCRIPTION}}/TEST_REPORT.md`*

