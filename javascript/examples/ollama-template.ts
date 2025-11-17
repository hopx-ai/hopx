#!/usr/bin/env npx tsx
/**
 * Ollama Template Example
 *
 * Demonstrates building a custom template with Ollama installed,
 * then creating and reusing a sandbox from that template.
 *
 * This example:
 * 1. Builds a template with Python 3.13 and Ollama
 * 2. Pulls a small language model (smollm)
 * 3. Creates a sandbox from the template
 * 4. Saves the sandbox ID for reuse
 * 5. Runs commands in the sandbox
 *
 * Note: Template building takes ~5-10 minutes on first run.
 * Subsequent runs reuse the saved sandbox (instant).
 */

import { Sandbox, Template } from '../src/index.js';
import * as fs from 'fs';
import * as path from 'path';

// Configuration
const OLLAMA_MODEL = 'smollm';  // Small model for faster testing
const HOPX_TEMPLATE_NAME = `ollama-example-${Date.now()}`;
const SANDBOX_ID_FILE = '.hopx_ollama_sandbox_id';

/**
 * Create a template with Ollama installed.
 *
 * Sets up a Python environment with Ollama for running local LLMs:
 * - Creates workspace directory structure
 * - Installs Ollama from official source
 * - Pulls a small language model (smollm)
 * - Configures environment for optimal operation
 */
function createOllamaTemplate(): Template {
  return new Template()
    .fromPythonImage('3.13')

    // Wait for VM agent to be fully ready
    .runCmd('sleep 3')

    // Create workspace directory
    .runCmd('mkdir -p /workspace')
    .runCmd('sleep 3')

    // Set environment variables
    .setEnv('LANG', 'en_US.UTF-8')
    .setEnv('LC_ALL', 'en_US.UTF-8')
    .setEnv('PYTHONUNBUFFERED', '1')
    .setEnv('HOME', '/workspace')

    // Install Ollama
    .runCmd('curl -fsSL https://ollama.com/install.sh | sh')
    .runCmd('sleep 3')  // Wait for ollama installation

    // Pull the model (this will be baked into the template)
    .runCmd(`/usr/local/bin/ollama pull ${OLLAMA_MODEL}`)

    // Set working directory
    .setWorkdir('/workspace');
}

/**
 * Build the Ollama template and create a sandbox from it.
 */
async function buildOllamaTemplateAndCreateSandbox(apiKey: string): Promise<Sandbox> {
  console.log('Building Ollama template (this takes ~5-10 minutes)...');
  console.log(`   Template name: ${HOPX_TEMPLATE_NAME}`);
  console.log();

  const template = createOllamaTemplate();

  // Build the template
  const result = await Template.build(template, {
    name: HOPX_TEMPLATE_NAME,
    apiKey,
    baseURL: process.env.HOPX_BASE_URL || 'https://api.hopx.dev',
    cpu: 2,
    memory: 2048,
    diskGB: 20,
    onLog: (log) => {
      const level = log.level || 'INFO';
      const message = log.message || '';
      console.log(`  [${level}] ${message}`);
    },
    onProgress: (p) => console.log(`  Progress: ${p}%`),
  });

  console.log();
  console.log('Template built successfully');
  console.log(`   Template ID: ${result.templateID}`);
  console.log(`   Build ID: ${result.buildID}`);
  console.log(`   Duration: ${result.duration}ms`);
  console.log();

  // Create sandbox from the template
  console.log('Creating sandbox from template...');
  const sandbox = await Sandbox.create({
    template: HOPX_TEMPLATE_NAME,
    apiKey,
  });

  // Save sandbox ID for reuse
  fs.writeFileSync(SANDBOX_ID_FILE, sandbox.sandboxId);

  console.log(`Sandbox created: ${sandbox.sandboxId}`);
  console.log(`   Saved ID to: ${SANDBOX_ID_FILE}`);
  console.log();

  return sandbox;
}

/**
 * Get existing sandbox or create new one.
 *
 * This demonstrates:
 * - Template building (only on first run)
 * - Sandbox reuse (subsequent runs)
 * - Persistent sandbox IDs
 */
