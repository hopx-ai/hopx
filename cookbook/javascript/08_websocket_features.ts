/**
 * 08. WebSocket Features - JavaScript/TypeScript SDK
 * Covers: terminal, streaming, file watching
 */

import { Sandbox } from '@hopx-ai/sdk';

const API_KEY = process.env.HOPX_API_KEY || 'your-api-key-here';

async function interactiveTerminal() {
  const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
  try {
    console.log('✅ Connecting to terminal...');
    
    const terminal = await sandbox.terminal.connect();
    
    await sandbox.terminal.sendInput(terminal, 'echo "Hello from terminal!"\n');
    await new Promise(r => setTimeout(r, 500));
    
    let count = 0;
    for await (const message of sandbox.terminal.iterOutput(terminal)) {
      if (message.type === 'output') {
        process.stdout.write(message.data);
      }
      if (++count >= 10) break;
    }
    
    console.log('\n✅ Terminal session complete');
  } finally {
    await sandbox.kill();
  }
}

async function codeStreaming() {
  const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
  try {
    console.log('✅ Streaming code execution:');
    
    for await (const message of sandbox.runCodeStream('import time\nfor i in range(3):\n    print(f"Step {i+1}")\n    time.sleep(1)')) {
      if (message.type === 'stdout') {
        process.stdout.write(`   ${message.data}`);
      } else if (message.type === 'complete') {
        console.log('✅ Streaming complete!');
      }
    }
  } finally {
    await sandbox.kill();
  }
}

async function main() {
  console.log('\nJAVASCRIPT/TYPESCRIPT SDK - WEBSOCKET FEATURES\n');
  await interactiveTerminal();
  await codeStreaming();
  console.log('✅ ALL WEBSOCKET FEATURES DEMONSTRATED!\n');
}

main().catch(console.error);
