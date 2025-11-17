"""
Command Execution with Hopx Sandbox

Execute shell commands in sandboxes:
- Run shell commands
- Capture stdout and stderr
- Check exit codes
- Handle errors
"""

from hopx_ai import Sandbox

def main():
    print("Command Execution\n")
    
    # Create sandbox
    print("1. Creating sandbox...")
    sandbox = Sandbox.create(template="code-interpreter")
    print(f"Sandbox created: {sandbox.sandbox_id}\n")

    try:
        # Simple command
        print("2. Running simple command: ls -la /workspace")
        result = sandbox.commands.run('ls -la /workspace')
        print(f"Exit code: {result.exit_code}")
        print(f"Output:\n{result.stdout}\n")

        # Command with output
        print("3. Running: echo 'Hello from shell!'")
        result = sandbox.commands.run('echo "Hello from shell!"')
        print(f"Output: {result.stdout.strip()}\n")
        
        # Create files via command
        print("4. Creating files with shell commands...")
        sandbox.commands.run('echo "First file" > /workspace/file1.txt')
        sandbox.commands.run('echo "Second file" > /workspace/file2.txt')
        sandbox.commands.run('echo "Third file" > /workspace/file3.txt')
        print("Files created\n")
        
        # List files
        print("5. Listing files: ls /workspace")
        result = sandbox.commands.run('ls /workspace')
        print(f"Files:\n{result.stdout}\n")

        # Command with error handling
        print("6. Running command that might fail...")
        result = sandbox.commands.run('cat /workspace/nonexistent.txt')
        if result.success:
            print(f"Success: {result.stdout}")
        else:
            print(f"Command failed (exit code: {result.exit_code})")
            print(f"   Error: {result.stderr.strip()}\n")
        
        # System information commands
        print("7. Getting system info...")
        commands_info = [
            ("Hostname", "hostname"),
            ("Current user", "whoami"),
            ("Working directory", "pwd"),
            ("Python version", "python3 --version"),
            ("Node version", "node --version"),
        ]
        
        for name, cmd in commands_info:
            result = sandbox.commands.run(cmd)
            if result.success:
                print(f"   {name}: {result.stdout.strip()}")
        print()
        
        # Command with multiple outputs
        print("8. Running command with multiple outputs...")
        result = sandbox.commands.run(
            'echo "Line 1" && echo "Line 2" && echo "Line 3"'
        )
        print(f"   📤 Output:\n{result.stdout}")
        print(f"✅ Execution time: {result.execution_time:.3f}s\n")
        
        # Pipeline command
        print("9. Running pipeline: find /workspace -type f | wc -l")
        result = sandbox.commands.run('find /workspace -type f | wc -l')
        file_count = result.stdout.strip()
        print(f"✅ Found {file_count} files in /workspace\n")
        
        # Multi-line command
        print("10. Running multi-line script...")
        script = """
        cd /workspace
        echo "Creating test data..."
        for i in {1..5}; do
            echo "Item $i" >> items.txt
        done
        cat items.txt
        """
        result = sandbox.commands.run(script)
        print(f"Script output:\n{result.stdout}\n")

        # Package installation
        print("11. Installing package with pip...")
        result = sandbox.commands.run('pip3 install requests --quiet', timeout=60)
        if result.success:
            print("Package installed")
            # Test it
            test_result = sandbox.commands.run('python3 -c "import requests; print(requests.__version__)"')
            print(f"   requests version: {test_result.stdout.strip()}\n")
        else:
            print(f"Installation failed: {result.stderr}\n")

        print("Command operations complete")

    finally:
        # Cleanup
        print("\nCleaning up...")
        sandbox.kill()
        print("Sandbox destroyed")


if __name__ == "__main__":
    main()

