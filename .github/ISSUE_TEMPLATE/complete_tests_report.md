# Test Results Report

- **Date:** {{DATE}}
- **Commit:** `{{COMMIT_SHA}}`
- **Branch:** `{{BRANCH_NAME}}`
- **Environment:** {{ENV_NAME}} ({{ENV_TYPE}}: local/CI/staging/prod)
- **Trigger:** {{TRIGGER_TYPE}} (manual / push / PR #{{PR_NUMBER}})
- **Test Runner:** pytest (via `run_tests.sh`)

---

## 1. Summary

- **Overall status:** ✅ PASSED / ❌ FAILED / ⚠️ UNSTABLE
- **Total tests:** {{TOTAL_TESTS}}
- **Passed:** {{PASSED_COUNT}}
- **Failed:** {{FAILED_COUNT}}
- **Skipped:** {{SKIPPED_COUNT}}
- **Duration:** {{TOTAL_DURATION}}
- **Success rate:** {{SUCCESS_RATE}}%

**High-level notes:**

- {{ONE_LINE_SUMMARY_1}}
- {{ONE_LINE_SUMMARY_2}}

---

## 2. Scope of this run

- **Test types executed:** {{INTEGRATION/E2E/ALL}}
- **Test markers used:** {{MARKERS}} (integration/e2e/slow)
- **Directories / modules covered:**
  - `tests/integration/sandbox/` - Sandbox operations (sync)
  - `tests/integration/async_sandbox/` - AsyncSandbox operations
  - `tests/integration/desktop/` - Desktop automation
  - `tests/integration/terminal/` - Terminal operations
  - `tests/integration/template/` - Template building
  - `tests/e2e/sandbox/` - Complete sandbox workflows
  - `tests/e2e/async_sandbox/` - Complete async workflows
- **Not covered (important gaps):**
  - {{GAP_1}}
  - {{GAP_2}}

---

## 3. Detailed results by suite

### 3.1 Integration tests

- **Status:** ✅ / ❌ / ⚠️
- **Total:** {{INT_TOTAL}}, **Passed:** {{INT_PASSED}}, **Failed:** {{INT_FAILED}}, **Skipped:** {{INT_SKIPPED}}
- **Duration:** {{INT_DURATION}}

#### 3.1.1 Sandbox (Sync) tests

- **Status:** ✅ / ❌ / ⚠️
- **Coverage areas:** Creation, connection, info, lifecycle, listing, code execution, resources (files, commands, env_vars, cache, agent_info), templates, auth
- **Key failures:**

1. `{{TEST_NAME}}`  
   - **File:** `tests/integration/sandbox/{{SUBDIRECTORY}}/{{FILE_NAME}}.py`
   - **Test path:** `{{FULL_TEST_PATH}}`
   - **Error:** {{SHORT_ERROR_MESSAGE}}
   - **Notes:** {{E.G. FLAKY, ENV ISSUE, API ISSUE}}

#### 3.1.2 AsyncSandbox tests

- **Status:** ✅ / ❌ / ⚠️
- **Coverage areas:** Creation, connection, lifecycle, listing, code execution, resources (files, commands, env_vars), auth
- **Key failures:**

1. `{{TEST_NAME}}`  
   - **File:** `tests/integration/async_sandbox/{{SUBDIRECTORY}}/{{FILE_NAME}}.py`
   - **Test path:** `{{FULL_TEST_PATH}}`
   - **Error:** {{SHORT_ERROR_MESSAGE}}
   - **Notes:** {{E.G. FLAKY, ENV ISSUE, API ISSUE}}

#### 3.1.3 Desktop tests

- **Status:** ✅ / ❌ / ⚠️
- **Coverage areas:** VNC, input operations, screenshots, recordings, window operations, UI automation, display operations, debug operations
- **Key failures:**

1. `{{TEST_NAME}}`  
   - **File:** `tests/integration/desktop/{{FILE_NAME}}.py`
   - **Test path:** `{{FULL_TEST_PATH}}`
   - **Error:** {{SHORT_ERROR_MESSAGE}}
   - **Notes:** {{E.G. TEMPLATE NOT AVAILABLE, DESKTOP NOT AVAILABLE}}

#### 3.1.4 Terminal tests

- **Status:** ✅ / ❌ / ⚠️
- **Coverage areas:** WebSocket connection, input/output streaming, terminal resizing
- **Key failures:**

1. `{{TEST_NAME}}`  
   - **File:** `tests/integration/terminal/{{FILE_NAME}}.py`
   - **Test path:** `{{FULL_TEST_PATH}}`
   - **Error:** {{SHORT_ERROR_MESSAGE}}

#### 3.1.5 Template building tests

- **Status:** ✅ / ❌ / ⚠️
- **Coverage areas:** Template creation, ready checks, builder methods
- **Key failures:**

1. `{{TEST_NAME}}`  
   - **File:** `tests/integration/template/{{FILE_NAME}}.py`
   - **Test path:** `{{FULL_TEST_PATH}}`
   - **Error:** {{SHORT_ERROR_MESSAGE}}

### 3.2 End-to-end tests

- **Status:** ✅ / ❌ / ⚠️
- **Total:** {{E2E_TOTAL}}, **Passed:** {{E2E_PASSED}}, **Failed:** {{E2E_FAILED}}, **Skipped:** {{E2E_SKIPPED}}
- **Duration:** {{E2E_DURATION}}

#### 3.2.1 Sandbox E2E workflows

- **Status:** ✅ / ❌ / ⚠️
- **Coverage:** Complete sandbox lifecycle workflows
- **Key failures:**

1. `{{FLOW_NAME}}`  
   - **File:** `tests/e2e/sandbox/{{FILE_NAME}}.py`
   - **Test path:** `{{FULL_TEST_PATH}}`
   - **Workflow:** {{BRIEF_FLOW_DESCRIPTION}}
   - **Break point:** {{WHERE_IT_FAILED}}
   - **Error:** {{SHORT_ERROR_MESSAGE}}

#### 3.2.2 AsyncSandbox E2E workflows

- **Status:** ✅ / ❌ / ⚠️
- **Coverage:** Complete async workflows
- **Key failures:**

1. `{{FLOW_NAME}}`  
   - **File:** `tests/e2e/async_sandbox/{{FILE_NAME}}.py`
   - **Test path:** `{{FULL_TEST_PATH}}`
   - **Workflow:** {{BRIEF_FLOW_DESCRIPTION}}
   - **Break point:** {{WHERE_IT_FAILED}}
   - **Error:** {{SHORT_ERROR_MESSAGE}}

---

## 4. Flakiness & reruns

- **Flaky tests detected:** {{FLAKY_COUNT}}
- **Detection method:** {{E.G. RETRIES, HISTORICAL INSTABILITY, MANUAL OBSERVATION}}

Notable flaky tests:

- `{{TEST_NAME_1}}` — {{BRIEF_REASON_OR_PATTERN}} (e.g., API timeout, network issue, template availability)
- `{{TEST_NAME_2}}` — {{BRIEF_REASON_OR_PATTERN}}

**Common flakiness patterns:**

- API rate limiting or timeouts
- Template availability issues
- Network connectivity issues
- Desktop template not available (gracefully skipped)

---

## 5. Comparison with previous run

- **Previous run ID:** {{PREV_RUN_ID}} ({{PREV_RUN_DATE}})
- **Delta tests:** `+{{ADDED_TESTS}} / -{{REMOVED_TESTS}}`
- **Pass rate change:** {{PREV_PASS_RATE}}% → {{CURRENT_PASS_RATE}}%
- **New failures since last run:**
  - `{{TEST_NAME}}` in `{{MODULE}}` – {{SHORT_NOTE}}
- **Newly passing tests:**
  - `{{TEST_NAME}}` in `{{MODULE}}` – {{SHORT_NOTE}}

---

## 6. Risks & impact

- **Impact on release:**  
  - ⛔ Blocker  
  - ⚠️ Release with known issues  
  - ✅ Safe to release

- **Key risks:**
  - {{RISK_1}} (e.g., Core sandbox operations failing, API compatibility issues)
  - {{RISK_2}} (e.g., Resource management issues, authentication problems)

- **Affected areas / features:**
  - {{AREA_OR_FEATURE_1}} (e.g., Sandbox creation, Code execution, File operations)
  - {{AREA_OR_FEATURE_2}} (e.g., Desktop automation, Template building, Async operations)

- **Coverage impact:**
  - Current coverage: ~{{CURRENT_COVERAGE}}% of documented SDK methods
  - See `python/tests/COVERAGE_REPORT.md` for detailed coverage information

---

## 7. Recommended actions

Short, actionable items (not a PM backlog):

1. **Fix:** {{TOP_PRIORITY_FAILURE}}  
   - **Owner:** {{OWNER}}  
   - **Priority:** High  
   - **File/Module:** `{{FILE_PATH}}`
2. **Investigate:** {{FLAKY_TEST_OR_ENV_ISSUE}}  
   - **Test:** `{{TEST_NAME}}`
   - **Pattern:** {{FLAKY_PATTERN}}
3. **Add tests for:** {{MISSING_COVERAGE_AREA}}  
   - **See:** `python/tests/INTENTIONALLY_UNTESTED.md` for documented gaps
4. **Review:** {{REVIEW_ITEM}} (e.g., API error handling, response structure validation)

---

## 8. Artifacts & references

- **CI job URL:** {{CI_JOB_URL}}
- **Test reports location:** `local/reports/`
  - `junit.xml` - JUnit XML format
  - `test_results.json` - JSON format results
  - `pytest_output.txt` - Full pytest output
  - `test_summary.md` - Markdown summary
  - `passed_tests_report.txt` - List of passed tests
  - `failed_tests_report.txt` - List of failed tests with details
  - `all_tests_report.txt` - Combined report
- **Coverage reports:**
  - HTML coverage report (if generated with `-c` flag): `htmlcov/index.html`
  - Coverage summary: `python/tests/COVERAGE_REPORT.md`
- **Test documentation:**
  - Test README: `python/tests/README.md`
  - Intentionally untested: `python/tests/INTENTIONALLY_UNTESTED.md`
- **Logs:** {{LOG_LOCATIONS}} (if available)
- **Screenshots / videos (E2E/Desktop):** {{ARTIFACT_LINKS}} (if available)

---

## 9. Test execution details

- **Command used:** `./run_tests.sh {{OPTIONS}}` or `pytest {{ARGS}}`
- **Environment variables:**
  - `HOPX_API_KEY`: {{SET/NOT_SET}}
  - `HOPX_TEST_BASE_URL`: {{VALUE}} (default: `https://api-eu.hopx.dev`)
  - `HOPX_TEST_TEMPLATE`: {{VALUE}} (default: `code-interpreter`)
  - `HOPX_DESKTOP_TEMPLATE`: {{VALUE}} (if used)
- **Pytest options:** {{PYTEST_OPTIONS}} (e.g., `-v`, `-c`, `-p`, `-m integration`)
