/**
 * 03. File Operations (Complete) - JavaScript/TypeScript SDK
 * Covers: read, write, list, upload, download, exists, remove, mkdir, watch (WebSocket)
 */

import { Sandbox } from '@hopx-ai/sdk';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

const API_KEY = process.env.HOPX_API_KEY || 'your-api-key-here';

async function basicFileOperations() {
  console.log('='.repeat(60));
  console.log('1. BASIC FILE READ/WRITE');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
  
  try {
    // Write text file
    await sandbox.files.write('/workspace/hello.txt', 'Hello, World!');
    console.log('✅ File written: /workspace/hello.txt');
    
    // Read file
    const content = await sandbox.files.read('/workspace/hello.txt');
    console.log(`✅ File content: ${content}`);
    
    // Write binary file
    const binaryData = Buffer.from([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]); // PNG header
    await sandbox.files.write('/workspace/test.png', binaryData);
    console.log('✅ Binary file written: /workspace/test.png');
    
    // Read binary file
    const binaryContent = await sandbox.files.read('/workspace/test.png');
    console.log(`✅ Binary content length: ${binaryContent.length} bytes`);
    
  } finally {
    await sandbox.kill();
  }
  
  console.log();
}

async function listFiles() {
  console.log('='.repeat(60));
  console.log('2. LIST DIRECTORY CONTENTS');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
  
  try {
    // Create some files
    await sandbox.files.write('/workspace/file1.txt', 'Content 1');
    await sandbox.files.write('/workspace/file2.txt', 'Content 2');
    await sandbox.files.mkdir('/workspace/subdir');
    await sandbox.files.write('/workspace/subdir/file3.txt', 'Content 3');
    
    // List directory
    const files = await sandbox.files.list('/workspace');
    console.log(`✅ Files in /workspace: ${files.length}`);
    
    files.forEach(file => {
      const fileType = file.isDir ? '📁' : '📄';
      console.log(`   ${fileType} ${file.name} (${file.sizeKb.toFixed(2)}KB)`);
    });
    
  } finally {
    await sandbox.kill();
  }
  
  console.log();
}

async function uploadDownload() {
  console.log('='.repeat(60));
  console.log('3. UPLOAD/DOWNLOAD FILES');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
  
  try {
    // Create a local file to upload
    const localFile = path.join(os.tmpdir(), 'upload-test.txt');
    fs.writeFileSync(localFile, 'This is a test file for upload!\\nLine 2\\nLine 3\\n');
    
    // Upload file
    await sandbox.files.upload(localFile, '/workspace/uploaded.txt');
    console.log(`✅ File uploaded: ${localFile} → /workspace/uploaded.txt`);
    
    // Verify upload
    const content = await sandbox.files.read('/workspace/uploaded.txt');
    console.log(`✅ Uploaded content:\\n${content}`);
    
    // Download file
    const downloadPath = path.join(os.tmpdir(), 'download-test.txt');
    await sandbox.files.download('/workspace/uploaded.txt', downloadPath);
    console.log(`✅ File downloaded: /workspace/uploaded.txt → ${downloadPath}`);
    
    // Verify download
    const downloadedContent = fs.readFileSync(downloadPath, 'utf8');
    console.log(`✅ Downloaded content matches: ${content === downloadedContent}`);
    
    // Cleanup local files
    fs.unlinkSync(localFile);
    fs.unlinkSync(downloadPath);
    
  } finally {
    await sandbox.kill();
  }
  
  console.log();
}

async function fileWatching() {
  console.log('='.repeat(60));
  console.log('4. FILE WATCHING (WEBSOCKET)');
  console.log('='.repeat(60));
  
  const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
  
  try {
    console.log('✅ Starting file watcher...');
    
    // Start watching and making changes concurrently
    let eventCount = 0;
    
    const watchPromise = (async () => {
      for await (const event of sandbox.files.watch('/workspace')) {
        if (event.type === 'change') {
          console.log(`   📂 ${event.event.toUpperCase()}: ${event.path}`);
          eventCount++;
          if (eventCount >= 5) break;
        }
      }
    })();
    
    const changesPromise = (async () => {
      await new Promise(r => setTimeout(r, 1000));
      
      await sandbox.files.write('/workspace/test1.txt', 'Content 1');
      await new Promise(r => setTimeout(r, 500));
      
      await sandbox.files.write('/workspace/test2.txt', 'Content 2');
      await new Promise(r => setTimeout(r, 500));
      
      await sandbox.files.remove('/workspace/test1.txt');
      await new Promise(r => setTimeout(r, 500));
    })();
    
    await Promise.race([watchPromise, changesPromise.then(() => watchPromise)]);
    
    console.log('✅ File watching complete!');
    
  } finally {
    await sandbox.kill();
  }
  
  console.log();
}

async function main() {
  console.log('\\n' + '='.repeat(60));
  console.log('JAVASCRIPT/TYPESCRIPT SDK - FILE OPERATIONS');
  console.log('='.repeat(60) + '\\n');
  
  await basicFileOperations();
  await listFiles();
  await uploadDownload();
  await fileWatching();
  
  console.log('='.repeat(60));
  console.log('✅ ALL FILE OPERATIONS DEMONSTRATED!');
  console.log('='.repeat(60) + '\\n');
}

main().catch(console.error);
