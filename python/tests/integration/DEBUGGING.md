# Debugging Integration Tests

This document explains how to use the debugging utilities to identify where tests get stuck or take too long.

## Enabling Debug Mode

Set the `HOPX_TEST_DEBUG` environment variable to enable verbose debugging output:

```bash
export HOPX_TEST_DEBUG=true
pytest tests/integration/template/
```

Or run with the environment variable inline:

```bash
HOPX_TEST_DEBUG=true pytest tests/integration/template/ -v
```

## What Debug Mode Provides

When debug mode is enabled, you'll see:

1. **Test Timing**: Each test logs its start and completion with duration
2. **Operation Timing**: Long-running operations (like `Template.build()`) log their duration
3. **Warnings**: Operations that exceed thresholds (default: 60 seconds) log warnings
4. **Progress Indicators**: For very long operations, periodic updates show progress

## Example Output

With `HOPX_TEST_DEBUG=true`, you'll see output like:

```
14:23:15 [INFO] hopx.test.debug: ============================================================
14:23:15 [INFO] hopx.test.debug: TEST: TestTemplateBuilding::test_create_simple_template
14:23:15 [INFO] hopx.test.debug: ============================================================
14:23:15 [DEBUG] hopx.test.debug: Starting: Template.build (template_name=test-template-1234567890)
14:23:45 [DEBUG] hopx.test.debug: Completed: Template.build in 30.12s (template_name=test-template-1234567890)
14:24:00 [INFO] hopx.test.debug: TEST COMPLETE: TestTemplateBuilding::test_create_simple_template (duration: 45.23s)
14:24:00 [INFO] hopx.test.debug: ============================================================
```

If an operation takes longer than the threshold (default 60s), you'll see:

```
14:25:00 [WARNING] hopx.test.debug: ⚠️  Template.build took 75.34s (>60s threshold)
```

## Using Debug Utilities in Tests

### Timing Operations

Wrap long-running operations with `timed_operation`:

```python
from tests.integration.debug_utils import timed_operation

# In your test
with timed_operation("Template.build", warn_threshold=60.0, template_name=name):
    result = await Template.build(template, options)
```

### Progress Indicators

For very long operations, use progress indicators:

```python
from tests.integration.debug_utils import ProgressIndicator

progress = ProgressIndicator("Building template", interval=30.0)
# In a loop or long operation:
progress.check()  # Prints update every 30 seconds
# When done:
progress.complete()
```

## Common Long-Running Operations

The following operations are known to take 1+ minutes and are already instrumented:

- `Template.build()` - Template building (60s threshold)
- `AsyncSandbox.create()` - Sandbox creation (30s threshold)
- `Sandbox.create()` - Synchronous sandbox creation (30s threshold)

## Troubleshooting

### Test appears stuck

1. Enable debug mode: `HOPX_TEST_DEBUG=true`
2. Look for the last logged operation - that's where it's stuck
3. Check if warnings appear for operations exceeding thresholds
4. Review the test output for the specific operation that's hanging

### Operation taking too long

1. Check the warning messages - they indicate which operations exceed thresholds
2. Review the operation context (template name, sandbox ID, etc.) in the logs
3. Consider if the operation is actually stuck or just slow
4. Check API status or network connectivity if operations consistently timeout

## Integration with Test Runner

The test runner script (`run_integration_suites.sh`) can be run with debug mode:

```bash
HOPX_TEST_DEBUG=true ./run_integration_suites.sh
```

This will show detailed timing information for all tests across all phases.

