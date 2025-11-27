import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { Sandbox } from '../src/index.js';
import { createSandboxWithRetry } from './test-helpers.ts';

describe('Sandbox Terminal', () => {
    let sandbox: Sandbox;
    const sandboxes: Sandbox[] = [];

    beforeAll(async () => {
        console.log('🚀 Creating sandbox for terminal tests...');
        console.log('📋 API Key present:', !!process.env['HOPX_API_KEY']);

        try {
            sandbox = await createSandboxWithRetry({
                template: 'code-interpreter',
                apiKey: process.env['HOPX_API_KEY'],
            });
            sandboxes.push(sandbox);
            console.log(`✅ Sandbox created: ${sandbox.sandboxId}`);

            // Give the sandbox a moment to fully initialize
            console.log('⏳ Waiting for sandbox to be fully ready...');
            await new Promise(resolve => setTimeout(resolve, 2000));
        } catch (error: any) {
            console.error('❌ Failed to create sandbox for terminal tests:');
            console.error('   Error type:', error.constructor.name);
            console.error('   Error message:', error.message);
            console.error('   Status code:', error.statusCode);
            console.error('   Request ID:', error.requestId);
            throw error;
        }
    }, 300000);

    afterAll(async () => {
        console.log(`🧹 Cleaning up ${sandboxes.length} sandboxes...`);
        for (const sb of sandboxes) {
            try {
                await sb.kill();
            } catch (e) {
                console.error(`❌ Failed to delete sandbox ${sb.sandboxId}:`, e);
            }
        }
    });

    it('should connect to terminal and echo input', async () => {
        console.log('💻 Testing terminal connection...');

        try {
            const ws = await sandbox.terminal.connect();
            expect(ws).toBeDefined();

            // Listen for output
            const outputPromise = new Promise<string>((resolve) => {
                const iterator = sandbox.terminal.output(ws);
                (async () => {
                    for await (const msg of iterator) {
                        if (msg.type === 'output' && msg.data.includes('hello terminal')) {
                            resolve(msg.data);
                            break;
                        }
                    }
                })();
            });

            // Send input
            // Give it a moment to connect
            await new Promise(resolve => setTimeout(resolve, 1000));
            console.log('⌨️ Sending input...');
            sandbox.terminal.sendInput(ws, 'echo "hello terminal"\r');

            // Wait for response
            const result = await Promise.race([
                outputPromise,
                new Promise<string>((_, reject) => setTimeout(() => reject(new Error('Timeout')), 10000))
            ]);

            expect(result).toContain('hello terminal');
            console.log('✅ Terminal echoed input');

            ws.close();
        } catch (error: any) {
            console.error('❌ Terminal connection failed:');
            console.error('   Error type:', error.constructor.name);
            console.error('   Error message:', error.message);
            console.error('   Sandbox ID:', sandbox.sandboxId);
            throw error;
        }
    });
});
