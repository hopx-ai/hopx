/**
 * HOPX JavaScript SDK - Template Building Flow Test
 * Tests the complete template building flow matching test-template-build.sh
 */

import { Template, Sandbox } from '../src/index.js';
import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';
import * as tar from 'tar';
import * as os from 'os';

// Colors for output
const RED = '\x1b[0;31m';
const GREEN = '\x1b[0;32m';
const YELLOW = '\x1b[1;33m';
const BLUE = '\x1b[0;34m';
const CYAN = '\x1b[0;36m';
const NC = '\x1b[0m'; // No Color

// Configuration
const API_BASE_URL = process.env.HOPX_BASE_URL || 'https://api.hopx.dev';
const API_KEY = process.env.HOPX_API_KEY || '';

// Test data
const TEST_TEMPLATE_NAME = `test-js-${Date.now()}`;
let TEST_FILES_HASH = '';

// Test results tracker
const testResults = {
  passed: 0,
  failed: 0,
  warnings: 0
};

// Helper functions
function printHeader(text: string): void {
  console.log();
  console.log(`${CYAN}${'━'.repeat(60)}${NC}`);
  console.log(`${CYAN}  ${text}${NC}`);
  console.log(`${CYAN}${'━'.repeat(60)}${NC}`);
  console.log();
}

function printStep(text: string): void {
  console.log(`${BLUE}▶ ${text}${NC}`);
}

function printSuccess(text: string): void {
  console.log(`${GREEN}✓ ${text}${NC}`);
  testResults.passed++;
}

function printError(text: string): void {
  console.log(`${RED}✗ ${text}${NC}`);
  testResults.failed++;
}

function printWarning(text: string): void {
  console.log(`${YELLOW}⚠ ${text}${NC}`);
  testResults.warnings++;
}

function checkApiKey(): void {
  printHeader('Checking API Key');
  
  if (!API_KEY) {
    printError('HOPX_API_KEY environment variable is not set');
    console.log();
    console.log('Usage:');
    console.log('  export HOPX_API_KEY=your_api_key_here');
    console.log('  npm run test:template-building');
    process.exit(1);
  }
  
  printSuccess(`API Key is set: ${API_KEY.substring(0, 10)}...`);
}

async function testUploadFiles(): Promise<void> {
  printHeader('Step 1: Get Presigned Upload URL & Upload to R2');
  
  printStep('Creating test tar.gz file');
  
  // Create temporary directory with test files
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'hopx-test-'));
  
  try {
    // Create test files
    fs.writeFileSync(path.join(tempDir, 'app.py'), "print('Hello from HOPX!')");
    fs.writeFileSync(path.join(tempDir, 'requirements.txt'), 'flask==3.0.0');
    
    // Create tar.gz
    const tarPath = path.join(tempDir, 'test-files.tar.gz');
    await tar.create(
      {
        gzip: true,
        file: tarPath,
        cwd: tempDir
      },
      ['app.py', 'requirements.txt']
    );
    
    // Calculate SHA256 hash
    const fileContent = fs.readFileSync(tarPath);
    const filesHash = crypto.createHash('sha256').update(fileContent).digest('hex');
    
    TEST_FILES_HASH = filesHash;
    const fileSize = fs.statSync(tarPath).size;
    
    printSuccess(`Test file created: ${fileSize} bytes`);
    printSuccess(`Files hash: ${filesHash}`);
    
    printStep('Requesting presigned upload URL');
    
    // Request upload link
    const response = await fetch(`${API_BASE_URL}/v1/templates/files/upload-link`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        files_hash: filesHash,
        content_length: fileSize,
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      printSuccess('Upload link received');
      
      if (data.present) {
        printWarning('File already exists in R2 (cache hit - skipping upload)');
      } else {
        const uploadUrl = data.upload_url;
        printSuccess('Upload URL received');
        
        // Upload to R2
        printStep('Uploading file to R2...');
        const uploadResponse = await fetch(uploadUrl, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/gzip',
            'Content-Length': String(fileSize),
          },
          body: fileContent
        });
        
        if (uploadResponse.ok || uploadResponse.status === 204) {
          printSuccess('File uploaded to R2 successfully!');
        } else {
          printError(`R2 upload failed (HTTP ${uploadResponse.status})`);
        }
      }
    } else {
      printError(`Failed to get upload link (HTTP ${response.status})`);
    }
    
  } finally {
    // Cleanup
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
}

