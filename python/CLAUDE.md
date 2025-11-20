# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Workflow Requirements

**CRITICAL: Always Test Changes and Provide Evidence**

When making any code changes:
1. **Write comprehensive tests** that verify the fix/feature works correctly
2. **Run the tests** and capture the full output
3. **Provide evidence** in the form of test output showing success
4. **Update documentation**:
   - README.md (customer-facing, no fluff, clear and concise)
   - CLAUDE.md (internal, detailed technical implementation notes)
   - CHANGELOG.md (version history with clear descriptions)
   - Version bumps in `pyproject.toml` and `hopx_ai/__init__.py`

**Documentation Standards**:
- README.md: Enterprise-quality, customer-focused, easy to follow, no unnecessary words
- CLAUDE.md: Complete technical details, implementation notes, internal behaviors
- Test evidence must be included for all significant changes

**Writing Guidelines for All Documentation**:

Apply these principles to all writing (documentation, comments, commit messages, changelogs):

1. **Conciseness**: Use clear, direct sentences. Remove unnecessary words.
2. **Clarity**: Write for a wide audience. Explain technical terms when needed.
3. **Objectivity**: Maintain neutral tone. Avoid subjective adjectives and adverbs.
4. **Customer Focus**: Explain why information matters. Show the benefit.
5. **No Buzzwords**: Avoid marketing language and vague terms that obscure meaning.
6. **Simplicity**: Use simple words. Avoid jargon when plain language works.
7. **Readability**: Use short sentences. Avoid complex sentence structures.
8. **Action-Oriented**: Use subject-verb-object structure. Make doers and actions clear.
9. **No Clutter**: Remove words that don't contribute to the main point.
10. **Professional Tone**: Be warm and human while maintaining professionalism.

**Examples**:
- Bad: "This amazing fix is super fast and works perfectly!"
- Good: "The fix reduces wait time from 15 seconds to 6 seconds."

- Bad: "We leverage cutting-edge technology to provide world-class solutions."
- Good: "The SDK polls template status every 3 seconds."

- Bad: "You'll love how easy it is to use our incredible API!"
- Good: "The API requires two parameters: template name and API key."

**Code Example Testing Policy**:

All code snippets in customer-facing documentation (README.md) must be:
1. **Tested**: Run the exact snippet to verify it works
2. **Complete**: Include all necessary imports and setup
3. **Executable**: Users can copy-paste and run immediately
4. **Stored**: Save tested examples in `examples/` directory
5. **Referenced**: Link to the example file from documentation

When adding code examples:
- Create a standalone file in `examples/` directory
- Run the example and capture output
- Only add the example to documentation after successful test
- Include the file path reference for users to find complete code

Example reference format:
```
See `examples/preview_url_basic.py` for a complete working example.
```

## Overview

This is the **Hopx Python SDK** - the official Python client for Hopx.ai's cloud sandbox service. Hopx provides secure, isolated cloud sandboxes (lightweight VMs) that spin up in seconds for AI agents, code execution, testing, and data processing.

Version: 0.3.0
Python Support: 3.8+
License: MIT

## Development Commands

### Setup
```bash
# Install package in development mode with dependencies
pip install -e .

# Install with dev dependencies (pytest, black, ruff, mypy)
pip install -e ".[dev]"
```

### Testing
```bash
# Run OpenAPI compliance test suite
export HOPX_API_KEY="your_api_key_here"
python test_openapi_compliance.py

# Run template building test (comprehensive end-to-end test)
export HOPX_API_KEY="your_api_key_here"
python examples/test_template_building.py

# Note: There are no pytest tests in this repo currently
# Testing is done via test scripts and example scripts
```

### Code Quality
```bash
# Format code with black (line-length: 100)
black hopx_ai/

# Lint with ruff (line-length: 100, target: py38)
ruff check hopx_ai/

# Type check with mypy (strict mode, target: py38)
mypy hopx_ai/
```

