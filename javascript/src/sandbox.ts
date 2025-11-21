/**
 * Sandbox - Main class for VM management
 */

import { HTTPClient } from './client.js';
import { WSClient } from './ws-client.js';
import { Files } from './resources/files.js';
import { Commands } from './resources/commands.js';
import { EnvironmentVariables } from './resources/env-vars.js';
import { Cache } from './resources/cache.js';
import { Desktop } from './resources/desktop.js';
import { Terminal } from './resources/terminal.js';
import { HopxError } from './errors.js';
import type {
  SandboxCreateOptions,
  TemplateInfo,
  SandboxInfo,
  CodeExecutionOptions,
  AsyncExecutionOptions,
  BackgroundExecutionOptions,
  ExecutionResult,
  ExecuteResponse,
  AsyncExecuteResponse,
  BackgroundExecuteResponse,
  ProcessInfo,
  MetricsSnapshot,
  HealthResponse,
  InfoResponse,
  StreamMessage,
  FileChangeMessage,
  RichOutput,
} from './types/index.js';
import { ExecutionResultImpl } from './types/index.js';

// JWT Token storage per sandbox
interface TokenData {
  token: string;
  expiresAt: Date;
}

// Global token cache (shared across all Sandbox instances)
const tokenCache = new Map<string, TokenData>();

export class Sandbox {
  private publicClient: HTTPClient;
  private agentClient?: HTTPClient;
  private wsClient?: WSClient;
  private _agentUrl?: string;
  private apiKey?: string;
  
  // Resources (lazy-loaded)
  private _files?: Files;
  private _commands?: Commands;
  private _env?: EnvironmentVariables;
  private _cache?: Cache;
  private _desktop?: Desktop;
  private _terminal?: Terminal;

  public readonly sandboxId: string;

  private constructor(sandboxId: string, apiKey?: string, baseURL = 'https://api.hopx.dev') {
    this.sandboxId = sandboxId;
    this.apiKey = apiKey;
    this.publicClient = new HTTPClient({
      baseURL,
      apiKey,
      timeout: 60000,
      maxRetries: 3,
    });
  }

  // ==========================================================================
  // STATIC METHODS
  // ==========================================================================

  /**
   * Create a new sandbox
   * API key can be provided via options.apiKey or HOPX_API_KEY environment variable
   * 
   * Two modes:
   * 1. Template-based: Specify templateId only (resources loaded from template)
   * 2. Custom: Specify template + vcpu + memoryMb
   * 
   * Optional parameters:
   * - timeoutSeconds: Auto-kill sandbox after specified seconds (default: no timeout)
   * - internetAccess: Enable/disable internet access (default: true)
   */
  static async create(options: SandboxCreateOptions): Promise<Sandbox> {
    const apiKey = options.apiKey || process.env['HOPX_API_KEY'];
    
    const client = new HTTPClient({
      baseURL: options.baseURL ?? 'https://api.hopx.dev',
      apiKey,
      timeout: (options.timeout ?? 300) * 1000,
      maxRetries: 3,
    });

    // Build request payload (resources from template)
    let requestData: any;
    
    if (options.templateId) {
      requestData = {
        template_id: String(options.templateId),  // ✅ FIXED: Force string for FlexibleTemplateID
        region: options.region,
        timeout_seconds: options.timeoutSeconds,
        internet_access: options.internetAccess,
        env_vars: options.envVars,
      };
    } else if (options.template) {
      requestData = {
        template_name: options.template,
        region: options.region,
        timeout_seconds: options.timeoutSeconds,
        internet_access: options.internetAccess,
        env_vars: options.envVars,
      };
    } else {
      throw new Error('Either "template" or "templateId" must be provided');
    }
    
    // Remove undefined values to let API apply its defaults
    Object.keys(requestData).forEach(key => {
      if (requestData[key] === undefined) {
        delete requestData[key];
      }
    });

    const response = await client.post<any>('/v1/sandboxes', requestData);

    // API returns sandbox_id in response
    const sandboxId = response.sandbox_id || response.sandboxId || response.id;
    if (!sandboxId) {
      throw new Error(`Failed to get sandbox ID from response: ${JSON.stringify(response)}`);
    }

    const sandbox = new Sandbox(sandboxId, apiKey, options.baseURL);

    // ⚠️ NEW: Store JWT token from create response
    if (response.auth_token && response.token_expires_at) {
      tokenCache.set(sandboxId, {
        token: response.auth_token,
        expiresAt: new Date(response.token_expires_at),
      });
    }

    // Auto-initialize agent client by calling getInfo()
    // This fetches public_host and sets up the agent client
    await sandbox.getInfo();

    // ✅ CRITICAL: Propagate env_vars to sandbox runtime
    // The API doesn't automatically set env_vars in the runtime environment.
    // We must explicitly set them via the Agent API after sandbox creation.
    if (options.envVars && Object.keys(options.envVars).length > 0) {
      await sandbox.env.update(options.envVars);
    }

    return sandbox;
  }

