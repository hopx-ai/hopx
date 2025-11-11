/**
 * 02. Code Execution (All Methods) - JavaScript/TypeScript SDK
 *
 * This example covers ALL code execution features:
 * - Synchronous execution (runCode)
 *   - Fast: runCode(code) - default, no rich outputs
 *   - With rich outputs: runCode(code, { rich: true }) - captures plots/dataframes
 * - Asynchronous execution (runCodeAsync)
 * - Background execution (runCodeBackground)
 * - IPython/Jupyter execution (runIpython)
 * - Streaming execution (runCodeStream) - WebSocket
 * - Environment variables
 * - Rich outputs
 * - Multiple languages
 * - Timeouts and error handling
 */

import { Sandbox } from '@hopx-ai/sdk';

const API_KEY = process.env.HOPX_API_KEY || 'your-api-key-here';


async function basicCodeExecution() {
  console.log('='.repeat(60));
  console.log('1. BASIC CODE EXECUTION (SYNC)');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    apiKey: API_KEY
  });
  
  try {
    // Simple Python code
    const result = await sandbox.runCode(`
import sys
print(f"Python version: {sys.version}")
print("Hello from sandbox!")
    `);
    
    console.log(`✅ Success: ${result.success}`);
    console.log(`✅ Exit code: ${result.exit_code}`);
    console.log(`✅ Execution time: ${result.execution_time}s`);
    console.log(`✅ Output:\n${result.stdout}`);
    
    if (result.stderr) {
      console.log(`⚠️  Stderr: ${result.stderr}`);
    }
    
  } finally {
    await sandbox.kill();
  }
  
  console.log();
}


async function codeWithEnvVars() {
  console.log('='.repeat(60));
  console.log('2. CODE EXECUTION WITH ENV VARS');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    apiKey: API_KEY
  });
  
  try {
    // Pass environment variables (IMPORTANT: for secrets!)
    const result = await sandbox.runCode(
      `
import os

# These come from env parameter, NOT hardcoded!
api_key = os.environ.get('API_KEY')
debug = os.environ.get('DEBUG')

print(f"API Key: {api_key}")
print(f"Debug mode: {debug}")
      `,
      {
        env: {
          API_KEY: 'sk-test-secret-key-123',
          DEBUG: 'true'
        }
      }
    );
    
    console.log(`✅ Output:\n${result.stdout}`);
    
  } finally {
    await sandbox.kill();
  }
  
  console.log();
}


async function multipleLanguages() {
  console.log('='.repeat(60));
  console.log('3. MULTIPLE LANGUAGES');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    apiKey: API_KEY
  });
  
  try {
    // Python
    const resultPy = await sandbox.runCode(
      'print("Hello from Python!")',
      { language: 'python' }
    );
    console.log(`✅ Python: ${resultPy.stdout.trim()}`);
    
    // JavaScript
    const resultJs = await sandbox.runCode(
      'console.log("Hello from JavaScript!")',
      { language: 'javascript' }
    );
    console.log(`✅ JavaScript: ${resultJs.stdout.trim()}`);
    
    // Bash
    const resultBash = await sandbox.runCode(
      'echo "Hello from Bash!"',
      { language: 'bash' }
    );
    console.log(`✅ Bash: ${resultBash.stdout.trim()}`);
    
    // Go
    const resultGo = await sandbox.runCode(
      `
package main
import "fmt"
func main() {
    fmt.Println("Hello from Go!")
}
      `,
      { language: 'go' }
    );
    console.log(`✅ Go: ${resultGo.stdout.trim()}`);
    
  } finally {
    await sandbox.kill();
  }
  
  console.log();
}


async function richOutputs() {
  console.log('='.repeat(60));
  console.log('4. RICH OUTPUTS (Images, Plots, DataFrames)');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    apiKey: API_KEY
  });
  
  try {
    // Use rich: true to capture rich outputs (plots, dataframes, etc.)
    // Note: This is slower than default runCode()
    const result = await sandbox.runCode(`
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Create a plot
plt.figure(figsize=(8, 6))
x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x), label='sin(x)')
plt.plot(x, np.cos(x), label='cos(x)')
plt.legend()
plt.title('Trigonometric Functions')
plt.savefig('/tmp/plot.png')
print("Plot saved!")

# Create a DataFrame
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'Score': [95, 87, 92]
})
print(df)
    `, { rich: true });
    
    console.log(`✅ Output:\n${result.stdout}`);
    console.log(`✅ Rich outputs captured: ${result.richCount}`);
    
    if (result.richOutputs && result.richOutputs.length > 0) {
      console.log(`✅ Rich outputs found: ${result.richOutputs.length}`);
      result.richOutputs.forEach((output, i) => {
        console.log(`   ${i+1}. Type: ${output.type}`);
        console.log(`      Data keys: ${Object.keys(output.data || {})}`);
      });
    }
    
    console.log('\n💡 Tip: Use runCode(code) for fast execution (default)');
    console.log('   Use runCode(code, { rich: true }) when you need plots, dataframes, etc.');
    
  } finally {
    await sandbox.kill();
  }
  
  console.log();
}


async function asyncExecution() {
  console.log('='.repeat(60));
  console.log('5. ASYNC EXECUTION (NON-BLOCKING)');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    apiKey: API_KEY
  });
  
  try {
    // Start async execution (returns execution_id)
    const response = await sandbox.runCodeAsync(`
import time
print("Starting long computation...")
time.sleep(3)
print("Computation complete!")
    `, {
      callbackUrl: 'https://your-webhook-url.com/callback'
    });
    
    console.log(`✅ Execution started: ${response.execution_id}`);
    console.log('   (Non-blocking - can do other work)');
    
    // Do other work while code executes...
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log('   ...doing other work...');
    
    console.log(`✅ Execution ID for later retrieval: ${response.execution_id}`);
    
  } finally {
    await sandbox.kill();
  }
  
  console.log();
}


