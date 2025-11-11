/**
 * 05. Environment Variables - JavaScript/TypeScript SDK
 * Covers all env var operations
 */

import { Sandbox } from '@hopx-ai/sdk';

const API_KEY = process.env.HOPX_API_KEY || 'your-api-key-here';

async function getAllEnvVars() {
  const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
  try {
    const envVars = await sandbox.env.getAll();
    console.log(`✅ Total environment variables: ${Object.keys(envVars).length}`);
  } finally {
    await sandbox.kill();
  }
}

async function setAndUpdateEnv() {
  const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
  try {
    await sandbox.env.setAll({ API_KEY: 'sk-123', DEBUG: 'true' });
    console.log('✅ Environment variables set');
    
    await sandbox.env.update({ DEBUG: 'false', NEW_VAR: 'value' });
    console.log('✅ Environment variables updated');
    
    const value = await sandbox.env.get('DEBUG');
    console.log(`✅ DEBUG: ${value}`);
  } finally {
    await sandbox.kill();
  }
}

async function main() {
  console.log('\nJAVASCRIPT/TYPESCRIPT SDK - ENVIRONMENT VARIABLES\n');
  await getAllEnvVars();
  await setAndUpdateEnv();
  console.log('✅ ALL ENV OPERATIONS DEMONSTRATED!\n');
}

main().catch(console.error);
