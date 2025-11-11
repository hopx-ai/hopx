/**
 * 04. Command Execution - JavaScript/TypeScript SDK
 * Covers: run commands, env vars, working directory
 */

import { Sandbox } from '@hopx-ai/sdk';

const API_KEY = process.env.HOPX_API_KEY || 'your-api-key-here';

async function basicCommands() {
  console.log('='.repeat(60));
  console.log('1. BASIC COMMAND EXECUTION');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
  
  try {
    const result = await sandbox.commands.run("echo 'Hello from bash!'");
    console.log(`✅ Output: ${result.stdout.trim()}`);
    console.log(`✅ Exit code: ${result.exit_code}`);
    
  } finally {
    await sandbox.kill();
  }
  
  console.log();
}

async function commandsWithEnv() {
  console.log('='.repeat(60));
  console.log('2. COMMANDS WITH ENV VARS');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
  
  try {
    const result = await sandbox.commands.run(
      'echo "API Key: $API_KEY, Region: $AWS_REGION"',
      {
        env: {
          API_KEY: 'sk-test-123',
          AWS_REGION: 'us-west-2'
        }
      }
    );
    
    console.log(`✅ Output: ${result.stdout.trim()}`);
    
  } finally {
    await sandbox.kill();
  }
  
  console.log();
}

async function workingDirectory() {
  console.log('='.repeat(60));
  console.log('3. CUSTOM WORKING DIRECTORY');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
  
  try {
    await sandbox.files.mkdir('/workspace/myproject');
    await sandbox.files.write('/workspace/myproject/file.txt', 'Hello!');
    
    const result = await sandbox.commands.run(
      'pwd && ls -la',
      { workingDir: '/workspace/myproject' }
    );
    
    console.log(`✅ Output:\n${result.stdout}`);
    
  } finally {
    await sandbox.kill();
  }
  
  console.log();
}

async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('JAVASCRIPT/TYPESCRIPT SDK - COMMAND EXECUTION');
  console.log('='.repeat(60) + '\n');
  
  await basicCommands();
  await commandsWithEnv();
  await workingDirectory();
  
  console.log('='.repeat(60));
  console.log('✅ ALL COMMAND OPERATIONS DEMONSTRATED!');
  console.log('='.repeat(60) + '\n');
}

main().catch(console.error);
