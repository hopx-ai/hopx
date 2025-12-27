/**
 * Enhanced TypeScript types with convenience properties
 * Combines auto-generated types with developer experience improvements
 */

export * from './generated.js';
import type {
  ExecuteResponse,
  FileInfo as GeneratedFileInfo,
  RichOutput,
  CommandResponse,
  RecordingInfo,
  DisplayInfo,
  VNCInfo,
} from './generated.js';

// =============================================================================
// ENHANCED EXECUTION RESULT
// =============================================================================

export interface ExecutionResult extends ExecuteResponse {
  richOutputs?: RichOutput[];
  
  // Convenience properties
  readonly richCount: number;
  readonly failed: boolean;
}

export class ExecutionResultImpl implements ExecutionResult {
  success: boolean;
  stdout: string;
  stderr: string;
  exit_code: number;
  execution_time: number;
  richOutputs?: RichOutput[];

  // New fields from Python SDK v0.3.0
  timestamp?: string;
  language?: string;
  svg?: string;
  markdown?: string;
  html?: string;
  jsonOutput?: any;
  png?: string;
  result?: string;

  constructor(data: ExecuteResponse & { richOutputs?: RichOutput[]; timestamp?: string; language?: string; svg?: string; markdown?: string; html?: string; jsonOutput?: any; png?: string; result?: string }) {
    this.success = data.success;
    this.stdout = data.stdout;
    this.stderr = data.stderr;
    this.exit_code = data.exit_code;
    this.execution_time = data.execution_time;
    this.richOutputs = data.richOutputs;
    this.timestamp = data.timestamp;
    this.language = data.language;
    this.svg = data.svg;
    this.markdown = data.markdown;
    this.html = data.html;
    this.jsonOutput = data.jsonOutput;
    this.png = data.png;
    this.result = data.result;
  }

  // Convenience getters (camelCase)
  get exitCode(): number {
    return this.exit_code;
  }

  get executionTime(): number {
    return this.execution_time;
  }

  get richCount(): number {
    return this.richOutputs?.length ?? 0;
  }

  get failed(): boolean {
    return !this.success;
  }

  get hasRichOutput(): boolean {
    return !!(
      this.richOutputs?.length ||
      this.svg ||
      this.markdown ||
      this.html ||
      this.jsonOutput ||
      this.png ||
      this.result
    );
  }

  toString(): string {
    const status = this.success ? '✅' : '❌';
    return `ExecutionResult ${status} time=${this.execution_time.toFixed(3)}s rich=${this.richCount}`;
  }
}

// =============================================================================
// ENHANCED FILE INFO
// =============================================================================

export interface EnhancedFileInfo extends GeneratedFileInfo {
  // Convenience properties
  readonly sizeKb: number;
  readonly sizeMb: number;
  readonly isFile: boolean;
  readonly extension: string;
}

export class FileInfoImpl implements EnhancedFileInfo {
  name: string;
  path: string;
  size: number;
  is_dir: boolean;
  modified: string;
  permissions?: string;

  constructor(data: GeneratedFileInfo) {
    this.name = data.name;
    this.path = data.path;
    this.size = data.size;
    this.is_dir = data.is_dir;
    this.modified = data.modified;
    this.permissions = data.permissions;
  }

  // Convenience getters (camelCase)
  get isDir(): boolean {
    return this.is_dir;
  }

  get modifiedTime(): string {
    return this.modified;
  }

  get sizeKb(): number {
    return this.size / 1024;
  }

  get sizeMb(): number {
    return this.size / (1024 * 1024);
  }

  get isFile(): boolean {
    return !this.is_dir;
  }

  get extension(): string {
    if (this.is_dir) return '';
    const parts = this.name.split('.');
    return parts.length > 1 ? parts[parts.length - 1]! : '';
  }

  toString(): string {
    const type = this.is_dir ? '📁' : '📄';
    return `${type} ${this.name} (${this.sizeKb.toFixed(2)}KB)`;
  }
}

// =============================================================================
// SANDBOX OPTIONS
// =============================================================================

