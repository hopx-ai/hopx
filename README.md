# Hopx - Cloud Sandboxes for AI Agents

[![PyPI version](https://badge.fury.io/py/hopx-ai.svg)](https://pypi.org/project/hopx-ai/)
[![npm version](https://badge.fury.io/js/@hopx-ai%2Fsdk.svg)](https://www.npmjs.com/package/@hopx-ai/sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official SDKs for [Hopx.ai](https://hopx.ai) - Secure, isolated cloud sandboxes that spin up in ~100ms.

## 🚀 What is Hopx?

**Hopx** provides lightweight VM sandboxes perfect for:
- 🤖 **AI Agents** - Safe code execution environments for LLMs
- 🔬 **Code Execution** - Run untrusted code securely
- 🧪 **Testing** - Isolated environments for integration tests
- 📊 **Data Processing** - Execute scripts with rich output capture

## 📦 Available SDKs

### Python SDK
```bash
pip install hopx-ai
```

**[📖 Python Documentation](python/)**

```python
from hopx_ai import Sandbox

sandbox = Sandbox.create(template="python")
result = sandbox.run_code("print('Hello, Hopx!')")
print(result.stdout)  # "Hello, Hopx!"
sandbox.kill()
```

### JavaScript/TypeScript SDK
```bash
npm install @hopx-ai/sdk
```

**[📖 JavaScript Documentation](javascript/)**

```typescript
import { Sandbox } from '@hopx-ai/sdk';

const sandbox = await Sandbox.create({ template: 'nodejs' });
const result = await sandbox.runCode("console.log('Hello, Hopx!')");
console.log(result.stdout);  // "Hello, Hopx!"
await sandbox.kill();
```

## ✨ Features

- ⚡ **Fast** - Sandbox creation in ~100ms
- 🔐 **Secure** - Isolated VM environments
- 🌍 **Multi-language** - Python, Node.js, Go, Rust, Java, and more
- 📊 **Rich Outputs** - Capture charts, tables, and visualizations
- 🗂️ **File Operations** - Full filesystem access
- 🖥️ **Desktop Support** - VNC, mouse, keyboard control (Premium)
- 🔧 **Template Building** - Create custom environments
- 📡 **Real-time** - WebSocket streaming support

## 📚 Quick Links

- **Website**: [hopx.ai](https://hopx.ai)
- **Documentation**: [docs.hopx.ai](https://docs.hopx.ai)
- **Dashboard**: [hopx.ai/dashboard](https://hopx.ai/dashboard)
- **Discord**: [discord.gg/hopx](https://discord.gg/hopx)

## 🏗️ Repository Structure

```
hopx/
├── python/          # Python SDK
│   ├── hopx_ai/    # Source code
│   ├── examples/   # Usage examples
│   └── README.md   # Python docs
├── javascript/      # JavaScript/TypeScript SDK
│   ├── src/        # Source code
│   ├── examples/   # Usage examples
│   └── README.md   # JavaScript docs
└── cookbook/        # Advanced examples
    ├── python/
    └── javascript/
```

## 🎯 Example Use Cases

### AI Code Agent
```python
# Your AI generates code, Hopx executes it safely
sandbox = Sandbox.create(template="python")
result = sandbox.run_code(agent_generated_code)
if result.success:
    return result.stdout
```

### Data Visualization
```python
# Automatically capture charts
code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [1, 4, 9])
plt.show()
"""
result = sandbox.run_code(code)
png_data = result.rich_outputs[0].data  # Base64 PNG
```

### Multi-Step Workflow
```typescript
const sandbox = await Sandbox.create({ template: 'nodejs' });

await sandbox.commands.run('git clone https://github.com/user/repo /app');
await sandbox.commands.run('cd /app && npm install');
const result = await sandbox.commands.run('cd /app && npm test');

console.log(result.exitCode === 0 ? '✅ PASSED' : '❌ FAILED');
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Quick start:**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing`
3. Make your changes
4. Run tests: `pytest` (Python) or `npm test` (JavaScript)
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Email**: support@hopx.ai
- **Discord**: [discord.gg/hopx](https://discord.gg/hopx)
- **Issues**: [GitHub Issues](https://github.com/hopx-ai/hopx/issues)

## 🔐 Security

Found a security issue? Please report it to **security@hopx.ai** instead of opening a public issue.

See [SECURITY.md](SECURITY.md) for our security policy.

---

**Built with ❤️ by the Hopx team**

[Website](https://hopx.ai) • [Documentation](https://docs.hopx.ai) • [Twitter](https://twitter.com/hopx_ai) • [Discord](https://discord.gg/hopx)

