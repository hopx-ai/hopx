/**
 * Template Building Types
 */

/**
 * Step types for template building
 * 
 * @deprecated FROM is no longer used as a step type. Use the fromImage parameter
 * in the Template constructor or the from*Image() methods instead.
 */
export enum StepType {
  COPY = 'COPY',
  RUN = 'RUN',
  ENV = 'ENV',
  WORKDIR = 'WORKDIR',
  USER = 'USER',
  CMD = 'CMD',
}

export interface RegistryAuth {
  username: string;
  password: string;
}

export interface GCPRegistryAuth {
  serviceAccountJSON: string | object;
}

export interface AWSRegistryAuth {
  accessKeyId: string;
  secretAccessKey: string;
  region: string;
  sessionToken?: string;
}

export interface Step {
  type: StepType;
  args: string[];
  filesHash?: string;  // For COPY steps
  copyOptions?: CopyOptions;  // For COPY steps
  skipCache?: boolean;
  registryAuth?: RegistryAuth;
  gcpAuth?: GCPRegistryAuth;
  awsAuth?: AWSRegistryAuth;
}

export interface CopyOptions {
  owner?: string;
  permissions?: string;
}

export enum ReadyCheckType {
  PORT = 'port',
  URL = 'url',
  FILE = 'file',
  PROCESS = 'process',
  COMMAND = 'command',
}

export interface ReadyCheck {
  type: ReadyCheckType;
  port?: number;
  url?: string;
  path?: string;
  processName?: string;
  command?: string;
  timeout?: number;
  interval?: number;
}

export interface BuildOptions {
  /** Template name (unique identifier) */
  name: string;
  
  /** Hopx API key */
  apiKey: string;
  
  /** Base URL for Hopx API (default: https://api.hopx.dev) */
  baseURL?: string;
  
  /** Number of CPU cores (default: 2) */
  cpu?: number;
  
  /** Memory in megabytes (default: 2048) */
  memory?: number;
  
  /** Disk size in gigabytes (default: 10) */
  diskGB?: number;
  
  /** Skip build cache and rebuild from scratch (default: false) */
  skipCache?: boolean;
  
  /**
   * Whether to update an existing template with the same name.
   * 
   * - If `false` (default): Will fail if a template with this name already exists
   * - If `true`: Will update the existing template if it exists, or create new if it doesn't
   * 
   * @default false
   * 
   * @example
   * // Create or update template
   * await Template.build(template, {
   *   name: 'my-app',
   *   update: true,  // Won't fail if 'my-app' exists
   *   apiKey: process.env.HOPX_API_KEY
   * });
   */
  update?: boolean;
  
  /** Context path for file operations (default: current working directory) */
  contextPath?: string;
  
  /** Callback function for build log entries */
  onLog?: (log: LogEntry) => void;

  /** Callback function for build progress updates (0-100) */
  onProgress?: (progress: number) => void;

  /**
   * Maximum time (in seconds) to wait for template activation after build completes.
   *
   * Template activation has multiple phases:
   * - building → active → publishing → active (stable)
   *
   * The SDK waits for 2 consecutive "active" status checks to ensure stability.
   *
   * @default 2700 (45 minutes) or HOPX_TEMPLATE_BAKE_SECONDS env var
   *
   * @example
   * await Template.build(template, {
   *   name: 'my-template',
   *   apiKey: '...',
   *   templateActivationTimeout: 1800  // 30 minutes
   * });
   */
  templateActivationTimeout?: number;
}

export interface BuildResult {
  buildID: string;
  templateID: string;
  duration: number;
  createVM: (options: CreateVMOptions) => Promise<VM>;
  getLogs: (offset?: number) => Promise<LogsResponse>;
}

export interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
}

export interface StatusUpdate {
  status: string;
  progress: number;
  currentStep?: string;
}

export interface CreateVMOptions {
  alias?: string;
  cpu?: number;
  memory?: number;
  diskGB?: number;
  envVars?: Record<string, string>;
}

export interface VM {
  vmID: string;
  templateID: string;
  status: string;
  ip: string;
  agentUrl: string;
  startedAt: string;
  delete: () => Promise<void>;
}

export interface UploadLinkResponse {
  present: boolean;
  uploadUrl?: string;
  expiresAt?: string;
  filesHash?: string;
}

export interface BuildResponse {
  buildID: string;
  templateID: string;
  status: string;
  logsUrl: string;
  requestId?: string;  // API request ID for debugging
}

export interface BuildStatusResponse {
  buildID: string;
  templateID: string;
  status: string;
  progress: number;
  currentStep?: string;
  startedAt: string;
  completedAt?: string;
  errorMessage?: string;
  buildDurationMs?: number;
  requestId?: string;  // API request ID for debugging
}

export interface LogsResponse {
  logs: string;
  offset: number;
  status: string;
  complete: boolean;
  requestId?: string;
}

