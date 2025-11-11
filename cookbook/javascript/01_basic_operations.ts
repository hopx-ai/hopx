/**
 * 01. Basic Operations - JavaScript/TypeScript SDK
 *
 * This example covers:
 * - Sandbox creation
 * - Agent initialization
 * - Getting sandbox info
 * - Health checks
 * - Sandbox deletion
 * - Async/await patterns
 */

import { Sandbox } from '@hopx-ai/sdk';

const API_KEY = process.env.HOPX_API_KEY || 'hopx_live_Lap0VJrWLii8.KSN6iLWELs13jHt960gSK9Eq63trgPApqMf7yLGVTNo';


async function basicCreation() {
  console.log('='.repeat(60));
  console.log('1. BASIC SANDBOX CREATION');
  console.log('='.repeat(60));
  
  // Create sandbox with minimal options
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    apiKey: API_KEY
  });
  
  console.log(`✅ Sandbox ID: ${sandbox.sandboxId}`);
  
  // Get sandbox info
  const info = await sandbox.getInfo();
  console.log(`✅ Status: ${info.status}`);
  console.log(`✅ Agent URL: ${info.publicHost}`);
  console.log(`✅ Template: ${info.templateName}`);
  
  // Cleanup
  await sandbox.kill();
  console.log('✅ Sandbox deleted\n');
}


async function advancedCreation() {
  console.log('='.repeat(60));
  console.log('2. ADVANCED SANDBOX CREATION');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',  // Template defines CPU/RAM/Disk resources
    apiKey: API_KEY,
    // region: 'us-west-2',        // Specific region (commented - use default)
    timeoutSeconds: 600,                  // 10 minute timeout
    envVars: {                     // Pre-set environment variables
      PYTHONPATH: '/workspace',
      DEBUG: 'true'
    }
  });
  
  console.log(`✅ Sandbox ID: ${sandbox.sandboxId}`);
  
  // Get detailed info (resources loaded from template)
  const info = await sandbox.getInfo();
  console.log(`✅ Template: ${info.templateName || 'code-interpreter'}`);
  console.log(`✅ vCPU: ${info.vcpu} (from template)`);
  console.log(`✅ Memory: ${info.memoryMb}MB (from template)`);
  
  // Check health
  const health = await sandbox.getHealth();
  console.log(`✅ Health: ${health.status}`);
  
  // Cleanup
  await sandbox.kill();
  console.log('✅ Sandbox deleted\n');
}


async function tryFinallyPattern() {
  console.log('='.repeat(60));
  console.log('3. TRY/FINALLY PATTERN (AUTO-CLEANUP)');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    apiKey: API_KEY
  });
  
  try {
    console.log(`✅ Sandbox ID: ${sandbox.sandboxId}`);
    
    // Do work here
    const result = await sandbox.runCode("console.log('Hello from sandbox!')");
    console.log(`✅ Output: ${result.stdout.trim()}`);
    
  } finally {
    // Always cleanup, even if error occurs
    await sandbox.kill();
    console.log('✅ Sandbox automatically deleted in finally block\n');
  }
}


async function connectToExistingSandbox() {
  console.log('='.repeat(60));
  console.log('4. CONNECT TO EXISTING SANDBOX');
  console.log('='.repeat(60));
  
  // Create sandbox
  const sandbox1 = await Sandbox.create({
    template: 'code-interpreter',
    apiKey: API_KEY
  });
  const sandboxId = sandbox1.sandboxId;
  console.log(`✅ Created sandbox: ${sandboxId}`);
  
  // Connect to same sandbox by ID
  const sandbox2 = Sandbox.connect(sandboxId, API_KEY);
  console.log(`✅ Connected to sandbox: ${sandbox2.sandboxId}`);
  
  // Verify they're the same
  const info1 = await sandbox1.getInfo();
  const info2 = await sandbox2.getInfo();
  console.assert(info1.publicHost === info2.publicHost, 'Same sandbox!');
  console.log('✅ Same sandbox confirmed!');
  
  // Cleanup
  await sandbox1.kill();
  console.log('✅ Sandbox deleted\n');
}


