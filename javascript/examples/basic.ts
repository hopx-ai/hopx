/**
 * Basic usage example
 */

import { Sandbox } from '../src/index.js';

async function main() {
  console.log('🚀 Creating sandbox...');
  
  // Create sandbox
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    apiKey: process.env.HOPX_API_KEY,
    envVars: {
      API_KEY: 'sk-test-123',
      DEBUG: 'true',
    },
  });

  console.log(`✅ Sandbox created: ${sandbox.sandboxId}`);

  // Initialize agent client
  await sandbox.init();

  // 1. Code execution
  console.log('\n📝 Running code...');
  const result = await sandbox.runCode('print("Hello from Hopx!")', {
    env: { GREETING: 'Hi' },
  });
  console.log(`✅ Output: ${result.stdout}`);
  console.log(`✅ Execution time: ${result.execution_time}s`);

  // 2. File operations
  console.log('\n📁 File operations...');
  await sandbox.files.write('/workspace/test.txt', 'Hello, Files!');
  const content = await sandbox.files.read('/workspace/test.txt');
  console.log(`✅ File content: ${content}`);

  const files = await sandbox.files.list('/workspace');
  console.log(`✅ Found ${files.length} files`);

  // 3. Commands
  console.log('\n💻 Running command...');
  const cmdResult = await sandbox.commands.run('echo "Hello from shell!"');
  console.log(`✅ Command output: ${cmdResult.stdout}`);

  // 4. Environment variables
  console.log('\n🔐 Environment variables...');
  await sandbox.env.set('MY_VAR', 'my_value');
  const myVar = await sandbox.env.get('MY_VAR');
  console.log(`✅ MY_VAR: ${myVar}`);

  // 5. Metrics
  console.log('\n📊 Metrics...');
  const metrics = await sandbox.getMetricsSnapshot();
  console.log(`✅ Total executions: ${metrics.total_executions}`);

  // 6. Cache
  console.log('\n💾 Cache...');
  const cacheStats = await sandbox.cache.stats();
  console.log(`✅ Cache size: ${cacheStats.cache.size}`);

  // Cleanup
  console.log('\n🧹 Cleaning up...');
  await sandbox.kill();
  console.log('✅ Sandbox deleted');

  console.log('\n🎉 All done!');
}

main().catch(console.error);

