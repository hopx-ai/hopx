/**
 * Template Building Cookbook - TypeScript/JavaScript
 * 
 * Examples of building custom templates with the Hopx SDK
 */

const { Template, waitForPort, waitForURL } = require('@hopx-ai/sdk');

// =============================================================================
// Example 1: Simple Python Web App
// =============================================================================

async function example1_pythonWebApp() {
  console.log('Example 1: Python Flask Web App\n');
  
  const template = new Template()
    .fromPythonImage('3.11')
    .copy('app/', '/app/')
    .pipInstall()  // Installs from requirements.txt
    .setEnv('FLASK_APP', 'app.py')
    .setEnv('FLASK_ENV', 'production')
    .setStartCmd('python /app/app.py', waitForPort(5000));
  
  const result = await Template.build(template, {
    alias: 'my-flask-app',
    apiKey: process.env.HOPX_API_KEY,
    cpu: 2,
    memory: 2048,
    diskGB: 10,
    onLog: (log) => console.log(`[${log.level}] ${log.message}`),
    onProgress: (progress) => console.log(`Progress: ${progress}%`)
  });
  
  console.log(`✅ Template built: ${result.templateID}`);
  
  // Create VM from template
  const vm = await result.createVM({
    alias: 'flask-instance-1'
  });
  
  console.log(`✅ VM created: ${vm.ip}`);
  
  // Cleanup
  await vm.delete();
}

// =============================================================================
// Example 2: Node.js API Server
// =============================================================================

async function example2_nodejsAPI() {
  console.log('Example 2: Node.js Express API\n');
  
  const template = new Template()
    .fromNodeImage('18-alpine')
    .copy('package.json', '/app/package.json')
    .copy('package-lock.json', '/app/package-lock.json')
    .copy('src/', '/app/src/')
    .setWorkdir('/app')
    .npmInstall()  // Installs from package.json
    .setEnv('NODE_ENV', 'production')
    .setEnv('PORT', '3000')
    .setStartCmd('node src/server.js', waitForPort(3000));
  
  const result = await Template.build(template, {
    alias: 'express-api',
    apiKey: process.env.HOPX_API_KEY,
    cpu: 4,
    memory: 4096,
    diskGB: 20
  });
  
  console.log(`✅ Template: ${result.templateID}`);
  
  // Create multiple instances
  const instances = await Promise.all([
    result.createVM({ alias: 'api-1' }),
    result.createVM({ alias: 'api-2' }),
    result.createVM({ alias: 'api-3' })
  ]);
  
  console.log(`✅ Created ${instances.length} instances`);
}

// =============================================================================
// Example 3: Full Stack App (Python + Redis)
// =============================================================================

async function example3_fullStack() {
  console.log('Example 3: Full Stack with Redis\n');
  
  const template = new Template()
    .fromUbuntuImage('22.04')
    .aptInstall(['python3-pip', 'redis-server'])
    .copy('backend/', '/app/')
    .pipInstall(['flask', 'redis', 'celery'])
    .setEnv('REDIS_URL', 'redis://localhost:6379')
    .setEnv('FLASK_APP', 'app.py')
    .setWorkdir('/app')
    .setStartCmd(
      'redis-server --daemonize yes && python app.py',
      waitForPort(8000)
    );
  
  const result = await Template.build(template, {
    alias: 'fullstack-app',
    apiKey: process.env.HOPX_API_KEY,
    cpu: 4,
    memory: 4096,
    diskGB: 20
  });
  
  console.log(`✅ Full stack template ready`);
}

// =============================================================================
// Example 4: Database Server (PostgreSQL)
// =============================================================================

async function example4_database() {
  console.log('Example 4: PostgreSQL Database\n');
  
  const template = new Template()
    .fromUbuntuImage('22.04')
    .aptInstall(['postgresql', 'postgresql-contrib'])
    .setEnv('POSTGRES_PASSWORD', 'secret')
    .setEnv('POSTGRES_DB', 'myapp')
    .setEnv('POSTGRES_USER', 'admin')
    .setStartCmd(
      'service postgresql start',
      waitForPort(5432)
    );
  
  const result = await Template.build(template, {
    alias: 'postgres-server',
    apiKey: process.env.HOPX_API_KEY,
    cpu: 2,
    memory: 4096,
    diskGB: 50
  });
  
  console.log(`✅ Database template: ${result.templateID}`);
}

// =============================================================================
// Example 5: ML/AI Workload
// =============================================================================

async function example5_mlWorkload() {
  console.log('Example 5: ML/AI with TensorFlow\n');
  
  const template = new Template()
    .fromPythonImage('3.11')
    .aptInstall(['git', 'curl', 'wget'])
    .pipInstall(['tensorflow', 'numpy', 'pandas', 'jupyter'])
    .copy('notebooks/', '/notebooks/')
    .copy('models/', '/models/')
    .setEnv('JUPYTER_TOKEN', 'secret123')
    .setWorkdir('/notebooks')
    .setStartCmd(
      'jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root',
      waitForPort(8888)
    );
  
  const result = await Template.build(template, {
    alias: 'ml-workload',
    apiKey: process.env.HOPX_API_KEY,
    cpu: 8,
    memory: 16384,
    diskGB: 100
  });
  
  console.log(`✅ ML template ready`);
}

// =============================================================================
// Example 6: Development Environment
// =============================================================================

