/**
 * Template Building Types
 */

export enum StepType {
  FROM = 'FROM',
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
  alias: string;
  apiKey: string;
  baseURL?: string;
  cpu?: number;
  memory?: number;
  diskGB?: number;
  skipCache?: boolean;
  contextPath?: string;
  onLog?: (log: LogEntry) => void;
  onProgress?: (progress: number) => void;
}

export interface BuildResult {
  buildID: string;
  templateID: string;
  duration: number;
  createVM: (options: CreateVMOptions) => Promise<VM>;
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
}

export interface BuildResponse {
  buildID: string;
  templateID: string;
  status: string;
  logsUrl: string;
}

export interface BuildStatusResponse {
  buildID: string;
  templateID: string;
  status: string;
  progress: number;
  currentStep?: string;
  startedAt: string;
  estimatedCompletion?: string;
  error?: string;
}

export interface LogsResponse {
  logs: string;
  offset: number;
  status: string;
  complete: boolean;
  requestId?: string;
}

