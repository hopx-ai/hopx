# Changelog

All notable changes to the Hopx Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3] - 2025-11-20

### Fixed

**Critical: WebSocket Authentication Missing JWT Token**
- Fixed WebSocket connections failing authentication due to missing JWT token
- Both sync (`WebSocketClient`) and async (`AsyncTerminal`) now include JWT authentication
- Terminal and streaming features now authenticate correctly with sandbox agents
- Added `update_jwt_token()` method to `WebSocketClient` for token refresh support
- `Sandbox.refresh_token()` now updates WebSocket client tokens automatically
- **Impact**: Terminal connections and WebSocket streaming features were failing with authentication errors

**High: WebSockets Library Import Compatibility**
- Fixed mixed usage of legacy and new websockets API imports
- Now consistently uses `websockets.asyncio.client` (websockets 11.0+)
- Updated type hints to use `ClientConnection` from new asyncio API
- Improved compatibility with websockets>=12.0 requirement

**Code Quality: WebSocket Error Handling**
- WebSocket connection errors now wrapped in SDK-specific exceptions
- `TimeoutError` mapped to `HopxTimeoutError` for consistency
- Other WebSocket errors wrapped in `AgentError` with proper exception chaining
- Improved error messages with context about failed connections

**Files Modified**:
- `hopx_ai/_ws_client.py` - Added JWT token support, fixed imports, improved error handling (lines 8-18, 29-32, 55-60, 80-102)
- `hopx_ai/_async_terminal.py` - Added JWT authentication to async terminal connections (lines 97-99)
- `hopx_ai/sandbox.py` - Pass token to WebSocketClient, update on refresh (lines 367-368, 384-385)

### Changed

**Documentation: Token Refresh Race Condition**
- Added warning to `refresh_token()` docstring about race conditions during WebSocket connections
- Clarified that SDK handles automatic token refresh before expiry
- Recommended avoiding manual refresh during active WebSocket establishment

## [0.3.2] - 2025-11-17

### Fixed

**Critical: npm_install() Method Uses Wrong Path**
- Fixed `npm_install()` using incorrect npm path `/usr/bin/npm`
- Official Node.js Docker images install npm at `/usr/local/bin/npm`
- Changed both `npm install` and `npm install -g` commands to use correct path
- **Impact**: All templates using `.npm_install()` were failing with "command not found" errors
- **Files Modified**: `hopx_ai/template/builder.py` (lines 315, 333)

### Changed

**Examples: Comprehensive Testing and Quality Improvements**
- Fixed 5 examples with outdated API usage
- Created `ollama_template.py` - demonstrates Ollama LLM integration
- Removed desktop automation examples (require premium template)
- Fixed `rotate_api_keys.py` - removed undefined variable references
- Updated all examples to use current SDK v0.3.1 API
- Created `examples/app/requirements.txt` for template building examples
- Created `package.json` and `src/index.js` for Node.js template example
- All 25+ examples tested with data-driven evidence

**Examples Fixed**:
- `agent_code_execution.py` - Removed invalid callback parameters
- `agent_v3_1_features.py` - Fixed exception handling
- `lifecycle.py` - Fixed invalid Sandbox.create() parameters
- `rotate_api_keys.py` - Fixed invalid parameters and undefined variables
- `template_build.py` - Added unique names, mkdir workaround, workdir fix
- `template_nodejs.py` - Rewrote to avoid file copy operations

## [0.3.1] - 2025-11-17

### Fixed

**Critical: Template Building Upload Link Response**
- Fixed `UploadLinkResponse` model missing `files_hash` field returned by API
- API returns `files_hash` in `/v1/templates/files/upload-link` response
- SDK model was missing this field, causing `TypeError` on template builds
- Added `files_hash: Optional[str] = None` to `UploadLinkResponse` dataclass

**Files Modified**:
- `hopx_ai/template/types.py` - Added `files_hash` field to UploadLinkResponse (line 204)

