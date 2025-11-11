/**
 * Hopx SDK for TypeScript/JavaScript
 * 100% feature coverage - HTTP + WebSocket + Template Building
 */

// Main exports
export { Sandbox } from './sandbox.js';

// Template Building
export { Template, createTemplate } from './template/builder.js';
export { getLogs } from './template/build-flow.js';
export { 
  waitForPort, 
  waitForURL, 
  waitForFile, 
  waitForProcess, 
  waitForCommand 
} from './template/ready-checks.js';

// Resources
export { Files } from './resources/files.js';
export { Commands } from './resources/commands.js';
export { EnvironmentVariables } from './resources/env-vars.js';
export { Cache } from './resources/cache.js';
export { Desktop } from './resources/desktop.js';
export { Terminal } from './resources/terminal.js';

// Clients
export { HTTPClient } from './client.js';
export { WSClient } from './ws-client.js';

// Types
export * from './types/index.js';
export * from './template/types.js';

// Errors (explicit exports to avoid conflicts)
export {
  HopxError,
  APIError,
  AuthenticationError,
  NotFoundError,
  FileNotFoundError,
  FileOperationError,
  CodeExecutionError,
  CommandExecutionError,
  DesktopNotAvailableError,
  ResourceLimitError,
  RateLimitError,
  ServerError
} from './errors.js';

// Default export
export { Sandbox as default } from './sandbox.js';

