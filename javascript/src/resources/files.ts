/**
 * Files resource - File system operations
 */

import { HTTPClient } from '../client.js';
import type {
  FileListResponse,
  FileContentResponse,
  FileWriteOptions,
  EnhancedFileInfo,
} from '../types/index.js';
import { FileInfoImpl } from '../types/index.js';

export class Files {
  constructor(private client: HTTPClient) {}

  /**
   * Read text file contents
   */
  async read(path: string): Promise<string> {
    const response = await this.client.get<FileContentResponse>('/files/read', {
      params: { path },
    });
    return response.content;
  }

  /**
   * Read binary file contents
   */
  async readBytes(path: string): Promise<Buffer> {
    const response = await this.client.get<ArrayBuffer>('/files/read', {
      params: { path },
      responseType: 'arraybuffer',
    });
    return Buffer.from(response);
  }

  /**
   * Write text file
   */
  async write(path: string, content: string, options?: FileWriteOptions): Promise<void> {
    await this.client.post('/files/write', {
      path,
      content,
      overwrite: options?.overwrite ?? true,
    });
  }

  /**
   * Write binary file
   */
  async writeBytes(path: string, content: Buffer, options?: FileWriteOptions): Promise<void> {
    const base64 = content.toString('base64');
    await this.client.post('/files/write', {
      path,
      content: base64,
      encoding: 'base64',
      overwrite: options?.overwrite ?? true,
    });
  }

  /**
   * List directory contents
   */
  async list(path: string): Promise<EnhancedFileInfo[]> {
    const response = await this.client.get<FileListResponse>('/files/list', {
      params: { path },
    });
    return response.files.map((f) => new FileInfoImpl(f));
  }

  /**
   * Check if file/directory exists
   */
  async exists(path: string): Promise<boolean> {
    const response = await this.client.get<{ exists: boolean }>('/files/exists', {
      params: { path },
    });
    return response.exists;
  }

  /**
   * Remove file or directory
   */
  async remove(path: string): Promise<void> {
    await this.client.delete('/files/remove', {
      params: { path },
    });
  }

  /**
   * Create directory
   */
  async mkdir(path: string): Promise<void> {
    await this.client.post('/files/mkdir', { path });
  }

  /**
   * Upload file (multipart)
   */
  async upload(_localPath: string, _remotePath: string): Promise<void> {
    // Note: Requires FormData implementation for actual file uploads
    throw new Error('File upload not yet implemented - use write() for content');
  }

  /**
   * Download file
   */
  async download(path: string): Promise<Buffer> {
    return this.readBytes(path);
  }
}