**Documentation: Incorrect Template References**
- Fixed all examples and documentation using non-existent template names
- Only 2 public templates exist: `code-interpreter` and `base`
- Replaced 27 occurrences of `template="python"` and `template="nodejs"` with `code-interpreter`
- **Impact**: All examples were failing with HTTP 500 errors, now work correctly

**Examples: Resource Access Pattern**
- Fixed incorrect resource access in example files
- Changed `info.vcpu` to `info.resources.vcpu` (with null check)
- Changed `info.memory_mb` to `info.resources.memory_mb` (with null check)
- **Impact**: Quick start examples were crashing, now work correctly

**Files Modified**:
- `examples/quick_start.py` - Fixed resource access pattern
- `examples/async_quick_start.py` - Fixed resource access pattern

### Documentation

**Updated Template Lists**:
- README.md: All examples now use correct template names
- All code snippets tested and verified working

**Code Example Testing Policy**:
- All code examples in documentation are now tested before inclusion
- Example test app file created: `examples/app/main.py`
- Template building example verified end-to-end

### Removed

**Deprecated Endpoints**:
- Removed `stop()` and `start()` methods (endpoints no longer exist in API)
- Use `pause()` and `resume()` for sandbox lifecycle management instead

## [0.3.0] - 2025-11-16

### Added

**Preview URL Access for Sandbox Services**

Added methods to easily access services running inside sandboxes via public URLs. Hopx automatically exposes all ports from sandboxes, and this feature makes it simple to discover and access those URLs.

**New Methods**:
1. **`sandbox.get_preview_url(port: int = 7777) -> str`**
   - Returns the public URL for accessing a service on the specified port
   - Default port is 7777 (sandbox agent)
   - Parses `public_host` from sandbox info to construct URLs for other ports
   - Works with both `Sandbox` and `AsyncSandbox` classes

2. **`sandbox.agent_url` (property)**
   - Convenience property for the default sandbox agent URL (port 7777)
   - Equivalent to calling `get_preview_url(7777)`
   - Available on both sync and async classes

**URL Format**:
```
https://{port}-{sandbox_id}.{region}.vms.hopx.dev/
```

**Example - Accessing a Web App**:
```python
from hopx_ai import Sandbox

# Create sandbox and run web server
sandbox = Sandbox.create(template="code-interpreter")
sandbox.run_code_background("""
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>Hello from Hopx!</h1>')

HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
""", language="python")

# Get preview URL for port 8080
url = sandbox.get_preview_url(8080)
print(f"Access your app at: {url}")
# Output: https://8080-sandbox123.eu-1001.vms.hopx.dev/

# Get agent URL
agent = sandbox.agent_url
print(f"Sandbox agent: {agent}")
# Output: https://7777-sandbox123.eu-1001.vms.hopx.dev/
```

**Use Cases**:
- Deploying and accessing web applications
- Testing APIs and webhooks
- Accessing development servers (React, Vue, etc.)
- Connecting to databases or services with web UIs
- Real-time collaboration on code running in sandboxes

**Implementation Details**:
- Uses regex to parse `public_host` and extract sandbox ID and domain
- Supports multiple URL formats (with/without port prefix)
- Raises `HopxError` if URL format cannot be parsed
- Works seamlessly with async/await in `AsyncSandbox`

**Tested Examples** (all verified working):
- `examples/preview_url_basic.py` - **NEW**: Basic usage example
- `examples/preview_url_web_app.py` - **NEW**: Web app deployment example
- `examples/preview_url_async.py` - **NEW**: Async usage example
- `examples/test_preview_urls.py` - **NEW**: Comprehensive test suite

**Test Coverage**:
- Agent URL generation (port 7777)
- Custom port URL generation
- Multiple ports tested (3000, 5000, 8000, 9000)
- URL format validation
- Async/await support
- Optional HTTP accessibility check