async function testBuildTemplateMinimal(): Promise<void> {
  printHeader('Step 2a: Build Template - Minimal (Required Fields Only)');
  
  printStep(`Building template: ${TEST_TEMPLATE_NAME}-minimal`);
  
  try {
    const template = new Template()
      .fromPythonImage('3.11-slim')
      .runCmd('pip install flask');
    
    const result = await Template.build(template, {
      name: `${TEST_TEMPLATE_NAME}-minimal`,
      apiKey: API_KEY,
      baseURL: API_BASE_URL,
      cpu: 2,
      memory: 1024,
      diskGB: 5,
      onLog: () => {}, // Suppress logs for cleaner output
    });
    
    printSuccess('Template build triggered');
    printSuccess(`Template ID: ${result.templateID}`);
    printSuccess(`Build ID: ${result.buildID}`);
    
    // Save for later tests
    fs.writeFileSync('/tmp/hopx_test_template_id_minimal_js.txt', result.templateID);
    
  } catch (error: any) {
    printError(`Failed to trigger build: ${error.message}`);
  }
}

async function testBuildTemplateFull(): Promise<void> {
  printHeader('Step 2b: Build Template - Full Features');
  
  printStep(`Building template with all features: ${TEST_TEMPLATE_NAME}-full`);
  
  try {
    const template = new Template()
      .fromPythonImage('3.11-slim')
      .runCmd('apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y git curl vim && apt-get clean && rm -rf /var/lib/apt/lists/*')
      .setEnv('PYTHON_VERSION', '3.11')
      .setEnv('DEBUG', 'true')
      .setEnv('PORT', '8000')
      .runCmd('pip install --upgrade pip')
      .runCmd('pip install flask gunicorn')
      .runCmd('useradd -m appuser')
      .setWorkdir('/app')
      .runCmd('chown appuser:appuser /app')
      .setUser('appuser');
    
    const result = await Template.build(template, {
      name: `${TEST_TEMPLATE_NAME}-full`,
      apiKey: API_KEY,
      baseURL: API_BASE_URL,
      cpu: 4,
      memory: 4096,
      diskGB: 20,
      onLog: () => {},
    });
    
    printSuccess('Template build triggered (with all features)');
    printSuccess(`Template ID: ${result.templateID}`);
    
    fs.writeFileSync('/tmp/hopx_test_template_id_full_js.txt', result.templateID);
    
  } catch (error: any) {
    printError(`Failed to trigger build: ${error.message}`);
  }
}

async function testBuildTemplateWithCopy(): Promise<void> {
  printHeader('Step 2c: Build Template - With COPY Step');
  
  printStep(`Building template with COPY step: ${TEST_TEMPLATE_NAME}-copy`);
  
  try {
    // Create temporary directory with files to copy
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'hopx-test-'));
    
    try {
      // Create test files
      fs.writeFileSync(path.join(tempDir, 'app.py'), `
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from HOPX!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
`);
      fs.writeFileSync(path.join(tempDir, 'requirements.txt'), 'flask==3.0.0');
      
      printStep(`Created test files in: ${tempDir}`);
      
      // Build template using SDK's .copy() method
      const template = new Template()
        .fromPythonImage('3.11-slim')
        .setWorkdir('/app')
        .copy(tempDir, '/app')  // SDK handles upload automatically
        .setEnv('FLASK_APP', 'app.py')
        .runCmd('pip install -r requirements.txt');
      
      const buildOptions: BuildOptions = {
        name: `${TEST_TEMPLATE_NAME}-copy`,
        apiKey: API_KEY,
        baseURL: API_BASE_URL,
        cpu: 2,
        memory: 2048,
        diskGB: 10,
        onLog: () => {},  // Suppress logs
      };
      
      const result = await Template.build(template, buildOptions);
      
      printSuccess('Template build triggered (with COPY using SDK)');
      printSuccess(`Template ID: ${result.templateID}`);
      
      fs.writeFileSync('/tmp/hopx_test_template_id_copy_js.txt', result.templateID);
    } finally {
      // Cleanup temp directory
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
    
  } catch (error: any) {
    printError(`Failed to trigger build: ${error.message}`);
  }
}

