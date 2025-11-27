import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { Sandbox } from '../src/index.ts';
import { retryWithBackoff, delayForRateLimit, createSandboxWithRetry } from './test-helpers.ts';

describe('Configuration', () => {
  it('should have a valid API key', async () => {
    console.log('🔑 Verifying API key...');
    const apiKey = process.env['HOPX_API_KEY'];
    expect(apiKey).toBeDefined();

    // Try to list templates (requires valid API key)
    // Use retry with backoff to handle potential rate limiting
    const templates = await retryWithBackoff(async () => {
      return await Sandbox.listTemplates({ apiKey });
    });

    expect(Array.isArray(templates)).toBe(true);
    console.log('✅ API Key is valid');
  });
});

describe('SDK Basic Actions', () => {
  let sandbox: Sandbox;
  const sandboxes: Sandbox[] = [];

  // Increase timeout for sandbox creation
  const TIMEOUT = 30000; // 30 seconds

  beforeAll(async () => {
    // Add a small delay to stagger sandbox creation when running all tests
    await delayForRateLimit(1000);

    console.log('🚀 Creating sandbox for tests...');
    console.log('📋 API Key present:', !!process.env['HOPX_API_KEY']);
    console.log('📋 API Key length:', process.env['HOPX_API_KEY']?.length);

    try {
      // Create sandbox WITHOUT envVars to avoid 401 during creation
      // sandbox = await Sandbox.create({
      sandbox = await createSandboxWithRetry({
        template: 'code-interpreter',
        apiKey: process.env['HOPX_API_KEY'],
        // envVars removed - will be set after delay
      });
      sandboxes.push(sandbox);
      console.log(`✅ Sandbox created: ${sandbox.sandboxId}`);

      // Give the sandbox a moment to fully initialize
      // This prevents intermittent 401 errors when the JWT token isn't fully ready
      console.log('⏳ Waiting for sandbox to be fully ready...');
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Now set environment variables after token is ready
      console.log('🔐 Setting environment variables...');
      await sandbox.env.set('TEST_ENV_VAR', 'initial_value');
      console.log('✅ Environment variables set');
    } catch (error: any) {
      console.error('❌ Failed to create sandbox:');
      console.error('   Error type:', error.constructor.name);
      console.error('   Error message:', error.message);
      console.error('   Status code:', error.statusCode);
      console.error('   Request ID:', error.requestId);
      console.error('   Full error:', JSON.stringify(error, null, 2));
      throw error; // Re-throw to fail the test
    }
  }, 300000);

  afterAll(async () => {
    console.log(`🧹 Cleaning up ${sandboxes.length} sandboxes...`);
    for (const sb of sandboxes) {
      if (sb.sandboxId) {
        try {
          await sb.kill();
          console.log(`✅ Sandbox ${sb.sandboxId} deleted`);
        } catch (e: any) {
          if (e.statusCode === 404) {
            console.log(`⚠️ Sandbox ${sb.sandboxId} already deleted or not found`);
          } else {
            console.error(`❌ Failed to delete sandbox ${sb.sandboxId}:`, e);
          }
        }
      }
    }
  });


  it('should execute code (Python)', async () => {
    console.log('📝 Testing code execution...');
    const result = await sandbox.runCode('print("Hello from Test!")', {
      language: 'python',
      env: { GREETING: 'Hi' },
    });
    console.log(`✅ Sandbox check Python run code: ${sandbox.sandboxId}`);
    expect(result.stdout).toContain('Hello from Test!');
    expect(result.execution_time).toBeDefined();
  }, 30000);

  it('should perform file operations', async () => {
    console.log('📁 Testing file operations...');
    const filePath = '/workspace/test-file.txt';
    const fileContent = 'Hello, Test Files!';

    // Write
    await sandbox.files.write(filePath, fileContent);

    // Read
    const content = await sandbox.files.read(filePath);
    expect(content).toBe(fileContent);

    // List
    const files = await sandbox.files.list('/workspace');
    const found = files.find(f => f.name === 'test-file.txt');
    expect(found).toBeDefined();
  });

  it('should run shell commands', async () => {
    console.log('💻 Testing shell commands...');
    const result = await sandbox.commands.run('echo "Hello from shell!"');
    console.log(`✅ Sandbox check run shell commands: ${sandbox.sandboxId}`);
    expect(result.stdout).toContain('Hello from shell!');
  });

  it('should manage environment variables', async () => {
    console.log('🔐 Testing environment variables...');

    // Check initial env var
    const initialVal = await sandbox.commands.run('echo $TEST_ENV_VAR');
    console.log(`✅ Sandbox check env var: ${sandbox.sandboxId}`);
    expect(initialVal.stdout.trim()).toBe('initial_value');

    // Set new var
    await sandbox.env.set('DYNAMIC_VAR', 'dynamic_value');
    console.log(`✅ Sandbox set env var: ${sandbox.sandboxId}`);

    // Get var using SDK
    const val = await sandbox.env.get('DYNAMIC_VAR');
    console.log(`✅ Sandbox get env var: ${sandbox.sandboxId}`);
    expect(val).toBe('dynamic_value');

    // Verify in shell
    const shellVal = await sandbox.commands.run('echo $DYNAMIC_VAR');
    console.log(`✅ Sandbox verify env var in shell: ${sandbox.sandboxId}`);
    expect(shellVal.stdout.trim()).toBe('dynamic_value');
  });

  it('should retrieve metrics', async () => {
    console.log('📊 Testing metrics...');
    const metrics = await sandbox.getMetricsSnapshot();
    console.log(`✅ Sandbox metrics: ${sandbox.sandboxId}`);
    expect(metrics.total_executions).toBeGreaterThanOrEqual(0);
  });

  it('should retrieve cache stats', async () => {
    console.log('💾 Testing cache stats...');
    const stats = await sandbox.cache.stats();
    console.log(`✅ Sandbox cache stats: ${sandbox.sandboxId}`);
    expect(stats.cache).toBeDefined();
  });
});

