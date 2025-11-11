# Changelog

All notable changes to the Hopx SDKs will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.21] - 2025-01-11 - JavaScript SDK
## [0.1.19] - 2025-01-11 - Python SDK

### 🎉 Initial Public Release

This is the first public release of the Hopx SDKs - a complete, production-ready toolkit for creating and managing cloud sandboxes.

### ✨ Features

**Core Capabilities:**
- ⚡ Sandbox creation in ~100ms
- 🐍 Python SDK (v0.1.19)
- 📦 JavaScript/TypeScript SDK (v0.1.21)
- 🔐 Secure VM isolation
- 🌍 Multi-language support (Python, Node.js, Go, Rust, Java)
- 📊 Rich output capture (PNG, HTML, JSON)
- 🗂️ Complete file operations
- 🖥️ Desktop automation (VNC, mouse, keyboard)
- 🔧 Custom template building
- 📡 WebSocket streaming

**SDK Features:**
- Sandbox Management (create, kill, info, list)
- Code Execution (multi-language, rich outputs)
- File Operations (read, write, delete, list)
- Command Execution (sync & async)
- Environment Variables
- Process Management
- Cache Management
- Template Building (Docker-like)
- Desktop Automation (Premium)

**Developer Experience:**
- 📚 Comprehensive documentation
- 📖 20+ cookbook examples
- 🔄 Async/await support
- 🎯 TypeScript definitions
- ⚠️ Rich error handling
- 🧪 Production-ready

### 📦 Installation

```bash
# Python
pip install hopx-ai

# JavaScript
npm install @hopx-ai/sdk
```

### 🔗 Links

- Python SDK: [PyPI](https://pypi.org/project/hopx-ai/)
- JavaScript SDK: [npm](https://www.npmjs.com/package/@hopx-ai/sdk)
- Documentation: [docs.hopx.ai](https://docs.hopx.ai)
- Website: [hopx.ai](https://hopx.ai)

### 📝 SDK-Specific Changelogs

For detailed version history:
- [Python CHANGELOG](python/CHANGELOG.md)
- [JavaScript CHANGELOG](javascript/CHANGELOG.md)

---

## Release Notes Format

This monorepo contains two SDKs with independent versioning:

- **Python SDK** (`hopx-ai` on PyPI) - See [python/CHANGELOG.md](python/CHANGELOG.md)
- **JavaScript SDK** (`@hopx-ai/sdk` on npm) - See [javascript/CHANGELOG.md](javascript/CHANGELOG.md)

Each SDK has its own release schedule and version numbers.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