async function testBuildUbuntuWithApt(): Promise<void> {
  printHeader('Step 2d: Build Template - Ubuntu with aptInstall');
  
  printStep(`Building Ubuntu template with aptInstall: ${TEST_TEMPLATE_NAME}-ubuntu`);
  
  try {
    const template = new Template()
      .fromUbuntuImage('22.04')
      .aptInstall('curl', 'git', 'vim')
      .runCmd('curl --version')
      .setEnv('MY_VAR', 'test');
    
    const buildOptions: BuildOptions = {
      name: `${TEST_TEMPLATE_NAME}-ubuntu`,
      apiKey: API_KEY,
      baseURL: API_BASE_URL,
      cpu: 2,
      memory: 1024,
      diskGB: 5,
      onLog: () => {},  // Suppress logs
    };
    
    const result = await Template.build(template, buildOptions);
    
    printSuccess('Ubuntu template build triggered (with aptInstall)');
    printSuccess(`Template ID: ${result.templateID}`);
    
  } catch (error: any) {
    printError(`Failed to trigger build: ${error.message}`);
  }
}

async function testBuildNodejsTemplate(): Promise<void> {
  printHeader('Step 2e: Build Template - Node.js');
  
  printStep(`Building Node.js template: ${TEST_TEMPLATE_NAME}-nodejs`);
  
  try {
    const template = new Template()
      .fromNodeImage('20')
      .runCmd('node --version')
      .runCmd('npm --version')
      .setWorkdir('/app');
    
    const buildOptions: BuildOptions = {
      name: `${TEST_TEMPLATE_NAME}-nodejs`,
      apiKey: API_KEY,
      baseURL: API_BASE_URL,
      cpu: 2,
      memory: 1024,
      diskGB: 5,
      onLog: () => {},  // Suppress logs
    };
    
    const result = await Template.build(template, buildOptions);
    
    printSuccess('Node.js template build triggered');
    printSuccess(`Template ID: ${result.templateID}`);
    
  } catch (error: any) {
    printError(`Failed to trigger build: ${error.message}`);
  }
}

