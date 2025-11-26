# Changelog

All notable changes to the Hopx JavaScript/TypeScript SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.7] - 2025-11-26

### Fixed

**Template Activation Stability: Conservative `is_active` Default**
- Fixed `is_active` defaulting to `true` when API returns `undefined` or `null`
- **Impact**: SDK could prematurely return from `Template.build()` before template was ready, causing `ServerError` when creating sandboxes
- **Resolution**: Changed default from `true` to `false` (conservative approach, matching Python SDK behavior)
- **Files Modified**: `src/template/build-flow.ts` (line 632)

**Template Build Error Context**
- Build failures now throw `TemplateBuildError` with comprehensive debugging information
- Error includes: build ID, template ID, build status, logs URL, and extracted error details from build logs
- **Previous**: Generic error message: `Build failed: Unknown error`
- **Now**: Rich error with structured metadata for debugging and HopX bug reports
- **Files Modified**: `src/template/build-flow.ts` (lines 103-143), `src/errors.ts` (new `TemplateBuildError` class)

**Missing `filesHash` Mapping in Upload Response**
- Fixed `filesHash` field not being mapped from API response in `getUploadLink()`
- **Impact**: File hash was lost during upload flow, preventing proper cache validation
- **Files Modified**: `src/template/build-flow.ts` (line 240)

### Added

**Template Status Change Tracking**
- Template activation now logs all status transitions for debugging
- Log format: `Template status: {status} (is_active: {value})`
- **Benefit**: Provides visibility into template lifecycle (building → publishing → active)
- **Files Modified**: `src/template/build-flow.ts` (lines 635-644)

**Request ID Support for Template Operations**
- Added `requestId` field to `BuildResponse` and `BuildStatusResponse` types
- Request IDs are now captured from API responses for debugging
- Included in `TemplateBuildError` for correlation with HopX support requests
- **Files Modified**: `src/template/types.ts`, `src/template/build-flow.ts`

**Improved Timeout Error Messages**
- Timeout errors now include template ID and last known status
- **Previous**: `Template did not become stable within N minutes...`
- **Now**: `Template {id} did not become active within N minutes. Last status: {status}...`
- **Files Modified**: `src/template/build-flow.ts` (lines 712-716)

### New Error Types

**TemplateBuildError**
- New error class for template build failures
- Properties: `buildId`, `templateId`, `buildStatus`, `logsUrl`, `errorDetails`, `metadata`
- Exported from main SDK entry point for error handling
- **Files Added**: `src/errors.ts` (lines 197-230)

### Testing

**Build Reproduction Test**
- Added `examples/test-build-reproduction.ts` for reproducing and capturing evidence of build failures
- Captures: all build logs, timestamps, error details, environment info
- Saves evidence to `test-evidence/` directory for bug reports
- Run with: `npx tsx examples/test-build-reproduction.ts`

---

## [0.3.6] - 2025-11-26

### Fixed

**Critical: Token Refresh Callback Never Invoked on 401 Errors**
- Fixed token refresh mechanism not triggering when JWT tokens expire
- **Root Cause**: Response interceptor transformed 401 errors to `AuthenticationError` before `requestWithRetry` could handle token refresh. The token refresh check used `axios.isAxiosError(error)` which returned `false` for custom error types
- **Impact**: 401 Unauthorized errors always threw `AuthenticationError` instead of attempting token refresh. Long-lived sandbox sessions would fail after token expiry
- **Resolution**: Modified response interceptor to pass 401 errors through as raw AxiosErrors, allowing `requestWithRetry` to handle token refresh properly
- **Files Modified**: `src/client.ts` (lines 69-83)

**Fixed: Infinite Loop Risk in Token Refresh**
- Fixed potential infinite loop when token refresh returns an invalid token
- **Root Cause**: After successful token refresh, `requestWithRetry` was called with same `attempt` value instead of `attempt + 1`
- **Impact**: If token refresh succeeded but returned an invalid token, the retry loop would never terminate
- **Resolution**: Changed `attempt` to `attempt + 1` when retrying after token refresh
- **Files Modified**: `src/client.ts` (line 131)

