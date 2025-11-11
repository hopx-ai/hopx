/**
 * Auto-generated TypeScript types from OpenAPI Specification v3.1.2
 * DO NOT EDIT MANUALLY - Generated from openapi_specs_3.1.md
 */

// =============================================================================
// ENUMS
// =============================================================================

export enum Language {
  Python = 'python',
  JavaScript = 'javascript',
  Bash = 'bash',
  Go = 'go',
}

export enum ErrorCode {
  METHOD_NOT_ALLOWED = 'METHOD_NOT_ALLOWED',
  INVALID_JSON = 'INVALID_JSON',
  MISSING_PARAMETER = 'MISSING_PARAMETER',
  PATH_NOT_ALLOWED = 'PATH_NOT_ALLOWED',
  FILE_NOT_FOUND = 'FILE_NOT_FOUND',
  FILE_ALREADY_EXISTS = 'FILE_ALREADY_EXISTS',
  DIRECTORY_NOT_FOUND = 'DIRECTORY_NOT_FOUND',
  FILE_OPERATION_FAILED = 'FILE_OPERATION_FAILED',
  INVALID_PATH = 'INVALID_PATH',
  PERMISSION_DENIED = 'PERMISSION_DENIED',
  COMMAND_FAILED = 'COMMAND_FAILED',
  EXECUTION_TIMEOUT = 'EXECUTION_TIMEOUT',
  EXECUTION_FAILED = 'EXECUTION_FAILED',
  PROCESS_NOT_FOUND = 'PROCESS_NOT_FOUND',
  DESKTOP_NOT_AVAILABLE = 'DESKTOP_NOT_AVAILABLE',
  INVALID_REQUEST = 'INVALID_REQUEST',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
}

export enum ExecutionStatus {
  Running = 'running',
  Completed = 'completed',
  Failed = 'failed',
  Timeout = 'timeout',
}

export enum RichOutputType {
  Plot = 'plot',
  Image = 'image',
  DataFrame = 'dataframe',
  HTML = 'html',
  ImagePng = 'image/png',
  TextHtml = 'text/html',
  ApplicationJson = 'application/json',
  TextPlain = 'text/plain',
}

export enum FileEventType {
  Created = 'created',
  Modified = 'modified',
  Deleted = 'deleted',
  Renamed = 'renamed',
}

// =============================================================================
// SYSTEM & HEALTH
// =============================================================================

export interface HealthResponse {
  status: string;
  uptime_seconds: number;
  version: string;
}

export interface Features {
  code_execution: boolean;
  file_operations: boolean;
  process_management: boolean;
  desktop: boolean;
  ipython: boolean;
}

export interface InfoResponse {
  version: string;
  uptime_seconds: number;
  features: Features;
  endpoints: Record<string, string>;
}

export interface SystemMetrics {
  cpu: {
    usage_percent: number;
    cores: number;
  };
  memory: {
    total: number;
    used: number;
    free: number;
    usage_percent: number;
  };
  disk: {
    total: number;
    used: number;
    free: number;
    usage_percent: number;
  };
}

export interface MetricsSnapshot {
  uptime_seconds: number;
  total_executions: number;
  active_executions: number;
  requests_total: number;
  error_count: number;
  avg_duration_ms: number;
  p95_duration_ms: number;
  system?: SystemMetrics;
  process?: {
    count: number;
    running: number;
  };
  cache?: {
    size: number;
    hits: number;
    misses: number;
    hit_rate: number;
  };
}

// =============================================================================
// EXECUTION
// =============================================================================

export interface ExecuteRequest {
  code: string;
  language?: Language;
  timeout?: number;
  working_dir?: string;
  env?: Record<string, string>;
}

export interface ExecuteResponse {
  success: boolean;
  stdout: string;
  stderr: string;
  exit_code: number;
  execution_time: number;
}

export interface RichOutput {
  type: RichOutputType;
  data: Record<string, any>;
  metadata?: Record<string, any>;
  timestamp?: string;
}

export interface BackgroundExecuteRequest extends ExecuteRequest {
  name?: string;
}

export interface BackgroundExecuteResponse {
  process_id: string;
  execution_id: string;
  status: ExecutionStatus;
}

export interface AsyncExecuteRequest extends ExecuteRequest {
  callback_url: string;
  callback_headers?: Record<string, string>;
  callback_signature_secret?: string;
}