async function testValidationErrors(): Promise<void> {
  printHeader('Step 3: Testing Validations (Expected Errors)');
  
  // Test 3a: Missing CPU
  printStep('Test 3a: Missing CPU (should fail)');
  try {
    const response = await fetch(`${API_BASE_URL}/v1/templates/build`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: 'test-invalid',
        memory: 1024,
        diskGB: 5,
        from_image: 'ubuntu:22.04',
        steps: []
      })
    });
    
    if (response.status === 400) {
      printSuccess('Correctly rejected (HTTP 400)');
    } else {
      printError(`Should have failed with 400, got ${response.status}`);
    }
  } catch (error: any) {
    printError(`Test error: ${error.message}`);
  }
  
  // Test 3b: CPU too high
  printStep('Test 3b: CPU too high (should fail)');
  try {
    const response = await fetch(`${API_BASE_URL}/v1/templates/build`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: 'test-invalid',
        cpu: 100,
        memory: 1024,
        diskGB: 5,
        from_image: 'ubuntu:22.04',
        steps: []
      })
    });
    
    if (response.status === 400) {
      printSuccess('Correctly rejected (HTTP 400)');
    } else {
      printError(`Should have failed with 400, got ${response.status}`);
    }
  } catch (error: any) {
    printError(`Test error: ${error.message}`);
  }
  
  // Test 3c: Memory too low
  printStep('Test 3c: Memory too low (should fail)');
  try {
    const response = await fetch(`${API_BASE_URL}/v1/templates/build`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: 'test-invalid',
        cpu: 2,
        memory: 256,
        diskGB: 5,
        from_image: 'ubuntu:22.04',
        steps: []
      })
    });
    
    if (response.status === 400) {
      printSuccess('Correctly rejected (HTTP 400)');
    } else {
      printError(`Should have failed with 400, got ${response.status}`);
    }
  } catch (error: any) {
    printError(`Test error: ${error.message}`);
  }
  
  // Test 3d: Alpine (should fail)
  printStep('Test 3d: Alpine image (should fail)');
  try {
    const response = await fetch(`${API_BASE_URL}/v1/templates/build`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: 'test-invalid',
        cpu: 2,
        memory: 1024,
        diskGB: 5,
        from_image: 'alpine:latest',
        steps: []
      })
    });
    
    if (response.status === 400) {
      const data = await response.json();
      printSuccess('Correctly rejected Alpine (HTTP 400)');
      if (data.error?.message?.includes('hopx-agent')) {
        printSuccess('Error message mentions hopx-agent');
      }
    } else {
      printError(`Should have failed with 400, got ${response.status}`);
    }
  } catch (error: any) {
    printError(`Test error: ${error.message}`);
  }
  
  // Test 3e: Duplicate template name (should fail with 409)
  printStep('Test 3e: Duplicate template name without update flag (should fail with 409)');
  try {
    const template = new Template()
      .fromUbuntuImage('22.04')
      .runCmd('echo test');
    
    await Template.build(template, {
      name: `${TEST_TEMPLATE_NAME}-minimal`,
      apiKey: API_KEY,
      baseURL: API_BASE_URL,
      cpu: 2,
      memory: 1024,
      diskGB: 5,
    });
    
    printError('Duplicate should have been rejected but wasn\'t');
  } catch (error: any) {
    if (error.message.includes('409') || error.message.toLowerCase().includes('already exists')) {
      printSuccess('Correctly rejected duplicate (HTTP 409 Conflict)');
    } else {
      printWarning(`Failed but not with conflict error: ${error.message.substring(0, 100)}`);
    }
  }
  
  // Test 3f: Update non-existent template (should fail with 404)
  printStep('Test 3f: Update non-existent template (should fail with 404)');
  try {
    const template = new Template()
      .fromUbuntuImage('22.04')
      .runCmd('echo test');
    
    await Template.build(template, {
      name: `non-existent-template-${Date.now()}`,
      apiKey: API_KEY,
      baseURL: API_BASE_URL,
      cpu: 2,
      memory: 1024,
      diskGB: 5,
      update: true,
    });
    
    printError('Update of non-existent should have been rejected but wasn\'t');
  } catch (error: any) {
    if (error.message.includes('404') || error.message.toLowerCase().includes('not found')) {
      printSuccess('Correctly rejected update of non-existent template (HTTP 404 Not Found)');
    } else {
      printWarning(`Failed but not with 404 error: ${error.message.substring(0, 100)}`);
    }
  }
}

async function testUpdateTemplate(): Promise<void> {
  printHeader('Step 4: Testing Update Flag (Success Case)');
  
  printStep(`Updating existing template '${TEST_TEMPLATE_NAME}-minimal' with update=true`);
  
  try {
    const template = new Template()
      .fromPythonImage('3.11-slim')
      .runCmd('pip install flask redis');
    
    const result = await Template.build(template, {
      name: `${TEST_TEMPLATE_NAME}-minimal`,
      apiKey: API_KEY,
      baseURL: API_BASE_URL,
      cpu: 2,
      memory: 2048,
      diskGB: 10,
      update: true,
      onLog: () => {},
    });
    
    printSuccess('Template updated successfully (HTTP 202)');
    printSuccess(`Template ID: ${result.templateID}`);
    
  } catch (error: any) {
    printError(`Update failed: ${error.message}`);
  }
}

