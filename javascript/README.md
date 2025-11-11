# Hopx JavaScript/TypeScript SDK

[![npm version](https://img.shields.io/npm/v/@hopx-ai/sdk.svg)](https://www.npmjs.com/package/@hopx-ai/sdk)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0%2B-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.21-blue.svg)](CHANGELOG.md)

Official JavaScript/TypeScript SDK for [Hopx.ai](https://hopx.ai) - Cloud sandboxes for AI agents and code execution.

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

```typescript
import { Sandbox } from '@hopx-ai/sdk';

// Your AI agent generates code
const agentCode = `
const data = [1, 2, 3, 4, 5];
const sum = data.reduce((a, b) => a + b, 0);
console.log(\`Sum: \${sum}\`);
`;

// Execute safely in sandbox
const sandbox = await Sandbox.create({ template: 'nodejs' });
const result = await sandbox.runCode(agentCode);

if (result.success) {
  console.log(result.stdout);  // Show output to user
} else {
  console.error(`Error: ${result.error}`);
}

await sandbox.kill();
```

### 2. Data Visualization with Rich Outputs

```typescript
// Generate charts and capture them automatically
const code = `
const { createCanvas } = require('canvas');
const canvas = createCanvas(400, 300);
const ctx = canvas.getContext('2d');

// Draw chart
ctx.fillStyle = '#4CAF50';
ctx.fillRect(50, 100, 80, 150);
ctx.fillRect(150, 50, 80, 200);
ctx.fillRect(250, 80, 80, 170);

console.log(canvas.toDataURL());
`;

const sandbox = await Sandbox.create({ template: 'nodejs' });
const result = await sandbox.runCode(code);

// Get PNG chart data
if (result.richOutputs && result.richOutputs.length > 0) {
  const pngData = result.richOutputs[0].data;  // Base64 PNG
  // Save or display the chart
}

await sandbox.kill();
```

### 3. Multi-Step Workflow

```typescript
import { Sandbox } from '@hopx-ai/sdk';

const sandbox = await Sandbox.create({ 
  template: 'nodejs',
  timeoutSeconds: 600 
});

// Step 1: Clone repo and install dependencies
await sandbox.commands.run('git clone https://github.com/user/project.git /app');
await sandbox.commands.run('cd /app && npm install');

// Step 2: Run tests
const testResult = await sandbox.commands.run('cd /app && npm test');
console.log(`Tests: ${testResult.exitCode === 0 ? '✅ PASSED' : '❌ FAILED'}`);

// Step 3: Build
await sandbox.commands.run('cd /app && npm run build');

// Step 4: Get build artifacts
const files = await sandbox.files.list('/app/dist/');
files.forEach(file => {
  console.log(`Built: ${file.name} (${file.size} bytes)`);
});

await sandbox.kill();
```

### 4. File Processing

```typescript
const sandbox = await Sandbox.create({ template: 'python' });

// Upload data
await sandbox.files.write('/tmp/data.csv', csvContent);

// Process it
const result = await sandbox.runCode(`
import pandas as pd
df = pd.read_csv('/tmp/data.csv')
result = df.groupby('category').sum()
result.to_csv('/tmp/output.csv')
print(f"Processed {len(df)} rows")
`);

// Download result
const output = await sandbox.files.read('/tmp/output.csv');
console.log(output);

await sandbox.kill();
```

## 🎯 Quick Start

### Installation

```bash
npm install @hopx-ai/sdk
```

### Basic Example

```typescript
import { Sandbox } from '@hopx-ai/sdk';

// Create sandbox (~100ms)
const sandbox = await Sandbox.create({
  template: 'nodejs',  // or 'python', 'go', 'rust', etc.
  apiKey: 'your-api-key'  // or set HOPX_API_KEY env var
});

// Execute code
const result = await sandbox.runCode(`
console.log('Node.js', process.version);
console.log('Hello from Hopx!');
`);

console.log(result.stdout);
// Output:
// Node.js v20.x.x
// Hello from Hopx!

// Cleanup
await sandbox.kill();
```

### JavaScript (CommonJS)

```javascript
const { Sandbox } = require('@hopx-ai/sdk');

(async () => {
  const sandbox = await Sandbox.create({ template: 'nodejs' });
  const result = await sandbox.runCode("console.log('Hello!')");
  console.log(result.stdout);
  await sandbox.kill();
})();
```

### TypeScript (Full Type Safety)

```typescript
import { Sandbox, ExecutionResult, SandboxInfo } from '@hopx-ai/sdk';

const sandbox = await Sandbox.create({ template: 'python' });

const result: ExecutionResult = await sandbox.runCode("print('Hello!')");
const info: SandboxInfo = await sandbox.getInfo();

console.log(`Status: ${info.status}`);
console.log(`Output: ${result.stdout}`);

await sandbox.kill();
```

## 📚 Core Features

### Code Execution

Execute code in multiple languages with automatic output capture:

```typescript
// Python
const result = await sandbox.runCode("print('Hello')", { 
  language: 'python' 
});

// JavaScript
const result = await sandbox.runCode("console.log('Hello')", { 
  language: 'javascript' 
});

// Bash
const result = await sandbox.runCode("echo 'Hello'", { 
  language: 'bash' 
});

// With environment variables
const result = await sandbox.runCode(
  "console.log(process.env.API_KEY)",
  { env: { API_KEY: 'secret' } }
);
```

### File Operations

```typescript
// Write files
await sandbox.files.write('/app/config.json', '{"key": "value"}');

// Read files
const content = await sandbox.files.read('/app/config.json');

// List directory
const files = await sandbox.files.list('/app/');
files.forEach(file => {
  console.log(`${file.name}: ${file.size} bytes`);
});

// Delete files
await sandbox.files.delete('/app/temp.txt');
```

### Commands

```typescript
// Run command synchronously
const result = await sandbox.commands.run('ls -la /app');
console.log(result.stdout);

// Run in background
const cmdId = await sandbox.commands.runAsync('node long-task.js');
// ... do other work ...
const result = await sandbox.commands.getResult(cmdId);
```

### Environment Variables

```typescript
// Set single variable
await sandbox.env.set('DATABASE_URL', 'postgresql://...');

// Set multiple
await sandbox.env.setMany({
  API_KEY: 'key123',
  DEBUG: 'true'
});

// Get variable
const value = await sandbox.env.get('API_KEY');

// Delete variable
await sandbox.env.delete('DEBUG');
```

### Template Building

Build custom environments:

```typescript
import { Template, waitForPort } from '@hopx-ai/sdk';

// Define template
const template = new Template()
  .fromNodeImage('20-alpine')
  .copy('package.json', '/app/package.json')
  .copy('src/', '/app/src/')
  .run('cd /app && npm install')
  .setWorkdir('/app')
  .setEnv('PORT', '3000')
  .setStartCmd('node src/index.js', waitForPort(3000));

// Build template
const result = await Template.build(template, {
  alias: 'my-node-app',
  apiKey: 'your-api-key',
  onLog: (log) => console.log(`[${log.level}] ${log.message}`)
});

console.log(`Template ID: ${result.templateID}`);

// Create sandbox from template
const sandbox = await Sandbox.create({ templateId: result.templateID });
```

## 🔐 Authentication

Set your API key:

```bash
export HOPX_API_KEY="your-api-key"
```

Or pass it directly:

```typescript
const sandbox = await Sandbox.create({
  template: 'nodejs',
  apiKey: 'your-api-key'
});
```

Get your API key at [hopx.ai/dashboard](https://hopx.ai/dashboard)

## 🎓 Templates

Pre-built templates available:

- `nodejs` - Node.js 20 with npm, common packages
- `python` - Python 3.11 with pip, numpy, pandas, requests
- `code-interpreter` - Python with data science stack (pandas, numpy, matplotlib, seaborn, scikit-learn)
- `go` - Go 1.21
- `rust` - Rust with Cargo
- `java` - Java 17 with Maven

Or build your own with `Template.build()`!

## 📖 Documentation

- [Full Documentation](https://docs.hopx.ai)
- [API Reference](https://docs.hopx.ai/javascript/api)
- [Examples](https://github.com/hopx-ai/hopx/tree/main/javascript/examples)
- [Cookbook](https://github.com/hopx-ai/hopx/tree/main/cookbook/javascript)

## 🛠️ Advanced Features

### Rich Output Capture

Automatically capture charts, tables, and visualizations:

```typescript
const result = await sandbox.runCode(`
const { createCanvas } = require('canvas');
const canvas = createCanvas(200, 200);
const ctx = canvas.getContext('2d');
ctx.fillRect(0, 0, 200, 200);
console.log(canvas.toDataURL());
`);

// Get PNG data
for (const output of result.richOutputs || []) {
  if (output.type === 'image/png') {
    // Save to file
    const fs = require('fs');
    const buffer = Buffer.from(output.data, 'base64');
    fs.writeFileSync('chart.png', buffer);
  }
}
```

### Process Management

```typescript
// List processes
const processes = await sandbox.processes.list();
processes.forEach(proc => {
  console.log(`${proc.pid}: ${proc.name} (CPU: ${proc.cpuPercent}%)`);
});

// Kill process
await sandbox.processes.kill(1234);
```

### Desktop Automation (Premium)

```typescript
// Get VNC info
const vnc = await sandbox.desktop.getVNCInfo();
console.log(`Connect to: ${vnc.url}`);

// Take screenshot
const screenshot = await sandbox.desktop.screenshot();  // Returns Buffer

// Control mouse
await sandbox.desktop.mouseClick(100, 200);

// Type text
await sandbox.desktop.keyboardType('Hello, World!');
```

### Health & Metrics

```typescript
// Check health
const health = await sandbox.getHealth();
console.log(health.status);  // "healthy"

// Get metrics
const metrics = await sandbox.getMetrics();
console.log(`CPU: ${metrics.cpuPercent}%`);
console.log(`Memory: ${metrics.memoryMb}MB`);
console.log(`Disk: ${metrics.diskMb}MB`);
```

## 🤝 Error Handling

```typescript
import {
  HopxError,
  AuthenticationError,
  CodeExecutionError,
  FileNotFoundError,
  RateLimitError
} from '@hopx-ai/sdk';

try {
  const sandbox = await Sandbox.create({ template: 'python' });
  const result = await sandbox.runCode('1/0');  // Will raise error
  
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.error('Invalid API key');
  } else if (error instanceof CodeExecutionError) {
    console.error(`Code execution failed: ${error.message}`);
  } else if (error instanceof RateLimitError) {
    console.error('Rate limit exceeded');
  } else if (error instanceof HopxError) {
    console.error(`API error: ${error.message}`);
  }
}
```

## 💡 Best Practices

1. **Always clean up**: Call `.kill()` explicitly or use try/finally
2. **Set timeouts**: Prevent runaway sandboxes with `timeoutSeconds`
3. **Handle errors**: Wrap code in try/catch for production use
4. **Use templates**: Pre-built templates are faster than custom ones
5. **Batch operations**: Group related operations to reduce API calls
6. **Monitor resources**: Check metrics if running long tasks
7. **TypeScript**: Use types for better development experience

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

**TypeScript errors?**
- Ensure you have `@types/node` installed
- Update TypeScript to 4.9+
- Check your `tsconfig.json` settings

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Website](https://hopx.ai)
- [Documentation](https://docs.hopx.ai)
- [Dashboard](https://hopx.ai/dashboard)
- [GitHub](https://github.com/hopx-ai/hopx)
- [npm Package](https://www.npmjs.com/package/@hopx-ai/sdk)
- [Discord Community](https://discord.gg/hopx)
- [Twitter](https://twitter.com/hopx_ai)

## 🆘 Support

- Email: support@hopx.ai
- Discord: [discord.gg/hopx](https://discord.gg/hopx)
- Issues: [GitHub Issues](https://github.com/hopx-ai/hopx/issues)

---

**Built with ❤️ by the Hopx team**
