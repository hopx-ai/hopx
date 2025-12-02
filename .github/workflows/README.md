# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the Hopx Python SDK.

> **Note:** Workflows can be triggered manually using `gh workflow run` command or automatically via push/pull_request events with test directives in commit messages or PR descriptions.

## Workflows

### `python-tests.yml` - Full Test Suite

Runs the complete test suite across multiple Python versions (3.8, 3.9, 3.10, 3.11, 3.12).

**Triggers:**
- Pull requests to `main` or `test`
- Pushes to `main` or `test`
- Manual workflow dispatch (with optional feature selection)
- Only runs when Python files or workflow files change

**Features:**
- **Intelligent Test Selection**: Automatically detects which tests to run based on changed files
- **Python Version Selection**: Choose specific Python versions via commit messages, PR descriptions, or manual dispatch
- Tests on 5 Python versions in parallel (default) or selected versions
- Runs both integration and E2E tests (or specific subsets)
- Generates test reports and coverage
- Uploads artifacts for review
- Uploads coverage to Codecov (if configured)
- Creates GitHub issues for test failures

### `python-tests-quick.yml` - Quick PR Tests

Runs a quick test suite on Python 3.11 (default) or specified version for faster PR feedback.

**Triggers:**
- Pull requests to `main` or `test`
- Manual workflow dispatch (with optional feature and Python version selection)
- Only runs when Python files or workflow files change

**Features:**
- **Intelligent Test Selection**: Automatically detects which tests to run based on changed files
- **Python Version Selection**: Choose specific Python version via commit messages, PR descriptions, or manual dispatch
- Fast feedback (single Python version, default: 3.11)
- Runs integration tests (or specific subsets)
- Posts test results as PR comment
- Uploads test reports as artifacts

## Required Secrets

The following secrets must be configured in GitHub repository settings:

### Required
- `HOPX_API_KEY` - API key for running tests

### Optional
- `HOPX_TEST_BASE_URL` - Test API base URL (default: `https://api-eu.hopx.dev`)
- `HOPX_TEST_TEMPLATE` - Default template for tests (default: `code-interpreter`)

## Setting Up Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the required secrets listed above

## Workflow Behavior

### Test Execution
- Integration tests run first and must pass
- E2E tests run after integration tests (may be skipped if integration fails)
- E2E tests are set to `continue-on-error: true` to prevent blocking PRs due to flaky tests

### Artifacts
- Test reports are uploaded as artifacts for 7 days
- Coverage reports are generated and uploaded
- Reports can be downloaded from the Actions tab

### Notifications
- Quick test workflow posts results as PR comments
- Full test suite results are available in the Actions tab

## Intelligent Test Selection

The workflows automatically determine which tests to run based on the source code that changed. This makes CI/CD faster and more efficient by only running relevant tests.

### How It Works

1. **Test Directives** (highest priority): Check for `[test: ...]` and `[python: ...]` in PR descriptions or commit messages
2. **Automatic Detection**: If no directives found, analyze all changed files
3. **Smart Mapping**: Changed source files are mapped to their corresponding test directories
4. **Multiple Classes**: If multiple classes are changed, tests for all affected areas are run
5. **Safety Fallback**: If no specific mapping is found, all tests run (ensures nothing is missed)
6. **Python Version Selection**: If `[python: ...]` is specified, only those versions run; otherwise all supported versions run

### Source Code to Test Mapping

The mapping is defined in `.github/test_mapper.py`. Here's how it works:

| Source File | Tests Run |
|------------|-----------|
| `hopx_ai/sandbox.py` | `tests/integration/sandbox/`, `tests/e2e/sandbox/` |
| `hopx_ai/async_sandbox.py` | `tests/integration/async_sandbox/`, `tests/e2e/async_sandbox/` |
| `hopx_ai/desktop.py` | `tests/integration/desktop/` |
| `hopx_ai/template/*` | `tests/integration/template/` |
| `hopx_ai/files.py` | `tests/integration/sandbox/resources/files/`, `tests/integration/async_sandbox/resources/files/` |
| `hopx_ai/commands.py` | `tests/integration/sandbox/resources/commands/`, `tests/integration/async_sandbox/resources/commands/` |
| `hopx_ai/env_vars.py` | `tests/integration/sandbox/resources/env_vars/`, `tests/integration/async_sandbox/resources/env_vars/` |
| `hopx_ai/cache.py` | `tests/integration/sandbox/resources/cache/`, `tests/integration/async_sandbox/resources/cache/` |
| `hopx_ai/terminal.py` | `tests/integration/terminal/` |
| `hopx_ai/_client.py` | `tests/integration/`, `tests/e2e/` (runs all - core infrastructure) |
| `hopx_ai/errors.py` | `tests/integration/`, `tests/e2e/` (runs all - affects everything) |

### Examples

**Example 1: Single Class Change**
```
Changed: python/hopx_ai/sandbox.py
Result: Runs tests/integration/sandbox/ and tests/e2e/sandbox/
```

**Example 2: Multiple Classes in One Push**
```
Changed:
- python/hopx_ai/sandbox.py
- python/hopx_ai/files.py
- python/hopx_ai/commands.py

Result: Runs tests for all three:
- tests/integration/sandbox/
- tests/integration/sandbox/resources/files/
- tests/integration/sandbox/resources/commands/
- tests/integration/async_sandbox/resources/files/
- tests/integration/async_sandbox/resources/commands/
- tests/e2e/sandbox/
```

