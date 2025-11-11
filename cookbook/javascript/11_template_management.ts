/**
 * HOPX.AI JavaScript/TypeScript SDK - Template Management
 * 
 * This example demonstrates:
 * 1. Listing templates
 * 2. Getting template details
 * 3. Creating sandbox from template
 */

import { Sandbox } from '@hopx-ai/sdk';

const API_KEY = process.env.HOPX_API_KEY || 'your-api-key-here';

if (API_KEY === 'your-api-key-here') {
  throw new Error('HOPX_API_KEY environment variable not set');
}

async function listAllTemplates() {
  console.log('='.repeat(60));
  console.log('LIST ALL TEMPLATES');
  console.log('='.repeat(60));
  
  const templates = await Sandbox.listTemplates({ apiKey: API_KEY });
  
  console.log(`Found ${templates.length} template(s):\n`);
  
  for (const template of templates) {
    console.log(`📦 ${template.name}`);
    console.log(`   ID: ${template.id}`);
    console.log(`   Display Name: ${template.displayName}`);
    if (template.category) {
      console.log(`   Category: ${template.category}`);
    }
    if (template.language) {
      console.log(`   Language: ${template.language}`);
    }
    if (template.description) {
      console.log(`   Description: ${template.description}`);
    }
    if (template.status) {
      console.log(`   Status: ${template.status}`);
    }
    console.log();
  }
  
  return templates;
}

async function getTemplateDetails() {
  console.log('='.repeat(60));
  console.log('GET TEMPLATE DETAILS');
  console.log('='.repeat(60));
  
  const templateName = 'code-interpreter';
  console.log(`Getting details for '${templateName}'...\n`);
  
  const template = await Sandbox.getTemplate(templateName, { apiKey: API_KEY });
  
  console.log(`✅ Template: ${template.name}`);
  console.log(`   Display Name: ${template.displayName}`);
  if (template.category) {
    console.log(`   Category: ${template.category}`);
  }
  if (template.language) {
    console.log(`   Language: ${template.language}`);
  }
  if (template.description) {
    console.log(`   Description: ${template.description}`);
  }
  if (template.status) {
    console.log(`   Status: ${template.status}`);
  }
  console.log();
  
  return template;
}

async function createSandboxFromTemplate(templateName: string) {
  console.log('='.repeat(60));
  console.log(`CREATE SANDBOX FROM TEMPLATE: ${templateName}`);
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({
    template: templateName,
    apiKey: API_KEY
  });
  
  console.log(`✅ Sandbox created from template '${templateName}'`);
  console.log(`   Sandbox ID: ${sandbox.sandboxId}`);
  
  const info = await sandbox.getInfo();
  console.log(`   Status: ${info.status}`);
  console.log(`   Agent URL: ${info.publicHost}`);
  if (info.templateId) {
    console.log(`   Template ID: ${info.templateId}`);
  }
  console.log();
  
  console.log('Testing code execution...');
  const result = await sandbox.runCode("console.log('Hello from', process.platform);");
  if (result.success) {
    console.log(`✅ Code execution test passed`);
    console.log(`   Output: ${result.stdout.trim()}`);
  } else {
    console.log(`❌ Code execution test failed`);
    console.log(`   Error: ${result.stderr}`);
  }
  
  console.log();
  
  return sandbox;
}

async function templateStatusGuide() {
  console.log('='.repeat(60));
  console.log('TEMPLATE STATUS GUIDE');
  console.log('='.repeat(60));
  console.log();
  console.log('Template lifecycle statuses:');
  console.log();
  console.log('  building   - Template is being built (Dockerfile processing)');
  console.log('  publishing - Build complete, being published to registry');
  console.log('  active     - Ready to use! ✅');
  console.log('  failed     - Build or publishing failed ❌');
  console.log();
  console.log('⚠️  Only use templates with status=\'active\'');
  console.log();
  console.log('Template.build() waits automatically for \'active\' status,');
  console.log('so you can create sandboxes immediately after building.');
  console.log();
}

async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('JAVASCRIPT/TYPESCRIPT SDK - TEMPLATE MANAGEMENT');
  console.log('='.repeat(60));
  console.log();
  
  await templateStatusGuide();
  
  const templates = await listAllTemplates();
  const template = await getTemplateDetails();
  
  let sandbox: Awaited<ReturnType<typeof Sandbox.create>> | null = null;
  try {
    sandbox = await createSandboxFromTemplate('code-interpreter');
  } finally {
    if (sandbox) {
      console.log('Cleaning up...');
      await sandbox.kill();
      console.log('✅ Sandbox deleted');
    }
  }
  
  console.log('='.repeat(60));
  console.log('✅ ALL TESTS COMPLETED!');
  console.log('='.repeat(60));
  console.log();
}

main().catch(console.error);