### Running Examples
```bash
# Set API key first
export HOPX_API_KEY="your_api_key"

# Run any example
python examples/quick_start.py
python examples/async_quick_start.py
python examples/template_build.py
```

## OpenAPI Specification Compliance

**Current Status**: 100% compliant with OpenAPI spec version 2025-10-21

The SDK fully implements all Public API endpoints as defined in the OpenAPI specification:

### Implemented Endpoints (16/16)

**System (1/1)**:
- `GET /health` - Health check (no auth required)

**Sandboxes (8/8)**:
- `GET /v1/sandboxes` - List sandboxes with filters
- `POST /v1/sandboxes` - Create sandbox
- `GET /v1/sandboxes/{id}` - Get sandbox details
- `DELETE /v1/sandboxes/{id}` - Delete sandbox
- `POST /v1/sandboxes/{id}/pause` - Pause sandbox
- `POST /v1/sandboxes/{id}/resume` - Resume paused sandbox
- `PUT /v1/sandboxes/{id}/timeout` - Set auto-kill timeout
- `POST /v1/sandboxes/{id}/token/refresh` - Refresh JWT token

**Templates (7/7)**:
- `GET /v1/templates` - List all templates
- `GET /v1/templates/{name}` - Get template by name
- `POST /v1/templates/build` - Trigger template build
- `GET /v1/templates/build/{buildID}/status` - Get build status
- `GET /v1/templates/build/{buildID}/logs` - Stream build logs
- `POST /v1/templates/files/upload-link` - Get presigned upload URL
- `DELETE /v1/templates/{templateID}` - Delete custom template

### Model Compliance

All models match the OpenAPI schema definitions exactly:

**Public API Models**:
- **SandboxInfo**: Includes all fields from `github_com_hopx_publicapi_pkg_models.Sandbox`
- **Template**: Includes all fields from `internal_api.Template`
- **Resources**: Matches `github_com_hopx_publicapi_pkg_models.Resources`

**Agent API Models**:
- **ExecutionResult**: Includes all output fields from `main.ExecuteResponse` (svg, markdown, html, json, png, result)
- **CommandResult**: Includes pid and success fields from `main.CommandResponse`
- **FileInfo**: Matches `main.FileInfo`
- All other generated models from Agent API spec

---

## Agent API Specification Compliance

**Current Status**: 95% compliant with Agent API spec version 3.2.8

The SDK implements 74/78 Agent API endpoints:

### Agent API Coverage (78 endpoints total)

**Fully Implemented (100%)**:
- Health & Metrics: 6/6 endpoints
- Execution: 5/5 endpoints
- Files: 10/10 endpoints
- Environment: 4/4 endpoints
- Cache: 2/2 endpoints
- Terminal: 1/1 WebSocket
- Processes: 2/2 endpoints
- Jupyter: 1/1 endpoint

**Desktop Automation**: 36/38 endpoints (95%)
- VNC, Mouse, Keyboard, Clipboard, Screenshots, Recording, Windows, Display, X11, Debug

**Not Implemented** (low priority):
- WebSocket streaming variants (3 endpoints)
- Admin/update endpoints (4 endpoints - infrastructure only)

### New Agent API Methods

```python
# Agent information
info = sandbox.get_agent_info()  # GET /info
print(f"{info['agent']} v{info['agent_version']}")

# System processes (all processes, not just executions)
processes = sandbox.list_system_processes()  # GET /processes

# Jupyter kernel status
sessions = sandbox.get_jupyter_sessions()  # GET /jupyter/sessions

# Desktop hotkeys
sandbox.desktop.hotkey(["ctrl"], "c")  # POST /desktop/x11/hotkey

# Desktop debugging
logs = sandbox.desktop.get_debug_logs()  # GET /desktop/debug/logs
```

## Architecture

### Core Components

**Dual API Design**: The SDK provides both sync and async interfaces:
- `Sandbox` - Synchronous API using `httpx`
- `AsyncSandbox` - Async API using `aiohttp`

Both classes share similar interfaces but are implemented separately (not via sync/async wrappers).