export interface SandboxCreateOptions {
  template?: string;               // Template name
  templateId?: string;             // Template ID
  region?: string;
  timeout?: number;                // DEPRECATED: Use timeoutSeconds instead (HTTP timeout for create request)
  timeoutSeconds?: number;         // Auto-kill timeout in seconds (optional, default: no timeout)
  internetAccess?: boolean;        // Enable internet access (optional, default: true)
  envVars?: Record<string, string>;
  apiKey?: string;
  baseURL?: string;
  onExpiringSoon?: (info: ExpiryInfo) => void;  // Called when sandbox is about to expire
  expiryWarningThreshold?: number;  // Seconds before expiry to trigger warning (default: 300)
}

export interface SandboxInfo {
  sandboxId: string;
  templateName?: string;
  templateId?: string;
  organizationId: number;           // Organization ID
  nodeId?: string;                  // Node ID where VM is running
  region?: string;                  // Region
  status: string;                   // Sandbox status (running, stopped, paused, creating)
  publicHost: string;               // Public URL to access sandbox
  directUrl?: string;               // Direct VM URL (alternative to public_host)
  previewUrl?: string;              // Preview URL for sandbox
  resources?: {                     // Resource allocation
    vcpu: number;
    memoryMb: number;
    diskMb: number;
  };
  internetAccess?: boolean;         // Whether VM has internet access
  liveMode?: boolean;               // True for production, false for test
  timeoutSeconds?: number;          // Auto-kill timeout in seconds (null = no timeout)
  expiresAt?: string;               // Timestamp when VM will be auto-killed (null = no timeout)
  createdAt?: string;               // Creation timestamp

  // Deprecated/legacy fields (kept for backward compatibility)
  startedAt?: string;               // [Legacy] When sandbox started
  endAt?: string;                   // [Legacy] Alias for expiresAt
  vcpu?: number;                    // [Deprecated] Use resources.vcpu instead
  memoryMb?: number;                // [Deprecated] Use resources.memoryMb instead
  diskGb?: number;                  // [Deprecated] Use resources.diskMb/1024 instead
}

// =============================================================================
// TEMPLATE INFO
// =============================================================================

export interface TemplateResources {
  vcpu?: number;
  memoryMb?: number;
  diskGb?: number;
}

export interface TemplateInfo {
  id: string;                       // Template ID
  name: string;                     // Template name (slug)
  displayName: string;              // Display name
  description?: string;             // Description
  category?: string;                // Category
  language?: string;                // Primary language
  icon?: string;                    // Icon URL or emoji
  defaultResources?: TemplateResources;
  minResources?: TemplateResources;
  maxResources?: TemplateResources;
  features?: string[];
  tags?: string[];
  popularityScore?: number;
  docsUrl?: string;
  isActive?: boolean;               // Whether template is active
  isPublic?: boolean;               // Whether template is public (vs organization-specific)
  status?: string;                  // Template status: pending, building, active, failed, archived
  buildId?: string;                 // Build ID (for logs)
  organizationId?: string;          // Organization ID (if organization-specific)
  createdAt?: string;               // Creation timestamp
  updatedAt?: string;               // Last update timestamp
  object?: string;                  // Object type (always 'template')
  requestId?: string;               // Request ID for this operation
}

// =============================================================================
// ENHANCED COMMAND RESULT
// =============================================================================

export interface CommandResult extends CommandResponse {
  // Convenience properties
  readonly isSuccess: boolean;
}

export class CommandResultImpl implements CommandResult {
  success: boolean;
  stdout: string;
  stderr: string;
  exit_code: number;
  execution_time: number;
  command?: string;
  pid?: number;
  timestamp?: string;

  constructor(data: CommandResponse) {
    this.success = data.success;
    this.stdout = data.stdout;
    this.stderr = data.stderr;
    this.exit_code = data.exit_code;
    this.execution_time = data.execution_time;
    this.command = data.command;
    this.pid = data.pid;
    this.timestamp = data.timestamp;
  }

  // Convenience getters (camelCase)
  get exitCode(): number {
    return this.exit_code;
  }

  get executionTime(): number {
    return this.execution_time;
  }

  get isSuccess(): boolean {
    return this.exit_code === 0;
  }

  toString(): string {
    const status = this.isSuccess ? '✅' : '❌';
    return `CommandResult ${status} exit=${this.exit_code} time=${this.execution_time.toFixed(3)}s`;
  }
}

