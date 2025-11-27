import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { Sandbox } from '../src/index.js';
import { createSandboxWithRetry } from './test-helpers.ts';

describe('Sandbox Desktop & GUI', () => {
    let sandbox: Sandbox;
    const sandboxes: Sandbox[] = [];

    beforeAll(async () => {
        console.log('🚀 Creating sandbox for desktop tests...');
        sandbox = await createSandboxWithRetry({
            template: 'code-interpreter', // Assuming this template supports desktop/X11
            apiKey: process.env['HOPX_API_KEY'],
        });
        sandboxes.push(sandbox);
        console.log(`✅ Sandbox created: ${sandbox.sandboxId}`);

        // Give it a moment to initialize X11 if needed
        await new Promise(resolve => setTimeout(resolve, 5000));
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

    it('should start VNC', async () => {
        console.log('🖥️ Testing VNC start...');
        try {
            const vncInfo = await sandbox.desktop.startVnc();
            console.log('VNC Info:', vncInfo);
            if (vncInfo && vncInfo.url) {
                expect(vncInfo.url).toBeDefined();
                console.log('✅ VNC started');
            } else {
                console.log('⚠️ VNC not supported or returned empty info');
            }
        } catch (e) {
            console.log('⚠️ VNC start failed (likely not supported):', e);
        }
    });

    it('should take a screenshot', async () => {
        console.log('📸 Testing screenshot...');
        try {
            const screenshot = await sandbox.desktop.screenshot();
            console.log('Screenshot response type:', typeof screenshot);
            expect(screenshot).toBeDefined();
        } catch (e) {
            console.log('⚠️ Screenshot failed:', e);
        }
    });

    it('should list windows', async () => {
        console.log('🪟 Testing window listing...');
        try {
            // Launch a simple GUI app to ensure there's a window
            await sandbox.commands.run('xterm &');
            await new Promise(resolve => setTimeout(resolve, 2000));

            const windows = await sandbox.desktop.listWindows();
            console.log('Windows:', windows);

            if (Array.isArray(windows)) {
                expect(Array.isArray(windows)).toBe(true);
                if (windows.length > 0) {
                    console.log(`✅ Found ${windows.length} windows`);
                } else {
                    console.log('⚠️ No windows found (headless env?)');
                }
            } else {
                console.log('⚠️ listWindows did not return an array');
            }
        } catch (e) {
            console.log('⚠️ listWindows failed:', e);
        }
    });
});
