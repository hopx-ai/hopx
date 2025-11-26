# Test Mapping Documentation

This document explains how source code changes are automatically mapped to test paths in CI/CD workflows.

## Overview

The test mapping system (`test_mapper.py`) intelligently determines which tests to run based on the source code files that changed. This makes CI/CD faster and more efficient by only running relevant tests.

## How It Works

1. **File Detection**: The workflow detects all changed files in a push or PR
2. **Mapping**: Each changed file is mapped to its corresponding test directories
3. **Aggregation**: Test paths from all changed files are collected and deduplicated
4. **Execution**: Only the mapped tests are run

## Source Code to Test Mappings

### Main Classes

| Source File | Test Paths | Notes |
|------------|-----------|-------|
| `hopx_ai/sandbox.py` | `tests/integration/sandbox/`<br>`tests/e2e/sandbox/` | Main Sandbox class |
| `hopx_ai/async_sandbox.py` | `tests/integration/async_sandbox/`<br>`tests/e2e/async_sandbox/` | AsyncSandbox class |
| `hopx_ai/desktop.py` | `tests/integration/desktop/` | Desktop automation |
| `hopx_ai/template/*` | `tests/integration/template/` | Any file in template directory |
| `hopx_ai/terminal.py` | `tests/integration/terminal/` | Terminal/WebSocket |

### Resource Classes

Resource classes affect both sync and async sandboxes:

| Source File | Test Paths | Notes |
|------------|-----------|-------|
| `hopx_ai/files.py` | `tests/integration/sandbox/resources/files/`<br>`tests/integration/async_sandbox/resources/files/` | File operations |
| `hopx_ai/commands.py` | `tests/integration/sandbox/resources/commands/`<br>`tests/integration/async_sandbox/resources/commands/` | Command execution |
| `hopx_ai/env_vars.py` | `tests/integration/sandbox/resources/env_vars/`<br>`tests/integration/async_sandbox/resources/env_vars/` | Environment variables |
| `hopx_ai/cache.py` | `tests/integration/sandbox/resources/cache/`<br>`tests/integration/async_sandbox/resources/cache/` | Cache operations |

### Core Infrastructure

These files affect everything, so all tests run:

| Source File | Test Paths | Notes |
|------------|-----------|-------|
| `hopx_ai/_client.py` | `tests/integration/`<br>`tests/e2e/` | Core HTTP client |
| `hopx_ai/_async_client.py` | `tests/integration/`<br>`tests/e2e/` | Core async HTTP client |
| `hopx_ai/errors.py` | `tests/integration/`<br>`tests/e2e/` | Error handling affects all |
| `hopx_ai/models.py` | `tests/integration/`<br>`tests/e2e/` | Data models affect all |

### Test Files

If test files themselves change, only those specific tests run:

| Source File | Test Paths |
|------------|-----------|
| `tests/integration/sandbox/creation/sandbox_creation.py` | `tests/integration/sandbox/creation/sandbox_creation.py` |
| `tests/conftest.py` | `tests/integration/`<br>`tests/e2e/` | Shared fixtures affect all |

## Examples

### Example 1: Single File Change

**Changed:**
```
python/hopx_ai/sandbox.py
```

**Tests Run:**
```
tests/integration/sandbox/
tests/e2e/sandbox/
```

### Example 2: Multiple Files in One Commit

**Changed:**
```
python/hopx_ai/sandbox.py
python/hopx_ai/files.py
python/hopx_ai/commands.py
```

**Tests Run:**
```
tests/integration/sandbox/
tests/integration/sandbox/resources/files/
tests/integration/sandbox/resources/commands/
tests/integration/async_sandbox/resources/files/
tests/integration/async_sandbox/resources/commands/
tests/e2e/sandbox/
```

### Example 3: Multiple Commits in Push

**Commit 1:**
```
python/hopx_ai/sandbox.py
```

**Commit 2:**
```
python/hopx_ai/template/builder.py
```

**Commit 3:**
```
python/hopx_ai/desktop.py
```

**Tests Run (aggregated):**
```
tests/integration/sandbox/
tests/integration/template/
tests/integration/desktop/
tests/e2e/sandbox/
```

### Example 4: Core Infrastructure

**Changed:**
```
python/hopx_ai/_client.py
```

**Tests Run:**
```
tests/integration/
tests/e2e/
```
(All tests run for safety)

## Adding New Mappings

To add a new mapping, edit `.github/test_mapper.py`:

```python
SOURCE_TO_TESTS = {
    # Add your mapping here
    "hopx_ai/your_new_class.py": [
        "tests/integration/your_feature/",
        "tests/e2e/your_feature/",  # if applicable
    ],
}
```

### Pattern Matching

If you want automatic pattern matching, add to `PATTERN_TO_TESTS`:

```python
PATTERN_TO_TESTS = {
    "your_pattern": ["tests/integration/your_feature/"],
}
```

## Fallback Behavior

If a changed file doesn't match any mapping:
1. **Test files**: Run that specific test file
2. **Unknown source files**: Run all tests (safety fallback)
3. **Empty changes**: Run all tests

This ensures nothing is missed, even if mappings are incomplete.

## Manual Override

You can override automatic detection by:

1. **Workflow Dispatch**: Manually trigger workflow with specific feature
2. **Commit Message**: Use `[test all]` to force all tests
3. **Empty Feature**: Leave feature empty to use auto-detection

## Troubleshooting

### Tests Not Running

- Check that changed files are in the mapping
- Verify file paths match exactly (case-sensitive)
- Check workflow logs for mapping output

### Wrong Tests Running

- Verify mapping in `test_mapper.py`
- Check if file matches multiple patterns
- Review workflow logs for detected paths

### All Tests Running When They Shouldn't

- Check if core infrastructure file changed
- Verify mapping exists for your file
- Check if fallback was triggered

## Best Practices

1. **Keep Mappings Updated**: Add mappings when adding new source files
2. **Test Core Infrastructure Carefully**: Changes to `_client.py`, `errors.py` run all tests
3. **Review Mapping Logic**: Ensure resource classes map to both sync and async tests
4. **Document New Features**: Update this file when adding new test areas

