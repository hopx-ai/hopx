#!/usr/bin/env tsx
/**
 * Working Directory Example
 *
 * Demonstrates how to use the workingDir parameter with commands and code execution.
 * The workingDir parameter controls where commands and code execute.
 *
 * @see https://docs.hopx.ai
 */

import { Sandbox } from '../src/index.js';

async function main() {
  const apiKey = process.env.HOPX_API_KEY;
  if (!apiKey) {
    throw new Error('HOPX_API_KEY environment variable is required');
  }

  console.log('🚀 Working Directory Example\n');

  // Create a sandbox
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    apiKey
  });

  console.log(`✅ Created sandbox: ${sandbox.sandboxId}\n`);

  try {
    // =========================================================================
    // Example 1: Default working directory
    // =========================================================================
    console.log('Example 1: Default Working Directory');
    console.log('-'.repeat(70));

    const result1 = await sandbox.commands.run('pwd');
    console.log(`Current directory: ${result1.stdout.trim()}`);
    console.log('Default is /workspace\n');

    // =========================================================================
    // Example 2: Explicit working directory for commands
    // =========================================================================
    console.log('Example 2: Commands with Explicit Working Directory');
    console.log('-'.repeat(70));

    // Run pwd from /tmp
    const result2 = await sandbox.commands.run('pwd', { workingDir: '/tmp' });
    console.log(`Running 'pwd' in /tmp: ${result2.stdout.trim()}`);

    // List files in /etc
    const result3 = await sandbox.commands.run('ls -l | head -5', { workingDir: '/etc' });
    console.log(`\nListing files in /etc (first 5):`);
    console.log(result3.stdout);

    // =========================================================================
    // Example 3: Create files in different directories
    // =========================================================================
    console.log('Example 3: Create Files in Different Directories');
    console.log('-'.repeat(70));

    // Create file in /tmp
    await sandbox.commands.run(
      'echo "Hello from /tmp" > myfile.txt',
      { workingDir: '/tmp' }
    );

    // Create file in /workspace
    await sandbox.commands.run(
      'echo "Hello from /workspace" > myfile.txt',
      { workingDir: '/workspace' }
    );

    // Read both files
    const tmpFile = await sandbox.commands.run('cat myfile.txt', { workingDir: '/tmp' });
    const workspaceFile = await sandbox.commands.run('cat myfile.txt', { workingDir: '/workspace' });

    console.log(`File in /tmp: ${tmpFile.stdout.trim()}`);
    console.log(`File in /workspace: ${workspaceFile.stdout.trim()}`);
    console.log('✅ Same filename, different directories\n');

    // =========================================================================
    // Example 4: Code execution with working directory
    // =========================================================================
    console.log('Example 4: Code Execution with Working Directory');
    console.log('-'.repeat(70));

    // Python code to show current directory
    const pythonCode = `
import os
print(f"Current directory: {os.getcwd()}")
print(f"Files here: {os.listdir('.')}")
`;

    // Execute in /tmp
    const codeResult1 = await sandbox.runCode(pythonCode, {
      language: 'python',
      workingDir: '/tmp'
    });
    console.log('Python execution in /tmp:');
    console.log(codeResult1.stdout);

    // Execute in /workspace
    const codeResult2 = await sandbox.runCode(pythonCode, {
      language: 'python',
      workingDir: '/workspace'
    });
    console.log('Python execution in /workspace:');
    console.log(codeResult2.stdout);

    // =========================================================================
    // Example 5: Background commands with working directory
    // =========================================================================
    console.log('Example 5: Background Commands with Working Directory');
    console.log('-'.repeat(70));

    // Start a background command in /var
    await sandbox.commands.run(
      'pwd > /tmp/bg-output.txt && echo "Background task in $(pwd)" >> /tmp/bg-output.txt',
      { background: true, workingDir: '/var', timeout: 10 }
    );

    // Wait for completion
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Check the output
    const bgOutput = await sandbox.commands.run('cat /tmp/bg-output.txt');
    console.log('Background command output:');
    console.log(bgOutput.stdout);

    // =========================================================================
    // Example 6: Workflow - Process files in specific directory
    // =========================================================================
    console.log('Example 6: Practical Workflow - Process Files in Directory');
    console.log('-'.repeat(70));

    // Create a project directory
    await sandbox.commands.run('mkdir -p /workspace/myproject/data');

    // Create some data files
    await sandbox.commands.run(
      'echo "item1,100" > data.csv && echo "item2,200" >> data.csv',
      { workingDir: '/workspace/myproject/data' }
    );

    // Process the data with Python (working directory matters for relative paths)
    const processScript = `
import csv
import os

# Read CSV from current directory
with open('data.csv', 'r') as f:
    reader = csv.reader(f)
    total = sum(int(row[1]) for row in reader)

print(f"Working directory: {os.getcwd()}")
print(f"Total: {total}")
`;

    const processResult = await sandbox.runCode(processScript, {
      language: 'python',
      workingDir: '/workspace/myproject/data'
    });
    console.log('Data processing result:');
    console.log(processResult.stdout);

    // =========================================================================
    // Summary
    // =========================================================================
    console.log('\n' + '='.repeat(70));
    console.log('📋 Summary');
    console.log('='.repeat(70));
    console.log('✅ Working directory parameter works correctly for:');
    console.log('   - Command execution (sync and background)');
    console.log('   - Code execution (Python, JavaScript, etc.)');
    console.log('   - File operations relative to working directory');
    console.log('   - Complex workflows with multiple directories');

  } finally {
    // Cleanup
    console.log(`\n🧹 Cleaning up sandbox ${sandbox.sandboxId}...`);
    await sandbox.kill();
    console.log('✅ Done!');
  }
}

// Run the example
main().catch(error => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});