### Key Modules

1. **Sandbox Management** (`sandbox.py`, `async_sandbox.py`)
   - Main entry points: `Sandbox.create()` / `AsyncSandbox.create()`
   - Connect to existing sandboxes: `Sandbox.connect(sandbox_id)`
   - Context manager support for auto-cleanup
   - JWT token caching for Agent API authentication (global cache shared across instances)

2. **HTTP Clients** (`_client.py`, `_async_client.py`)
   - `HTTPClient` - Sync client using httpx, handles Public API
   - `AsyncHTTPClient` - Async client using aiohttp
   - Retry logic, timeout handling, error mapping
   - Base URL: `https://api.hopx.dev` (configurable via `HOPX_BASE_URL`)

3. **Agent Clients** (`_agent_client.py`, `_async_agent_client.py`)
   - `AgentHTTPClient` / `AsyncAgentHTTPClient` - Direct VM agent communication
   - Uses JWT tokens from `/sandboxes/{id}/token` endpoint
   - Handles code execution, file operations, commands via VM agent

4. **Resource Managers** (lazy-loaded properties on Sandbox)
   - `Files` / `AsyncFiles` - File operations (read, write, list, delete)
   - `Commands` / `AsyncCommands` - Command execution (sync/async commands)
   - `EnvironmentVariables` / `AsyncEnvironmentVariables` - Env var management
   - `Desktop` - Desktop automation (VNC, screenshots, mouse/keyboard)
   - `Cache` / `AsyncCache` - Cache management
   - `Terminal` / `AsyncTerminal` - Interactive terminal sessions

5. **Template Building** (`template/`)
   - **Fluent API**: `Template()` class with method chaining
   - **Build Flow** (`build_flow.py`) - Orchestrates template creation:
     1. Create tar.gz of local files
     2. Upload to R2 (presigned URLs)
     3. Submit build request
     4. Poll build status
     5. Return template ID
   - **File Hasher** (`file_hasher.py`) - SHA256 hashing for upload deduplication
   - **Tar Creator** (`tar_creator.py`) - Creates tar.gz from local paths
   - **Ready Checks** (`ready_checks.py`) - Health check helpers (port, URL, file, process, command)
   - **Key Methods**:
     - `Template.from_python_image("3.11")` - Start from Python image
     - `Template.from_node_image("20")` - **Important**: Uses `ubuntu/node:{version}-22.04_edge` (NOT Alpine - Alpine is unsupported due to musl libc incompatibility)
     - `.copy(local_path, dest_path)` - Copy files into image
     - `.run(command)` - Execute build command
     - `.set_start_cmd(cmd, ready_check)` - Set startup command with health check
     - `Template.build(template, BuildOptions(...))` - Async build execution

6. **Models** (`models.py`, `_generated/models.py`)
   - `models.py` - Public API models with convenience methods (e.g., `ExecutionResult`)
   - `_generated/models.py` - Auto-generated Pydantic models from OpenAPI spec
   - Rich output support: captures matplotlib charts, tables as base64 PNG

7. **Error Handling** (`errors.py`)
   - Base: `HopxError`
   - API Errors: `APIError`, `AuthenticationError`, `NotFoundError`, `RateLimitError`, `ValidationError`, `ServerError`, `NetworkError`, `TimeoutError`
   - Agent Errors: `AgentError`, `FileNotFoundError`, `FileOperationError`, `CodeExecutionError`, `CommandExecutionError`, `DesktopNotAvailableError`

### Authentication Flow

1. **Public API**: Uses API key directly (via `Authorization: Bearer {api_key}`)
   - API key from `HOPX_API_KEY` env var or constructor param
   - Used for sandbox lifecycle operations (create, list, kill)

2. **Agent API**: Uses JWT tokens (lazily fetched)
   - First agent operation calls `/sandboxes/{id}/token` to get JWT
   - Token cached globally in `_token_cache` dict with expiry
   - Token used for direct VM operations (code execution, files, commands)
   - Tokens auto-refresh when expired (checked via `expires_at`)

