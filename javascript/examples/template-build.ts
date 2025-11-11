/**
 * Template Building Example
 * 
 * Shows how to build a custom template and create VMs from it.
 */

import { Template, waitForPort } from '../src/index.js';

async function main() {
  console.log('🚀 Template Building Example\n');
  
  // 1. Define a Python web app template
  console.log('1. Defining template...');
  const template = new Template()
    .fromPythonImage('3.11')
    .copy('app/', '/app/')
    .pipInstall()
    .setEnv('PORT', '8000')
    .setStartCmd('python /app/main.py', waitForPort(8000));
  
  console.log('   ✅ Template defined with', template.getSteps().length, 'steps');
  
  // 2. Build the template
  console.log('\n2. Building template...');
  const result = await Template.build(template, {
    alias: 'my-python-app',
    apiKey: process.env.HOPX_API_KEY || '',
    baseURL: process.env.HOPX_BASE_URL || 'https://api.hopx.dev',
    cpu: 2,
    memory: 2048,
    diskGB: 10,
    contextPath: process.cwd(),
    onLog: (log) => {
      console.log(`   [${log.level}] ${log.message}`);
    },
    onProgress: (progress) => {
      console.log(`   Progress: ${progress}%`);
    },
  });
  
  console.log('\n   ✅ Template built successfully!');
  console.log(`   Template ID: ${result.templateID}`);
  console.log(`   Build ID: ${result.buildID}`);
  console.log(`   Duration: ${result.duration}ms`);
  
  // 3. Create VM from template
  console.log('\n3. Creating VM from template...');
  const vm = await result.createVM({
    alias: 'instance-1',
    envVars: {
      DATABASE_URL: 'postgresql://localhost/mydb',
      API_KEY: 'secret123',
    },
  });
  
  console.log('   ✅ VM created!');
  console.log(`   VM ID: ${vm.vmID}`);
  console.log(`   IP: ${vm.ip}`);
  console.log(`   Agent URL: ${vm.agentUrl}`);
  
  // 4. Use the VM
  console.log('\n4. Testing VM...');
  const response = await fetch(`${vm.agentUrl}/health`);
  const health = await response.json();
  console.log('   Health status:', health);
  
  // 5. Cleanup
  console.log('\n5. Cleaning up...');
  await vm.delete();
  console.log('   ✅ VM deleted');
  
  console.log('\n✨ Done!');
}

// Run example
main().catch(error => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});

