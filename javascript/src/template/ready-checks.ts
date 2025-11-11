/**
 * Ready Check Helpers
 */

import { ReadyCheck, ReadyCheckType } from './types.js';

/**
 * Wait for TCP port to be open
 */
export function waitForPort(port: number, timeout: number = 30000, interval: number = 2000): ReadyCheck {
  return {
    type: ReadyCheckType.PORT,
    port,
    timeout,
    interval,
  };
}

/**
 * Wait for HTTP URL to return 200
 */
export function waitForURL(url: string, timeout: number = 30000, interval: number = 2000): ReadyCheck {
  return {
    type: ReadyCheckType.URL,
    url,
    timeout,
    interval,
  };
}

/**
 * Wait for file to exist
 */
export function waitForFile(path: string, timeout: number = 30000, interval: number = 2000): ReadyCheck {
  return {
    type: ReadyCheckType.FILE,
    path,
    timeout,
    interval,
  };
}

/**
 * Wait for process to be running
 */
export function waitForProcess(processName: string, timeout: number = 30000, interval: number = 2000): ReadyCheck {
  return {
    type: ReadyCheckType.PROCESS,
    processName,
    timeout,
    interval,
  };
}

/**
 * Wait for command to exit with code 0
 */
export function waitForCommand(command: string, timeout: number = 30000, interval: number = 2000): ReadyCheck {
  return {
    type: ReadyCheckType.COMMAND,
    command,
    timeout,
    interval,
  };
}

