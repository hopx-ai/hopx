# Changelog

All notable changes to the Hopx Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.8] - 2025-11-16

### Fixed

**Commands API - Critical Shell Execution Bug**
- Fixed critical bug affecting ALL command execution (sync, async, regular, background)
- Commands now properly wrapped in bash for shell feature support: `{"command": "bash", "args": ["-c", command]}`
- Fixes commands with pipes, redirects, variables, and other shell features
- Resolves HTTP 500 "executable file not found" errors for background commands
- Resolves empty stdout for regular commands that use shell features

**Specific Fixes**:
- `Commands.run()` (sync regular): Now uses bash wrapper
- `Commands._run_background()` (sync background): Now uses bash wrapper + added `timeout` parameter
- `AsyncCommands.run()` (async regular): Now uses bash wrapper
- `AsyncCommands._run_background()` (async background): New method with bash wrapper

### Changed

**Architecture: Consolidated Commands Implementation**
- Eliminated code duplication between sync and async Commands classes
- Introduced base class pattern (`_CommandsBase`) for shared logic
- Payload building logic now in single location (DRY principle)
- All command execution endpoints now send: `{"command": "bash", "args": ["-c", user_command], ...}`
- `Commands._run_background()`: Added `timeout` parameter (default: 30 seconds)
- `AsyncCommands.run()`: Added `background` parameter to match sync API

**Technical Implementation**:
- Created `hopx_ai/_base_commands.py` with shared payload building methods
- `Commands` and `AsyncCommands` now inherit from `_CommandsBase`
- Shared methods: `_build_run_payload()`, `_build_background_payload()`, `_log_command_start()`
- Zero runtime overhead, full type safety maintained
- Single source of truth for payload format (easier maintenance)

### Documentation
- Updated README.md with correct command execution examples
- Documented that background commands don't capture stdout/stderr (redirect to files required)
- Fixed incorrect `run_async()` example (now uses `background=True` parameter)

### Testing
- Verified all 4 execution paths: sync regular, async regular, sync background, async background
- Confirmed shell features work: pipes, redirects, variables, multi-line commands
- Confirmed stdout is returned correctly for regular commands

## [0.2.6] - 2025-11-16

### Fixed

**Template Build Activation**
- Fixed race condition in `wait_for_template_active()` that caused premature returns
- Templates show `status="active"` immediately after build but transition to "publishing" for 60-120 seconds
- SDK now requires 2 consecutive "active" status checks (6 seconds) before returning
- Polling interval increased from 2 seconds to 3 seconds
- Counter resets if status changes (e.g., `active` → `publishing`)
- Prevents ServerError when creating sandboxes from newly built templates
- Adds 3-6 seconds to build time, eliminates need to rebuild failed templates

### Changed
- Environment variable: `HOPX_TEMPLATE_BAKE_SECONDS` (default: 2700 seconds)
- Poll interval: 3 seconds (previously 2 seconds)
- Stability verification: 2 consecutive "active" checks required
- Logging: Shows verification status and regression detection messages

### Documentation
- Added writing guidelines to CLAUDE.md for enterprise documentation standards
- Updated CLAUDE.md with technical implementation details
- Updated README.md with timeout configuration
- Documented template lifecycle: `building → publishing → active`

### Testing
- Added `test_template_activation_fix.py` test script
- Test verifies template build, sandbox creation, and code execution
- Test detects `active → publishing` status transition correctly

## [0.1.19] - 2025-01-11

### 🎉 Public Release - Complete Feature Set

This release represents the complete, production-ready Hopx Python SDK with full agent capabilities.

### ✨ Core Features

**Sandbox Management**
- Create lightweight VM sandboxes in seconds with `Sandbox.create()`
- Multiple language environments: Python, Node.js, Go, Rust, Java, and more
- Pre-built templates for instant deployment
- Custom template building with `Template.build()`
- Auto-cleanup with timeout management (`timeout_seconds`)
- Internet access control per sandbox

