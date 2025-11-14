/**
 * Build Flow - Orchestrates the complete build process
 */

import { Template } from './builder.js';
import { FileHasher } from './file-hasher.js';
import { TarCreator, TarResult } from './tar-creator.js';
import { 
  BuildOptions, 
  BuildResult, 
  Step, 
  StepType,
  UploadLinkResponse,
  BuildResponse,
  BuildStatusResponse,
  CreateVMOptions,
  VM,
  LogsResponse
} from './types.js';
import * as fs from 'fs/promises';

const DEFAULT_BASE_URL = 'https://api.hopx.dev';

/**
 * Validate template before building
 */
function validateTemplate(template: Template): void {
  // Check for from_image
  const fromImage = template.getFromImage();
  if (!fromImage) {
    throw new Error(
      'Template must specify a base image.\n\n' +
      'Examples:\n' +
      '  new Template(\'python:3.11-slim\')\n' +
      '  .fromUbuntuImage(\'22.04\')\n' +
      '  .fromPythonImage(\'3.12\')\n' +
      '  .fromNodeImage(\'20\')\n\n' +
      'See: https://docs.hopx.ai/templates/base-images'
    );
  }
  
  const steps = template.getSteps();
  
  // Check for meaningful steps (at least one build step)
  const meaningfulSteps = steps.filter(
    step => step.type !== StepType.ENV &&
            step.type !== StepType.WORKDIR &&
            step.type !== StepType.USER
  );
  
  if (meaningfulSteps.length === 0) {
    throw new Error(
      'Template must have at least one build step besides ENV/WORKDIR/USER.\n' +
      'Environment variables can be set when creating a sandbox.\n\n' +
      'Add at least one of:\n' +
      '  .runCmd(\'...\')     - Execute shell command\n' +
      '  .aptInstall(...)   - Install system packages\n' +
      '  .pipInstall(...)   - Install Python packages\n' +
      '  .npmInstall(...)   - Install Node packages\n' +
      '  .copy(\'src\', \'dst\') - Copy files\n\n' +
      'See: https://docs.hopx.ai/templates/building'
    );
  }
}

/**
 * Build a template
 */
export async function buildTemplate(template: Template, options: BuildOptions): Promise<BuildResult> {
  const baseURL = options.baseURL || DEFAULT_BASE_URL;
  const contextPath = options.contextPath || process.cwd();
  
  // Validate template
  validateTemplate(template);
  
  // Step 1: Calculate file hashes for COPY steps
  const stepsWithHashes = await calculateStepHashes(template.getSteps(), contextPath, options);
  
  // Step 2: Upload files for COPY steps
  await uploadFiles(stepsWithHashes, contextPath, baseURL, options);
  
  // Step 3: Trigger build
  const buildResponse = await triggerBuild(
    template,
    stepsWithHashes,
    template.getStartCmd(),
    template.getReadyCheck(),
    baseURL,
    options
  );
  
  // Step 4: Stream logs (if callback provided)
  // Note: Logs endpoint uses templateID
  if (options.onLog || options.onProgress) {
    await streamLogs(buildResponse.templateID, baseURL, options);
  }
  
  // Step 5: Poll status until complete (build process)
  // Note: Status endpoint uses buildID
  const finalStatus = await pollStatus(buildResponse.buildID, baseURL, options);
  
  if (finalStatus.status !== 'active' && finalStatus.status !== 'success') {
    throw new Error(`Build failed: ${finalStatus.errorMessage || 'Unknown error'}`);
  }
  
  // Step 6: Wait for template to be published (background job: publishing → active)
  // Build is done, but template needs to be published to public API
  await waitForTemplateActive(finalStatus.templateID, baseURL, options);
  
  // Calculate duration
  const duration = Date.now() - new Date(finalStatus.startedAt).getTime();
  
  // Return result with createVM and getLogs helpers
  return {
    buildID: buildResponse.buildID,
    templateID: finalStatus.templateID,
    duration,
    createVM: async (vmOptions: CreateVMOptions) => {
      return createVMFromTemplate(finalStatus.templateID, baseURL, options, vmOptions);
    },
    getLogs: async (offset: number = 0): Promise<LogsResponse> => {
      return getLogs(buildResponse.templateID, options.apiKey, offset, baseURL);
    },
  };
}

/**
 * Calculate file hashes for COPY steps
 */
