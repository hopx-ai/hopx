/**
 * Tar Creator - Create tar.gz archives
 */

import * as tar from 'tar';
import { createGzip } from 'zlib';
import { createReadStream, createWriteStream } from 'fs';
import { readFile, stat } from 'fs/promises';
import { glob } from 'glob';
import * as path from 'path';
import * as os from 'os';
import { Readable } from 'stream';

export interface TarResult {
  stream: Readable;
  size: number;
  filePath: string;  // Temporary file path
}

export class TarCreator {
  /**
   * Create tar.gz from files
   * 
   * @param src - Source pattern (e.g., "app/")
   * @param contextPath - Base path for resolving src
   * @returns Stream and size of tar.gz
   */
  async createTarGz(src: string, contextPath: string): Promise<TarResult> {
    // Get all files matching the pattern
    const pattern = path.join(contextPath, src);
    const files = await glob(pattern, {
      nodir: false,
      dot: true,
      absolute: true,
    });
    
    // Convert to relative paths
    const relativePaths = files.map(file => path.relative(contextPath, file));
    
    // Create temporary tar.gz file
    const tmpDir = os.tmpdir();
    const tmpFile = path.join(tmpDir, `tar-${Date.now()}-${Math.random().toString(36).substr(2, 9)}.tar.gz`);
    
    // Create tar.gz
    await tar.create(
      {
        gzip: true,
        file: tmpFile,
        cwd: contextPath,
        portable: true,
        preservePaths: false,
      },
      relativePaths
    );
    
    // Get file size
    const stats = await stat(tmpFile);
    
    // Create read stream
    const stream = createReadStream(tmpFile);
    
    return {
      stream: stream as Readable,
      size: stats.size,
      filePath: tmpFile,
    };
  }
  
  /**
   * Create tar.gz from multiple sources
   */
  async createMultiTarGz(sources: string[], contextPath: string): Promise<TarResult> {
    const allFiles: string[] = [];
    
    // Collect all files from all sources
    for (const src of sources) {
      const pattern = path.join(contextPath, src);
      const files = await glob(pattern, {
        nodir: false,
        dot: true,
        absolute: true,
      });
      
      const relativePaths = files.map(file => path.relative(contextPath, file));
      allFiles.push(...relativePaths);
    }
    
    // Remove duplicates
    const uniqueFiles = [...new Set(allFiles)];
    
    // Create temporary tar.gz file
    const tmpDir = os.tmpdir();
    const tmpFile = path.join(tmpDir, `tar-${Date.now()}-${Math.random().toString(36).substr(2, 9)}.tar.gz`);
    
    // Create tar.gz
    await tar.create(
      {
        gzip: true,
        file: tmpFile,
        cwd: contextPath,
        portable: true,
        preservePaths: false,
      },
      uniqueFiles
    );
    
    // Get file size
    const stats = await stat(tmpFile);
    
    // Create read stream
    const stream = createReadStream(tmpFile);
    
    return {
      stream: stream as Readable,
      size: stats.size,
      filePath: tmpFile,
    };
  }
}