  /**
   * Connect to an existing sandbox by ID
   * Typical workflow: Sandbox.list() → find your sandbox → Sandbox.connect(id)
   * API key can be provided as parameter or via HOPX_API_KEY environment variable
   * 
   * NEW JWT Behavior:
   * - If VM is paused → resumes it and refreshes JWT token
   * - If VM is stopped → throws error (cannot connect to stopped VM)
   * - If VM is running/active → refreshes JWT token
   * - Stores JWT token for agent authentication
   */
  static async connect(sandboxId: string, apiKey?: string, baseURL?: string): Promise<Sandbox> {
    const finalApiKey = apiKey || process.env['HOPX_API_KEY'];
    const sandbox = new Sandbox(sandboxId, finalApiKey, baseURL);
    
    // Get current VM status
    const info = await sandbox.getInfo();
    
    // Handle different VM states
    if (info.status === 'stopped') {
      throw new Error(
        `Cannot connect to stopped sandbox ${sandboxId}. ` +
        `Please create a new sandbox.`
      );
    }
    
    if (info.status === 'paused') {
      // Resume paused VM
      await sandbox.resume();
    }
    
    if (info.status !== 'running' && info.status !== 'paused') {
      throw new Error(
        `Cannot connect to sandbox ${sandboxId} with status '${info.status}'. ` +
        `Expected 'running' or 'paused'.`
      );
    }
    
    // Refresh JWT token for agent authentication
    await sandbox.refreshToken();
    
    // ✅ FIXED: Update agentClient with new token after refresh
    if (sandbox.agentClient) {
      const tokenData = tokenCache.get(sandboxId);
      if (tokenData) {
        sandbox.agentClient.updateJwtToken(tokenData.token);
      }
    }
    
    return sandbox;
  }

  /**
   * Lazy iterator for sandboxes using cursor pagination
   *
   * Yields sandboxes one by one, fetching pages as needed.
   * Doesn't load all sandboxes into memory at once.
   *
   * Python reference: sandbox.py lines 652-711
   *
   * @param options - Filter options
   * @returns AsyncGenerator yielding Sandbox instances
   *
   * @example
   * ```typescript
   * // Lazy loading - fetches pages as needed
   * for await (const sandbox of Sandbox.iter({ status: 'running' })) {
   *   console.log(sandbox.sandboxId);
   *   if (found) {
   *     break;  // Doesn't fetch remaining pages!
   *   }
   * }
   * ```
   */
  static async *iter(options?: {
    status?: 'running' | 'stopped' | 'paused' | 'creating';
    region?: string;
    apiKey?: string;
    baseURL?: string;
  }): AsyncGenerator<Sandbox> {
    const apiKey = options?.apiKey || process.env['HOPX_API_KEY'];
    const baseURL = options?.baseURL ?? 'https://api.hopx.dev';

    const client = new HTTPClient({
      baseURL,
      apiKey,
      timeout: 60000,
      maxRetries: 3,
    });

    let hasMore = true;
    let cursor: string | null = null;
    const limit = 100;

    while (hasMore) {
      const params = new URLSearchParams();
      params.append('limit', limit.toString());
      if (options?.status) params.append('status', options.status);
      if (options?.region) params.append('region', options.region);
      if (cursor) params.append('cursor', cursor);

      const query = params.toString() ? `?${params.toString()}` : '';
      const response = await client.get<any>(`/v1/sandboxes${query}`);

      const sandboxes = response.data || [];
      for (const item of sandboxes) {
        const sandboxId = item.id || item.sandbox_id;
        yield new Sandbox(sandboxId, apiKey, baseURL);
      }

      hasMore = response.has_more ?? false;
      cursor = response.next_cursor ?? null;
    }
  }