async function listAndConnect() {
  console.log('='.repeat(60));
  console.log('5. LIST SANDBOXES AND CONNECT (RECOMMENDED WORKFLOW)');
  console.log('='.repeat(60));
  
  // Create a sandbox first
  const newSandbox = await Sandbox.create({
    template: 'code-interpreter',
    apiKey: API_KEY
  });
  console.log(`✅ Created sandbox: ${newSandbox.sandboxId}`);
  
  try {
    // List all running sandboxes
    const sandboxes = await Sandbox.list({
      apiKey: API_KEY,
      status: 'running',
      limit: 10
    });
    
    console.log(`✅ Found ${sandboxes.length} running sandbox(es)`);
    
    // Find our sandbox
    const mySandbox = sandboxes.find(s => s.sandboxId === newSandbox.sandboxId);
    if (mySandbox) {
      console.log(`✅ Found our sandbox in list: ${mySandbox.sandboxId}`);
      console.log(`   Template: ${mySandbox.templateName}`);
      console.log(`   Status: ${mySandbox.status}`);
      
      // Connect to it
      const connected = Sandbox.connect(mySandbox.sandboxId, API_KEY);
      console.log(`✅ Connected to sandbox!`);
      
      // Use it
      const result = await connected.runCode('print("Hello from connected sandbox!")');
      console.log(`✅ Executed code: ${result.stdout.trim()}`);
    }
  } finally {
    // Cleanup
    await newSandbox.kill();
    console.log('✅ Sandbox deleted\n');
  }
}


async function errorHandling() {
  console.log('='.repeat(60));
  console.log('6. ERROR HANDLING');
  console.log('='.repeat(60));
  
  try {
    // This will succeed
    const sandbox = await Sandbox.create({
      template: 'code-interpreter',
      apiKey: API_KEY
    });
    
    console.log(`✅ Sandbox created: ${sandbox.sandboxId}`);
    
    try {
      // Try to get non-existent file (will throw FileNotFoundError)
      await sandbox.files.read('/non-existent-file.txt');
    } catch (error: any) {
      if (error.constructor.name === 'FileNotFoundError') {
        console.log(`✅ Caught FileNotFoundError: ${error.message}`);
        console.log(`   Request ID: ${error.requestId}`);
      }
    }
    
    // Cleanup
    await sandbox.kill();
    console.log('✅ Sandbox deleted');
    
  } catch (error: any) {
    if (error.constructor.name === 'AuthenticationError') {
      console.log(`❌ Authentication failed: ${error.message}`);
    } else if (error.constructor.name === 'ResourceLimitError') {
      console.log(`❌ Resource limit exceeded: ${error.message}`);
    } else if (error.constructor.name === 'APIError') {
      console.log(`❌ API error: ${error.message}`);
      console.log(`   Status code: ${error.statusCode}`);
      console.log(`   Request ID: ${error.requestId}`);
    }
  }
  
  console.log();
}


async function asyncAwaitPatterns() {
  console.log('='.repeat(60));
  console.log('7. ASYNC/AWAIT PATTERNS');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    apiKey: API_KEY
  });
  
  try {
    // Sequential operations
    console.log('✅ Sequential operations:');
    const result1 = await sandbox.runCode('console.log("Step 1")');
    console.log(`   Step 1 done: ${result1.stdout.trim()}`);
    
    const result2 = await sandbox.runCode('console.log("Step 2")');
    console.log(`   Step 2 done: ${result2.stdout.trim()}`);
    
    // Parallel operations (Promise.all)
    console.log('\n✅ Parallel operations:');
    const [r1, r2, r3] = await Promise.all([
      sandbox.runCode('console.log("Parallel 1")'),
      sandbox.runCode('console.log("Parallel 2")'),
      sandbox.runCode('console.log("Parallel 3")')
    ]);
    
    console.log(`   All done: ${r1.success && r2.success && r3.success}`);
    
  } finally {
    await sandbox.kill();
    console.log('✅ Sandbox deleted\n');
  }
}


async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('JAVASCRIPT/TYPESCRIPT SDK - BASIC OPERATIONS');
  console.log('='.repeat(60) + '\n');
  
  await basicCreation();
  await advancedCreation();
  await tryFinallyPattern();
  await connectToExistingSandbox();
  await listAndConnect();
  await errorHandling();
  await asyncAwaitPatterns();
  
  console.log('='.repeat(60));
  console.log('✅ ALL BASIC OPERATIONS DEMONSTRATED!');
  console.log('='.repeat(60) + '\n');
}

main().catch(console.error);