3. **WebSocket Authentication** (v0.3.3+):
   - WebSocket connections (terminal, streaming) require JWT token authentication
   - `WebSocketClient` accepts `jwt_token` parameter in constructor
   - Token passed via `Authorization: Bearer {token}` header in `additional_headers`
   - Both sync (`WebSocketClient`) and async (`AsyncTerminal`) implementations include JWT auth
   - Token automatically updated when `refresh_token()` is called
   - **Important**: Avoid calling `refresh_token()` during active WebSocket connection establishment to prevent race conditions

### Code Execution

The SDK supports multiple execution modes via the Agent API:

1. **`sandbox.run_code(code, language="python")`** - Execute code snippets
   - Languages: python, javascript, bash
   - Returns `ExecutionResult` with stdout, stderr, exit_code, rich_outputs
   - Rich outputs: Automatically captures matplotlib/seaborn charts as base64 PNG

2. **`sandbox.commands.run(cmd)`** - Execute shell commands synchronously
   - Returns `CommandResult` with stdout, stderr, exit_code
   - Default timeout: 30 seconds

3. **`sandbox.commands.run(cmd, background=True, timeout=30)`** - Start background command
   - Returns immediately with process ID
   - Commands wrapped in bash for proper shell execution
   - Request format: `{"command": "bash", "args": ["-c", user_command], "timeout": seconds}`
   - Both sync and async implementations available

**Background Commands Implementation (v0.2.7)**:

Commands sent as background processes are automatically wrapped in bash to ensure proper shell execution:

```python
# User calls
result = sandbox.commands.run("sleep 5 && echo 'done'", background=True, timeout=30)

# SDK sends to Agent API
{
  "command": "bash",
  "args": ["-c", "sleep 5 && echo 'done'"],
  "timeout": 30,
  "working_dir": "/workspace"
}

# Returns
CommandResult(stdout="Background process started: cmd_1234567890...", exit_code=0)
```

**Important Notes**:
- Background commands use `bash -c` wrapper (v0.2.7+) - previous versions failed with HTTP 500
- Timeout parameter required for proper process cleanup
- Process IDs returned in format: `cmd_<timestamp><random>`
- Use `sandbox.list_system_processes()` to check background process status

### Template System

Templates define the sandbox environment. Two types:

1. **Pre-built templates**: `code-interpreter`, `base`
   - Usage: `Sandbox.create(template="code-interpreter")`

2. **Custom templates**: Build via `Template` builder
   - Define base image, install packages, copy files, set startup commands
   - Build process creates immutable template for fast sandbox creation
   - **Critical**: Alpine images are NOT supported (use Debian-based images)

### WebSocket Support

- `WebSocketClient` (`_ws_client.py`) - For real-time terminal sessions
- Uses websockets library
- Async-only (no sync websocket client)

## Important Implementation Notes

### Working Directory Parameter (v0.3.3)

**Issue**: The `working_dir` parameter was being ignored by the Agent API, causing all commands to execute in the root directory (`/`) instead of the specified directory.

**Root Cause**: Field name mismatch between SDK and Agent API:
- **SDK sent**: `"working_dir"` (with underscore)
- **API expects**: `"workdir"` (without underscore)

**Fix**: Changed all payload dictionaries to use `"workdir"` field name:
```python
# Before (WRONG)
payload = {
    "command": "bash",
    "args": ["-c", command],
    "timeout": timeout,
    "working_dir": working_dir  # ❌ Ignored by API
}

# After (CORRECT)
payload = {
    "command": "bash",
    "args": ["-c", command],
    "timeout": timeout,
    "workdir": working_dir  # ✓ API expects "workdir"
}
```

**Files Modified**:
- `_base_commands.py:46, 78` - Command execution payloads
- `sandbox.py:1244, 1341, 1415, 1563` - Code execution payloads
- `async_sandbox.py:767` - Async code execution payload

