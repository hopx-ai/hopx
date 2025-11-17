/**
 * Node.js Template Example
 *
 * Build a custom Node.js template with Express
 */

import { Template, waitForPort, Sandbox } from '../src/index.js';

async function main() {
  console.log('Node.js Template Example\n');

  // Generate unique template name
  const templateName = `nodejs-express-${Date.now()}`;
  console.log(`Template name: ${templateName}\n`);

  // Build template with embedded file content
  const template = new Template('node:20-bookworm')  // Standard Node.js 20 image (Debian-based)
    .runCmd('mkdir -p /app/src')
    .setWorkdir('/app')
    .runCmd(`cat > package.json << 'EOF'
{
  "name": "hopx-express-app",
  "version": "1.0.0",
  "main": "src/index.js",
  "dependencies": {
    "express": "^4.18.2"
  }
}
EOF`)
    .runCmd(`cat > src/index.js << 'EOF'
const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;
const INSTANCE = process.env.INSTANCE || '1';

app.get('/', (req, res) => {
    res.json({
        message: 'Hello from Hopx Node.js!',
        instance: INSTANCE,
        timestamp: new Date().toISOString()
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log('Server running on port ' + PORT);
});
EOF`)
    .runCmd('npm install')  // Use npm from PATH (works across Node images)
    .setEnv('NODE_ENV', 'production')
    .setEnv('PORT', '3000')
    .setStartCmd('node src/index.js', waitForPort(3000, 60000));

  console.log('Building Node.js template...');
  console.log('Note: This may take 5-10 minutes...\n');

  const result = await Template.build(template, {
    name: templateName,
    apiKey: process.env.HOPX_API_KEY!,
    onLog: (log) => {
      const level = log.level || 'INFO';
      const message = log.message || '';
      console.log(`  [${level}] ${message}`);
    },
  });

  console.log(`\nTemplate built: ${result.templateID}\n`);

  // Create multiple sandbox instances
  console.log('Creating 3 sandbox instances...');
  const sandboxes = await Promise.all([
    Sandbox.create({ template: templateName, envVars: { INSTANCE: '1' } }),
    Sandbox.create({ template: templateName, envVars: { INSTANCE: '2' } }),
    Sandbox.create({ template: templateName, envVars: { INSTANCE: '3' } }),
  ]);

  console.log('\nSandboxes created:');
  for (const sandbox of sandboxes) {
    const info = await sandbox.getInfo();
    console.log(`   - ${sandbox.sandboxId}: ${info.publicHost}`);
  }

  // Test one instance
  console.log('\nTesting instance 1...');
  const testResult = await sandboxes[0].runCode('console.log(process.env.INSTANCE)', { language: 'javascript' });
  console.log(`   Instance ID: ${testResult.stdout?.trim()}`);

  // Cleanup
  console.log('\nCleaning up...');
  await Promise.all(sandboxes.map(sb => sb.kill()));
  console.log('All sandboxes killed');
}

main().catch(console.error);
