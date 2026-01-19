# Automated GitHub Issue Creation from Test Failures

This workflow automatically creates GitHub issues when tests fail in CI/CD.

## How It Works

1. **Test Execution**: Tests run in the `test` job across multiple Python versions
2. **Report Collection**: JUnit XML reports are collected from all test runs
3. **Issue Generation**: The `create-test-issues` job:
   - Parses JUnit XML files
   - Generates formatted issue body using `create_github_issue.py`
   - Creates GitHub issues only when tests fail
   - Updates existing issues if similar failures were already reported

## Files

- **`python/tests/create_github_issue.py`**: Script that parses JUnit XML and generates GitHub issue body
- **`.github/workflows/test.yml`**: Updated workflow with issue creation step

## Features

### Automatic Issue Creation
- Creates issues only when tests fail (not on every run)
- Includes detailed failure information:
  - Test name, class, and method
  - Error messages and tracebacks
  - Duration and status
  - Links to CI workflow runs

### Smart Issue Management
- **Deduplication**: Checks for existing open issues with same commit or date
- **Updates**: Comments on existing issues instead of creating duplicates
- **Labels**: Automatically labels issues with `tests`, `automated`, and `bug`

### Issue Format
Issues include:
- Summary statistics (passed/failed/skipped)
- Detailed failure information
- Error messages and tracebacks
- Links to CI artifacts and workflow runs
- Recommended actions

## Manual Usage

You can also use the script manually:

```bash
# Generate issue body from JUnit XML
python3 python/tests/create_github_issue.py \
  path/to/junit.xml \
  --output issue_body.md \
  --commit-sha "abc123" \
  --branch "main" \
  --workflow-url "https://github.com/owner/repo/actions/runs/123" \
  --only-if-failed

# Then create issue using GitHub CLI
gh issue create \
  --title "[TEST FAILURES] Test Run - $(date +%Y-%m-%d)" \
  --body-file issue_body.md \
  --label "tests,automated"
```

## Configuration

### Required Permissions
The workflow requires:
- `issues: write` - To create and update issues
- `contents: read` - To read repository files

These are set in the workflow file.

### Environment Variables
The script automatically uses GitHub Actions environment variables:
- `GITHUB_SHA` - Commit SHA
- `GITHUB_REF_NAME` - Branch name
- `GITHUB_SERVER_URL` - GitHub server URL
- `GITHUB_REPOSITORY` - Repository name
- `GITHUB_RUN_ID` - Workflow run ID

## Example Issue

When tests fail, an issue will be created with:

```markdown
# Test Results Report

- **Date:** 2024-11-26 16:30:00 UTC
- **Commit:** `abc123def`
- **Branch:** `main`
- **Environment:** CI (GitHub Actions)

## 1. Summary

- **Overall status:** ❌ FAILED
- **Total tests:** 150
- **Passed:** 145 ✅
- **Failed:** 3 ❌
- **Skipped:** 2 ⏭️
- **Success rate:** 96.7%

## 2. Failed Tests

### 1. `TestCodeExecution::test_run_code_with_error`
- **Error Type:** `AssertionError`
- **Error Message:** ...
- **Traceback:** ...
```

## Troubleshooting

### Issues Not Created
- Check workflow logs for errors
- Verify JUnit XML files are being generated
- Ensure workflow has `issues: write` permission
- Check if `--only-if-failed` flag is preventing creation

### Duplicate Issues
- The workflow checks for existing issues, but may create duplicates if:
  - Issue title format changes
  - Multiple workflow runs happen simultaneously
  - Manual issues exist with similar content

### Missing Information
- Ensure JUnit XML files contain complete test information
- Check that pytest is generating detailed XML reports
- Verify environment variables are set correctly

## Customization

### Modify Issue Format
Edit `python/tests/create_github_issue.py` to customize:
- Issue body structure
- Information included
- Formatting style

### Change Issue Labels
Modify the workflow file to add/remove labels:
```yaml
labels: ['tests', 'automated', 'bug', 'your-label']
```

### Adjust When Issues Are Created
Modify the `if` condition in the workflow:
```yaml
if: failure()  # Only on failure
# or
if: always()   # Always check (but script filters)
```