  /**
   * List all sandboxes
   * API key can be provided via options.apiKey or HOPX_API_KEY environment variable
   */
  static async list(options: {
    apiKey?: string;
    baseURL?: string;
    limit?: number;
    status?: 'running' | 'stopped' | 'paused' | 'creating';
    region?: string;
  } = {}): Promise<SandboxInfo[]> {
    const apiKey = options.apiKey || process.env['HOPX_API_KEY'];

    const client = new HTTPClient({
      baseURL: options.baseURL ?? 'https://api.hopx.dev',
      apiKey,
      timeout: 60000,
      maxRetries: 3,
    });

    const params = new URLSearchParams();
    if (options.limit) params.append('limit', options.limit.toString());
    if (options.status) params.append('status', options.status);
    if (options.region) params.append('region', options.region);

    const query = params.toString() ? `?${params.toString()}` : '';
    const response = await client.get<any>(`/v1/sandboxes${query}`);

    // Map API response to SandboxInfo array
    const sandboxes = response.data || [];
    return sandboxes.map((s: any) => {
      const resources = s.resources || {};
      return {
        sandboxId: s.id || s.sandbox_id,
        templateName: s.template_name,
        templateId: s.template_id,
        status: s.status,
        publicHost: s.public_host,
        createdAt: s.created_at,
        vcpu: resources.vcpu,
        memoryMb: resources.memory_mb,
        diskGb: resources.disk_gb ? Math.round(resources.disk_gb / 1024) : undefined,
      };
    });
  }

  /**
   * List available templates
   * API key can be provided via options.apiKey or HOPX_API_KEY environment variable
   */
  static async listTemplates(options: {
    category?: string;
    language?: string;
    apiKey?: string;
    baseURL?: string;
  } = {}): Promise<TemplateInfo[]> {
    const apiKey = options.apiKey || process.env['HOPX_API_KEY'];
    
    const client = new HTTPClient({
      baseURL: options.baseURL ?? 'https://api.hopx.dev',
      apiKey,
      timeout: 60000,
      maxRetries: 3,
    });

    const params = new URLSearchParams();
    if (options.category) params.append('category', options.category);
    if (options.language) params.append('language', options.language);

    const query = params.toString() ? `?${params.toString()}` : '';
    const response = await client.get<any>(`/v1/templates${query}`);

    const templates = response.data || [];
    return templates.map((t: any) => ({
      id: t.id,
      name: t.name,
      displayName: t.display_name,
      description: t.description,
      category: t.category,
      language: t.language,
      icon: t.icon,
      defaultResources: t.default_resources ? {
        vcpu: t.default_resources.vcpu,
        memoryMb: t.default_resources.memory_mb,
        diskGb: t.default_resources.disk_gb,
      } : undefined,
      minResources: t.min_resources ? {
        vcpu: t.min_resources.vcpu,
        memoryMb: t.min_resources.memory_mb,
        diskGb: t.min_resources.disk_gb,
      } : undefined,
      maxResources: t.max_resources ? {
        vcpu: t.max_resources.vcpu,
        memoryMb: t.max_resources.memory_mb,
        diskGb: t.max_resources.disk_gb,
      } : undefined,
      features: t.features || [],
      tags: t.tags || [],
      popularityScore: t.popularity_score,
      docsUrl: t.docs_url,
      isActive: t.is_active,
      status: t.status,  // ✅ NEW: Template status field
    }));
  }

