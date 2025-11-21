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
  status: string;                   // Health status (e.g., 'healthy')
  agent?: string;                   // Agent name (e.g., 'hopx-vm-agent-desktop')
  version: string;                  // Agent version
  uptime?: string;                  // Uptime as string (e.g., '2h34m12s')
  uptime_seconds: number;           // [Deprecated] Use uptime instead
  go_version?: string;              // Go version (e.g., 'go1.22.2')
  vm_id?: string;                   // VM ID
  features?: {                      // Available features
    code_execution?: boolean;
    file_operations?: boolean;
    terminal_access?: boolean;
    websocket_streaming?: boolean;
    rich_output?: boolean;
    background_jobs?: boolean;
    ipython_kernel?: boolean;
    system_metrics?: boolean;
    languages?: string[];
  };
  active_streams?: number;          // Number of active streams
}

export interface Features {
  code_execution: boolean;
  file_operations: boolean;
  process_management: boolean;
  desktop: boolean;
  ipython: boolean;
}

export interface InfoResponse {
  vm_id?: string;                   // VM ID
  agent?: string;                   // Agent name
  agent_version?: string;           // Agent version
  version: string;                  // [Deprecated] Use agent_version instead
  os?: string;                      // Operating system
  arch?: string;                    // Architecture (e.g., 'amd64')
  go_version?: string;              // Go version
  vm_ip?: string;                   // VM IP address
  vm_port?: string;                 // VM port
  start_time?: string;              // Start time
  uptime?: number;                  // Uptime in seconds
  uptime_seconds: number;           // [Deprecated] Use uptime instead
  endpoints?: Record<string, string>; // Map of endpoint names to HTTP methods + paths
  features?: Record<string, any>;   // Available features
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
  workdir?: string;  // FIXED: API expects "workdir" not "working_dir"
  env?: Record<string, string>;
}

export interface ExecuteResponse {
  success: boolean;
  stdout: string;
  stderr: string;
  exit_code: number;
  execution_time: number;
  timestamp?: string;               // Execution timestamp
  language?: string;                // Programming language used
  // Rich output fields (from /execute/rich endpoint)
  svg?: string;                     // SVG output (image/svg+xml)
  markdown?: string;                // Markdown output (text/markdown)
  html?: string;                    // HTML output (text/html)
  json_output?: any;                // JSON output (application/json)
  png?: string;                     // PNG output base64 (image/png)
  result?: string;                  // Rich output from Jupyter (when available)
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
  execution_id?: string;            // Execution identifier
  name?: string;
  status: ExecutionStatus;
  language?: string;                // Programming language
  started_at: string;
  end_time?: string;                // End time (if completed)
  exit_code?: number;               // Exit code
  duration?: number;                // Duration in seconds
  pid?: number;                     // System process ID
  execution_time?: number;          // [Deprecated] Use duration instead
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
  workdir?: string;  // FIXED: API expects "workdir" not "working_dir"
  env?: Record<string, string>;
}

export interface CommandResponse {
  success: boolean;
  stdout: string;
  stderr: string;
  exit_code: number;
  execution_time: number;
  command?: string;                 // Command that was executed
  pid?: number;                     // Process ID
  timestamp?: string;               // Execution timestamp
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
  id: string;                       // Window ID (X11 window identifier)
  title: string;                    // Window title
  x: number;                        // X coordinate
  y: number;                        // Y coordinate
  width: number;                    // Window width
  height: number;                   // Window height
  focused: boolean;                 // [Deprecated] Use isActive instead
  isActive?: boolean;               // Whether this window is currently active
  isMinimized?: boolean;            // Whether this window is minimized
  pid?: number;                     // Process ID owning this window
}

export interface RecordingInfo {
  recording_id?: string;            // Unique recording identifier
  recording: boolean;               // [Deprecated] Check status === 'recording'
  status?: string;                  // Recording status: 'recording', 'stopped', 'failed'
  start_time?: string;              // Recording start time
  end_time?: string;                // Recording end time (if stopped)
  duration?: number;                // Recording duration in seconds
  file_path?: string;               // Path to recorded video file
  output_file?: string;             // [Deprecated] Use file_path instead
  file_size?: number;               // Video file size in bytes
  format?: string;                  // Video format: 'mp4', 'webm'
}

export interface DisplayInfo {
  width: number;                    // Display width in pixels
  height: number;                   // Display height in pixels
  depth: number;                    // Color depth (bits per pixel)
  refresh_rate?: number;            // Refresh rate in Hz
  displays?: Array<{                // List of available displays (multi-monitor support)
    id?: number;
    name?: string;
    width?: number;
    height?: number;
    primary?: boolean;
  }>;
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
  workdir?: string;  // FIXED: API expects "workdir" not "working_dir"
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

