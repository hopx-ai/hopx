/**
 * Enhanced TypeScript types with convenience properties
 * Combines auto-generated types with developer experience improvements
 */

export * from './generated.js';
import type {
  ExecuteResponse,
  FileInfo as GeneratedFileInfo,
  RichOutput,
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

  constructor(data: ExecuteResponse & { richOutputs?: RichOutput[] }) {
    this.success = data.success;
    this.stdout = data.stdout;
    this.stderr = data.stderr;
    this.exit_code = data.exit_code;
    this.execution_time = data.execution_time;
    this.richOutputs = data.richOutputs;
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
}

export interface SandboxInfo {
  sandboxId: string;
  templateName?: string;
  templateId?: string;
  status: string;
  publicHost: string;
  createdAt?: string;
  vcpu?: number;
  memoryMb?: number;
  diskGb?: number;
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
  id: string;
  name: string;
  displayName: string;
  description?: string;
  category?: string;
  language?: string;
  icon?: string;
  defaultResources?: TemplateResources;
  minResources?: TemplateResources;
  maxResources?: TemplateResources;
  features?: string[];
  tags?: string[];
  popularityScore?: number;
  docsUrl?: string;
  isActive?: boolean;
  status?: string;  // ✅ NEW: Template status (building, publishing, active, failed)
}

// =============================================================================
// CODE EXECUTION OPTIONS
// =============================================================================

export interface CodeExecutionOptions {
  language?: string;
  timeout?: number;
  env?: Record<string, string>;
  workingDir?: string;
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