  /**
   * Get template details
   * API key can be provided via options.apiKey or HOPX_API_KEY environment variable
   */
  static async getTemplate(name: string, options: {
    apiKey?: string;
    baseURL?: string;
  } = {}): Promise<TemplateInfo> {
    const apiKey = options.apiKey || process.env['HOPX_API_KEY'];

    const client = new HTTPClient({
      baseURL: options.baseURL ?? 'https://api.hopx.dev',
      apiKey,
      timeout: 60000,
      maxRetries: 3,
    });

    const response = await client.get<any>(`/v1/templates/${name}`);

    return {
      id: response.id,
      name: response.name,
      displayName: response.display_name,
      description: response.description,
      category: response.category,
      language: response.language,
      icon: response.icon,
      defaultResources: response.default_resources ? {
        vcpu: response.default_resources.vcpu,
        memoryMb: response.default_resources.memory_mb,
        diskGb: response.default_resources.disk_gb,
      } : undefined,
      minResources: response.min_resources ? {
        vcpu: response.min_resources.vcpu,
        memoryMb: response.min_resources.memory_mb,
        diskGb: response.min_resources.disk_gb,
      } : undefined,
      maxResources: response.max_resources ? {
        vcpu: response.max_resources.vcpu,
        memoryMb: response.max_resources.memory_mb,
        diskGb: response.max_resources.disk_gb,
      } : undefined,
      features: response.features || [],
      tags: response.tags || [],
      popularityScore: response.popularity_score,
      docsUrl: response.docs_url,
      isActive: response.is_active,
      status: response.status,  // ✅ NEW: Template status field
    };
  }

  /**
   * Delete a custom template
   *
   * Only organization-owned templates can be deleted. Public templates cannot be deleted.
   *
   * Python reference: sandbox.py lines 842-874
   *
   * @param templateId - Template ID to delete
   * @param options - API configuration options
   * @returns Deletion confirmation response
   *
   * @example
   * ```typescript
   * // Delete a custom template by ID
   * const result = await Sandbox.deleteTemplate('template_123abc');
   * console.log(result);
   * ```
   */
  static async deleteTemplate(
    templateId: string,
    options?: { apiKey?: string; baseURL?: string }
  ): Promise<any> {
    const apiKey = options?.apiKey || process.env['HOPX_API_KEY'];

    const client = new HTTPClient({
      baseURL: options?.baseURL ?? 'https://api.hopx.dev',
      apiKey,
      timeout: 60000,
      maxRetries: 3,
    });

    return await client.delete<any>(`/v1/templates/${templateId}`);
  }

  /**
   * Check API health status
   *
   * This endpoint does not require authentication and can be used to verify
   * API availability and connectivity.
   *
   * Python reference: sandbox.py lines 877-909
   *
   * @param baseURL - API base URL (default: production)
   * @returns Health status information
   *
   * @example
   * ```typescript
   * // Check production API health
   * const health = await Sandbox.healthCheck();
   * console.log(health);  // { status: 'ok', ... }
   *
   * // Check custom/staging API
   * const health = await Sandbox.healthCheck('https://staging-api.hopx.dev');
   * ```
   */
  static async healthCheck(baseURL?: string): Promise<HealthResponse> {
    const url = `${(baseURL ?? 'https://api.hopx.dev').replace(/\/$/, '')}/health`;

    try {
      // Use axios directly without authentication for health check
      const axios = (await import('axios')).default;
      const response = await axios.get(url, { timeout: 10000 });
      return response.data;
    } catch (error: any) {
      throw new HopxError(`Health check failed: ${error.message}`);
    }
  }

  // ==========================================================================
  // RESOURCES (Lazy-loaded)
  // ==========================================================================

  get files(): Files {
    if (!this._files) {
      this.ensureAgentClientSync();
      this._files = new Files(this.agentClient!);
    }
    return this._files;
  }

  get commands(): Commands {
    if (!this._commands) {
      this.ensureAgentClientSync();
      this._commands = new Commands(this.agentClient!);
    }
    return this._commands;
  }

  get env(): EnvironmentVariables {
    if (!this._env) {
      this.ensureAgentClientSync();
      this._env = new EnvironmentVariables(this.agentClient!);
    }
    return this._env;
  }

  get cache(): Cache {
    if (!this._cache) {
      this.ensureAgentClientSync();
      this._cache = new Cache(this.agentClient!);
    }
    return this._cache;
  }

  get desktop(): Desktop {
    if (!this._desktop) {
      this.ensureAgentClientSync();
      this._desktop = new Desktop(this.agentClient!);
    }
    return this._desktop;
  }

  get terminal(): Terminal {
    if (!this._terminal) {
      this.ensureWSClientSync();
      this._terminal = new Terminal(this.wsClient!);
    }
    return this._terminal;
  }

  // ==========================================================================
  // SANDBOX LIFECYCLE
  // ==========================================================================