async function example6_devEnvironment() {
  console.log('Example 6: Development Environment\n');
  
  const template = new Template()
    .fromUbuntuImage('22.04')
    .aptInstall(['git', 'curl', 'wget', 'vim', 'build-essential'])
    .runCmd('curl -fsSL https://deb.nodesource.com/setup_18.x | bash -')
    .aptInstall(['nodejs', 'python3-pip'])
    .pipInstall(['ipython', 'pytest', 'black'])
    .npmInstall(['typescript', 'eslint', 'prettier'])
    .setEnv('EDITOR', 'vim')
    .setWorkdir('/workspace');
  
  const result = await Template.build(template, {
    alias: 'dev-environment',
    apiKey: process.env.HOPX_API_KEY,
    cpu: 4,
    memory: 8192,
    diskGB: 50
  });
  
  console.log(`✅ Dev environment template ready`);
}

// =============================================================================
// Example 7: Git Clone + Build
// =============================================================================

async function example7_gitClone() {
  console.log('Example 7: Clone GitHub Repo & Build\n');
  
  const template = new Template()
    .fromNodeImage('18')
    .aptInstall(['git'])
    .gitClone('https://github.com/example/repo.git', '/app')
    .setWorkdir('/app')
    .npmInstall()
    .runCmd('npm run build')
    .setEnv('NODE_ENV', 'production')
    .setStartCmd('npm start', waitForPort(3000));
  
  const result = await Template.build(template, {
    alias: 'github-app',
    apiKey: process.env.HOPX_API_KEY
  });
  
  console.log(`✅ Template from GitHub: ${result.templateID}`);
}

// =============================================================================
// Example 8: Multi-Language Environment
// =============================================================================

async function example8_multiLanguage() {
  console.log('Example 8: Multi-Language (Python + Node + Go)\n');
  
  const template = new Template()
    .fromUbuntuImage('22.04')
    // Python
    .aptInstall(['python3-pip'])
    .pipInstall(['flask', 'requests'])
    // Node.js
    .runCmd('curl -fsSL https://deb.nodesource.com/setup_18.x | bash -')
    .aptInstall(['nodejs'])
    // Go
    .runCmd('wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz')
    .runCmd('tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz')
    .setEnv('PATH', '/usr/local/go/bin:$PATH')
    .setWorkdir('/workspace');
  
  const result = await Template.build(template, {
    alias: 'multi-lang-env',
    apiKey: process.env.HOPX_API_KEY,
    cpu: 4,
    memory: 8192,
    diskGB: 30
  });
  
  console.log(`✅ Multi-language environment ready`);
}

// =============================================================================
// Example 9: Caching Strategy
// =============================================================================

async function example9_cachingStrategy() {
  console.log('Example 9: Efficient Caching\n');
  
  // First build - installs dependencies
  const template1 = new Template()
    .fromPythonImage('3.11')
    .pipInstall(['flask', 'gunicorn', 'redis', 'celery'])
    .copy('app/', '/app/')
    .skipCache()  // Force rebuild
    .setStartCmd('gunicorn app:app', waitForPort(8000));
  
  const result1 = await Template.build(template1, {
    alias: 'app-v1',
    apiKey: process.env.HOPX_API_KEY
  });
  
  console.log(`✅ V1 built: ${result1.templateID}`);
  
  // Second build - will use cache for dependencies
  const template2 = new Template()
    .fromPythonImage('3.11')
    .pipInstall(['flask', 'gunicorn', 'redis', 'celery'])  // Cached!
    .copy('app/', '/app/')  // New files
    .setStartCmd('gunicorn app:app', waitForPort(8000));
  
  const result2 = await Template.build(template2, {
    alias: 'app-v2',
    apiKey: process.env.HOPX_API_KEY
  });
  
  console.log(`✅ V2 built (with cache): ${result2.templateID}`);
}

// =============================================================================
// Example 10: Health Check Patterns
// =============================================================================

async function example10_healthChecks() {
  console.log('Example 10: Different Health Check Types\n');
  
  // Port-based health check
  const template1 = new Template()
    .fromPythonImage('3.11')
    .pipInstall(['flask'])
    .setStartCmd('flask run', waitForPort(5000));
  
  // URL-based health check
  const template2 = new Template()
    .fromNodeImage('18')
    .npmInstall(['express'])
    .setStartCmd('node server.js', waitForURL('http://localhost:3000/health'));
  
  // File-based health check
  const template3 = new Template()
    .fromUbuntuImage('22.04')
    .runCmd('touch /tmp/ready')
    .setStartCmd('/bin/bash', waitForFile('/tmp/ready'));
  
  // Process-based health check
  const template4 = new Template()
    .fromUbuntuImage('22.04')
    .aptInstall(['nginx'])
    .setStartCmd('nginx -g "daemon off;"', waitForProcess('nginx'));
  
  // Command-based health check
  const template5 = new Template()
    .fromUbuntuImage('22.04')
    .aptInstall(['postgresql'])
    .setStartCmd('service postgresql start', waitForCommand('pg_isready'));
  
  console.log('✅ 5 different health check patterns defined');
}

// =============================================================================
// Run Examples
// =============================================================================

async function runAll() {
  try {
    await example1_pythonWebApp();
    await example2_nodejsAPI();
    await example3_fullStack();
    await example4_database();
    await example5_mlWorkload();
    await example6_devEnvironment();
    await example7_gitClone();
    await example8_multiLanguage();
    await example9_cachingStrategy();
    await example10_healthChecks();
    
    console.log('\n✨ All examples completed!');
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

// Run if called directly
if (require.main === module) {
  runAll();
}

module.exports = {
  example1_pythonWebApp,
  example2_nodejsAPI,
  example3_fullStack,
  example4_database,
  example5_mlWorkload,
  example6_devEnvironment,
  example7_gitClone,
  example8_multiLanguage,
  example9_cachingStrategy,
  example10_healthChecks
};

