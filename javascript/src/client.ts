/**
 * HTTP client with retry logic and error handling
 */

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import http from 'http';
import https from 'https';
import {
  APIError,
  AuthenticationError,
  RateLimitError,
  ServerError,
  FileNotFoundError,
  FileOperationError,
  DesktopNotAvailableError,
  SandboxExpiredError,
  TokenExpiredError,
  ErrorCode,
} from './errors.js';

export interface ClientConfig {
  baseURL: string;
  apiKey?: string;
  jwtToken?: string;  // NEW: JWT token for agent authentication
  timeout?: number;
  maxRetries?: number;
}

export class HTTPClient {
  private client: AxiosInstance;
  private maxRetries: number;
  private jwtToken?: string;  // Store JWT token
  private tokenRefreshCallback?: () => Promise<string | null>;  // ✅ NEW: Token refresh callback

  constructor(config: ClientConfig & { tokenRefreshCallback?: () => Promise<string | null> }) {
    this.maxRetries = config.maxRetries ?? 3;
    this.jwtToken = config.jwtToken;
    this.tokenRefreshCallback = config.tokenRefreshCallback;

    // Try to get API key from config, then from environment variable
    const apiKey = config.apiKey || process.env['HOPX_API_KEY'];

    // Determine which auth header to use
    const authHeaders: Record<string, string> = {};
    if (this.jwtToken) {
      // For agent calls: use JWT Bearer token
      authHeaders['Authorization'] = `Bearer ${this.jwtToken}`;
    } else if (apiKey) {
      // For Public API calls: use X-API-Key
      authHeaders['X-API-Key'] = apiKey;
    }

    // Force IPv4 to avoid IPv6 timeout issues (270s delay)
    // Node.js dns.lookup defaults to IPv6 first, causing timeouts
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout ?? 60000,
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
      },
      // Force IPv4 resolution
      httpAgent: new http.Agent({ family: 4 }),
      httpsAgent: new https.Agent({ family: 4 }),
    });

    // Response interceptor for error handling
    // Note: Do NOT throw here for retryable errors (5xx) - let requestWithRetry handle them
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        const status = error.response?.status;
        // Pass through errors that requestWithRetry needs to handle:
        // - 5xx (retryable server errors)
        // - Network errors (retryable connectivity issues)
        // - 401 (token refresh - must remain as AxiosError for refresh logic)
        if (this.isRetryableError(error) || this.isNetworkError(error) || status === 401) {
          return Promise.reject(error); // Keep as AxiosError for retry/refresh
        }
        // For non-retryable errors, transform to custom error
        return this.handleError(error);
      }
    );
  }

  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.requestWithRetry(() => this.client.get<T>(url, config));
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.requestWithRetry(() => this.client.post<T>(url, data, config));
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.requestWithRetry(() => this.client.put<T>(url, data, config));
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.requestWithRetry(() => this.client.patch<T>(url, data, config));
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.requestWithRetry(() => this.client.delete<T>(url, config));
  }

  /**
   * Update JWT token for agent authentication
   * Used internally when token is refreshed
   */
  updateJwtToken(token: string): void {
    this.jwtToken = token;
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  private async requestWithRetry<T>(
    requestFn: () => Promise<{ data: T }>,
    attempt = 1
  ): Promise<T> {
    try {
      const response = await requestFn();
      return response.data;
    } catch (error) {
      // Handle 401 Unauthorized - try to refresh token (only on first attempt)
      if (axios.isAxiosError(error) && error.response?.status === 401 && this.tokenRefreshCallback && attempt === 1) {
        console.log('[SDK] Got 401 Unauthorized, attempting token refresh...');
        try {
          const newToken = await this.tokenRefreshCallback();
          if (newToken) {
            this.updateJwtToken(newToken);
            console.log('[SDK] Token refreshed, retrying request...');
            return this.requestWithRetry(requestFn, attempt + 1);  // Increment to prevent infinite loop
          }
        } catch (refreshError) {
          console.error('[SDK] Token refresh failed:', refreshError);
          // Fall through to normal error handling
        }
      }
      
      // Retry on 5xx errors and network errors
      if (
        attempt < this.maxRetries &&
        (this.isRetryableError(error) || this.isNetworkError(error))
      ) {
        const delay = Math.min(1000 * Math.pow(2, attempt - 1), 10000);
        await this.sleep(delay);
        return this.requestWithRetry(requestFn, attempt + 1);
      }
      
      // After all retries exhausted, handle error if it's still an AxiosError
      if (axios.isAxiosError(error)) {
        this.handleError(error);
      }
      throw error;
    }
  }

  private isRetryableError(error: any): boolean {
    if (!axios.isAxiosError(error)) return false;
    const status = error.response?.status;
    return status !== undefined && status >= 500 && status < 600;
  }

  private isNetworkError(error: any): boolean {
    return axios.isAxiosError(error) && !error.response;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  private handleError(error: AxiosError): never {
    const requestId = error.response?.headers?.['x-request-id'] as string | undefined;
    const status = error.response?.status;
    const data: any = error.response?.data;
    const errorCode = data?.code as ErrorCode | undefined;
    const message = String(data?.message || data?.error?.message || error.message || 'Unknown error');

    // Sandbox expiry detection (410 Gone or specific error codes)
    if (
      errorCode === ErrorCode.SANDBOX_EXPIRED ||
      status === 410 ||
      (status === 404 && message.toLowerCase().includes('sandbox') && message.toLowerCase().includes('not found'))
    ) {
      throw new SandboxExpiredError(message, {
        sandboxId: data?.sandbox_id,
        createdAt: data?.created_at,
        expiresAt: data?.expires_at,
        status: data?.status,
      }, requestId);
    }

    // Token expiry detection
    if (status === 401 && (errorCode === ErrorCode.TOKEN_EXPIRED || message.toLowerCase().includes('token expired'))) {
      throw new TokenExpiredError(message, requestId);
    }

    // Authentication errors (general)
    if (status === 401) {
      throw new AuthenticationError(message, requestId);
    }

    // Rate limiting
    if (status === 429) {
      throw new RateLimitError(message, requestId);
    }

    // File not found (404 or 403 with FILE_NOT_FOUND code)
    if (
      (status === 404 || status === 403) &&
      (errorCode === ErrorCode.FILE_NOT_FOUND || message?.includes('not found'))
    ) {
      const path = data?.path || '';
      throw new FileNotFoundError(path, message, requestId);
    }

    // File operation errors
    if (errorCode === ErrorCode.FILE_OPERATION_FAILED || errorCode === ErrorCode.PERMISSION_DENIED) {
      throw new FileOperationError(message, data?.path, errorCode, requestId);
    }

    // Desktop not available
    if (errorCode === ErrorCode.DESKTOP_NOT_AVAILABLE || status === 501) {
      throw new DesktopNotAvailableError(message, requestId);
    }

    // Server errors
    if (status && status >= 500) {
      throw new ServerError(message, errorCode, requestId);
    }

    // Generic API error
    throw new APIError(message, errorCode, requestId, status);
  }
}

