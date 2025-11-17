/**
 * Sandbox Lifecycle Demo
 *
 * Demonstrates sandbox lifecycle management: create, pause, resume, kill
 */

import { Sandbox } from '../src/index.js';

async function main() {
  console.log('Sandbox Lifecycle Demo\n');

  // 1. Create sandbox
  console.log('1. Creating sandbox...');
  const sandbox = await Sandbox.create({
    template: 'code-interpreter',
    timeoutSeconds: 600,  // 10 minutes auto-kill timeout
  });
  console.log(`   Created: ${sandbox.sandboxId}`);

  const info = await sandbox.getInfo();
  console.log(`   URL: ${info.publicHost}`);
  if (info.resources) {
    console.log(`   Resources: ${info.resources.vcpu} vCPU, ${info.resources.memoryMb}MB RAM`);
  }

  // 2. Check status
  console.log('\n2. Checking status...');
  const info2 = await sandbox.getInfo();
  console.log(`   Status: ${info2.status}`);
  console.log(`   Created: ${new Date(info2.createdAt).toLocaleString()}`);

  // 3. Run code
  console.log('\n3. Running code...');
  const result = await sandbox.runCode('print(2 + 2)', { language: 'python' });
  console.log(`   Output: ${result.stdout?.trim()}`);

  // 4. Pause sandbox
  console.log('\n4. Pausing sandbox...');
  await sandbox.pause();
  console.log('   Sandbox paused');

  // Verify paused status
  const info3 = await sandbox.getInfo();
  console.log(`   Status: ${info3.status}`);

  // 5. Resume sandbox
  console.log('\n5. Resuming sandbox...');
  await sandbox.resume();
  console.log('   Sandbox resumed');

  // Verify running status
  const info4 = await sandbox.getInfo();
  console.log(`   Status: ${info4.status}`);

  // 6. Run code again
  console.log('\n6. Running code again...');
  const result2 = await sandbox.runCode('print("Still works!")', { language: 'python' });
  console.log(`   Output: ${result2.stdout?.trim()}`);

  // 7. Kill sandbox
  console.log('\n7. Killing sandbox...');
  await sandbox.kill();
  console.log('   Sandbox killed');

  console.log('\nDemo complete');
}

main().catch((error) => {
  console.error('Error:', error.message);
  process.exit(1);
});