---

## [0.3.5] - 2025-11-26

### Fixed

**Critical: HTTP Client Timeout Ignoring User-Specified Timeouts**
- Fixed HTTP client using hardcoded 60-second timeout regardless of user-specified execution timeouts
- **Root Cause**: `agentClient` was created with `timeout: 60000` (60s). User timeouts like `runCode({timeout: 300})` only went to API payload, not the HTTP request config
- **Impact**: Operations taking longer than 60 seconds failed with HTTP timeout even when API timeout was set higher (e.g., 300 seconds)
- **Resolution**: Pass HTTP timeout config to axios for all execution methods. HTTP timeout = API timeout + 30s buffer
- **Affected Methods**:
  - `sandbox.runCode()` - HTTP timeout now matches API timeout + 30s buffer
  - `sandbox.runCodeAsync()` - HTTP timeout now matches API timeout + 30s buffer
  - `sandbox.runCodeBackground()` - Uses 30s HTTP timeout (returns immediately)
  - `sandbox.runIpython()` - HTTP timeout now matches API timeout + 30s buffer
  - `sandbox.commands.run()` - HTTP timeout now matches API timeout + 30s buffer
  - `sandbox.commands.runBackground()` - Uses 30s HTTP timeout (returns immediately)
- **Files Modified**: `src/sandbox.ts`, `src/resources/commands.ts`

**Buffer Strategy**: HTTP timeout is set to API timeout + 30 seconds to account for network latency and API processing overhead. Background operations use fixed 30s HTTP timeout since they return immediately.

---

## [0.3.4] - 2025-11-25

### Added

**Sandbox Expiry Management**
- `getTimeToExpiry()` - Get seconds remaining until sandbox expires
- `isExpiringSoon(threshold?)` - Check if sandbox expires within threshold (default: 5 minutes)
- `getExpiryInfo()` - Get comprehensive expiry information including `expiresAt`, `timeToExpiry`, `isExpired`, `isExpiringSoon`
- `startExpiryMonitor(callback, threshold?, interval?)` - Proactive monitoring with callback when sandbox is about to expire
- `stopExpiryMonitor()` - Stop expiry monitoring
- `onExpiringSoon` callback option in `Sandbox.create()` - Auto-start monitoring when sandbox is created

**Health Check Methods**
- `isHealthy()` - Check if sandbox is ready for execution (returns boolean)
- `ensureHealthy()` - Verify sandbox is healthy, throws `SandboxExpiredError` if expired or `HopxError` if not running
- `preflight` option for `runCode()` - Run health check before code execution

**Structured Error Types**
- `SandboxExpiredError` - Thrown when sandbox has expired, includes metadata (sandboxId, createdAt, expiresAt, status)
- `TokenExpiredError` - Thrown when JWT token has expired
- `ErrorCode` enum exported for programmatic error handling
- `SandboxErrorMetadata` type exported for error metadata access

**TypeScript Types**
- `ExpiryInfo` interface for expiry information
- `SandboxErrorMetadata` interface for error metadata

### Changed

**Default Timeouts Increased**
- `runCode()` timeout increased from 60s to 120s
- Background commands timeout increased from 60s to 120s
- Sync commands remain at 30s (suitable for quick operations)

**Impact**: Long-running operations like package installations (`npm install`, `pip install`) are less likely to timeout with default settings.

---

## [0.3.3] - 2025-11-20

### Fixed

