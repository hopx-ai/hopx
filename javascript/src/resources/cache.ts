/**
 * Cache resource - Execution cache management
 */

import { HTTPClient } from '../client.js';
import type { CacheStatsResponse, CacheClearResponse } from '../types/index.js';

export class Cache {
  constructor(private client: HTTPClient) {}

  /**
   * Get cache statistics
   */
  async stats(): Promise<CacheStatsResponse> {
    return this.client.get<CacheStatsResponse>('/cache/stats');
  }

  /**
   * Clear execution cache
   */
  async clear(): Promise<CacheClearResponse> {
    return this.client.post<CacheClearResponse>('/cache/clear');
  }
}

