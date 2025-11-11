/**
 * Node.js Template Example
 * 
 * Build a custom Node.js template with Express
 */

import { Template, waitForPort } from '../src/index.js';

async function main() {
  console.log('🚀 Node.js Template Example\n');
  
  const template = new Template()
    .fromNodeImage('18-alpine')
    .copy('package.json', '/app/package.json')
    .copy('src/', '/app/src/')
    .setWorkdir('/app')
    .npmInstall()
    .setEnv('NODE_ENV', 'production')
    .setEnv('PORT', '3000')
    .setStartCmd('node src/index.js', waitForPort(3000, 60000));
  
  console.log('Building Node.js template...');
  const result = await Template.build(template, {
    alias: 'nodejs-express-app',
    apiKey: process.env.HOPX_API_KEY!,
    onLog: (log) => console.log(`[${log.level}] ${log.message}`),
  });
  
  console.log(`✅ Template built: ${result.templateID}`);
  
  // Create multiple instances
  console.log('\nCreating 3 VM instances...');
  const vms = await Promise.all([
    result.createVM({ alias: 'instance-1' }),
    result.createVM({ alias: 'instance-2' }),
    result.createVM({ alias: 'instance-3' }),
  ]);
  
  console.log('\n✅ VMs created:');
  vms.forEach(vm => {
    console.log(`   - ${vm.vmID}: ${vm.ip}`);
  });
  
  // Cleanup
  console.log('\nCleaning up...');
  await Promise.all(vms.map(vm => vm.delete()));
  console.log('✅ All VMs deleted');
}

main().catch(console.error);