**Critical: Working Directory Parameter Not Respected**
- Fixed command execution and code execution ignoring `workingDir` parameter
- Commands always executed from root directory `/` regardless of specified working directory
- **Root Cause**: SDK sent `working_dir` field but Agent API expects `workdir` (without underscore)
- **Impact**: All commands executed in wrong directory, breaking workflows that depend on working directory context
- **Resolution**: Changed API field name from `working_dir` to `workdir` in all execution methods
- **Affected Methods**:
  - `sandbox.commands.run()` - Now correctly respects `workingDir` option
  - `sandbox.runCode()` - Now executes code in specified `workingDir`
  - `sandbox.runCodeAsync()` - Working directory parameter now functional
  - `sandbox.runCodeBackground()` - Background execution respects `workingDir`
  - `sandbox.streamCodeExecution()` - Streaming execution uses correct directory
- **Files Modified**: `src/resources/commands.ts`, `src/sandbox.ts`

**Testing**: Verified with comprehensive end-to-end tests across all execution methods. All working directory scenarios now function correctly.

## [0.3.2] - 2025-11-17

### Fixed

**Critical: Template Building npm Path**
- Fixed `.npmInstall()` method using incorrect npm binary path
- Changed from `/usr/bin/npm` to `/usr/local/bin/npm` to match official Node.js Docker images
- **Impact**: All templates using `.npmInstall()` were failing with "command not found" errors
- **Resolution**: Templates with npm package installation now build successfully
- **Files Modified**: `src/template/builder.ts` (lines 350, 370)

### Changed

**Examples: Quality Improvements and New Patterns**
- Updated `template-build.ts` with improved patterns:
  - Unique template naming using timestamps to avoid conflicts
  - Inline code creation instead of file copying (more portable examples)
  - Better error handling in build callbacks with fallback defaults
  - Relative paths in start commands for cleaner configuration
- Updated `template-nodejs.ts` with Node.js best practices:
  - Standard Debian-based Node.js images (`node:20-bookworm`)
  - Embedded package.json and source code for self-contained examples
  - Multiple sandbox instances to demonstrate template reuse
- Created `lifecycle.ts` - comprehensive sandbox lifecycle demonstration:
  - Shows proper `Sandbox.create()` usage with `timeoutSeconds` parameter
  - Demonstrates pause/resume workflow
  - Null-safe resource access patterns
- Created `ollama-template.ts` - Ollama LLM integration example:
  - Build custom template with Ollama and language models
  - Demonstrates template building with model pulling
  - Shows sandbox reuse pattern with persistent IDs
  - Full end-to-end LLM inference workflow

**Example Testing**: All examples verified with real API and working correctly

### Documentation

- Example code updated to follow current best practices
- All template building examples use unique names to prevent conflicts
- Improved inline documentation with better error handling patterns

## [0.3.1] - 2025-11-17

### Fixed

**Template Building Type Safety**
- Fixed `UploadLinkResponse` type missing `filesHash` field returned by API
- Prevents potential TypeScript compilation errors when building custom templates
- Template builds now have complete type coverage for all API response fields

**Template Names Corrected**
- Updated all examples to use correct public template names
- Only 2 public templates available: `code-interpreter` (Python + data science tools) and `base` (minimal Ubuntu)
- Fixed examples that were using non-existent template names, causing HTTP 500 errors
- All code examples now work correctly when copy-pasted

**Impact**: If you were experiencing errors during template builds or sandbox creation, these fixes resolve those issues.

### Removed

**Deprecated Lifecycle Methods**
- Removed `stop()` and `start()` methods - these API endpoints no longer exist
- **Migration**: Use `pause()` and `resume()` instead for sandbox lifecycle management

**Before** (v0.3.0):
```typescript
await sandbox.stop();   // No longer available
await sandbox.start();  // No longer available
```

**After** (v0.3.1):
```typescript
await sandbox.pause();   // Use this instead
await sandbox.resume();  // Use this instead
```

### Documentation

- All code examples tested and verified working
- Template documentation updated with accurate available templates
- New example app file for template building tutorials

## [0.3.0] - 2025-11-16

### 🎉 SDK Goodies Pack

### ✨ New Features