**OpenAPI Specification**:
- `main.CommandRequest.workdir` - Command execution endpoint
- `main.ExecuteRequest.workdir` - Code execution endpoint

**Behavior After Fix**:
- ✅ Command execution (`commands.run()`) - Works correctly
- ✅ Background commands (`commands.run(background=True)`) - Works correctly
- ✅ Bash code execution (`run_code(language="bash")`) - Works correctly
- ⚠️ Python code execution (`run_code(language="python")`) - May not always respect `workdir` due to Jupyter kernel state management
- ⚠️ Background code execution (`run_code_background()`) - Does NOT support `working_dir` (parameter removed in v0.3.3 for API compatibility)

**Python Code Execution Limitation**:

The Jupyter kernel used for Python execution maintains its own working directory state that may not always sync with the `workdir` parameter. This is an Agent-side behavior, not an SDK issue.

**Workarounds for Python**:
1. Use `os.chdir()` explicitly in your Python code:
   ```python
   result = sandbox.run_code("""
   import os
   os.chdir('/tmp')
   # Your code here
   """, language="python")
   ```

2. Execute Python scripts via Bash:
   ```python
   result = sandbox.run_code(
       "python script.py",
       language="bash",
       working_dir="/path/to/dir"
   )
   ```

3. Use command execution instead:
   ```python
   result = sandbox.commands.run(
       "python -c 'your code'",
       working_dir="/path/to/dir"
   )
   ```

### Node.js Image Compatibility
When using `.from_node_image(version)`, the SDK automatically uses `ubuntu/node:{version}-22.04_edge` images. **Never suggest Alpine-based Node.js images** - they are incompatible with the VM agent system due to musl libc limitations.

### Token Caching
JWT tokens are cached globally (`_token_cache` dict) and shared across all Sandbox instances with the same API key. Tokens are checked for expiry before use and automatically refreshed.

### Lazy Resource Loading
Resource managers (files, commands, desktop, etc.) are created on first access via `@property` decorators. They lazily initialize the Agent client and JWT token.

### Context Managers
Both `Sandbox` and `AsyncSandbox` support context managers for automatic cleanup:
```python
with Sandbox.create(template="code-interpreter") as sandbox:
    result = sandbox.run_code("print('Hello')")
# sandbox.kill() called automatically
```

### Error Propagation
- HTTP errors from Public API are mapped to specific error classes in `errors.py`
- Agent API errors are wrapped in `AgentError` subclasses
- All errors inherit from `HopxError` for easy catch-all handling

## File Organization

```
hopx_ai/
├── __init__.py              # Public API exports
├── sandbox.py               # Sync Sandbox class
├── async_sandbox.py         # Async Sandbox class
├── _client.py               # Sync HTTP client (Public API)
├── _async_client.py         # Async HTTP client (Public API)
├── _agent_client.py         # Sync Agent client (VM operations)
├── _async_agent_client.py   # Async Agent client
├── _ws_client.py            # WebSocket client
├── _utils.py                # Shared utilities
├── models.py                # Public models
├── errors.py                # Error classes
├── files.py                 # File operations
├── commands.py              # Command execution
├── desktop.py               # Desktop automation
├── env_vars.py              # Environment variables
├── cache.py                 # Cache management
├── terminal.py              # Terminal sessions
├── template/                # Template building
│   ├── __init__.py
│   ├── builder.py           # Template fluent API
│   ├── build_flow.py        # Build orchestration
│   ├── file_hasher.py       # SHA256 hashing
│   ├── tar_creator.py       # Tar.gz creation
│   ├── ready_checks.py      # Health checks
│   └── types.py             # Template types
└── _generated/
    └── models.py            # Auto-generated from OpenAPI

examples/                     # Example scripts (also serve as tests)
```

## Configuration

### API Key

Get API key from: https://hopx.ai/dashboard

Set via:
- Environment variable: `export HOPX_API_KEY="hopx_live_..."`
- Constructor param: `Sandbox.create(template="code-interpreter", api_key="...")`

