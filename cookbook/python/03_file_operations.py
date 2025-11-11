"""
03. File Operations (Complete) - Python SDK

This example covers ALL file operations:
- Read/write files
- List directories
- Upload/download files
- Check existence
- Remove files/directories
- Create directories
- File watching (WebSocket streaming)
"""

from hopx_ai import Sandbox
import os
import asyncio
import tempfile

API_KEY = os.getenv("HOPX_API_KEY", "your-api-key-here")


def ensure_workspace(sandbox):
    """Create /workspace directory if it doesn't exist"""
    try:
        sandbox.run_code("import os; os.makedirs('/workspace', exist_ok=True)")
    except Exception:
        pass


def basic_file_operations():
    """Basic file read/write operations"""
    print("=" * 60)
    print("1. BASIC FILE READ/WRITE")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Write text file
        sandbox.files.write("/workspace/hello.txt", "Hello, World!")
        print("✅ File written: /workspace/hello.txt")
        
        # Read file
        content = sandbox.files.read("/workspace/hello.txt")
        print(f"✅ File content: {content}")
        
        # Write binary file
        binary_data = b"\x89PNG\r\n\x1a\n"  # PNG header
        sandbox.files.write_bytes("/workspace/test.png", binary_data)
        print("✅ Binary file written: /workspace/test.png")
        
        # Read binary file
        binary_content = sandbox.files.read_bytes("/workspace/test.png")
        print(f"✅ Binary content length: {len(binary_content)} bytes")
    
    print()


def list_files():
    """List directory contents"""
    print("=" * 60)
    print("2. LIST DIRECTORY CONTENTS")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Create some files
        sandbox.files.write("/workspace/file1.txt", "Content 1")
        sandbox.files.write("/workspace/file2.txt", "Content 2")
        sandbox.files.mkdir("/workspace/subdir")
        sandbox.files.write("/workspace/subdir/file3.txt", "Content 3")
        
        # List directory
        files = sandbox.files.list("/workspace")
        print(f"✅ Files in /workspace: {len(files)}")
        
        for file in files:
            file_type = "📁" if file.is_dir else "📄"
            print(f"   {file_type} {file.name} ({file.size_kb:.2f}KB)")
        
        # List with details
        print("\n✅ Detailed file info:")
        for file in files:
            print(f"   Name: {file.name}")
            print(f"   Path: {file.path}")
            print(f"   Size: {file.size} bytes ({file.size_kb:.2f}KB)")
            print(f"   Is dir: {file.is_dir}")
            print(f"   Modified: {file.modified_time}")
            print()
    
    print()


def upload_download():
    """Upload and download files"""
    print("=" * 60)
    print("3. UPLOAD/DOWNLOAD FILES")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Create a local file to upload
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            local_file = f.name
            f.write("This is a test file for upload!\n")
            f.write("Line 2\n")
            f.write("Line 3\n")
        
        try:
            # Upload file
            sandbox.files.upload(local_file, "/workspace/uploaded.txt")
            print(f"✅ File uploaded: {local_file} → /workspace/uploaded.txt")
            
            # Verify upload
            content = sandbox.files.read("/workspace/uploaded.txt")
            print(f"✅ Uploaded content:\n{content}")
            
            # Download file
            download_path = tempfile.mktemp(suffix='.txt')
            sandbox.files.download("/workspace/uploaded.txt", download_path)
            print(f"✅ File downloaded: /workspace/uploaded.txt → {download_path}")
            
            # Verify download
            with open(download_path, 'r') as f:
                downloaded_content = f.read()
            print(f"✅ Downloaded content matches: {content == downloaded_content}")
            
            # Cleanup local files
            os.remove(download_path)
            
        finally:
            os.remove(local_file)
    
    print()


def check_existence():
    """Check if files/directories exist"""
    print("=" * 60)
    print("4. CHECK FILE/DIRECTORY EXISTENCE")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Create file
        sandbox.files.write("/workspace/exists.txt", "I exist!")
        
        # Check existence
        exists = sandbox.files.exists("/workspace/exists.txt")
        print(f"✅ /workspace/exists.txt exists: {exists}")
        
        not_exists = sandbox.files.exists("/workspace/not-here.txt")
        print(f"✅ /workspace/not-here.txt exists: {not_exists}")
        
        # Check directory existence
        sandbox.files.mkdir("/workspace/mydir")
        dir_exists = sandbox.files.exists("/workspace/mydir")
        print(f"✅ /workspace/mydir exists: {dir_exists}")
    
    print()


def remove_files():
    """Remove files and directories"""
    print("=" * 60)
    print("5. REMOVE FILES/DIRECTORIES")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Create file and remove it
        sandbox.files.write("/workspace/temp.txt", "Temporary")
        print("✅ Created /workspace/temp.txt")
        
        sandbox.files.remove("/workspace/temp.txt")
        print("✅ Removed /workspace/temp.txt")
        
        assert not sandbox.files.exists("/workspace/temp.txt")
        print("✅ File no longer exists")
        
        # Create directory with files and remove it
        sandbox.files.mkdir("/workspace/tempdir")
        sandbox.files.write("/workspace/tempdir/file1.txt", "Content")
        sandbox.files.write("/workspace/tempdir/file2.txt", "Content")
        print("✅ Created /workspace/tempdir with files")
        
        sandbox.files.remove("/workspace/tempdir")
        print("✅ Removed /workspace/tempdir (recursive)")
        
        assert not sandbox.files.exists("/workspace/tempdir")
        print("✅ Directory no longer exists")
    
    print()


