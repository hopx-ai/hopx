/**
 * 06. Process Management - JavaScript/TypeScript SDK
 * Covers: list processes, kill processes
 */

import { Sandbox } from '@hopx-ai/sdk';

const API_KEY = process.env.HOPX_API_KEY || 'your-api-key-here';

async function listProcesses() {
  const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
  try {
    await sandbox.runCodeBackground('import time; time.sleep(60)');
    await new Promise(r => setTimeout(r, 1000));
    
    const processes = await sandbox.listProcesses();
    console.log(`✅ Total processes: ${processes.length}`);
    
    processes.slice(0, 5).forEach(proc => {
      console.log(`   ${proc.pid} ${proc.name} (CPU: ${proc.cpu_percent}%, Mem: ${proc.memory_percent}%)`);
    });
  } finally {
    await sandbox.kill();
  }
}

async function main() {
  console.log('\nJAVASCRIPT/TYPESCRIPT SDK - PROCESS MANAGEMENT\n');
  await listProcesses();
  console.log('✅ ALL PROCESS OPERATIONS DEMONSTRATED!\n');
}

main().catch(console.error);
