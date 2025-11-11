"""
Tar Creator - Create tar.gz archives
"""

import os
import tarfile
import tempfile
import glob as glob_module
from typing import List, BinaryIO
from dataclasses import dataclass


@dataclass
class TarResult:
    """Result of tar creation"""
    file_path: str
    size: int
    
    def open(self, mode: str = 'rb') -> BinaryIO:
        """Open the tar file"""
        return open(self.file_path, mode)
    
    def cleanup(self):
        """Delete the temporary file"""
        if os.path.exists(self.file_path):
            os.unlink(self.file_path)


class TarCreator:
    """Create tar.gz archives"""
    
    async def create_tar_gz(self, src: str, context_path: str) -> TarResult:
        """
        Create tar.gz from files
        
        Args:
            src: Source pattern (e.g., "app/")
            context_path: Base path for resolving src
            
        Returns:
            TarResult with file path and size
        """
        # Get all files matching the pattern
        pattern = os.path.join(context_path, src)
        files = glob_module.glob(pattern, recursive=True)
        
        # Convert to relative paths
        relative_paths = []
        for file_path in files:
            if os.path.exists(file_path):
                relative_path = os.path.relpath(file_path, context_path)
                relative_paths.append(relative_path)
        
        # Create temporary tar.gz file
        fd, tmp_file = tempfile.mkstemp(suffix='.tar.gz', prefix='tar-')
        os.close(fd)
        
        try:
            # Create tar.gz
            with tarfile.open(tmp_file, 'w:gz') as tar:
                for relative_path in relative_paths:
                    full_path = os.path.join(context_path, relative_path)
                    tar.add(full_path, arcname=relative_path)
            
            # Get file size
            size = os.path.getsize(tmp_file)
            
            return TarResult(file_path=tmp_file, size=size)
        except Exception as e:
            # Cleanup on error
            if os.path.exists(tmp_file):
                os.unlink(tmp_file)
            raise e
    
    async def create_multi_tar_gz(
        self, 
        sources: List[str], 
        context_path: str
    ) -> TarResult:
        """
        Create tar.gz from multiple sources
        
        Args:
            sources: List of source patterns
            context_path: Base path
            
        Returns:
            TarResult with file path and size
        """
        all_files = set()
        
        # Collect all files from all sources
        for src in sources:
            pattern = os.path.join(context_path, src)
            files = glob_module.glob(pattern, recursive=True)
            
            for file_path in files:
                if os.path.exists(file_path):
                    relative_path = os.path.relpath(file_path, context_path)
                    all_files.add(relative_path)
        
        # Create temporary tar.gz file
        fd, tmp_file = tempfile.mkstemp(suffix='.tar.gz', prefix='tar-')
        os.close(fd)
        
        try:
            # Create tar.gz
            with tarfile.open(tmp_file, 'w:gz') as tar:
                for relative_path in sorted(all_files):
                    full_path = os.path.join(context_path, relative_path)
                    tar.add(full_path, arcname=relative_path)
            
            # Get file size
            size = os.path.getsize(tmp_file)
            
            return TarResult(file_path=tmp_file, size=size)
        except Exception as e:
            # Cleanup on error
            if os.path.exists(tmp_file):
                os.unlink(tmp_file)
            raise e