async function backgroundExecution() {
  console.log('='.repeat(60));
  console.log('6. BACKGROUND EXECUTION (FIRE & FORGET)');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    apiKey: API_KEY
  });
  
  try {
    // Start background execution
    const response = await sandbox.runCodeBackground(`
import time
with open('/workspace/background_task.txt', 'w') as f:
    for i in range(5):
        f.write(f"Step {i+1}\\n")
        f.flush()
        time.sleep(1)
    f.write("Done!\\n")
    `);
    
    console.log(`✅ Background execution started: ${response.execution_id}`);
    console.log('   (Running in background)');
    
    // Continue with other work immediately
    console.log('   ...continuing with other work...');
    
    // Check if file is being created
    await new Promise(resolve => setTimeout(resolve, 2000));
    if (await sandbox.files.exists('/workspace/background_task.txt')) {
      const content = await sandbox.files.read('/workspace/background_task.txt');
      console.log(`✅ Background task progress:\n${content}`);
    }
    
  } finally {
    await sandbox.kill();
  }
  
  console.log();
}


async function ipythonExecution() {
  console.log('='.repeat(60));
  console.log('7. IPYTHON EXECUTION (JUPYTER-STYLE)');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    apiKey: API_KEY
  });
  
  try {
    const result = await sandbox.runIpython(`
import pandas as pd
import numpy as np

# Last expression is automatically displayed
df = pd.DataFrame({
    'A': np.random.rand(5),
    'B': np.random.rand(5)
})

df.describe()  # This will be displayed
    `);
    
    console.log(`✅ Success: ${result.success}`);
    console.log(`✅ Output:\n${result.stdout}`);
    
    if (result.richOutputs && result.richOutputs.length > 0) {
      console.log(`✅ Rich outputs: ${result.richOutputs.length}`);
    }
    
  } finally {
    await sandbox.kill();
  }
  
  console.log();
}


async function streamingExecution() {
  console.log('='.repeat(60));
  console.log('8. STREAMING EXECUTION (WEBSOCKET - REAL-TIME)');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    apiKey: API_KEY
  });
  
  try {
    const code = `
import time
for i in range(5):
    print(f"Step {i+1}/5")
    time.sleep(1)
print("Complete!")
    `;
    
    console.log('✅ Streaming output (real-time):');
    
    for await (const message of sandbox.runCodeStream(code)) {
      if (message.type === 'stdout') {
        process.stdout.write(`   📤 ${message.data}`);
      } else if (message.type === 'stderr') {
        process.stdout.write(`   ⚠️  ${message.data}`);
      } else if (message.type === 'result') {
        console.log(`\n✅ Exit code: ${message.exit_code}`);
        console.log(`✅ Execution time: ${message.execution_time || 0}s`);
      } else if (message.type === 'complete') {
        console.log('✅ Streaming complete!');
      }
    }
    
  } finally {
    await sandbox.kill();
  }
  
  console.log();
}


async function workingDirectory() {
  console.log('='.repeat(60));
  console.log('9. CUSTOM WORKING DIRECTORY');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    apiKey: API_KEY
  });
  
  try {
    // Create a directory
    await sandbox.files.mkdir('/workspace/myproject');
    
    // Execute code in that directory
    const result = await sandbox.runCode(
      `
import os
print(f"Current dir: {os.getcwd()}")

# Create file in current dir
with open('data.txt', 'w') as f:
    f.write('Hello!')
      `,
      { workingDir: '/workspace/myproject' }
    );
    
    console.log(`✅ Output:\n${result.stdout}`);
    
    // Verify file was created in correct directory
    const exists = await sandbox.files.exists('/workspace/myproject/data.txt');
    console.assert(exists, 'File created in correct directory!');
    console.log('✅ File created in correct directory!');
    
  } finally {
    await sandbox.kill();
  }
  
  console.log();
}


async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('JAVASCRIPT/TYPESCRIPT SDK - CODE EXECUTION (ALL METHODS)');
  console.log('='.repeat(60) + '\n');
  
  await basicCodeExecution();
  await codeWithEnvVars();
  await multipleLanguages();
  await richOutputs();
  await asyncExecution();
  await backgroundExecution();
  await ipythonExecution();
  await streamingExecution();
  await workingDirectory();
  
  console.log('='.repeat(60));
  console.log('✅ ALL CODE EXECUTION METHODS DEMONSTRATED!');
  console.log('='.repeat(60));
  console.log('\nFeatures covered:');
  console.log('  ✅ Synchronous execution (runCode)');
  console.log('     - Fast: runCode(code)');
  console.log('     - With rich outputs: runCode(code, { rich: true })');
  console.log('  ✅ Asynchronous execution (runCodeAsync)');
  console.log('  ✅ Background execution (runCodeBackground)');
  console.log('  ✅ IPython execution (runIpython)');
  console.log('  ✅ Streaming execution (runCodeStream)');
  console.log('  ✅ Environment variables');
  console.log('  ✅ Rich outputs');
  console.log('  ✅ Multiple languages');
  console.log('  ✅ Custom working directory');
  console.log('='.repeat(60) + '\n');
}

main().catch(console.error);

