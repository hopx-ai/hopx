"""
File Hasher - Calculate SHA256 hash for COPY steps
"""

import hashlib
import os
from pathlib import Path
from typing import List, Tuple
import glob as glob_module


class FileHasher:
    """Calculate SHA256 hashes for files"""
    
    async def calculate_hash(self, src: str, dest: str, context_path: str) -> str:
        """
        Calculate SHA256 hash of files and metadata
        
        Args:
            src: Source pattern (e.g., "app/")
            dest: Destination path (e.g., "/app/")
            context_path: Base path for resolving src
            
        Returns:
            SHA256 hash string
        """
        hasher = hashlib.sha256()
        
        # Hash the COPY command
        hasher.update(f"COPY {src} {dest}".encode('utf-8'))
        
        # Get all files matching the pattern
        pattern = os.path.join(context_path, src)
        files = glob_module.glob(pattern, recursive=True)
        
        # Sort files for consistent hashing
        files = sorted(files)
        
        # Hash each file
        for file_path in files:
            if os.path.isfile(file_path):
                # Relative path from context
                relative_path = os.path.relpath(file_path, context_path)
                hasher.update(relative_path.encode('utf-8'))
                
                # File stats
                stat = os.stat(file_path)
                hasher.update(str(stat.st_mode).encode('utf-8'))
                hasher.update(str(stat.st_size).encode('utf-8'))
                hasher.update(str(int(stat.st_mtime * 1000)).encode('utf-8'))
                
                # File content
                with open(file_path, 'rb') as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)
        
        return hasher.hexdigest()
    
    async def calculate_multi_hash(
        self, 
        sources: List[Tuple[str, str]], 
        context_path: str
    ) -> str:
        """
        Calculate hash for multiple sources
        
        Args:
            sources: List of (src, dest) tuples
            context_path: Base path
            
        Returns:
            Combined SHA256 hash
        """
        hasher = hashlib.sha256()
        
        for src, dest in sources:
            file_hash = await self.calculate_hash(src, dest, context_path)
            hasher.update(file_hash.encode('utf-8'))
        
        return hasher.hexdigest()

