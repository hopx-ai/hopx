/**
 * File Hasher - Calculate SHA256 hash for COPY steps
 */

import { createHash } from 'crypto';
import { readFile, stat } from 'fs/promises';
import { glob } from 'glob';
import * as path from 'path';

export class FileHasher {
  /**
   * Calculate SHA256 hash of files and metadata
   * 
   * @param src - Source pattern (e.g., "app/")
   * @param dest - Destination path (e.g., "/app/")
   * @param contextPath - Base path for resolving src
   * @returns SHA256 hash string
   */
  async calculateHash(src: string, dest: string, contextPath: string): Promise<string> {
    const hash = createHash('sha256');
    
    // Hash the COPY command
    hash.update(`COPY ${src} ${dest}`);
    
    // Get all files matching the pattern
    const pattern = path.join(contextPath, src);
    const files = await glob(pattern, {
      nodir: true,
      dot: true,
      absolute: true,
    });
    
    // Sort files for consistent hashing
    files.sort();
    
    // Hash each file
    for (const file of files) {
      // Relative path from context
      const relativePath = path.relative(contextPath, file);
      hash.update(relativePath);
      
      // File stats
      const stats = await stat(file);
      hash.update(stats.mode.toString());
      hash.update(stats.size.toString());
      hash.update(stats.mtimeMs.toString());
      
      // File content
      if (stats.isFile()) {
        const content = await readFile(file);
        hash.update(content);
      }
    }
    
    return hash.digest('hex');
  }
  
  /**
   * Calculate hash for multiple sources (used for combined COPY steps)
   */
  async calculateMultiHash(sources: Array<{ src: string; dest: string }>, contextPath: string): Promise<string> {
    const hash = createHash('sha256');
    
    for (const { src, dest } of sources) {
      const fileHash = await this.calculateHash(src, dest, contextPath);
      hash.update(fileHash);
    }
    
    return hash.digest('hex');
  }
}

