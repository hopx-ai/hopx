# Changelog

All notable changes to the Hopx JavaScript/TypeScript SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
