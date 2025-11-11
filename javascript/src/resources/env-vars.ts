/**
 * Environment Variables resource - Manage runtime env vars
 */

import { HTTPClient } from '../client.js';
import type { EnvVarsResponse } from '../types/index.js';

export class EnvironmentVariables {
  constructor(private client: HTTPClient) {}

  /**
   * Get all environment variables
   */
  async getAll(): Promise<Record<string, string>> {
    const response = await this.client.get<EnvVarsResponse>('/env');
    return response.env_vars || {};
  }

  /**
   * Get specific environment variable
   * Note: This fetches all env vars and returns the requested one.
   * For better performance, consider using getAll() if you need multiple values.
   */
  async get(key: string): Promise<string | undefined> {
    const vars = await this.getAll();
    return vars[key];
  }

  /**
   * Replace all environment variables (destructive - removes existing vars not in the provided object)
   * Use update() instead if you want to merge with existing variables.
   */
  async setAll(envVars: Record<string, string>): Promise<Record<string, string>> {
    const response = await this.client.put<EnvVarsResponse>('/env', { env_vars: envVars });
    return response.env_vars;
  }

  /**
   * Set a single environment variable (merges with existing variables)
   */
  async set(key: string, value: string): Promise<void> {
    await this.update({ [key]: value });
  }

  /**
   * Update environment variables (merge with existing)
   * This is safer than setAll() as it preserves existing variables.
   */
  async update(envVars: Record<string, string>): Promise<Record<string, string>> {
    const response = await this.client.patch<EnvVarsResponse>('/env', { 
      env_vars: envVars,
      merge: true  // ✅ FIXED: Agent requires merge flag
    });
    return response.env_vars || {};
  }

  /**
   * Delete a single environment variable by key
   * 
   * Note: Agent's DELETE /env removes ALL custom variables.
   * We work around this by fetching all vars, removing the specified one, and re-setting.
   */
  async delete(key: string): Promise<void> {
    // Get all current env vars
    const currentVars = await this.getAll();
    
    // Remove the specified variable
    if (key in currentVars) {
      delete currentVars[key];
      // Re-set all vars without the deleted one
      await this.setAll(currentVars);
    }
    // If key doesn't exist, silently succeed (idempotent operation)
  }
}

