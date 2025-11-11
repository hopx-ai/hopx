/**
 * 10. Best Practices - JavaScript/TypeScript SDK
 * Production-ready patterns
 */

import { Sandbox } from '@hopx-ai/sdk';

const API_KEY = process.env.HOPX_API_KEY || 'your-api-key-here';

async function useTryFinally() {
  console.log('ALWAYS USE TRY/FINALLY FOR CLEANUP');
  
  const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
  try {
    const result = await sandbox.runCode('print("Hello")');
    console.log('✅ Output:', result.stdout.trim());
  } finally {
    await sandbox.kill();
    console.log('✅ Sandbox cleaned up');
  }
}

async function handleErrorsProperly() {
  console.log('PROPER ERROR HANDLING');
  
  try {
    const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
    try {
      await sandbox.files.read('/non-existent.txt');
    } catch (error: any) {
      console.log(`✅ Caught error: ${error.constructor.name}`);
      console.log(`   Request ID: ${error.requestId}`);
    } finally {
      await sandbox.kill();
    }
  } catch (error: any) {
    console.log(`❌ Failed: ${error.message}`);
  }
}

async function securityBestPractices() {
  console.log('SECURITY BEST PRACTICES');
  
  const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
  try {
    // ✅ GOOD: Pass secrets via env, not in code
    await sandbox.runCode(
      'import os; api_key = os.getenv("API_KEY")',
      { env: { API_KEY: 'sk-secret-123' } }
    );
    console.log('✅ Secrets passed via environment variables');
    
    // ✅ GOOD: Set timeouts
    await sandbox.runCode('print("Quick task")', { timeoutSeconds: 5 });
    console.log('✅ Timeout set for execution');
    
  } finally {
    await sandbox.kill();
  }
}

async function performanceOptimization() {
  console.log('PERFORMANCE OPTIMIZATION');
  
  const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
  try {
    // ✅ Set env vars once
    await sandbox.env.setAll({
      DATABASE_URL: 'postgres://...',
      API_KEY: 'sk-...'
    });
    console.log('✅ Environment variables set once');
    
    // Now available in all executions
    for (let i = 0; i < 3; i++) {
      await sandbox.runCode('import os; db = os.getenv("DATABASE_URL")');
    }
    console.log('✅ Reused env vars across multiple executions');
    
    // ✅ Parallel execution with Promise.all
    const [r1, r2, r3] = await Promise.all([
      sandbox.runCode('print(1)'),
      sandbox.runCode('print(2)'),
      sandbox.runCode('print(3)')
    ]);
    console.log('✅ Parallel execution for better performance');
    
  } finally {
    await sandbox.kill();
  }
}

async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('JAVASCRIPT/TYPESCRIPT SDK - BEST PRACTICES');
  console.log('='.repeat(60) + '\n');
  
  await useTryFinally();
  console.log();
  
  await handleErrorsProperly();
  console.log();
  
  await securityBestPractices();
  console.log();
  
  await performanceOptimization();
  console.log();
  
  console.log('='.repeat(60));
  console.log('✅ ALL BEST PRACTICES DEMONSTRATED!');
  console.log('='.repeat(60));
  console.log('\nKEY TAKEAWAYS:');
  console.log('1. Always use try/finally for cleanup');
  console.log('2. Handle errors with specific error types');
  console.log('3. Never hardcode secrets - use environment variables');
  console.log('4. Set execution timeouts');
  console.log('5. Use Promise.all for parallel operations');
  console.log('6. Set env vars once, reuse across executions');
  console.log('7. Monitor metrics and log operations');
  console.log('8. Validate inputs before execution');
  console.log('9. Request appropriate resources');
  console.log('10. Test error scenarios\n');
}

main().catch(console.error);