async function testGetBuildStatus(): Promise<void> {
  printHeader('Step 5: Check Build Status');
  
  const templateIdFile = '/tmp/hopx_test_template_id_minimal_js.txt';
  if (!fs.existsSync(templateIdFile)) {
    printWarning('No template ID found, skipping status check');
    return;
  }
  
  const templateId = fs.readFileSync(templateIdFile, 'utf-8').trim();
  printStep(`Checking status for template: ${templateId}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}/v1/templates/build/${templateId}/status`, {
      headers: {
        'Authorization': `Bearer ${API_KEY}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      printSuccess('Build status retrieved');
      const buildStatus = data.status || 'unknown';
      printSuccess(`Build status: ${buildStatus}`);
      console.log(`  Progress: ${data.progress || 0}%`);
    } else {
      printError(`Failed to get build status (HTTP ${response.status})`);
    }
  } catch (error: any) {
    printError(`Status check error: ${error.message}`);
  }
}

async function testGetBuildLogs(): Promise<void> {
  printHeader('Step 6: Get Build Logs (Polling Mode)');
  
  const templateIdFile = '/tmp/hopx_test_template_id_minimal_js.txt';
  if (!fs.existsSync(templateIdFile)) {
    printWarning('No template ID found, skipping logs check');
    return;
  }
  
  const templateId = fs.readFileSync(templateIdFile, 'utf-8').trim();
  printStep(`Fetching logs for template: ${templateId}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}/v1/templates/build/${templateId}/logs?offset=0`, {
      headers: {
        'Authorization': `Bearer ${API_KEY}`
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      printSuccess('Build logs retrieved');
      const logs = data.logs || '';
      console.log(`  Log lines: ${logs.split('\n').length}`);
      console.log(`  Status: ${data.status || 'unknown'}`);
      console.log(`  Complete: ${data.complete || false}`);
    } else {
      printError(`Failed to get build logs (HTTP ${response.status})`);
    }
  } catch (error: any) {
    printError(`Logs check error: ${error.message}`);
  }
}

async function testListTemplates(): Promise<void> {
  printHeader('Step 7: List Templates');
  
  printStep('Listing all templates');
  
  try {
    const templates = Sandbox.listTemplates({ apiKey: API_KEY, baseURL: API_BASE_URL });
    printSuccess('Templates listed');
    printSuccess(`Found ${templates.length} templates`);
    
    // Show our test templates
    for (const template of templates) {
      if (template.name.includes(TEST_TEMPLATE_NAME)) {
        console.log(`  - ${template.name} (ID: ${template.id})`);
      }
    }
    
  } catch (error: any) {
    printError(`Failed to list templates: ${error.message}`);
  }
}

function cleanup(): void {
  printHeader('Cleanup');
  
  printStep('Cleaning up temporary files');
  const files = fs.readdirSync('/tmp')
    .filter(f => f.startsWith('hopx_test_template_id_') && f.endsWith('_js.txt'));
  
  for (const file of files) {
    fs.unlinkSync(path.join('/tmp', file));
  }
  
  printSuccess('Cleanup complete');
}

async function main(): Promise<void> {
  console.log();
  console.log(`${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}`);
  console.log(`${GREEN}║     HOPX JavaScript SDK - Template Building Flow Test         ║${NC}`);
  console.log(`${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}`);
  console.log();
  console.log(`${CYAN}API Base URL: ${NC}${API_BASE_URL}`);
  console.log(`${CYAN}Test Template: ${NC}${TEST_TEMPLATE_NAME}`);
  console.log();
  
  // Run all tests
  checkApiKey();
  
  await testUploadFiles();
  await testBuildTemplateMinimal();
  await testBuildTemplateFull();
  await testBuildTemplateWithCopy();
  
  await testValidationErrors();
  await testUpdateTemplate();
  
  await new Promise(resolve => setTimeout(resolve, 2000)); // Give build a moment to start
  
  await testGetBuildStatus();
  await testGetBuildLogs();
  await testListTemplates();
  
  cleanup();
  
  // Summary
  printHeader('Test Summary');
  console.log(`${GREEN}Passed: ${testResults.passed}${NC}`);
  console.log(`${RED}Failed: ${testResults.failed}${NC}`);
  console.log(`${YELLOW}Warnings: ${testResults.warnings}${NC}`);
  console.log();
  
  if (testResults.failed === 0) {
    printSuccess('All tests completed successfully!');
  } else {
    printError(`${testResults.failed} tests failed`);
  }
  
  console.log();
  console.log('Next steps:');
  console.log('  1. Check template build status in NodeMgr logs');
  console.log('  2. Verify templates in database');
  console.log('  3. Test VM creation with built templates');
  console.log();
}

// Run tests
main().catch((error) => {
  console.error(`\n${RED}Fatal error: ${error.message}${NC}`);
  console.error(error.stack);
  process.exit(1);
});