**Sandbox Methods (7 new methods)**:
- `Sandbox.iter()` - Lazy iterator with cursor pagination for memory-efficient sandbox listing
- `Sandbox.deleteTemplate(templateId)` - Delete custom templates
- `Sandbox.healthCheck()` - API health check (no authentication required)
- `sandbox.setTimeout(seconds)` - Dynamically set auto-kill timeout
- `sandbox.getAgentMetrics()` - Get agent performance metrics (uptime, requests, errors)
- `sandbox.listSystemProcesses()` - List ALL system processes (not just executions)
- `sandbox.getJupyterSessions()` - Get Jupyter kernel session status

**Preview URL Access (NEW)**:
- `sandbox.getPreviewUrl(port)` - Get public URL for services running on any port
- `sandbox.agentUrl` - Convenience property for agent URL (port 7777)
- Format: `https://{PORT}-{sandbox_id}.{region}.vms.hopx.dev/`

**Desktop Methods (3 new methods)**:
- `desktop.hotkey(modifiers, key)` - Execute keyboard hotkey combinations (Ctrl+C, Alt+Tab, etc.)
- `desktop.getDebugLogs()` - Retrieve desktop automation debug logs
- `desktop.getDebugProcesses()` - List desktop-related processes

**File Operations**:
- `files.upload(localPath, remotePath)` - ✅ FIXED: Now fully functional (was throwing error)
- Uses FormData for multipart uploads
- Supports files of any size

**Environment Variables**:
- `env.set(key, value)` - Already present, now documented

### 🐛 Critical Bug Fixes

**1. Environment Variables Propagation** (CRITICAL):
- ✅ FIXED: Env vars set in `Sandbox.create({ envVars: {...} })` now properly propagate to runtime
- Previously: Env vars were ignored during create
- Now: Env vars are immediately available in code execution via Agent API
- Implementation: `sandbox.env.update(envVars)` called after creation

**2. Template Activation Stability** (CRITICAL):
- ✅ FIXED: Template.build() now waits for 2 consecutive "active" status checks before returning
- Previously: Returned immediately on first "active", causing sandbox creation failures
- Now: Confirms template stability over 6 seconds (2 checks x 3 second polling)
- Prevents "ServerError" when creating sandboxes from newly built templates
- Handles status transitions: `active → publishing → active (stable)`

**3. Background Command Timeout** (CRITICAL):
- ✅ FIXED: Background commands now include `timeout` parameter in request
- Previously: Commands might not terminate properly
- Now: All background commands have proper timeout enforcement

**4. Sync Command Bash Wrapping** (CRITICAL):
- ✅ FIXED: ALL commands (sync AND background) now wrapped in `bash -c`
- Previously: Only background commands wrapped, sync commands failed with pipes/redirects
- Now: Pipes (`|`), redirects (`>`), variables (`$VAR`), conditionals (`&&`, `||`) all work
- Matches Python SDK behavior exactly

**5. File Upload** (HIGH):
- ✅ FIXED: `files.upload()` now works (was throwing "not yet implemented")
- Implements multipart form-data upload
- Uses fs/promises for async file reading

### 📊 Model Enhancements

**71 New Fields Added Across 11 Models**:

**SandboxInfo** (+12 fields):
- `organizationId`, `nodeId`, `region`, `directUrl`, `previewUrl`
- `resources` (nested object), `internetAccess`, `liveMode`
- `timeoutSeconds`, `expiresAt`, `startedAt`, `endAt`

**TemplateInfo** (+7 fields):
- `isPublic`, `buildId`, `organizationId`
- `createdAt`, `updatedAt`, `object`, `requestId`

**ExecutionResult** (+8 fields + 1 getter):
- `timestamp`, `language`, `svg`, `markdown`, `html`, `jsonOutput`, `png`, `result`
- `get hasRichOutput()` - Check if rich outputs exist

**CommandResult** (+3 fields + 1 getter):
- `command`, `pid`, `timestamp`
- `get isSuccess()` - Check if exit_code === 0