**Code Execution**
- Execute Python, JavaScript, Bash, and more languages
- Real-time stdout/stderr streaming
- Rich output capture (PNG charts, HTML tables, JSON data)
- Environment variable injection
- Execution timeout controls
- Async/await support with `AsyncSandbox`

**File Operations**
- Full filesystem access: read, write, delete, list
- Directory operations and recursive listing
- File upload/download with streaming support
- Permission management
- Large file handling (up to 100MB)

**Command Execution**
- Run shell commands with full control
- Async command execution with background processes
- Real-time output streaming
- Exit code and error handling
- Working directory control

**Environment Management**
- Set/get environment variables
- Batch operations for multiple variables
- Persistent environment across executions
- Delete individual or all variables

**Process Management**
- List running processes with CPU/memory stats
- Kill processes by PID
- Process monitoring and health checks
- Resource usage tracking

**Desktop Automation** (Premium)
- VNC access to graphical desktop
- Mouse and keyboard control
- Screenshot capture
- Window management
- OCR text extraction
- Screen recording

**Cache Management**
- Built-in cache for dependencies and artifacts
- List cached files with size info
- Clear cache by pattern or entirely
- Cache statistics (size, file count, age)

**Real-time Features**
- WebSocket support for live updates
- File watching with change notifications
- Terminal streaming
- Log streaming from builds

### 🔧 Template Building

- Build custom Docker-like templates from code
- Multi-stage builds with caching
- Copy local files with hash-based deduplication
- Run commands during build
- Set environment variables
- Configure start commands and health checks
- Wait for ports, files, processes, or HTTP endpoints
- Private registry support (Docker Hub, GCR, ECR)

### 🚀 Performance

- Sandbox creation: ~100ms
- Code execution: <100ms overhead
- File operations: <50ms for small files
- Parallel sandbox support: 100+ concurrent

### 🔐 Security

- Isolated VM environments
- Network policies (internet access control)
- Resource limits (CPU, memory, disk)
- Automatic cleanup on timeout
- Secure API key authentication

### 📚 API Highlights

```python
from hopx_ai import Sandbox

# Quick start
sandbox = Sandbox.create(template="python")
result = sandbox.run_code("print('Hello, Hopx!')")
print(result.stdout)  # "Hello, Hopx!"
sandbox.kill()

# Rich outputs (charts, tables)
result = sandbox.run_code("""
import matplotlib.pyplot as plt
plt.plot([1,2,3], [1,4,9])
plt.show()
""")
png_data = result.rich_outputs[0].data  # Base64 PNG

# File operations
sandbox.files.write("/app/data.txt", "Hello, World!")
content = sandbox.files.read("/app/data.txt")

# Template building
from hopx_ai import Template, wait_for_port

template = (
    Template()
    .from_python_image("3.11")
    .copy("app/", "/app/")
    .pip_install()
    .set_start_cmd("python /app/main.py", wait_for_port(8000))
)

result = await Template.build(template, BuildOptions(
    alias="my-app",
    api_key="your-api-key"
))

# Create sandbox from template
sandbox = Sandbox.create(template_id=result.template_id)
```

### 🐛 Bug Fixes

- Fixed `template_id` type conversion in sandbox creation
- Fixed WebSocket connection handling
- Fixed file upload for large files
- Improved error messages and types
- Fixed async cleanup in context managers

### 🔄 Breaking Changes

- Renamed `BunnyshellError` → `HopxError`
- Renamed `timeout` → `timeout_seconds` in `Sandbox.create()`
- Removed deprecated `/v1/vms` endpoints (use `Sandbox.create()` instead)
- Environment variable: `BUNNYSHELL_API_KEY` → `HOPX_API_KEY`

### 📦 Dependencies

- Python 3.8+
- httpx >= 0.24.0
- websockets >= 11.0
- aiohttp >= 3.8.0 (for template building)

---

## Previous Versions

See [GitHub Releases](https://github.com/hopx-ai/hopx/releases) for older versions.
