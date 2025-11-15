# Hopx Python SDK

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.19-blue.svg)](CHANGELOG.md)

Official Python SDK for [Hopx.ai](https://hopx.ai) - Cloud sandboxes for AI agents and code execution.

## 🚀 What is Hopx.ai?

**Hopx.ai** provides secure, isolated cloud sandboxes that spin up in seconds. Perfect for:

- 🤖 **AI Agents** - Give your LLM agents safe environments to execute code, run commands, and manipulate files
- 🔬 **Code Execution** - Run untrusted code safely in isolated VMs
- 🧪 **Testing & CI/CD** - Spin up clean environments for integration tests
- 📊 **Data Processing** - Execute data analysis scripts with rich output capture
- 🌐 **Web Scraping** - Run browser automation in controlled environments
- 🎓 **Education** - Provide students with sandboxed coding environments

Each sandbox is a **lightweight VM** with:
- Full root access
- Pre-installed development tools
- Network access (configurable)
- Persistent filesystem during session
- Auto-cleanup after timeout

## 📋 Key Use Cases

### 1. AI Code Execution Agent

```python
from hopx_ai import Sandbox

# Your AI agent generates code
agent_code = """
import pandas as pd
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
print(df.describe())
"""

# Execute safely in sandbox
sandbox = Sandbox.create(template="python")
result = sandbox.run_code(agent_code)

if result.success:
    print(result.stdout)  # Show output to user
else:
    print(f"Error: {result.error}")

sandbox.kill()
```

### 2. Data Analysis with Rich Outputs

```python
# Generate charts and capture them automatically
code = """
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x))
plt.title('Sine Wave')
plt.show()
"""

sandbox = Sandbox.create(template="python")
result = sandbox.run_code(code)

# Get PNG chart data
if result.rich_outputs:
    png_data = result.rich_outputs[0].data  # Base64 PNG
    # Save or display the chart
    
sandbox.kill()
```

### 3. Multi-Step Workflow

```python
from hopx_ai import Sandbox

sandbox = Sandbox.create(template="nodejs", timeout_seconds=600)

# Step 1: Clone repo and install dependencies
sandbox.commands.run("git clone https://github.com/user/project.git /app")
sandbox.commands.run("cd /app && npm install")

# Step 2: Run tests
result = sandbox.commands.run("cd /app && npm test")
print(f"Tests: {'✅ PASSED' if result.exit_code == 0 else '❌ FAILED'}")

# Step 3: Build
sandbox.commands.run("cd /app && npm run build")

# Step 4: Get build artifacts
files = sandbox.files.list("/app/dist/")
for file in files:
    print(f"Built: {file.name} ({file.size} bytes)")

sandbox.kill()
```

### 4. File Processing

```python
sandbox = Sandbox.create(template="python")

# Upload data
sandbox.files.write("/tmp/data.csv", csv_content)

# Process it
result = sandbox.run_code("""
import pandas as pd
df = pd.read_csv('/tmp/data.csv')
result = df.groupby('category').sum()
result.to_csv('/tmp/output.csv')
print(f"Processed {len(df)} rows")
""")

# Download result
output = sandbox.files.read("/tmp/output.csv")
print(output)

sandbox.kill()
```

## 🎯 Quick Start

### Installation

```bash
pip install hopx-ai
```

### Basic Example

```python
from hopx_ai import Sandbox

# Create sandbox (~100ms)
sandbox = Sandbox.create(
    template="python",  # or "nodejs", "go", "rust", etc.
    api_key="your-api-key"  # or set HOPX_API_KEY env var
)

# Execute code
result = sandbox.run_code("""
import sys
print(f"Python {sys.version}")
print("Hello from Hopx!")
""")

print(result.stdout)
# Output:
# Python 3.11.x
# Hello from Hopx!

# Cleanup
sandbox.kill()
```

### Context Manager (Auto-Cleanup)

```python
from hopx_ai import Sandbox

with Sandbox.create(template="python") as sandbox:
    result = sandbox.run_code("print(2 + 2)")
    print(result.stdout)  # "4"
# Sandbox automatically cleaned up
```

### Async Support

```python
from hopx_ai import AsyncSandbox
import asyncio

async def main():
    async with AsyncSandbox.create(template="python") as sandbox:
        result = await sandbox.run_code("print('Async!')")
        print(result.stdout)

asyncio.run(main())
```

## 📚 Core Features

### Code Execution

Execute code in multiple languages with automatic output capture:

```python
# Python
result = sandbox.run_code("print('Hello')", language="python")

# JavaScript
result = sandbox.run_code("console.log('Hello')", language="javascript")

# Bash
result = sandbox.run_code("echo 'Hello'", language="bash")

# With environment variables
result = sandbox.run_code(
    "import os; print(os.environ['API_KEY'])",
    env={"API_KEY": "secret"}
)
```

### File Operations

```python
# Write files
sandbox.files.write("/app/config.json", '{"key": "value"}')

# Read files
content = sandbox.files.read("/app/config.json")

# List directory
files = sandbox.files.list("/app/")
for file in files:
    print(f"{file.name}: {file.size} bytes")

# Delete files
sandbox.files.delete("/app/temp.txt")
```

### Commands

```python
# Run command synchronously
result = sandbox.commands.run("ls -la /app")
print(result.stdout)

# Run in background
cmd_id = sandbox.commands.run_async("python long_task.py")
# ... do other work ...
result = sandbox.commands.get_result(cmd_id)
```

### Environment Variables

```python
# Set single variable
sandbox.env.set("DATABASE_URL", "postgresql://...")

# Set multiple
sandbox.env.set_many({
    "API_KEY": "key123",
    "DEBUG": "true"
})

# Get variable
value = sandbox.env.get("API_KEY")

# Delete variable
sandbox.env.delete("DEBUG")
```

### Template Building

Build custom environments:

```python
from hopx_ai import Template, wait_for_port
from hopx_ai.template import BuildOptions

# Define template
template = (
    Template()
    .from_python_image("3.11")
    .copy("requirements.txt", "/app/requirements.txt")
    .copy("src/", "/app/src/")
    .run("cd /app && pip install -r requirements.txt")
    .set_workdir("/app")
    .set_env("PORT", "8000")
    .set_start_cmd("python src/main.py", wait_for_port(8000))
)

# Build template
result = await Template.build(
    template,
    BuildOptions(
        alias="my-python-app",
        api_key="your-api-key",
        on_log=lambda log: print(f"[{log['level']}] {log['message']}")
    )
)

print(f"Template ID: {result.template_id}")

# Create sandbox from template
sandbox = Sandbox.create(template_id=result.template_id)
```

## 🔐 Authentication

Set your API key:

```bash
export HOPX_API_KEY="your-api-key"
```

Or pass it directly:

```python
sandbox = Sandbox.create(
    template="python",
    api_key="your-api-key"
)
```

Get your API key at [hopx.ai/dashboard](https://hopx.ai/dashboard)

## ⚙️ Configuration

### Template Activation Timeout

`Template.build()` waits for templates to reach "active" status before returning. Default: 45 minutes.

**Via environment variable:**
```bash
export HOPX_TEMPLATE_ACTIVATION_TIMEOUT=2700  # seconds (45 min default)
```

**Via BuildOptions:**
```python
result = await Template.build(
    template,
    BuildOptions(
        name="my-template",
        api_key="...",
        template_activation_timeout=1800  # 30 minutes
    )
)
```

## 🎓 Templates

Pre-built templates available:

- `python` - Python 3.11 with pip, numpy, pandas, requests
- `nodejs` - Node.js 20 with npm, common packages
- `code-interpreter` - Python with data science stack (pandas, numpy, matplotlib, seaborn, scikit-learn)
- `go` - Go 1.21
- `rust` - Rust with Cargo
- `java` - Java 17 with Maven

Or build your own with `Template.build()`!

## 📖 Documentation

- [Full Documentation](https://docs.hopx.ai)
- [API Reference](https://docs.hopx.ai/python/api)
- [Examples](https://github.com/hopx-ai/hopx/tree/main/python/examples)
- [Cookbook](https://github.com/hopx-ai/hopx/tree/main/cookbook/python)

## 🛠️ Advanced Features

### Rich Output Capture

Automatically capture charts, tables, and visualizations:

```python
result = sandbox.run_code("""
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [1, 4, 9])
plt.title('My Chart')
plt.show()
""")

# Get PNG data
for output in result.rich_outputs:
    if output.type == "image/png":
        # Save to file
        import base64
        with open("chart.png", "wb") as f:
            f.write(base64.b64decode(output.data))
```

### Process Management

```python
# List processes
processes = sandbox.processes.list()
for proc in processes:
    print(f"{proc.pid}: {proc.name} (CPU: {proc.cpu_percent}%)")

# Kill process
sandbox.processes.kill(1234)
```

### Desktop Automation (Premium)

```python
# Get VNC info
vnc = sandbox.desktop.get_vnc_info()
print(f"Connect to: {vnc.url}")

# Take screenshot
screenshot = sandbox.desktop.screenshot()  # Returns PNG bytes

# Control mouse
sandbox.desktop.mouse_click(100, 200)

# Type text
sandbox.desktop.keyboard_type("Hello, World!")
```

### Health & Metrics

```python
# Check health
health = sandbox.get_health()
print(health.status)  # "healthy"

# Get metrics
metrics = sandbox.get_metrics()
print(f"CPU: {metrics.cpu_percent}%")
print(f"Memory: {metrics.memory_mb}MB")
print(f"Disk: {metrics.disk_mb}MB")
```

## 🤝 Error Handling

```python
from hopx_ai import (
    HopxError,
    AuthenticationError,
    CodeExecutionError,
    FileNotFoundError,
    RateLimitError
)

try:
    sandbox = Sandbox.create(template="python")
    result = sandbox.run_code("1/0")  # Will raise CodeExecutionError
    
except AuthenticationError:
    print("Invalid API key")
except CodeExecutionError as e:
    print(f"Code execution failed: {e.stderr}")
except RateLimitError:
    print("Rate limit exceeded")
except HopxError as e:
    print(f"API error: {e.message}")
```

## 💡 Best Practices

1. **Always clean up**: Use context managers or call `.kill()` explicitly
2. **Set timeouts**: Prevent runaway sandboxes with `timeout_seconds`
3. **Handle errors**: Wrap code in try/except for production use
4. **Use templates**: Pre-built templates are faster than custom ones
5. **Batch operations**: Group related operations to reduce API calls
6. **Monitor resources**: Check metrics if running long tasks

## 🐛 Troubleshooting

**Sandbox creation timeout?**
- Check your API key is valid
- Verify network connectivity
- Try a different region

**Code execution fails?**
- Check `result.stderr` for error messages
- Ensure required packages are installed in sandbox
- Verify file paths are correct

**File not found?**
- Use absolute paths (e.g., `/app/file.txt`)
- Check file was uploaded successfully
- Verify working directory

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Website](https://hopx.ai)
- [Documentation](https://docs.hopx.ai)
- [Dashboard](https://hopx.ai/dashboard)
- [GitHub](https://github.com/hopx-ai/hopx)
- [Discord Community](https://discord.gg/hopx)
- [Twitter](https://twitter.com/hopx_ai)

## 🆘 Support

- Email: support@hopx.ai
- Discord: [discord.gg/hopx](https://discord.gg/hopx)
- Issues: [GitHub Issues](https://github.com/hopx-ai/hopx/issues)

---

**Built with ❤️ by the Hopx team**