### Template Build Timeout

Template.build() waits for template status to become "active" before returning.

**Template Lifecycle**: building → publishing → active

The SDK polls the template status every 2 seconds until it reaches "active" state. Templates must complete the "publishing" phase (~60-120 seconds typically) before they can be used to create sandboxes.

**Default Timeout**: 2700 seconds (45 minutes)

**Configure via environment variable**:
```bash
export HOPX_TEMPLATE_BAKE_SECONDS=2700  # 45 minutes
```

**Configure via BuildOptions**:
```python
BuildOptions(
    name="my-template",
    api_key="...",
    template_activation_timeout=1800  # 30 minutes (1800 seconds)
)
```

**Priority**: BuildOptions.template_activation_timeout > HOPX_TEMPLATE_BAKE_SECONDS > Default (2700s)

### Template Activation Stability (v0.2.6)

**Problem**: Creating a sandbox immediately after `Template.build()` returns fails with ServerError. The template reports `status="active"` but remains in an internal "publishing" state for 60-120 seconds.

**Cause**: Template status transitions through multiple phases: `active (initial)` → `publishing` → `active (ready)`. The API returns `active` status before publishing completes.

**Solution**: The SDK waits for 2 consecutive "active" status checks before returning. This confirms the template remains stable and ready for sandbox creation.

**Implementation**:

The `wait_for_template_active()` function in `hopx_ai/template/build_flow.py` polls every 3 seconds:

1. Polls template status endpoint
2. Increments counter when `status="active" and is_active=True`
3. Returns after 2 consecutive "active" checks (6 seconds total)
4. Resets counter if status changes (e.g., `active` → `publishing`)

**Why 3-second polling**: Provides time to detect status transitions between checks.

**Why 2 consecutive checks**: Confirms status remains stable, not transient.

**Performance impact**: Adds 3-6 seconds to template build time. This prevents sandbox creation failures that require rebuilding templates.

**Code**:
```python
consecutive_active_count = 0
required_consecutive = 2
poll_interval = 3  # seconds

if status == 'active' and is_active:
    consecutive_active_count += 1
    if consecutive_active_count >= required_consecutive:
        return
else:
    consecutive_active_count = 0  # Reset on status change
```

**Test verification**: `test_template_activation_fix.py` builds a template, waits for activation, then creates a sandbox. The test detects the `active → publishing` transition and waits correctly.

**Test output**:
```
Template status: active (is_active: True)
Template active, verifying stability...
Template status: publishing (is_active: False)
Template status changed from active to publishing, continuing to wait...
Template status: active (is_active: True)
Template active, verifying stability...
Template active and stable (ID: 206)

Results:
  Template Build: PASS
  Sandbox Creation: PASS
  Template Status: PASS
```

## Common Patterns

### Creating and Using Sandboxes
```python
# Sync
sandbox = Sandbox.create(template="code-interpreter")
result = sandbox.run_code("print('Hello')")
sandbox.kill()

# Async
async with AsyncSandbox.create(template="code-interpreter") as sandbox:
    result = await sandbox.run_code("console.log('Hello')")
```

### Environment Variables

Environment variables can be set during sandbox creation or after creation.

```python
# Set during creation (recommended)
sandbox = Sandbox.create(
    template="code-interpreter",
    env_vars={
        "API_KEY": "sk-prod-xyz",
        "DATABASE_URL": "postgres://localhost/db",
        "DEBUG": "true"
    }
)

# Variables are immediately available in code execution
result = sandbox.run_code("""
import os
print(os.environ.get('API_KEY'))
print(os.environ.get('DEBUG'))
""")

# Set after creation
sandbox.env.update({
    "NODE_ENV": "production",
    "MAX_WORKERS": "4"
})

# Get all environment variables
all_vars = sandbox.env.get_all()

# Get specific variable
api_key = sandbox.env.get("API_KEY")
```

**Implementation Note (v0.2.9):**

