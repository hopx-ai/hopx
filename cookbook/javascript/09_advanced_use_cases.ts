/**
 * 09. Advanced Use Cases - JavaScript/TypeScript SDK
 * Production-ready examples
 */

import { Sandbox } from '@hopx-ai/sdk';

const API_KEY = process.env.HOPX_API_KEY || 'your-api-key-here';

async function dataAnalysisPipeline() {
  console.log('DATA ANALYSIS PIPELINE');
  
  const sandbox = await Sandbox.create({ template: 'code-interpreter', apiKey: API_KEY });
  try {
    // Upload data
    await sandbox.files.write('/workspace/data.csv', 'name,age,score\nAlice,25,95\nBob,30,87');
    
    // Process
    const result = await sandbox.runCode(`
import pandas as pd
df = pd.read_csv('/workspace/data.csv')
print(df.describe())
    `);
    
    console.log('✅ Analysis:\n', result.stdout);
    
  } finally {
    await sandbox.kill();
  }
}

async function mlModelTraining() {
  console.log('ML MODEL TRAINING');
  
  const sandbox = await Sandbox.create({ 
    template: 'code-interpreter', 
    apiKey: API_KEY,
    vcpu: 4,
    memoryMb: 4096
  });
  
  try {
    const result = await sandbox.runCode(`
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
iris = load_iris()
model = RandomForestClassifier()
model.fit(iris.data, iris.target)
print("Model trained successfully!")
    `, { timeoutSeconds: 120 });
    
    console.log('✅ ML Training:\n', result.stdout);
    
  } finally {
    await sandbox.kill();
  }
}

async function main() {
  console.log('\nJAVASCRIPT/TYPESCRIPT SDK - ADVANCED USE CASES\n');
  await dataAnalysisPipeline();
  await mlModelTraining();
  console.log('✅ ALL ADVANCED USE CASES DEMONSTRATED!\n');
}

main().catch(console.error);