// =============================================================================
// ENHANCED RECORDING INFO
// =============================================================================

export class RecordingInfoImpl implements RecordingInfo {
  recording_id?: string;
  recording: boolean;
  status?: string;
  start_time?: string;
  end_time?: string;
  duration?: number;
  file_path?: string;
  output_file?: string;
  file_size?: number;
  format?: string;

  constructor(data: RecordingInfo) {
    this.recording_id = data.recording_id;
    this.recording = data.recording;
    this.status = data.status;
    this.start_time = data.start_time;
    this.end_time = data.end_time;
    this.duration = data.duration;
    this.file_path = data.file_path;
    this.output_file = data.output_file;
    this.file_size = data.file_size;
    this.format = data.format;
  }

  get isRecording(): boolean {
    return this.status === 'recording' || this.recording;
  }

  get isReady(): boolean {
    return this.status === 'stopped';
  }

  get recordingId(): string | undefined {
    return this.recording_id;
  }

  get startTime(): string | undefined {
    return this.start_time;
  }

  get endTime(): string | undefined {
    return this.end_time;
  }

  get filePath(): string | undefined {
    return this.file_path || this.output_file;
  }

  get fileSize(): number | undefined {
    return this.file_size;
  }
}

// =============================================================================
// ENHANCED DISPLAY INFO
// =============================================================================

export class DisplayInfoImpl implements DisplayInfo {
  width: number;
  height: number;
  depth: number;
  refresh_rate?: number;
  displays?: Array<{
    id?: number;
    name?: string;
    width?: number;
    height?: number;
    primary?: boolean;
  }>;

  constructor(data: DisplayInfo) {
    this.width = data.width;
    this.height = data.height;
    this.depth = data.depth;
    this.refresh_rate = data.refresh_rate;
    this.displays = data.displays;
  }

  get resolution(): string {
    return `${this.width}x${this.height}`;
  }

  get refreshRate(): number | undefined {
    return this.refresh_rate;
  }
}

// =============================================================================
// ENHANCED VNC INFO
// =============================================================================

export class VNCInfoImpl implements VNCInfo {
  url: string;
  password?: string;
  port: number;
  display: string;

  constructor(data: VNCInfo) {
    this.url = data.url;
    this.password = data.password;
    this.port = data.port;
    this.display = data.display;
  }

  get running(): boolean {
    return true; // If we have VNC info, VNC is running
  }
}

// =============================================================================
// CODE EXECUTION OPTIONS
// =============================================================================

export interface CodeExecutionOptions {
  language?: string;
  timeout?: number;
  env?: Record<string, string>;
  workingDir?: string;
  preflight?: boolean;  // Run health check before execution
}

export interface AsyncExecutionOptions extends CodeExecutionOptions {
  callbackUrl: string;
  callbackHeaders?: Record<string, string>;
  callbackSignatureSecret?: string;
}

export interface BackgroundExecutionOptions extends CodeExecutionOptions {
  name?: string;
}

// =============================================================================
// COMMAND OPTIONS
// =============================================================================

export interface CommandOptions {
  timeout?: number;
  env?: Record<string, string>;
  workingDir?: string;
  background?: boolean;
}

// =============================================================================
// FILE OPTIONS
// =============================================================================

export interface FileWriteOptions {
  overwrite?: boolean;
  mode?: string;  // File permissions (e.g., '0644', '0755')
}

export interface FileListOptions {
  recursive?: boolean;
}

// =============================================================================
// DESKTOP OPTIONS
// =============================================================================

export interface MouseClickOptions {
  button?: 'left' | 'right' | 'middle';
  clicks?: number;
}

export interface OCROptions {
  language?: string;
}

// =============================================================================
// WEBSOCKET OPTIONS
// =============================================================================

export interface TerminalOptions {
  timeout?: number;
}

export interface StreamOptions {
  timeout?: number;
}

export interface FileWatchOptions {
  timeout?: number;
}

// =============================================================================
// EXPIRY INFO
// =============================================================================

export interface ExpiryInfo {
  expiresAt: Date | null;
  timeToExpiry: number | null;  // seconds (negative if expired)
  isExpired: boolean;
  isExpiringSoon: boolean;  // < 5 minutes by default
  hasTimeout: boolean;
}

