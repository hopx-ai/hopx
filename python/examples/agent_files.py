"""
File Operations with Hopx Sandbox

Manage files in sandboxes:
- Write files
- Read files
- List directory contents
- Upload and download files
- Check file existence
"""

from hopx_ai import Sandbox

def main():
    print("File Operations\n")

    # Create sandbox
    print("1. Creating sandbox...")
    sandbox = Sandbox.create(template="code-interpreter")
    print(f"Sandbox created: {sandbox.sandbox_id}")
    print(f"   Agent URL: {sandbox.get_info().public_host}\n")

    try:
        # Write a file
        print("2. Writing file...")
        sandbox.files.write(
            '/workspace/hello.py',
            'print("Hello from Hopx!")\nprint("This file was created via SDK")'
        )
        print("File written: /workspace/hello.py\n")

        # Read the file back
        print("3. Reading file...")
        content = sandbox.files.read('/workspace/hello.py')
        print(f"File content:\n{content}\n")

        # List directory contents
        print("4. Listing /workspace...")
        files = sandbox.files.list('/workspace')
        print(f"Found {len(files)} items:")
        for f in files:
            icon = "📁" if f.is_dir else "📄"
            size = f"{f.size_kb:.2f} KB" if f.is_file else ""
            print(f"   {icon} {f.name} {size}")
        print()
        
        # Create directory
        print("5. Creating directory...")
        sandbox.files.mkdir('/workspace/data')
        print("Directory created: /workspace/data\n")

        # Write data file
        print("6. Writing CSV file...")
        csv_data = """name,age,city
Alice,25,New York
Bob,30,San Francisco
Charlie,35,Seattle"""
        sandbox.files.write('/workspace/data/users.csv', csv_data)
        print("CSV file written\n")

        # Check if file exists
        print("7. Checking file existence...")
        exists = sandbox.files.exists('/workspace/data/users.csv')
        print(f"/workspace/data/users.csv exists: {exists}\n")

        # Upload a local file (create one first)
        print("8. Creating local file to upload...")
        with open('/tmp/local_file.txt', 'w') as f:
            f.write("This file was uploaded from local filesystem!")

        sandbox.files.upload('/tmp/local_file.txt', '/workspace/uploaded.txt')
        print("File uploaded to /workspace/uploaded.txt\n")

        # Download a file
        print("9. Downloading file from sandbox...")
        sandbox.files.download('/workspace/data/users.csv', '/tmp/downloaded_users.csv')
        print("File downloaded to /tmp/downloaded_users.csv\n")
        
        # Verify downloaded content
        with open('/tmp/downloaded_users.csv', 'r') as f:
            downloaded = f.read()
        print(f"Downloaded content:\n{downloaded}\n")
        
        # List all files (recursive-like)
        print("10. Final directory listing...")
        files = sandbox.files.list('/workspace')
        print(f"Total items in /workspace: {len(files)}")
        for f in files:
            icon = "📁" if f.is_dir else "📄"
            print(f"   {icon} {f.name}")

        # Remove a file
        print("\n11. Removing temporary file...")
        sandbox.files.remove('/workspace/uploaded.txt')
        print("File removed\n")

        print("File operations complete")

    finally:
        # Cleanup
        print("\nCleaning up...")
        sandbox.kill()
        print("Sandbox destroyed")


if __name__ == "__main__":
    main()

