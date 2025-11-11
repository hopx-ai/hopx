/**
 * 07. Desktop Automation - JavaScript/TypeScript SDK
 * Covers: mouse, keyboard, clipboard, screenshots, VNC, etc.
 */

import { Sandbox } from '@hopx-ai/sdk';

const API_KEY = process.env.HOPX_API_KEY || 'your-api-key-here';

async function desktopOperations() {
  const sandbox = await Sandbox.create({ template: 'desktop', apiKey: API_KEY });
  try {
    // Mouse operations
    await sandbox.desktop.mouseClick({ x: 500, y: 300, button: 'left' });
    console.log('✅ Mouse click');
    
    // Keyboard
    await sandbox.desktop.keyboardType('Hello, World!');
    console.log('✅ Keyboard typed');
    
    // Clipboard
    await sandbox.desktop.clipboardSet('Test content');
    const content = await sandbox.desktop.clipboardGet();
    console.log(`✅ Clipboard: ${content}`);
    
    // Screenshot
    const screenshot = await sandbox.desktop.screenshot();
    console.log(`✅ Screenshot: ${screenshot.length} bytes`);
    
  } catch (error: any) {
    console.log('⚠️  Desktop features require "desktop" template');
  } finally {
    await sandbox.kill();
  }
}

async function main() {
  console.log('\nJAVASCRIPT/TYPESCRIPT SDK - DESKTOP AUTOMATION\n');
  await desktopOperations();
  console.log('✅ DESKTOP OPERATIONS DEMONSTRATED!\n');
}

main().catch(console.error);
