# Hopx Python SDK - Examples Documentation

This directory contains comprehensive examples demonstrating all features of the Hopx Python SDK.

## Recent Updates (2025-11-16)

**Updated Examples**:
- `agent_commands.py` - Removed non-existent callback parameters (on_stdout, on_stderr)
- `template_build.py` - Fixed to use `AsyncSandbox.create()` instead of deprecated `create_vm()` API
- `template_nodejs.py` - Fixed to use `AsyncSandbox.create()` instead of deprecated `create_vm()` API
- `debug_logging.py` - Removed hardcoded API key, now uses HOPX_API_KEY env var
- `lazy_iterator.py` - Removed hardcoded API key, now uses HOPX_API_KEY env var
- `async_iterator.py` - Removed hardcoded API key, now uses HOPX_API_KEY env var

**New Examples**:
- `env_vars_example.py` - Comprehensive environment variables demonstration (NEW v0.3.0 feature)

## Prerequisites

```bash
# Install the SDK in development mode
pip install -e .

# Or using uv (recommended)
uv venv
uv pip install -e .

# Set your API key
export HOPX_API_KEY="your_api_key_here"
```

## Running Examples

All examples require the `HOPX_API_KEY` environment variable to be set:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run any example
python3 examples/quick_start.py
python3 examples/env_vars_example.py
python3 examples/agent_commands.py
```

## Example Categories

### Basic Usage
- `quick_start.py` - Simple sandbox creation and basic operations
- `async_quick_start.py` - Async version of quick start
- `context_manager.py` - Using context managers for automatic cleanup
- `list_sandboxes.py` - Listing and filtering sandboxes

### Code Execution
- `agent_code_execution.py` - Comprehensive code execution examples (Python, JS, Bash)
- `agent_complete_workflow.py` - End-to-end data science workflow

### Environment Variables (NEW)
- `env_vars_example.py` - Environment variable management
  - Setting env vars during sandbox creation
  - Updating env vars after creation
  - Per-request env var overrides
  - Environment variable precedence

### Command Execution
- `agent_commands.py` - Shell command execution examples
  - Running commands synchronously
  - Error handling
  - Pipeline commands
  - Multi-line scripts

### File Operations
- `agent_files.py` - File operations (read, write, upload, download, list)

### Template Building
- `template_build.py` - Custom Python template building
- `template_nodejs.py` - Custom Node.js template with multiple instances
- `template_build_with_logs.py` - Template building with log monitoring
- `templates.py` - Browsing and using pre-built templates

### Preview URLs (v0.3.0)
- `preview_url_basic.py` - Basic preview URL usage
- `preview_url_web_app.py` - Web app deployment example
- `preview_url_async.py` - Async preview URL usage

### Desktop Automation
- `desktop_automation.py` - Mouse and keyboard control
- `desktop_vnc.py` - VNC server management
- `desktop_windows.py` - Window management
- `desktop_screenshot_recording.py` - Screenshots and recording
- `desktop_complete_workflow.py` - Complete desktop automation workflow

### Advanced Features
- `lazy_iterator.py` - Memory-efficient sandbox iteration
- `async_iterator.py` - Async memory-efficient iteration
- `debug_logging.py` - Enabling debug logging for API inspection
- `rotate_api_keys.py` - Automatic API key rotation on rate limits
- `lifecycle.py` - Sandbox lifecycle management (pause, resume, stop, start)

### Tests
- `test_template_building.py` - Comprehensive template building test suite
- `test_preview_urls.py` - Preview URLs test suite

## Template Building Tests

### Python SDK Test

The `test_template_building.py` script tests the complete template building flow for the Python SDK, matching all tests from `test-template-build.sh`.

### Prerequisites

```bash
# Install dependencies
pip install aiohttp

# Or if using the SDK from source
cd python/
pip install -e .
```

### Running the Test

```bash
# Set your API key
export HOPX_API_KEY="your_api_key_here"

# Optional: Set custom API base URL
export HOPX_BASE_URL="http://localhost:8080"  # Default: https://api.hopx.dev

# Run the test
python examples/test_template_building.py
```

### What Gets Tested

1. **Step 1**: File upload to R2
   - Creates test files (app.py, requirements.txt)
   - Gets presigned upload URL
   - Uploads tar.gz to R2

2. **Step 2a**: Minimal template build
   - Required fields only: name, cpu, memory, diskGB, from_image
   - Single RUN step

3. **Step 2b**: Full features template
   - Multiple RUN steps
   - ENV variables
   - WORKDIR
   - USER
   - System packages installation

4. **Step 2c**: Template with COPY step
   - Uses uploaded files from Step 1
   - Tests COPY step with filesHash

5. **Step 3**: Validation errors (negative tests)
   - Missing required fields
   - CPU/Memory out of range
   - Alpine image rejection
   - Duplicate template name
   - Update non-existent template

6. **Step 4**: Update existing template
   - Tests update=true flag

7. **Step 5**: Build status check
   - Polls template build status

8. **Step 6**: Build logs retrieval
   - Gets build logs with offset

9. **Step 7**: List templates
   - Lists all templates and finds test templates

### Test Output

The script uses color-coded output:
- 🟢 Green ✓ = Success
- 🔴 Red ✗ = Error
- 🟡 Yellow ⚠ = Warning
- 🔵 Blue ▶ = Step

### Cleanup

Test creates temporary files in `/tmp/hopx_test_template_id_*_py.txt` which are automatically cleaned up at the end.

### Example Output

```
╔════════════════════════════════════════════════════════════════╗
║     HOPX Python SDK - Template Building Flow Test             ║
╚════════════════════════════════════════════════════════════════╝

API Base URL: https://api.hopx.dev
Test Template: test-python-1234567890

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Checking API Key
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ API Key is set: hopx_live_...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 1: Get Presigned Upload URL & Upload to R2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▶ Creating test tar.gz file
✓ Test file created: 256 bytes
✓ Files hash: abc123...
▶ Requesting presigned upload URL
✓ Upload link received
✓ Upload URL received
▶ Uploading file to R2...
✓ File uploaded to R2 successfully!

[... more tests ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Test Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Passed: 25
Failed: 0
Warnings: 2

✓ All tests completed successfully!
```

### Troubleshooting

**Error: "API_KEY environment variable is not set"**
- Make sure to export HOPX_API_KEY before running

**Error: "Failed to get upload link"**
- Check if R2/S3 is configured in api-public
- Verify API key has proper permissions

**Error: "Alpine should have been rejected"**
- This is expected - Alpine images are not supported

**Warnings about cache hits**
- Files already uploaded to R2 - this is normal and expected