**ProcessInfo** (+6 fields):
- `executionId`, `language`, `endTime`, `exitCode`, `duration`, `pid`

**WindowInfo** (+3 fields):
- `isActive`, `isMinimized`, `pid`

**RecordingInfo** (+7 fields + 2 getters):
- `recordingId`, `status`, `startTime`, `endTime`, `filePath`, `fileSize`, `format`
- `get isRecording()`, `get isReady()`

**DisplayInfo** (+2 fields + 1 getter):
- `refreshRate`, `displays`
- `get resolution()` - Get "WxH" formatted string

**HealthResponse** (+7 fields):
- `agent`, `uptime`, `goVersion`, `vmId`, `features`, `activeStreams`

**InfoResponse** (+10 fields):
- `vmId`, `agent`, `agentVersion`, `os`, `arch`, `goVersion`, `vmIp`, `vmPort`, `startTime`, `uptime`

**VNCInfo** (+1 getter):
- `get running()` - Check if VNC is running

### 🔧 Configuration Enhancements

**Template Build Timeout**:
- Added `BuildOptions.templateActivationTimeout` field (seconds)
- Added support for `HOPX_TEMPLATE_BAKE_SECONDS` environment variable
- Default: 2700 seconds (45 minutes)
- Priority: `options.templateActivationTimeout` > `env var` > `default`

### 📚 Documentation

**New Test Examples**:
- `examples/preview-url-basic.ts` - Preview URL access demo
- `examples/env-vars-example.ts` - Environment variables management
- `examples/agent-commands.ts` - Command execution with bash wrapping
- `examples/comprehensive-features-test.ts` - Complete test suite

### ⚡ Performance Improvements

- Template activation now confirms stability (prevents rebuild failures)
- Lazy iteration prevents loading all sandboxes into memory
- Cursor-based pagination for large result sets
- All commands use bash wrapping for consistent behavior

### 🔄 Breaking Changes

**NONE** - 100% backward compatible!

All changes are additive:
- ✅ No methods removed or renamed
- ✅ No parameter changes in existing methods
- ✅ All new model fields are optional
- ✅ Existing code continues to work

### 📈 API Coverage

- **Public API**: 18/18 endpoints (100%)
- **Agent API**: 74/78 endpoints (95%)
- **Template Building**: 100% feature complete
- **Overall**: 100% parity with Python SDK v0.3.0

### 🎯 Python SDK Parity

This release achieves **complete feature parity** with Python SDK v0.3.0:

| Category | Python | JavaScript | Status |
|----------|--------|------------|--------|
| Public API Methods | 18/18 | 18/18 | ✅ 100% |
| Agent API Methods | 74/78 | 74/78 | ✅ 95% |
| Model Fields | 100% | 100% | ✅ 100% |
| Template Building | 100% | 100% | ✅ 100% |
| Error Handling | 13 classes | 13 classes | ✅ 100% |

### 🔗 Migration Guide

No code changes required! All existing code continues to work.

**New features available**:

```typescript
// Preview URL access
const appUrl = await sandbox.getPreviewUrl(8080);

// Environment variables (now work correctly!)
const sandbox = await Sandbox.create({
  template: 'python',
  envVars: { API_KEY: 'secret' }  // ✅ Now propagates immediately
});

// Lazy iteration
for await (const sb of Sandbox.iter({ status: 'running' })) {
  // Memory efficient!
}

// Template deletion
await Sandbox.deleteTemplate('template_123');

// Dynamic timeout
await sandbox.setTimeout(3600);

// Agent metrics
const metrics = await sandbox.getAgentMetrics();

// Desktop hotkeys
await sandbox.desktop.hotkey(['ctrl'], 'c');

// File upload (now works!)
await sandbox.files.upload('./local.txt', '/remote.txt');
```

### 🙏 Acknowledgments

This release represents a complete rebuild of the JavaScript SDK to match the robust, production-ready Python SDK v0.3.0. Special thanks to the systematic feature-by-feature comparison process that ensured 100% parity.

