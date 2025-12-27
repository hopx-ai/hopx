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
import FormData from 'form-data';
import { readFile } from 'fs/promises';
import { existsSync } from 'fs';

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
    const response = await this.client.get<ArrayBuffer>('/files/download', {
      params: { path },
      responseType: 'arraybuffer',
    });
    return Buffer.from(response);
  }

  /**
   * Write text file
   *
   * @param path - File path (e.g., '/workspace/output.txt')
   * @param content - File contents to write (string)
   * @param options - Write options (overwrite, mode)
   *
   * @example
   * ```typescript
   * // Basic write
   * await sandbox.files.write('/workspace/hello.py', 'print("Hello!")');
   *
   * // With custom permissions
   * await sandbox.files.write('/workspace/script.sh', '#!/bin/bash\necho hi', { mode: '0755' });
   * ```
   */
  async write(path: string, content: string, options?: FileWriteOptions): Promise<void> {
    await this.client.post('/files/write', {
      path,
      content,
      overwrite: options?.overwrite ?? true,
      mode: options?.mode ?? '0644',
    });
  }

  /**
   * Write binary file
   *
   * @param path - File path (e.g., '/workspace/image.png')
   * @param content - File contents to write (Buffer)
   * @param options - Write options (overwrite, mode)
   *
   * @example
   * ```typescript
   * // Save binary data
   * await sandbox.files.writeBytes('/workspace/image.png', imageBuffer);
   *
   * // With custom permissions
   * await sandbox.files.writeBytes('/workspace/data.bin', buffer, { mode: '0600' });
   * ```
   */
  async writeBytes(path: string, content: Buffer, options?: FileWriteOptions): Promise<void> {
    const base64 = content.toString('base64');
    await this.client.post('/files/write', {
      path,
      content: base64,
      encoding: 'base64',
      overwrite: options?.overwrite ?? true,
      mode: options?.mode ?? '0644',
    });
  }

  /**
   * List directory contents
   */
  async list(path: string): Promise<EnhancedFileInfo[]> {
    const response = await this.client.get<FileListResponse>('/files/list', {
      params: { path },
    });
    // Fix null handling: filter out null entries from response
    const files = (response.files || []).filter((f) => f != null);
    return files.map((f) => new FileInfoImpl(f));
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
   * Upload file from local filesystem to sandbox
   *
   * Uses multipart form-data to upload binary files efficiently.
   * Python reference: files.py lines 259-295
   *
   * @param localPath - Path to local file
   * @param remotePath - Destination path in sandbox
   *
   * @throws FileNotFoundError if local file doesn't exist
   * @throws FileOperationError if upload fails
   *
   * @example
   * ```typescript
   * // Upload local file to sandbox
   * await sandbox.files.upload('./data.csv', '/workspace/data.csv');
   *
   * // Upload large file
   * await sandbox.files.upload('./large.zip', '/workspace/large.zip');
   * ```
   */
  async upload(localPath: string, remotePath: string): Promise<void> {
    // Verify local file exists
    if (!existsSync(localPath)) {
      throw new Error(`Local file not found: ${localPath}`);
    }

    // Read file contents
    const fileBuffer = await readFile(localPath);

    // Create FormData with file and path
    const form = new FormData();
    form.append('file', fileBuffer, { filename: localPath.split('/').pop() || 'file' });
    form.append('path', remotePath);

    // Upload via multipart form-data
    await this.client.post('/files/upload', form, {
      headers: form.getHeaders(),
      timeout: 60000, // 60 second default for uploads
    });
  }

  /**
   * Download file
   */
  async download(path: string): Promise<Buffer> {
    return this.readBytes(path);
  }
}