async function calculateStepHashes(
  steps: Step[],
  contextPath: string,
  _options: BuildOptions
): Promise<Step[]> {
  const hasher = new FileHasher();
  
  return Promise.all(steps.map(async (step) => {
    if (step.type === StepType.COPY) {
      const [src, dest] = step.args;
      const sources = src.split(',');
      
      // Calculate hash for all sources
      const hash = await hasher.calculateMultiHash(
        sources.map(s => ({ src: s, dest })),
        contextPath
      );
      
      return {
        ...step,
        filesHash: hash,
      };
    }
    
    return step;
  }));
}

/**
 * Upload files for COPY steps
 */
async function uploadFiles(
  steps: Step[],
  contextPath: string,
  baseURL: string,
  options: BuildOptions
): Promise<void> {
  const tarCreator = new TarCreator();
  const uploadedHashes = new Set<string>();
  
  for (const step of steps) {
    if (step.type === StepType.COPY && step.filesHash) {
      // Skip if already uploaded
      if (uploadedHashes.has(step.filesHash)) {
        continue;
      }
      
      // Get presigned URL
      const [src] = step.args;
      const sources = src.split(',');
      
      // Create tar.gz
      const tarResult = await tarCreator.createMultiTarGz(sources, contextPath);
      
      try {
        // Request upload link
        const uploadLink = await getUploadLink(
          step.filesHash,
          tarResult.size,
          baseURL,
          options.apiKey
        );
        
        // Upload if not already present
        if (!uploadLink.present && uploadLink.uploadUrl) {
          await uploadFile(uploadLink.uploadUrl, tarResult);
        }
        
        uploadedHashes.add(step.filesHash);
      } finally {
        // Cleanup temporary file
        await fs.unlink(tarResult.filePath).catch(() => {});
      }
    }
  }
}

/**
 * Get presigned upload URL
 */
async function getUploadLink(
  filesHash: string,
  contentLength: number,
  baseURL: string,
  apiKey: string
): Promise<UploadLinkResponse> {
  const response = await fetch(`${baseURL}/v1/templates/files/upload-link`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      files_hash: filesHash,  // API uses snake_case
      content_length: contentLength,
    }),
  });
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to get upload link: ${response.statusText} - ${errorText}`);
  }
  
  const data = await response.json() as any;
  
  // Transform response to camelCase
  return {
    present: data.present,
    uploadUrl: data.upload_url,
    expiresAt: data.expires_at,
  };
}

/**
 * Upload file to R2
 */
async function uploadFile(uploadUrl: string, tarResult: TarResult): Promise<void> {
  const fileContent = await fs.readFile(tarResult.filePath);
  
  const response = await fetch(uploadUrl, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/gzip',
      'Content-Length': tarResult.size.toString(),
    },
    body: fileContent,
  });
  
  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }
}

/**
 * Transform SDK steps to API format
 */
function transformStepsForAPI(steps: Step[]): any[] {
  const apiSteps: any[] = [];
  
  for (const step of steps) {
    // Note: FROM is no longer a step - it's in from_image field
    
    // Transform COPY steps
    if (step.type === StepType.COPY) {
      const copyStep: any = {
        type: 'COPY',
        args: step.args,
        filesHash: step.filesHash,
      };
      
      // Add copy options if present
      if (step.copyOptions) {
        if (step.copyOptions.owner) {
          copyStep.owner = step.copyOptions.owner;
        }
        if (step.copyOptions.permissions) {
          copyStep.permissions = step.copyOptions.permissions;
        }
      }
      
      apiSteps.push(copyStep);
      continue;
    }
    
    // Transform RUN steps
    if (step.type === StepType.RUN) {
      apiSteps.push({
        type: 'RUN',
        args: step.args,
      });
      continue;
    }
    
    // Transform ENV steps
    if (step.type === StepType.ENV) {
      apiSteps.push({
        type: 'env',
        key: step.args[0],
        value: step.args[1],
      });
      continue;
    }
    
    // Transform WORKDIR steps
    if (step.type === StepType.WORKDIR) {
      apiSteps.push({
        type: 'workdir',
        path: step.args[0],
      });
      continue;
    }
  }
  
  return apiSteps;
}

/**
 * Transform ready check to API format
 */
function transformReadyCheckForAPI(readyCheck: any): any {
  if (!readyCheck) return undefined;
  
  const apiReady: any = {
    type: readyCheck.type,
  };
  
  if (readyCheck.port) apiReady.port = readyCheck.port;
  if (readyCheck.url) apiReady.url = readyCheck.url;
  if (readyCheck.path) apiReady.path = readyCheck.path;
  if (readyCheck.processName) apiReady.name = readyCheck.processName;
  if (readyCheck.command) apiReady.command = readyCheck.command;
  
  return apiReady;
}

/**
 * Trigger build
 */
async function triggerBuild(
  template: Template,
  steps: Step[],
  startCmd: string | undefined,
  readyCmd: any,
  baseURL: string,
  options: BuildOptions
): Promise<BuildResponse> {
  // Get from_image and registry credentials
  const fromImage = template.getFromImage();
  const registryAuth = template.getRegistryAuth();
  
  // Transform steps to API format
  const apiSteps = transformStepsForAPI(steps);
  const apiReadyCmd = transformReadyCheckForAPI(readyCmd);
  
  const body: any = {
    name: options.name,
    from_image: fromImage,  // Required, separate from steps
    steps: apiSteps,
    cpu: options.cpu || 2,
    memory: options.memory || 2048,
    diskGB: options.diskGB || 10,
    skipCache: options.skipCache || false,
    update: options.update || false,
  };
  
  // Add registry credentials if present
  if (registryAuth) {
    body.registry_credentials = {
      type: 'basic',
      username: registryAuth.username,
      password: registryAuth.password,
    };
  }
  
  // Only include startCmd if defined
  if (startCmd) {
    body.startCmd = startCmd;
  }
  
  // Only include readyCmd if defined
  if (apiReadyCmd) {
    body.readyCmd = apiReadyCmd;
  }
  
  const response = await fetch(`${baseURL}/v1/templates/build`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${options.apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Build trigger failed: ${response.statusText} - ${errorText}`);
  }
  
  const data = await response.json() as any;
  
  // API returns snake_case
  return {
    buildID: data.build_id,
    templateID: data.template_id,
    status: data.status,
    logsUrl: data.logs_url,
  };
}