def create_directories():
    """Create directory structures"""
    print("=" * 60)
    print("6. CREATE DIRECTORIES")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Create single directory
        sandbox.files.mkdir("/workspace/mydir")
        print("✅ Created /workspace/mydir")
        
        # Create nested directories (parents=True)
        sandbox.files.mkdir("/workspace/a/b/c")
        print("✅ Created /workspace/a/b/c (with parents)")
        
        # Verify structure
        files = sandbox.files.list("/workspace")
        print(f"✅ Directories created: {len([f for f in files if f.is_dir])}")
        
        # Create directory and add files
        sandbox.files.mkdir("/workspace/project")
        sandbox.files.write("/workspace/project/README.md", "# My Project")
        sandbox.files.write("/workspace/project/main.py", "print('Hello')")
        
        project_files = sandbox.files.list("/workspace/project")
        print(f"✅ Files in project: {len(project_files)}")
        for f in project_files:
            print(f"   - {f.name}")
    
    print()


def binary_files():
    """Handle binary files (images, PDFs, etc.)"""
    print("=" * 60)
    print("7. BINARY FILES")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        # Binary files still use /tmp/plots (already fixed)
        # Generate an image with matplotlib
        sandbox.run_code("""
import matplotlib
matplotlib.use('Agg')  # Set backend for headless
import matplotlib.pyplot as plt
import numpy as np
import os

# Ensure directory exists
os.makedirs('/tmp/plots', exist_ok=True)

x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x))
plt.title('Sine Wave')
plt.savefig('/tmp/plots/plot.png')
        """)
        
        print("✅ Generated plot.png")
        
        # Read binary file
        image_data = sandbox.files.read("/tmp/plots/plot.png")
        print(f"✅ Read binary file: {len(image_data)} bytes")
        
        # Download binary file
        local_path = tempfile.mktemp(suffix='.png')
        sandbox.files.download("/tmp/plots/plot.png", local_path)
        print(f"✅ Downloaded to: {local_path}")
        
        # Verify it's a valid PNG
        with open(local_path, 'rb') as f:
            header = f.read(8)
        is_png = header == b'\x89PNG\r\n\x1a\n'
        print(f"✅ Valid PNG file: {is_png}")
        
        os.remove(local_path)
    
    print()


async def watch_files():
    """Watch filesystem for changes (WebSocket streaming)"""
    print("=" * 60)
    print("8. WATCH FILESYSTEM (WEBSOCKET - REAL-TIME)")
    print("=" * 60)
    
    sandbox = Sandbox.create(template="code-interpreter", api_key=API_KEY)
    
    try:
        print("✅ Starting file watcher...")
        
        # Start watching in background
        import asyncio
        
        async def watch():
            event_count = 0
            async for event in sandbox.files.watch("/workspace"):
                if event['type'] == 'change':
                    print(f"   📂 {event['event'].upper()}: {event['path']}")
                    event_count += 1
                    if event_count >= 5:  # Stop after 5 events
                        break
        
        async def make_changes():
            # Wait a bit for watcher to start
            await asyncio.sleep(1)
            
            # Make some file changes
            sandbox.files.write("/workspace/test1.txt", "Content 1")
            await asyncio.sleep(0.5)
            
            sandbox.files.write("/workspace/test2.txt", "Content 2")
            await asyncio.sleep(0.5)
            
            sandbox.files.remove("/workspace/test1.txt")
            await asyncio.sleep(0.5)
            
            sandbox.files.mkdir("/workspace/newdir")
            await asyncio.sleep(0.5)
        
        # Run watcher and file changes concurrently
        await asyncio.gather(
            watch(),
            make_changes()
        )
        
        print("✅ File watching complete!")
        
    finally:
        sandbox.kill()
    
    print()


def large_files():
    """Handle large files efficiently"""
    print("=" * 60)
    print("9. LARGE FILES")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Generate a large file (10MB)
        sandbox.run_code("""
with open('/workspace/large_file.txt', 'w') as f:
    for i in range(1000000):
        f.write(f"Line {i}: This is a test line with some content\\n")
        """)
        
        # Check file size
        files = sandbox.files.list("/workspace")
        large_file = [f for f in files if f.name == "large_file.txt"][0]
        print(f"✅ Created large file: {large_file.size_kb / 1024:.2f}MB")
        
        # Read file (streamed automatically for large files)
        content = sandbox.files.read("/workspace/large_file.txt")
        lines = content.split('\n')
        print(f"✅ Read large file: {len(lines)} lines")
        print(f"   First line: {lines[0]}")
        print(f"   Last line: {lines[-2]}")  # -2 because last is empty
    
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("PYTHON SDK - FILE OPERATIONS (COMPLETE)")
    print("=" * 60 + "\n")
    
    # Synchronous examples
    basic_file_operations()
    list_files()
    upload_download()
    check_existence()
    remove_files()
    create_directories()
    binary_files()
    large_files()
    
    # Asynchronous examples
    print("Running async examples...")
    asyncio.run(watch_files())
    
    print("=" * 60)
    print("✅ ALL FILE OPERATIONS DEMONSTRATED!")
    print("=" * 60)
    print("\nFeatures covered:")
    print("  ✅ Read/write files")
    print("  ✅ List directories")
    print("  ✅ Upload/download files")
    print("  ✅ Check existence")
    print("  ✅ Remove files/directories")
    print("  ✅ Create directories")
    print("  ✅ Binary files")
    print("  ✅ Large files")
    print("  ✅ File watching (WebSocket)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