**Example 3: Multiple Commits in Push**
```
Commit 1: Changed sandbox.py
Commit 2: Changed template/builder.py
Commit 3: Changed desktop.py

Result: Runs all affected tests:
- tests/integration/sandbox/
- tests/integration/template/
- tests/integration/desktop/
```

**Example 4: Core Infrastructure Change**
```
Changed: python/hopx_ai/_client.py

Result: Runs all tests (safety):
- tests/integration/
- tests/e2e/
```

### Test Directives (Recommended)

You can control which tests run and which Python versions to test by adding directives in your PR description or commit messages. This is the easiest and most flexible way to specify test scope and Python versions.

#### Format

Use `[test: ...]` and `[python: ...]` formats anywhere in your PR description or commit messages:

**Test Scope Directives:**
- **Run specific feature tests:** `[test: desktop]` - Runs all desktop tests
- **Run specific test type:** `[test: integration]` - Runs all integration tests
- **Run feature + type:** `[test: desktop, integration]` - Runs only desktop integration tests
- **Run all tests:** `[test: all]` - Runs all tests (overrides file-based detection)

**Python Version Directives:**
- **Single version:** `[python: 3.11]` - Run tests on Python 3.11 only
- **Multiple versions:** `[python: 3.10,3.11]` - Run tests on Python 3.10 and 3.11
- **Multiple versions with spaces:** `[python: 3.10, 3.11, 3.12]` - Also works
- **No directive:** Runs on all supported versions (3.8, 3.9, 3.10, 3.11, 3.12)

#### Examples

**In PR Description:**
```markdown
## Changes
Fixes desktop VNC connection issue

[test: desktop, integration]
[python: 3.11]
```

**In Commit Message:**
```bash
git commit -m "fix: desktop VNC bug [test: desktop] [python: 3.11]"
```

**Multiple Python Versions:**
```markdown
## Changes
Fixes sandbox cleanup issues

[test: sandbox]
[python: 3.10,3.11,3.12]
```

**Combined Directives:**
```markdown
## Changes
Template building improvements

[test: template, integration]
[python: 3.11]
```

**Available Test Scopes:**
- `desktop` - Desktop automation tests
- `sandbox` - Sandbox tests (integration + e2e)
- `async_sandbox` or `async-sandbox` - Async sandbox tests
- `template` - Template building tests
- `terminal` - Terminal/WebSocket tests
- Full path: `tests/integration/desktop/` (also supported)

**Test Types:**
- `integration` - Integration tests only
- `e2e` - End-to-end tests only
- `all` - Both integration and e2e (default)

**Priority Order:**
1. PR description directives (highest priority)
2. Commit message directives
3. Manual workflow dispatch inputs
4. File-based auto-detection (default for test scope)
5. All Python versions (default for Python version selection)

### Manual Test Selection

You can manually trigger workflows with specific test selection and Python versions:

1. Go to **Actions** → Select workflow → **Run workflow**
2. Choose options:
   - **Test type**: Choose `integration`, `e2e`, or `all`
   - **Scope**: Enter feature name (e.g., `desktop`, `sandbox`, `template`)
   - **Python version**: Enter version(s) (e.g., `3.11` or `3.10,3.11,3.12`) - leave empty for all versions
3. Click **Run workflow**

**Manual Examples:**
- Test type: `integration`, Scope: `desktop`, Python version: `3.11` → Runs desktop integration tests on Python 3.11
- Test type: `e2e`, Scope: `sandbox`, Python version: `3.10,3.11` → Runs sandbox e2e tests on Python 3.10 and 3.11
- Test type: `all`, Scope: (empty), Python version: (empty) → Auto-detects from changed files, runs on all Python versions
- Test type: `all`, Scope: `all`, Python version: `3.12` → Runs all tests on Python 3.12 only

### Customization

#### Adding New Mappings

Edit `.github/test_mapper.py` to add new source-to-test mappings:

```python
SOURCE_TO_TESTS = {
    "hopx_ai/your_new_class.py": [
        "tests/integration/your_feature/",
    ],
}
```

#### Changing Default Python Versions

The default Python versions are defined in the workflow file. To change the default set of versions tested, edit the default value in `python-tests.yml`:

```yaml
# In the "Determine Python versions to test" step
PYTHON_VERSIONS='["3.10", "3.11", "3.12"]'  # Only test recent versions by default
```

**Note:** You can also specify Python versions per test run using:
- Commit messages: `[python: 3.11]`
- PR descriptions: `[python: 3.10,3.11]`
- Manual workflow dispatch: Enter versions in the `python_version` input field

### Skipping Tests

Add `[skip ci]` or `[ci skip]` to your commit message to skip CI runs.

## Troubleshooting

### Tests are skipped
- Check that `HOPX_API_KEY` secret is set
- Verify the secret name matches exactly (case-sensitive)

### Tests fail with import errors
- Ensure `pip install -e .` completes successfully
- Check that all dependencies are listed in `pyproject.toml`

### Workflow doesn't trigger
- Check that file paths match the `paths` filter
- Verify the branch name matches the trigger branches
- Ensure the workflow file is in `.github/workflows/`

### Wrong tests are running
- Check the test mapping in `.github/TEST_MAPPING.md`
- Review workflow logs to see which files were detected
- Verify your source file has a mapping in `test_mapper.py`

## Additional Documentation

- **[Test Mapping Guide](TEST_MAPPING.md)**: Detailed documentation on how source code changes map to test paths
- **[Test Issues Guide](README_TEST_ISSUES.md)**: How automated GitHub issue creation works for test failures