/**
 * Stream logs via SSE
 */
async function streamLogs(
  templateID: string,
  baseURL: string,
  options: BuildOptions
): Promise<void> {
  let offset = 0;
  
  while (true) {
    try {
      const response = await fetch(
        `${baseURL}/v1/templates/build/${templateID}/logs?offset=${offset}`,
        {
          headers: {
            'Authorization': `Bearer ${options.apiKey}`,
          },
        }
      );
      
      if (!response.ok) {
        return; // Stop streaming on error
      }
      
      const data = await response.json() as any;
      const logs = data.logs || '';
      offset = data.offset || offset;
      const status = data.status || 'unknown';
      const complete = data.complete || false;
      
      // Output logs line by line
      if (logs && options.onLog) {
        for (const line of logs.split('\n')) {
          if (line.trim()) {
            // Extract log level if present
            let level = 'INFO';
            if (line.includes('❌') || line.includes('ERROR')) {
              level = 'ERROR';
            } else if (line.includes('✅')) {
              level = 'INFO';
            } else if (line.includes('⚠') || line.includes('WARN')) {
              level = 'WARN';
            }
            
            options.onLog({
              level,
              message: line,
              timestamp: '',
            });
          }
        }
      }
      
      // Update progress if provided by server
      if (options.onProgress && status === 'building') {
        // Note: Progress tracking would need to be implemented by API
        // For now, we don't report intermediate progress to avoid misleading information
      }
      
      // Check if complete
      if (complete || status === 'active' || status === 'success' || status === 'failed') {
        if (options.onProgress && (status === 'active' || status === 'success')) {
          options.onProgress(100);
        }
        return;
      }
      
      // Wait before next poll
      await new Promise(resolve => setTimeout(resolve, 2000));
      
    } catch (error) {
      // Stop streaming on error
      return;
    }
  }
}

/**
 * Poll build status
 */
async function pollStatus(
  buildID: string,
  baseURL: string,
  options: BuildOptions,
  intervalMs: number = 2000
): Promise<BuildStatusResponse> {
  while (true) {
    const response = await fetch(`${baseURL}/v1/templates/build/${buildID}/status`, {
      headers: {
        'Authorization': `Bearer ${options.apiKey}`,
      },
    });
    
    if (!response.ok) {
      throw new Error(`Status check failed: ${response.statusText}`);
    }
    
    const data = await response.json() as any;
    
  // Transform response from snake_case to camelCase
  const status: BuildStatusResponse = {
    buildID: data.build_id,
    templateID: data.template_id,
    status: data.status,
    progress: data.progress || 0,
    currentStep: data.current_step,
    startedAt: data.started_at,
    completedAt: data.completed_at,
    errorMessage: data.error_message,
    buildDurationMs: data.build_duration_ms,
  };
    
    // Status can be: building, active (success), failed
    if (status.status === 'active' || status.status === 'completed' || status.status === 'success' || status.status === 'failed') {
      return status;
    }
    
    // Wait before next poll
    await new Promise(resolve => setTimeout(resolve, intervalMs));
  }
}