  async getInfo(): Promise<SandboxInfo> {
    const response = await this.publicClient.get<any>(`/v1/sandboxes/${this.sandboxId}`);
    
    // Initialize agent client if we have the public_host
    if (response.public_host && !this.agentClient) {
      this._agentUrl = response.public_host;
      
      // Get JWT token for agent authentication
      let jwtToken: string | undefined;
      try {
        await this.ensureValidToken();
        jwtToken = (await this.getToken());
      } catch (error) {
        // Token might not be available yet (e.g., on first connect)
        // Will be set later when refreshToken() is called
      }
      
      this.agentClient = new HTTPClient({
        baseURL: this._agentUrl,
        apiKey: this.apiKey,
        timeout: 60000,
        maxRetries: 3,
        jwtToken,
        // ✅ NEW: Auto-refresh token on 401 Unauthorized
        tokenRefreshCallback: async () => {
          await this.refreshToken();
          const tokenData = tokenCache.get(this.sandboxId);
          return tokenData?.token || null;
        },
      });
      this.wsClient = new WSClient(this._agentUrl, jwtToken);
    }
    
    // Resources are under .resources in API response
    const resources = response.resources || {};

    return {
      sandboxId: response.id || response.sandbox_id,
      templateName: response.template_name,
      templateId: response.template_id,
      organizationId: response.organization_id,
      nodeId: response.node_id,
      region: response.region,
      status: response.status,
      publicHost: response.public_host,
      directUrl: response.direct_url,
      previewUrl: response.preview_url,
      resources: resources.vcpu || resources.memory_mb || resources.disk_mb ? {
        vcpu: resources.vcpu,
        memoryMb: resources.memory_mb,
        diskMb: resources.disk_mb,
      } : undefined,
      internetAccess: response.internet_access,
      liveMode: response.live_mode,
      timeoutSeconds: response.timeout_seconds,
      expiresAt: response.expires_at,
      createdAt: response.created_at,
      startedAt: response.started_at,
      endAt: response.end_at,
      // Deprecated flat resource fields (for backward compatibility)
      vcpu: resources.vcpu,
      memoryMb: resources.memory_mb,
      diskGb: resources.disk_mb ? Math.round(resources.disk_mb / 1024) : undefined,
    };
  }