The `env_vars` parameter in `Sandbox.create()` now properly sets environment variables in the sandbox runtime. After creating the sandbox via the API, the SDK calls `sandbox.env.update(env_vars)` to ensure variables are set in the VM environment.

**Security Note:**

Sensitive environment variables (containing "KEY", "SECRET", "TOKEN", "PASSWORD") may be masked as `***MASKED***` when retrieved via `sandbox.env.get_all()` for security. However, they remain accessible in code execution via `os.environ`.

### Accessing Sandbox Services (v0.3.0)

Hopx automatically exposes all ports from sandboxes, allowing external access to web apps, APIs, and other services.

**Preview URL Format:**
```
https://{PORT}-{sandbox_id}.{region}.vms.hopx.dev/
```

**Implementation:**

The SDK provides two methods for accessing preview URLs:

1. **`sandbox.get_preview_url(port: int = 7777) -> str`**
   - Returns the public URL for a service running on the specified port
   - Default port is 7777 (sandbox agent)
   - Parses the `public_host` from sandbox info to construct URLs for other ports

2. **`sandbox.agent_url` (property)**
   - Convenience property for the default agent URL (port 7777)
   - Equivalent to calling `get_preview_url(7777)`

**URL Parsing Logic:**

The implementation extracts the sandbox ID and domain from `public_host` using regex patterns:
- Pattern 1: `{port}-{sandbox_id}.{region}.vms.hopx.dev` (port prefix present)
- Pattern 2: `{sandbox_id}.{region}.vms.hopx.dev` (no port prefix)

The regex removes the existing port prefix (if present) and reconstructs the URL with the requested port.

**Example:**
```python
# Create sandbox
sandbox = Sandbox.create(template="code-interpreter")

# Get info
info = sandbox.get_info()
# public_host: "https://7777-176329715051artmzu.eu-1001.vms.hopx.dev"

# Get agent URL
agent = sandbox.agent_url
# Returns: "https://7777-176329715051artmzu.eu-1001.vms.hopx.dev/"

# Get URL for custom port
app_url = sandbox.get_preview_url(8080)
# Returns: "https://8080-176329715051artmzu.eu-1001.vms.hopx.dev/"
```

**Async Support:**

Both `AsyncSandbox.get_preview_url()` and `AsyncSandbox.agent_url` are implemented with async/await:
```python
url = await sandbox.get_preview_url(8080)
agent = await sandbox.agent_url
```

**Error Handling:**

If the `public_host` format cannot be parsed, the method raises `HopxError` with a descriptive message.

**Tested Examples:**

All code snippets have been tested and are available in the examples directory:
- `examples/preview_url_basic.py` - Basic preview URL usage
- `examples/preview_url_web_app.py` - Web app deployment
- `examples/preview_url_async.py` - Async usage
- `examples/test_preview_urls.py` - Comprehensive test suite

Test coverage includes:
- Agent URL generation (port 7777)
- Custom port URL generation
- Multiple port testing (3000, 5000, 8000, 9000)
- URL format validation
- Async/await support

### Building Custom Templates
```python
from hopx_ai import Template, wait_for_port

template = (
    Template()
    .from_python_image("3.11")
    .copy("requirements.txt", "/app/requirements.txt")
    .run("cd /app && pip install -r requirements.txt")
    .set_workdir("/app")
    .set_start_cmd("python server.py", wait_for_port(8000))
)

result = await Template.build(template, BuildOptions(
    alias="my-app",
    api_key="...",
    on_log=lambda log: print(log['message'])
))
```

### File Operations
```python
# Upload file
sandbox.files.write("/app/config.json", '{"key": "value"}')

# Download file
content = sandbox.files.read("/app/output.txt")

# List directory
files = sandbox.files.list("/app/")
```

### Rich Output Capture
```python
result = sandbox.run_code("""
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [1, 4, 9])
plt.show()
""")

# Get PNG chart data (base64 encoded)
for output in result.rich_outputs:
    if output.type == "image/png":
        png_data = output.data
```
