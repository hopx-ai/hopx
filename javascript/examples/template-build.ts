/**
 * Template Building Example
 *
 * Shows how to build a custom template and create sandboxes from it.
 */

import { Template, waitForPort, Sandbox } from '../src/index.js';

async function main() {
  console.log('Template Building Example\n');

  // Generate unique template name
  const templateName = `example-python-app-${Date.now()}`;
  console.log(`Template name: ${templateName}\n`);

  // 1. Define a Python web app template
  console.log('1. Defining template...');
  const template = new Template()
    .fromPythonImage('3.11')
    .runCmd('mkdir -p /app')
    .setWorkdir('/app')
    .runCmd(`cat > main.py << 'EOF'
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

PORT = int(os.environ.get("PORT", 8000))

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Hello from Hopx!</h1>")

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), SimpleHandler)
    print(f"Server running on port {PORT}")
    server.serve_forever()
EOF`)
    .setEnv('PORT', '8000')
    .setStartCmd('python main.py', waitForPort(8000));

  console.log(`   Template defined with ${template.getSteps().length} build steps`);

  // 2. Build the template
  console.log('\n2. Building template...');
  const result = await Template.build(template, {
    name: templateName,
    apiKey: process.env.HOPX_API_KEY || '',
    baseURL: process.env.HOPX_BASE_URL || 'https://api.hopx.dev',
    cpu: 2,
    memory: 2048,
    diskGB: 10,
    contextPath: process.cwd(),
    onLog: (log) => {
      const level = log.level || 'INFO';
      const message = log.message || '';
      console.log(`   [${level}] ${message}`);
    },
    onProgress: (progress) => {
      console.log(`   Progress: ${progress}%`);
    },
  });

  console.log('\n   Template built successfully');
  console.log(`   Template ID: ${result.templateID}`);
  console.log(`   Build ID: ${result.buildID}`);
  console.log(`   Duration: ${result.duration}ms`);

  // 3. Create sandbox from template
  console.log('\n3. Creating sandbox from template...');
  const sandbox = await Sandbox.create({
    template: templateName,  // Use the template we just built
    envVars: {
      DATABASE_URL: 'postgresql://localhost/mydb',
      API_KEY: 'secret123',
    },
  });

  console.log('   Sandbox created');
  console.log(`   Sandbox ID: ${sandbox.sandboxId}`);

  // 4. Test the sandbox
  console.log('\n4. Testing sandbox...');
  const result2 = await sandbox.runCode('print("Template is working!")', { language: 'python' });
  console.log(`   Output: ${result2.stdout?.trim()}`);

  // 5. Get preview URL
  const previewUrl = await sandbox.getPreviewUrl(8000);
  console.log(`   Preview URL: ${previewUrl}`);

  // 6. Cleanup
  console.log('\n5. Cleaning up...');
  await sandbox.kill();
  console.log('   Sandbox killed');

  console.log('\nDone');
}

// Run example
main().catch(error => {
  console.error('Error:', error.message);
  process.exit(1);
});