  /**
   * Get preview URL for accessing services running on a specific port in the sandbox
   *
   * Hopx automatically exposes all ports from sandboxes via public URLs.
   * URL format: https://{PORT}-{sandbox_id}.{region}.vms.hopx.dev/
   *
   * @param port - Port number (default: 7777, the agent port)
   * @returns Public URL for accessing the service
   *
   * @example
   * ```typescript
   * const sandbox = await Sandbox.create({ template: 'code-interpreter' });
   *
   * // Get URL for service on port 8080
   * const appUrl = await sandbox.getPreviewUrl(8080);
   * // Returns: "https://8080-176329715051artmzu.eu-1001.vms.hopx.dev/"
   *
   * // Get agent URL (port 7777)
   * const agentUrl = await sandbox.getPreviewUrl(7777);
   * ```
   */
  async getPreviewUrl(port: number = 7777): Promise<string> {
    const info = await this.getInfo();
    const publicHost = info.publicHost;

    if (!publicHost) {
      throw new HopxError('Sandbox does not have a public host URL');
    }

    // Remove protocol and trailing slash
    const host = publicHost.replace(/^https?:\/\//, '').replace(/\/$/, '');

    // Pattern 1: {port}-{sandbox_id}.{region}.vms.hopx.dev
    const match = host.match(/^(?:\d+-)?([^.]+)\.(.+\.vms\.hopx\.dev)$/);
    if (match) {
      const [, sandboxPart, domainPart] = match;
      return `https://${port}-${sandboxPart}.${domainPart}/`;
    }

    throw new HopxError(`Unable to determine preview URL from: ${publicHost}`);
  }

  /**
   * Convenience property for getting the agent URL (port 7777)
   *
   * @example
   * ```typescript
   * const sandbox = await Sandbox.create({ template: 'code-interpreter' });
   * const agentUrl = await sandbox.agentUrl;
   * // Returns: "https://7777-176329715051artmzu.eu-1001.vms.hopx.dev/"
   * ```
   */
  get agentUrl(): Promise<string> {
    return this.getPreviewUrl(7777);
  }

  async kill(): Promise<void> {
    await this.publicClient.delete(`/v1/sandboxes/${this.sandboxId}`);
  }

  /**
   * Pause a running sandbox
   */
  async pause(): Promise<void> {
    await this.publicClient.post(`/v1/sandboxes/${this.sandboxId}/pause`);
  }

  /**
   * Resume a paused sandbox
   */
  async resume(): Promise<void> {
    await this.publicClient.post(`/v1/sandboxes/${this.sandboxId}/resume`);
  }

  /**
   * Set sandbox auto-kill timeout
   *
   * Sets a new timeout duration. The sandbox will be automatically terminated
   * after the specified number of seconds from now.
   *
   * Python reference: sandbox.py lines 1578-1612
   *
   * @param timeoutSeconds - New timeout duration in seconds from now (must be > 0)
   *
   * @example
   * ```typescript
   * const sandbox = await Sandbox.create({ template: 'code-interpreter', timeoutSeconds: 300 });
   *
   * // Extend to 10 minutes from now
   * await sandbox.setTimeout(600);
   *
   * // Extend to 1 hour
   * await sandbox.setTimeout(3600);
   * ```
   */
  async setTimeout(timeoutSeconds: number): Promise<void> {
    if (timeoutSeconds <= 0) {
      throw new Error('Timeout must be greater than 0');
    }

    const payload = { timeout_seconds: timeoutSeconds };
    await this.publicClient.put(`/v1/sandboxes/${this.sandboxId}/timeout`, payload);
  }

  // ==========================================================================
  // CODE EXECUTION
  // ==========================================================================

  /**
   * Execute code synchronously
   * @param code - Code to execute
   * @param options - Execution options
   */
  async runCode(code: string, options?: CodeExecutionOptions): Promise<ExecutionResult> {
    await this.ensureAgentClient();

    const response = await this.agentClient!.post<ExecuteResponse & {
      png?: string;
      html?: string;
      json?: any;
      result?: string;
    }>(
      '/execute',
      {
        code,
        language: options?.language ?? 'python',
        timeout: options?.timeout ?? 60,
        workdir: options?.workingDir ?? '/workspace',
        env: options?.env,
      }
    );

    // Parse rich outputs from Jupyter (agent returns: .png, .html, .json, .result)
    const richOutputs: RichOutput[] = [];
    
    if (response.png) {
      richOutputs.push({
        type: 'image/png' as any,
        data: { 'image/png': response.png },
      });
    }
    
    if (response.html) {
      richOutputs.push({
        type: 'text/html' as any,
        data: { 'text/html': response.html },
      });
    }
    
    if (response.json) {
      richOutputs.push({
        type: 'application/json' as any,
        data: { 'application/json': response.json },
      });
    }
    
    if (response.result && response.result !== response.stdout) {
      richOutputs.push({
        type: 'text/plain' as any,
        data: { 'text/plain': response.result },
      });
    }

    return new ExecutionResultImpl({
      ...response,
      richOutputs: richOutputs.length > 0 ? richOutputs : undefined,
    });
  }

  async runCodeAsync(code: string, options: AsyncExecutionOptions): Promise<AsyncExecuteResponse> {
    await this.ensureAgentClient();

    return this.agentClient!.post<AsyncExecuteResponse>('/execute/async', {
      code,
      language: options.language ?? 'python',
      timeout: options.timeout ?? 1800,
      workdir: options.workingDir ?? '/workspace',
      env: options.env,
      callback_url: options.callbackUrl,
      callback_headers: options.callbackHeaders,
      callback_signature_secret: options.callbackSignatureSecret,
    });
  }

  async runCodeBackground(code: string, options?: BackgroundExecutionOptions): Promise<BackgroundExecuteResponse> {
    await this.ensureAgentClient();

    return this.agentClient!.post<BackgroundExecuteResponse>('/execute/background', {
      code,
      language: options?.language ?? 'python',
      timeout: options?.timeout ?? 300,
      workdir: options?.workingDir ?? '/workspace',
      env: options?.env,
      name: options?.name,
    });
  }

  async runIpython(code: string, options?: Omit<CodeExecutionOptions, 'language'>): Promise<ExecutionResult> {
    await this.ensureAgentClient();

    const response = await this.agentClient!.post<ExecuteResponse>('/execute/ipython', {
      code,
      timeout: options?.timeout ?? 60,
      env: options?.env,
    });

    return new ExecutionResultImpl(response);
  }

  // ==========================================================================
  // PROCESS MANAGEMENT
  // ==========================================================================

  async listProcesses(): Promise<ProcessInfo[]> {
    await this.ensureAgentClient();
    const response = await this.agentClient!.get<{ processes: ProcessInfo[] }>('/execute/processes');
    return response.processes;
  }

  /**
   * List all running system processes in the sandbox
   *
   * Returns a list of all processes running in the VM, not just background
   * code executions. Useful for debugging and monitoring system state.
   *
   * Python reference: sandbox.py lines 1110-1143
   *
   * @returns List of process information objects
   *
   * @example
   * ```typescript
   * const processes = await sandbox.listSystemProcesses();
   * for (const proc of processes) {
   *   console.log(`${proc.pid}: ${proc.name} (CPU: ${proc.cpu_percent || 0}%)`);
   * }
   * ```
   */
  async listSystemProcesses(): Promise<ProcessInfo[]> {
    await this.ensureAgentClient();
    const response = await this.agentClient!.get<{ processes: ProcessInfo[] }>('/processes');
    return response.processes || [];
  }

  /**
   * Get Jupyter kernel session status
   *
   * Returns information about active Jupyter kernel sessions, useful for
   * debugging kernel state and managing long-running Python executions.
   *
   * Python reference: sandbox.py lines 1145-1176
   *
   * @returns List of active Jupyter sessions
   *
   * @example
   * ```typescript
   * const sessions = await sandbox.getJupyterSessions();
   * for (const session of sessions) {
   *   console.log(`Kernel ${session.kernel_id}: ${session.execution_state}`);
   * }
   * ```
   */
  async getJupyterSessions(): Promise<any[]> {
    await this.ensureAgentClient();
    const response = await this.agentClient!.get<{ sessions: any[] }>('/jupyter/sessions');
    return response.sessions || [];
  }

  async killProcess(processId: string): Promise<void> {
    await this.ensureAgentClient();
    await this.agentClient!.post(`/execute/kill/${processId}`);
  }

  // ==========================================================================
  // METRICS
  // ==========================================================================

  async getMetricsSnapshot(): Promise<MetricsSnapshot> {
    await this.ensureAgentClient();
    return this.agentClient!.get<MetricsSnapshot>('/metrics/snapshot');
  }

  /**
   * Get real-time agent metrics
   *
   * Returns agent performance and health metrics including uptime,
   * request counts, error counts, and performance statistics.
   *
   * Python reference: sandbox.py lines 1075-1108
   *
   * @returns Metrics including uptime, requests, errors, and performance stats
   *
   * @example
   * ```typescript
   * const metrics = await sandbox.getAgentMetrics();
   * console.log(`Uptime: ${metrics.uptime_seconds}s`);
   * console.log(`Total requests: ${metrics.total_requests || 0}`);
   * console.log(`Errors: ${metrics.total_errors || 0}`);
   * ```
   */
  async getAgentMetrics(): Promise<MetricsSnapshot> {
    await this.ensureAgentClient();
    return this.agentClient!.get<MetricsSnapshot>('/metrics/snapshot');
  }

  async getHealth(): Promise<HealthResponse> {
    await this.ensureAgentClient();
    return this.agentClient!.get<HealthResponse>('/health');
  }

  async getAgentInfo(): Promise<InfoResponse> {
    await this.ensureAgentClient();
    return this.agentClient!.get<InfoResponse>('/info');
  }

  // ==========================================================================
  // WEBSOCKET STREAMING
  // ==========================================================================

  async *runCodeStream(code: string, options?: CodeExecutionOptions): AsyncIterableIterator<StreamMessage> {
    await this.ensureWSClient();

    const ws = await this.wsClient!.connect('/execute/stream');

    // Send execute request
    this.wsClient!.send(ws, {
      type: 'execute',
      code,
      language: options?.language ?? 'python',
      timeout: options?.timeout ?? 60,
      workdir: options?.workingDir ?? '/workspace',
      env: options?.env,
    });

    // Stream messages
    for await (const message of this.wsClient!.messages(ws)) {
      yield message as StreamMessage;
      if (message.type === 'complete') {
        ws.close();
        break;
      }
    }
  }

  // File watching is in Files resource via lazy-loading
  async *watchFiles(path = '/workspace'): AsyncIterableIterator<FileChangeMessage> {
    await this.ensureWSClient();

    const ws = await this.wsClient!.connect('/files/watch');

    // Send watch request
    this.wsClient!.send(ws, { action: 'watch', path });

    // Stream change events
    for await (const message of this.wsClient!.messages(ws)) {
      yield message as FileChangeMessage;
    }
  }

  // ==========================================================================
  // JWT TOKEN MANAGEMENT
  // ==========================================================================

  /**
   * Refresh JWT token for agent authentication
   * Called automatically when token is about to expire (<1 hour left)
   */
  async refreshToken(): Promise<void> {
    const response = await this.publicClient.post<any>(
      `/v1/sandboxes/${this.sandboxId}/token/refresh`
    );
    
    if (response.auth_token && response.token_expires_at) {
      tokenCache.set(this.sandboxId, {
        token: response.auth_token,
        expiresAt: new Date(response.token_expires_at),
      });
      
      // Update agent client's JWT token if already initialized
      if (this.agentClient) {
        this.agentClient.updateJwtToken(response.auth_token);
      }
      
      // Update WebSocket client's JWT token if already initialized
      if (this.wsClient) {
        this.wsClient.updateJwtToken(response.auth_token);
      }
    }
  }

  /**
   * Ensure JWT token is valid (not expired or expiring soon)
   * Auto-refreshes if less than 1 hour remaining
   */
  private async ensureValidToken(): Promise<void> {
    const tokenData = tokenCache.get(this.sandboxId);
    
    if (!tokenData) {
      // No token yet, try to refresh
      await this.refreshToken();
      return;
    }
    
    // Check if token expires soon (< 1 hour)
    const now = new Date();
    const hoursLeft = (tokenData.expiresAt.getTime() - now.getTime()) / (1000 * 60 * 60);
    
    if (hoursLeft < 1) {
      // Refresh token
      await this.refreshToken();
    }
  }

  /**
   * Get current JWT token (for advanced use cases)
   * Automatically refreshes if needed
   */
  async getToken(): Promise<string> {
    await this.ensureValidToken();
    const tokenData = tokenCache.get(this.sandboxId);
    
    if (!tokenData) {
      throw new Error('No JWT token available for sandbox');
    }
    
    return tokenData.token;
  }

  // ==========================================================================
  // PRIVATE HELPERS
  // ==========================================================================

  private ensureAgentClientSync(): void {
    if (!this.agentClient) {
      throw new Error('Agent client not initialized. This should not happen after Sandbox.create(). If using Sandbox.get(), call getInfo() first.');
    }
  }

  private ensureWSClientSync(): void {
    if (!this.wsClient) {
      throw new Error('WebSocket client not initialized. This should not happen after Sandbox.create(). If using Sandbox.get(), call getInfo() first.');
    }
  }

  private async ensureAgentClient(): Promise<void> {
    if (!this.agentClient) {
      // Auto-initialize by calling getInfo() to fetch public_host
      await this.getInfo();
    }
    
    // Ensure JWT token is valid before agent calls
    await this.ensureValidToken();
  }

  private async ensureWSClient(): Promise<void> {
    if (!this.wsClient) {
      // Auto-initialize by calling getInfo() to fetch public_host
      await this.getInfo();
    }
    
    // Ensure JWT token is valid before WebSocket calls
    await this.ensureValidToken();
  }

  /**
   * Initialize agent client (call this after create or when needed)
   */
  async init(): Promise<void> {
    const info = await this.getInfo();
    
    // Ensure we have a valid JWT token
    await this.ensureValidToken();
    const token = await this.getToken();
    
    this.agentClient = new HTTPClient({
      baseURL: info.publicHost,
      timeout: 60000,
      maxRetries: 3,
      jwtToken: token,
      // ✅ FIXED: Auto-refresh token on 401 Unauthorized
      tokenRefreshCallback: async () => {
        await this.refreshToken();
        const tokenData = tokenCache.get(this.sandboxId);
        return tokenData?.token || null;
      },
    });
    this.wsClient = new WSClient(info.publicHost, token);
  }
}

