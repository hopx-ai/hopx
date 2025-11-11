/**
 * Private Registry Authentication Examples
 * 
 * Shows how to use private Docker registries with templates
 */

import { Template, waitForPort } from '../src/index.js';

// =============================================================================
// Example 1: GitHub Container Registry
// =============================================================================

async function example1_githubRegistry() {
  console.log('Example 1: GitHub Container Registry\n');
  
  const template = new Template()
    .fromImage('ghcr.io/mycompany/api-server:v2.1.0', {
      username: process.env.GITHUB_USER!,
      password: process.env.GITHUB_TOKEN! // Personal access token
    })
    .setEnv('PORT', '8080')
    .setStartCmd('node dist/server.js', waitForPort(8080));
  
  const result = await Template.build(template, {
    alias: 'api-server-private',
    apiKey: process.env.HOPX_API_KEY!
  });
  
  console.log(`✅ Template built: ${result.templateID}\n`);
}

// =============================================================================
// Example 2: GitLab Container Registry
// =============================================================================

async function example2_gitlabRegistry() {
  console.log('Example 2: GitLab Container Registry\n');
  
  const template = new Template()
    .fromImage('registry.gitlab.com/mygroup/myproject/app:latest', {
      username: process.env.GITLAB_USER!,
      password: process.env.GITLAB_TOKEN! // Deploy token or personal access token
    })
    .setStartCmd('python app.py', waitForPort(5000));
  
  const result = await Template.build(template, {
    alias: 'gitlab-app',
    apiKey: process.env.HOPX_API_KEY!
  });
  
  console.log(`✅ Template built: ${result.templateID}\n`);
}

// =============================================================================
// Example 3: GCP Container Registry
// =============================================================================

async function example3_gcpRegistry() {
  console.log('Example 3: GCP Container Registry\n');
  
  // From file path
  const template1 = new Template()
    .fromGCPRegistry('gcr.io/my-project/ml-model:v1', {
      serviceAccountJSON: './gcp-service-account.json'
    })
    .setEnv('MODEL_PATH', '/models/latest')
    .setStartCmd('python serve.py', waitForPort(8080));
  
  // From object
  const template2 = new Template()
    .fromGCPRegistry('us.gcr.io/my-project/app:latest', {
      serviceAccountJSON: {
        type: 'service_account',
        project_id: 'my-project',
        private_key_id: '...',
        private_key: '-----BEGIN PRIVATE KEY-----\n...',
        client_email: 'service@my-project.iam.gserviceaccount.com'
      }
    })
    .setStartCmd('./app', waitForPort(3000));
  
  console.log('✅ GCP templates configured\n');
}

// =============================================================================
// Example 4: AWS Elastic Container Registry (ECR)
// =============================================================================

async function example4_awsECR() {
  console.log('Example 4: AWS ECR\n');
  
  const template = new Template()
    .fromAWSRegistry(
      '123456789.dkr.ecr.us-west-1.amazonaws.com/webapp:v3.0',
      {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
        region: 'us-west-1'
      }
    )
    .setStartCmd('./webapp', waitForPort(8080));
  
  const result = await Template.build(template, {
    alias: 'aws-webapp',
    apiKey: process.env.HOPX_API_KEY!
  });
  
  console.log(`✅ Template built: ${result.templateID}\n`);
}

// =============================================================================
// Example 5: Private Docker Hub
// =============================================================================

async function example5_privateDockerHub() {
  console.log('Example 5: Private Docker Hub\n');
  
  const template = new Template()
    .fromImage('myusername/private-image:latest', {
      username: process.env.DOCKER_HUB_USER!,
      password: process.env.DOCKER_HUB_TOKEN! // Access token
    })
    .setStartCmd('npm start', waitForPort(3000));
  
  const result = await Template.build(template, {
    alias: 'dockerhub-app',
    apiKey: process.env.HOPX_API_KEY!
  });
  
  console.log(`✅ Template built: ${result.templateID}\n`);
}

// =============================================================================
// Example 6: Self-Hosted Registry
// =============================================================================

async function example6_selfHostedRegistry() {
  console.log('Example 6: Self-Hosted Registry\n');
  
  const template = new Template()
    .fromImage('registry.mycompany.com:5000/internal/app:latest', {
      username: 'deploy',
      password: process.env.REGISTRY_PASSWORD!
    })
    .setStartCmd('./app', waitForPort(8080));
  
  const result = await Template.build(template, {
    alias: 'internal-app',
    apiKey: process.env.HOPX_API_KEY!
  });
  
  console.log(`✅ Template built: ${result.templateID}\n`);
}

// =============================================================================
// Run Examples
// =============================================================================

async function main() {
  try {
    // Uncomment the examples you want to run:
    
    // await example1_githubRegistry();
    // await example2_gitlabRegistry();
    // await example3_gcpRegistry();
    // await example4_awsECR();
    // await example5_privateDockerHub();
    // await example6_selfHostedRegistry();
    
    console.log('\n✨ Done! Uncomment examples to run them.\n');
  } catch (error: any) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

export {
  example1_githubRegistry,
  example2_gitlabRegistry,
  example3_gcpRegistry,
  example4_awsECR,
  example5_privateDockerHub,
  example6_selfHostedRegistry
};

