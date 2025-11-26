/**
 * Custom error classes for Hopx SDK
 */

export enum ErrorCode {
  // HTTP errors
  METHOD_NOT_ALLOWED = 'METHOD_NOT_ALLOWED',
  INVALID_JSON = 'INVALID_JSON',
  MISSING_PARAMETER = 'MISSING_PARAMETER',

  // File errors
  PATH_NOT_ALLOWED = 'PATH_NOT_ALLOWED',
  FILE_NOT_FOUND = 'FILE_NOT_FOUND',
  FILE_ALREADY_EXISTS = 'FILE_ALREADY_EXISTS',
  DIRECTORY_NOT_FOUND = 'DIRECTORY_NOT_FOUND',
  FILE_OPERATION_FAILED = 'FILE_OPERATION_FAILED',
  INVALID_PATH = 'INVALID_PATH',
  PERMISSION_DENIED = 'PERMISSION_DENIED',

  // Execution errors
  COMMAND_FAILED = 'COMMAND_FAILED',
  EXECUTION_TIMEOUT = 'EXECUTION_TIMEOUT',
  EXECUTION_FAILED = 'EXECUTION_FAILED',

  // Process errors
  PROCESS_NOT_FOUND = 'PROCESS_NOT_FOUND',

  // Desktop errors
  DESKTOP_NOT_AVAILABLE = 'DESKTOP_NOT_AVAILABLE',

  // System errors
  INVALID_REQUEST = 'INVALID_REQUEST',
  INTERNAL_ERROR = 'INTERNAL_ERROR',

  // Sandbox lifecycle errors
  SANDBOX_EXPIRED = 'SANDBOX_EXPIRED',
  SANDBOX_NOT_FOUND = 'SANDBOX_NOT_FOUND',
  SANDBOX_CREATING = 'SANDBOX_CREATING',
  SANDBOX_STOPPED = 'SANDBOX_STOPPED',
  TOKEN_EXPIRED = 'TOKEN_EXPIRED',
  TOKEN_INVALID = 'TOKEN_INVALID',

  // Template errors
  TEMPLATE_BUILD_FAILED = 'TEMPLATE_BUILD_FAILED',
}

export class HopxError extends Error {
  public readonly code?: ErrorCode;
  public readonly requestId?: string;
  public readonly statusCode?: number;

  constructor(message: string, code?: ErrorCode, requestId?: string, statusCode?: number) {
    super(message);
    this.name = 'HopxError';
    this.code = code;
    this.requestId = requestId;
    this.statusCode = statusCode;
    
    // Maintains proper stack trace for where our error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }
}

export class APIError extends HopxError {
  constructor(message: string, code?: ErrorCode, requestId?: string, statusCode?: number) {
    super(message, code, requestId, statusCode);
    this.name = 'APIError';
  }
}

export class AuthenticationError extends HopxError {
  constructor(message = 'Authentication failed', requestId?: string) {
    super(message, undefined, requestId, 401);
    this.name = 'AuthenticationError';
  }
}

export class RateLimitError extends HopxError {
  constructor(message = 'Rate limit exceeded', requestId?: string) {
    super(message, undefined, requestId, 429);
    this.name = 'RateLimitError';
  }
}

export class ServerError extends HopxError {
  constructor(message = 'Internal server error', code?: ErrorCode, requestId?: string) {
    super(message, code, requestId, 500);
    this.name = 'ServerError';
  }
}

export class FileNotFoundError extends HopxError {
  public readonly path: string;

  constructor(path: string, message?: string, requestId?: string) {
    super(message || `File not found: ${path}`, ErrorCode.FILE_NOT_FOUND, requestId, 404);
    this.name = 'FileNotFoundError';
    this.path = path;
  }
}

export class FileOperationError extends HopxError {
  public readonly path?: string;

  constructor(message: string, path?: string, code?: ErrorCode, requestId?: string) {
    super(message, code || ErrorCode.FILE_OPERATION_FAILED, requestId);
    this.name = 'FileOperationError';
    this.path = path;
  }
}

export class CommandExecutionError extends HopxError {
  public readonly command?: string;
  public readonly exitCode?: number;

  constructor(message: string, command?: string, exitCode?: number, requestId?: string) {
    super(message, ErrorCode.COMMAND_FAILED, requestId);
    this.name = 'CommandExecutionError';
    this.command = command;
    this.exitCode = exitCode;
  }
}

export class CodeExecutionError extends HopxError {
  public readonly language?: string;

  constructor(message: string, language?: string, code?: ErrorCode, requestId?: string) {
    super(message, code || ErrorCode.EXECUTION_FAILED, requestId);
    this.name = 'CodeExecutionError';
    this.language = language;
  }
}

export class DesktopNotAvailableError extends HopxError {
  constructor(message = 'Desktop features not available in this template', requestId?: string) {
    super(message, ErrorCode.DESKTOP_NOT_AVAILABLE, requestId, 400);
    this.name = 'DesktopNotAvailableError';
  }
}

export class NotFoundError extends HopxError {
  constructor(message: string, requestId?: string) {
    super(message, undefined, requestId, 404);
    this.name = 'NotFoundError';
  }
}

export class ResourceLimitError extends HopxError {
  constructor(message: string, requestId?: string) {
    super(message, undefined, requestId, 429);
    this.name = 'ResourceLimitError';
  }
}

/**
 * Metadata about sandbox state when an error occurs
 */
export interface SandboxErrorMetadata {
  sandboxId?: string;
  createdAt?: string;
  expiresAt?: string;
  timeToLive?: number;
  status?: string;
}

/**
 * Error thrown when sandbox has expired
 */
export class SandboxExpiredError extends HopxError {
  public readonly sandboxId?: string;
  public readonly createdAt?: string;
  public readonly expiresAt?: string;
  public readonly metadata: SandboxErrorMetadata;

  constructor(message: string, metadata: SandboxErrorMetadata, requestId?: string) {
    super(message, ErrorCode.SANDBOX_EXPIRED, requestId, 410);
    this.name = 'SandboxExpiredError';
    this.sandboxId = metadata.sandboxId;
    this.createdAt = metadata.createdAt;
    this.expiresAt = metadata.expiresAt;
    this.metadata = metadata;
  }
}

/**
 * Error thrown when JWT token has expired
 */
export class TokenExpiredError extends HopxError {
  constructor(message = 'JWT token has expired', requestId?: string) {
    super(message, ErrorCode.TOKEN_EXPIRED, requestId, 401);
    this.name = 'TokenExpiredError';
  }
}

/**
 * Metadata about template build state when an error occurs
 */
export interface TemplateBuildErrorMetadata {
  buildId?: string;
  templateId?: string;
  buildStatus?: string;
  logsUrl?: string;
  errorDetails?: string;
}

/**
 * Error thrown when template build fails
 * Provides comprehensive context for debugging build failures
 */
export class TemplateBuildError extends HopxError {
  public readonly buildId?: string;
  public readonly templateId?: string;
  public readonly buildStatus?: string;
  public readonly logsUrl?: string;
  public readonly errorDetails?: string;
  public readonly metadata: TemplateBuildErrorMetadata;

  constructor(message: string, metadata: TemplateBuildErrorMetadata, requestId?: string) {
    super(message, ErrorCode.TEMPLATE_BUILD_FAILED, requestId);
    this.name = 'TemplateBuildError';
    this.buildId = metadata.buildId;
    this.templateId = metadata.templateId;
    this.buildStatus = metadata.buildStatus;
    this.logsUrl = metadata.logsUrl;
    this.errorDetails = metadata.errorDetails;
    this.metadata = metadata;
  }
}