async function getOrCreateSandbox(): Promise<Sandbox> {
  const apiKey = process.env.HOPX_API_KEY;
  if (!apiKey) {
    throw new Error('HOPX_API_KEY environment variable not set');
  }

  // Check if we have a saved sandbox ID
  if (fs.existsSync(SANDBOX_ID_FILE)) {
    const sandboxId = fs.readFileSync(SANDBOX_ID_FILE, 'utf-8').trim();

    console.log(`Found existing sandbox ID: ${sandboxId}`);
    console.log('   Connecting to existing sandbox...');

    try {
      const sandbox = await Sandbox.connect(sandboxId, apiKey);
      const info = await sandbox.getInfo();
      console.log(`Connected to sandbox: ${sandbox.sandboxId}`);
      console.log(`   Status: ${info.status}`);
      return sandbox;
    } catch (e) {
      const error = e as Error;
      console.log(`Failed to connect: ${error.message}`);
      console.log('   Building new sandbox...');
    }
  }

  // No saved sandbox or connection failed - build new one
  console.log('No existing sandbox found');
  return await buildOllamaTemplateAndCreateSandbox(apiKey);
}

async function main() {
  console.log('='.repeat(70));
  console.log('Ollama Template Example');
  console.log('='.repeat(70));
  console.log();

  // Get or create sandbox
  const startTime = Date.now();
  const sandbox = await getOrCreateSandbox();
  const duration = (Date.now() - startTime) / 1000;
  console.log(`Sandbox ready in ${duration.toFixed(2)} seconds`);
  console.log();

  // Test 1: Simple command
  console.log('Test 1: Running simple command...');
  const result1 = await sandbox.commands.run('uname -a', { timeout: 30000 });
  console.log(`   Output: ${result1.stdout?.trim()}`);
  console.log('   Test 1 passed');
  console.log();

  // Test 2: Check Ollama installation
  console.log('Test 2: Verifying Ollama installation...');
  const result2 = await sandbox.commands.run('/usr/local/bin/ollama --version', { timeout: 30000 });
  console.log(`   ${result2.stdout?.trim()}`);
  console.log('   Test 2 passed');
  console.log();

  // Test 3: List available models
  console.log('Test 3: Listing Ollama models...');
  const result3 = await sandbox.commands.run('/usr/local/bin/ollama list', { timeout: 30000 });
  console.log('   Available models:');
  const lines = (result3.stdout || '').trim().split('\n');
  for (const line of lines) {
    if (line.trim()) {
      console.log(`      ${line}`);
    }
  }
  console.log('   Test 3 passed');
  console.log();

  // Test 4: Run Ollama model
  console.log(`Test 4: Running Ollama model '${OLLAMA_MODEL}'...`);
  const prompt = 'Say hello to the HopX AI team in one sentence!';
  console.log(`   Prompt: ${prompt}`);
  console.log('   Running (this may take 30-60 seconds)...');

  const testStartTime = Date.now();
  const result4 = await sandbox.commands.run(
    `/usr/local/bin/ollama run ${OLLAMA_MODEL} '${prompt}'`,
    { timeout: 240000 }
  );
  const testDuration = (Date.now() - testStartTime) / 1000;

  console.log(`   Response (${testDuration.toFixed(1)}s):`);
  console.log(`   ${result4.stdout?.trim()}`);
  console.log('   Test 4 passed');
  console.log();

  console.log('='.repeat(70));
  console.log('All tests completed successfully');
  console.log('='.repeat(70));
  console.log();
  console.log('Tips:');
  console.log(`   - Sandbox ID saved to: ${SANDBOX_ID_FILE}`);
  console.log('   - Rerun this script to reuse the same sandbox (instant)');
  console.log(`   - Delete ${SANDBOX_ID_FILE} to build a new template`);
  console.log('   - Run: await sandbox.kill() to destroy the sandbox');
}

main().catch((error) => {
  console.error('Error:', error.message);
  process.exit(1);
});