/**
 * Get build logs with offset-based polling
 * 
 * Note: The API uses templateID for the logs endpoint (not buildID).
 * BuildID and templateID are the same for template builds.
 * 
 * @param templateID - Template ID to retrieve logs for
 * @param apiKey - API key
 * @param offset - Starting offset (default: 0)
 * @param baseURL - Base URL (default: https://api.hopx.dev)
 * @returns LogsResponse with logs, offset, status, complete
 * 
 * @example
 * ```typescript
 * import { getLogs } from 'hopx';
 * 
 * // Get logs from beginning
 * const response = await getLogs("123", "api_key");
 * console.log(response.logs);
 * 
 * // Get new logs from last offset
 * const response2 = await getLogs("123", "api_key", response.offset);
 * ```
 */
export async function getLogs(
  templateID: string,
  apiKey: string,
  offset: number = 0,
  baseURL: string = DEFAULT_BASE_URL
): Promise<LogsResponse> {
  const url = new URL(`${baseURL}/v1/templates/build/${templateID}/logs`);
  url.searchParams.set('offset', offset.toString());
  
  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
    },
  });
  
  if (!response.ok) {
    throw new Error(`Get logs failed: ${response.status} ${response.statusText}`);
  }
  
  const data = await response.json() as any;
  
  return {
    logs: data.logs || '',
    offset: data.offset || 0,
    status: data.status || 'unknown',
    complete: data.complete || false,
    requestId: data.request_id,
  };
}

/**
 * Wait for template to be published and active in public API
 * 
 * After build completes, a background job publishes the template:
 * - Build done (success) → publishing → active
 * 
 * This ensures the template is immediately usable after Template.build() returns.
 */
async function waitForTemplateActive(
  templateID: string,
  baseURL: string,
  options: BuildOptions,
  maxWaitSeconds: number = 60
): Promise<void> {
  const startTime = Date.now();
  
  while (Date.now() - startTime < maxWaitSeconds * 1000) {
    try {
      const response = await fetch(`${baseURL}/v1/templates/${templateID}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${options.apiKey}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json() as any;
        const status = data.status || '';
        
        if (status === 'active') {
          // Template is published and ready!
          if (options.onLog) {
            options.onLog({ 
              message: `✅ Template published and active (ID: ${templateID})`,
              timestamp: new Date().toISOString(),
              level: 'info'
            });
          }
          return;
        } else if (status === 'failed') {
          throw new Error('Template publishing failed');
        } else if (status === 'building' || status === 'publishing') {
          // Still processing, wait more
          if (options.onLog) {
            options.onLog({ 
              message: `⏳ Template status: ${status}, waiting for active...`,
              timestamp: new Date().toISOString(),
              level: 'info'
            });
          }
        }
      }
    } catch (error) {
      // Template might not be visible yet, continue waiting
    }
    
    // Wait 2 seconds before next check
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  // Timeout - but don't fail, template might still become active later
  if (options.onLog) {
    options.onLog({ 
      message: `⚠️  Template not yet active after ${maxWaitSeconds}s, but build succeeded`,
      timestamp: new Date().toISOString(),
      level: 'warn'
    });
  }
}

/**
 * Create sandbox from template
 * Uses Sandbox.create() API with templateId
 */
async function createVMFromTemplate(
  templateID: string,
  baseURL: string,
  buildOptions: BuildOptions,
  vmOptions: CreateVMOptions
): Promise<VM> {
  // Import Sandbox dynamically to avoid circular dependency
  const { Sandbox } = await import('../sandbox.js');
  
  const sandbox = await Sandbox.create({
    templateId: templateID,
    apiKey: buildOptions.apiKey,
    baseURL: baseURL,
    envVars: vmOptions.envVars,
    timeoutSeconds: undefined, // No timeout by default
  });
  
  // Return VM-like interface for backward compatibility
  const info = await sandbox.getInfo();
  
  return {
    vmID: sandbox.sandboxId,
    templateID: info.templateId || templateID,
    status: info.status,
    ip: info.publicHost?.split('://')[1] || '',
    agentUrl: info.publicHost,
    startedAt: info.createdAt,
    delete: async () => {
      await sandbox.kill();
    },
  };
}