**Files Modified**:
- `hopx_ai/sandbox.py` - Added `get_preview_url()` method and `agent_url` property
- `hopx_ai/async_sandbox.py` - Added async versions of both methods
- `README.md` - Added "Accessing Sandbox Services" section with tested examples
- `CLAUDE.md` - Added implementation details and testing policy
- 4 new tested example files

## [0.2.9] - 2025-11-16

### Fixed

**Environment Variables Propagation**
- Fixed bug where `env_vars` parameter in `Sandbox.create()` was not setting environment variables in the sandbox runtime
- Environment variables are now properly set via `sandbox.env.update()` after sandbox creation
- Applies to both sync (`Sandbox.create()`) and async (`AsyncSandbox.create()`)
- Variables are immediately available for code execution via `os.environ`

**Implementation**:
- After creating sandbox via API, SDK explicitly calls `sandbox.env.update(env_vars)` to set variables in the VM environment
- Both sync and async implementations updated

**Example**:
```python
sandbox = Sandbox.create(
    template="code-interpreter",
    env_vars={"API_KEY": "secret", "DEBUG": "true"}
)
result = sandbox.run_code("import os; print(os.environ['API_KEY'])")
# Now correctly prints: secret
```

### Changed

**Architecture: Code Deduplication and Shared Utilities**

Extracted 180+ lines of duplicated code into shared utility modules:

1. **`_parsers.py` (225 lines)** - Pure parsing functions:
   - `_parse_sandbox_info_response()` - SandboxInfo parsing (removed 98 duplicate lines)
   - `_parse_rich_outputs()` - Rich output parsing (removed 76 duplicate lines)
   - `_parse_iso_timestamp()` - Timestamp parsing (removed 24 duplicate lines)
   - `_parse_template_response()` - Template parsing
   - `_parse_template_list_response()` - Template list parsing

2. **`_token_cache.py` (136 lines)** - Shared token management:
   - `TokenData` dataclass (previously duplicated in both files)
   - Global `_token_cache` dict (now shared between Sandbox and AsyncSandbox)
   - `store_token_from_response()` - Token storage utility
   - `get_cached_token()` - Token retrieval utility
   - Token cache now properly shared between sync and async instances

3. **`_sandbox_utils.py` (158 lines)** - Payload builders:
   - `build_sandbox_create_payload()` - Sandbox creation payload (removed 40 duplicate lines)
   - `build_list_templates_params()` - Template list query params
   - `build_list_sandboxes_params()` - Sandbox list query params
   - `build_set_timeout_payload()` - Timeout update payload

**Benefits**:
- **DRY Principle**: Eliminated code duplication between Sandbox and AsyncSandbox
- **Maintainability**: Single source of truth for parsing, validation, and payload building
- **Testability**: Pure functions easier to test in isolation
- **Consistency**: Both sync and async use identical logic
- **Type Safety**: Shared utilities enforce consistent types

**Impact**:
- Sandbox.py: 251 insertions, 419 deletions (-168 lines net with refactoring)
- AsyncSandbox.py: 407 changes with significant deduplication
- **180+ duplicate lines eliminated**
- 3 new utility modules (519 lines total)
- **~28% code duplication reduction** in core sandbox classes

**Files Modified**:
- `hopx_ai/sandbox.py` - Uses shared utilities
- `hopx_ai/async_sandbox.py` - Uses shared utilities
- `hopx_ai/_parsers.py` - **NEW**: Pure parsing functions
- `hopx_ai/_token_cache.py` - **NEW**: Shared token management
- `hopx_ai/_sandbox_utils.py` - **NEW**: Payload builders

### Documentation
- Updated README.md with environment variables examples
- Documented that sensitive env vars (API_KEY, SECRET, TOKEN, PASSWORD) may be masked in `get_all()` responses

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
sandbox = Sandbox.create(template="code-interpreter")
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