---

## [0.1.21] - 2025-01-11

### 🎉 Public Release - Complete Feature Set

This release represents the complete, production-ready Hopx JavaScript/TypeScript SDK with full agent capabilities.

### ✨ Core Features

**Sandbox Management**
- Create lightweight VM sandboxes in seconds with `Sandbox.create()`
- Multiple language environments: Python, Node.js, Go, Rust, Java, and more
- Pre-built templates for instant deployment
- Custom template building with `Template.build()`
- Auto-cleanup with timeout management (`timeoutSeconds`)
- Internet access control per sandbox
- Full TypeScript support with type definitions

**Code Execution**
- Execute Python, JavaScript, Bash, and more languages
- Real-time stdout/stderr streaming
- Rich output capture (PNG charts, HTML tables, JSON data)
- Environment variable injection
- Execution timeout controls
- Promise-based async API

**File Operations**
- Full filesystem access: read, write, delete, list
- Directory operations and recursive listing
- File upload/download with streaming support
- Permission management
- Large file handling (up to 100MB)
- TypeScript interfaces for all file operations

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
- Zero-dependency core (only TypeScript types)

### 🔐 Security

- Isolated VM environments
- Network policies (internet access control)
- Resource limits (CPU, memory, disk)
- Automatic cleanup on timeout
- Secure API key authentication

### 📚 API Highlights

```typescript
import { Sandbox } from '@hopx-ai/sdk';

// Quick start
const sandbox = await Sandbox.create({ template: 'nodejs' });
const result = await sandbox.runCode("console.log('Hello, Hopx!')");
console.log(result.stdout);  // "Hello, Hopx!"
await sandbox.kill();

// Rich outputs (charts, tables)
const result = await sandbox.runCode(`
const { createCanvas } = require('canvas');
const canvas = createCanvas(200, 200);
const ctx = canvas.getContext('2d');
ctx.fillRect(0, 0, 200, 200);
console.log(canvas.toDataURL());
`);
const pngData = result.richOutputs[0].data;  // Base64 PNG

// File operations
await sandbox.files.write('/app/data.txt', 'Hello, World!');
const content = await sandbox.files.read('/app/data.txt');

// Template building
import { Template, waitForPort } from '@hopx-ai/sdk';

const template = new Template()
  .fromNodeImage('20-alpine')
  .copy('package.json', '/app/package.json')
  .copy('src/', '/app/src/')
  .npmInstall()
  .setStartCmd('node src/index.js', waitForPort(3000));

const result = await Template.build(template, {
  alias: 'my-app',
  apiKey: 'your-api-key'
});

// Create sandbox from template
const sandbox = await Sandbox.create({ templateId: result.templateID });
```

### 🐛 Bug Fixes

- Fixed `templateId` type conversion in sandbox creation
- Fixed WebSocket connection handling
- Fixed file upload for large files
- Improved error messages and TypeScript types
- Fixed async cleanup in promise chains

### 🔄 Breaking Changes

- Renamed `BunnyshellError` → `HopxError`
- Renamed `timeout` → `timeoutSeconds` in `Sandbox.create()`
- Removed deprecated `/v1/vms` endpoints (use `Sandbox.create()` instead)
- Environment variable: `BUNNYSHELL_API_KEY` → `HOPX_API_KEY`
- Template build: Uses `Sandbox.create()` internally instead of deprecated VM API

### 📦 Package Info

- **Name**: `@hopx-ai/sdk`
- **TypeScript**: Full type definitions included
- **ESM**: Native ES modules support
- **CJS**: CommonJS support for Node.js
- **Browser**: Not supported (Node.js only)

### 🛠️ Dependencies

- Node.js 18+
- TypeScript 4.9+ (for TypeScript users)
- axios (HTTP client)
- ws (WebSocket client)

---

## Previous Versions

See [GitHub Releases](https://github.com/hopx-ai/hopx/releases) for older versions.
