/**
 * Commands resource - Shell command execution
 */

import { HTTPClient } from '../client.js';
import type { CommandResponse, CommandOptions } from '../types/index.js';

export class Commands {
  constructor(private client: HTTPClient) {}

  /**
   * Run shell command
   */
  async run(command: string, options?: CommandOptions): Promise<CommandResponse> {
    const response = await this.client.post<CommandResponse>(
      options?.background ? '/commands/background' : '/commands/run',
      {
        command,
        timeout: options?.timeout ?? 30,
        working_dir: options?.workingDir ?? '/workspace',
        env: options?.env,
      }
    );
    return response;
  }

  /**
   * Run command in background
   */
  async runBackground(command: string, options?: Omit<CommandOptions, 'background'>): Promise<{ process_id: string }> {
    const response = await this.client.post<{ process_id: string }>('/commands/background', {
      command,
      timeout: options?.timeout ?? 300,
      working_dir: options?.workingDir ?? '/workspace',
      env: options?.env,
    });
    return response;
  }
}

