"""
04. Command Execution - Python SDK

This example covers:
- Run shell commands
- Stream command output
- Environment variables in commands
- Custom working directory
- Background command execution
- Command timeouts
"""

from hopx_ai import Sandbox
import os

API_KEY = os.getenv("HOPX_API_KEY", "your-api-key-here")

def ensure_workspace(sandbox):
    """Create /workspace directory if it doesn't exist"""
    try:
        sandbox.run_code("import os; os.makedirs('/workspace', exist_ok=True)")
    except Exception:
        pass



def basic_commands():
    """Basic command execution"""
    print("=" * 60)
    print("1. BASIC COMMAND EXECUTION")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Simple command
        result = sandbox.commands.run("echo 'Hello from bash!'")
        print(f"✅ Output: {result.stdout.strip()}")
        print(f"✅ Exit code: {result.exit_code}")
        
        # List files
        result = sandbox.commands.run("ls -lah /workspace")
        print(f"✅ /workspace contents:\n{result.stdout}")
        
        # Check Python version
        result = sandbox.commands.run("python --version")
        print(f"✅ Python version: {result.stdout.strip()}")
    
    print()


def commands_with_env():
    """Commands with environment variables"""
    print("=" * 60)
    print("2. COMMANDS WITH ENV VARS")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Use environment variables in command
        result = sandbox.commands.run(
            'echo "API Key: $API_KEY, Region: $AWS_REGION"',
            env={
                "API_KEY": "sk-test-123",
                "AWS_REGION": "us-west-2"
            }
        )
        
        print(f"✅ Output: {result.stdout.strip()}")
        
        # Run Python with custom PYTHONPATH
        result = sandbox.commands.run(
            "python -c 'import sys; print(sys.path)'",
            env={"PYTHONPATH": "/workspace/custom:/workspace/lib"}
        )
        
        print(f"✅ Python path:\n{result.stdout}")
    
    print()


def working_directory():
    """Commands with custom working directory"""
    print("=" * 60)
    print("3. CUSTOM WORKING DIRECTORY")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Create a directory
        sandbox.files.mkdir("/workspace/myproject")
        sandbox.files.write("/workspace/myproject/file.txt", "Hello!")
        
        # Run command in that directory
        result = sandbox.commands.run(
            "pwd && ls -la",
            working_dir="/workspace/myproject"
        )
        
        print(f"✅ Output:\n{result.stdout}")
        
        # Verify working directory
        result = sandbox.commands.run(
            "cat file.txt",  # No path needed, we're in the dir
            working_dir="/workspace/myproject"
        )
        
        print(f"✅ File content: {result.stdout.strip()}")
    
    print()


def piped_commands():
    """Complex commands with pipes"""
    print("=" * 60)
    print("4. PIPED COMMANDS")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Create test files
        sandbox.files.write("/workspace/data.txt", "apple\nbanana\napple\norange\napple\n")
        
        # Use pipes
        result = sandbox.commands.run(
            "cat /workspace/data.txt | sort | uniq -c"
        )
        
        print(f"✅ Word count:\n{result.stdout}")
        
        # More complex pipeline
        result = sandbox.commands.run(
            "ps aux | grep python | wc -l"
        )
        
        print(f"✅ Python processes: {result.stdout.strip()}")
    
    print()


def install_packages():
    """Install packages and use them"""
    print("=" * 60)
    print("5. INSTALL PACKAGES")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Install Python package
        result = sandbox.commands.run("pip install requests")
        print(f"✅ Package installed")
        
        # Use the package
        code_result = sandbox.run_code("""
import requests
print("requests library version:", requests.__version__)
        """)
        
        print(f"✅ Using installed package:\n{code_result.stdout}")
        
        # Install Node.js package
        result = sandbox.commands.run("npm install -g cowsay")
        print(f"✅ cowsay installed")
        
        # Use it
        result = sandbox.commands.run("cowsay 'Hello from Node!'")
        print(f"✅ Output:\n{result.stdout}")
    
    print()


def git_operations():
    """Git operations"""
    print("=" * 60)
    print("6. GIT OPERATIONS")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Initialize git repo
        sandbox.commands.run("git config --global user.email 'test@example.com'")
        sandbox.commands.run("git config --global user.name 'Test User'")
        
        sandbox.commands.run("git init /workspace/myrepo")
        print("✅ Git repo initialized")
        
        # Create files and commit
        sandbox.files.write("/workspace/myrepo/README.md", "# My Project")
        
        sandbox.commands.run(
            "git add . && git commit -m 'Initial commit'",
            working_dir="/workspace/myrepo"
        )
        
        # Check git log
        result = sandbox.commands.run(
            "git log --oneline",
            working_dir="/workspace/myrepo"
        )
        
        print(f"✅ Git log:\n{result.stdout}")
    
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("PYTHON SDK - COMMAND EXECUTION")
    print("=" * 60 + "\n")
    
    basic_commands()
    commands_with_env()
    working_directory()
    piped_commands()
    install_packages()
    git_operations()
    
    print("=" * 60)
    print("✅ ALL COMMAND OPERATIONS DEMONSTRATED!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