export interface AsyncExecuteResponse {
  execution_id: string;
  status: ExecutionStatus;
  callback_url: string;
}

export interface ProcessInfo {
  process_id: string;
  name?: string;
  status: ExecutionStatus;
  started_at: string;
  execution_time?: number;
}

export interface ProcessListResponse {
  processes: ProcessInfo[];
}

// =============================================================================
// FILES
// =============================================================================

export interface FileInfo {
  name: string;
  path: string;
  size: number;
  is_dir: boolean;
  modified: string;
  permissions?: string;
}

export interface FileListResponse {
  files: FileInfo[];
  path: string;
}

export interface FileContentResponse {
  content: string;
  path: string;
  size: number;
}

export interface FileWriteRequest {
  path: string;
  content: string;
  overwrite?: boolean;
}

export interface FileResponse {
  path: string;
  success: boolean;
  message?: string;
}

// =============================================================================
// COMMANDS
// =============================================================================

export interface CommandRequest {
  command: string;
  timeout?: number;
  working_dir?: string;
  env?: Record<string, string>;
}

export interface CommandResponse {
  success: boolean;
  stdout: string;
  stderr: string;
  exit_code: number;
  execution_time: number;
}

// =============================================================================
// ENVIRONMENT VARIABLES
// =============================================================================

export interface EnvVarsResponse {
  env_vars: Record<string, string>;
}

export interface EnvVarsSetRequest {
  env_vars: Record<string, string>;
}

// =============================================================================
// CACHE
// =============================================================================

export interface CacheStatsResponse {
  cache: {
    size: number;
    max_size: number;
    total_hits: number;
    ttl: string;
  };
  timestamp: string;
}

export interface CacheClearResponse {
  message: string;
  entries_removed?: number;
}

// =============================================================================
// DESKTOP
// =============================================================================

export interface VNCInfo {
  url: string;
  password?: string;
  port: number;
  display: string;
}

export interface WindowInfo {
  id: string;
  title: string;
  x: number;
  y: number;
  width: number;
  height: number;
  focused: boolean;
}

export interface RecordingInfo {
  recording: boolean;
  output_file?: string;
  duration?: number;
}

export interface DisplayInfo {
  width: number;
  height: number;
  depth: number;
}

export interface ScreenshotResponse {
  image: string; // base64 encoded
  format: string;
  width: number;
  height: number;
}

// =============================================================================
// WEBSOCKET MESSAGES
// =============================================================================

export interface TerminalInputMessage {
  type: 'input';
  data: string;
}

export interface TerminalResizeMessage {
  type: 'resize';
  cols: number;
  rows: number;
}

export interface TerminalOutputMessage {
  type: 'output';
  data: string;
}

export interface TerminalExitMessage {
  type: 'exit';
  code: number;
}

export type TerminalMessage =
  | TerminalInputMessage
  | TerminalResizeMessage
  | TerminalOutputMessage
  | TerminalExitMessage;

export interface StreamExecuteMessage {
  type: 'execute';
  code: string;
  language?: Language;
  timeout?: number;
  working_dir?: string;
  env?: Record<string, string>;
}

export interface StreamStdoutMessage {
  type: 'stdout';
  data: string;
  timestamp: string;
}

export interface StreamStderrMessage {
  type: 'stderr';
  data: string;
  timestamp: string;
}

export interface StreamResultMessage {
  type: 'result';
  exit_code: number;
  execution_time: number;
  timestamp: string;
}

export interface StreamErrorMessage {
  type: 'error';
  error: string;
  code: ErrorCode;
  timestamp: string;
}

export interface StreamCompleteMessage {
  type: 'complete';
  success: boolean;
}

export type StreamMessage =
  | StreamExecuteMessage
  | StreamStdoutMessage
  | StreamStderrMessage
  | StreamResultMessage
  | StreamErrorMessage
  | StreamCompleteMessage;

export interface FileWatchMessage {
  action: 'watch';
  path: string;
}

export interface FileChangeMessage {
  type: 'change';
  path: string;
  event: FileEventType;
  timestamp: string;
}

// =============================================================================
// ERROR
// =============================================================================

export interface ErrorResponse {
  error: string;
  code?: ErrorCode;
  message?: string;
  path?: string;
  details?: Record<string, any>;
}

