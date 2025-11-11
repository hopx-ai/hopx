"""
02. Code Execution (All Methods) - Python SDK

This example covers ALL code execution features:
- Synchronous execution (run_code)
- Asynchronous execution (run_code_async)
- Background execution (run_code_background)
- IPython/Jupyter execution (run_ipython)
- Streaming execution (run_code_stream) - WebSocket
- Environment variables
- Rich outputs (images, plots, DataFrames)
- Multiple languages (Python, JavaScript, Bash, Go)
- Timeouts and error handling
"""

from hopx_ai import Sandbox
import os
import asyncio

API_KEY = os.getenv("HOPX_API_KEY", "your-api-key-here")

def ensure_workspace(sandbox):
    """Create /workspace directory if it doesn't exist"""
    try:
        sandbox.run_code("import os; os.makedirs('/workspace', exist_ok=True)")
    except Exception:
        pass



def basic_code_execution():
    """Basic synchronous code execution"""
    print("=" * 60)
    print("1. BASIC CODE EXECUTION (SYNC)")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Simple Python code
        result = sandbox.run_code("""
import sys
print(f"Python version: {sys.version}")
print("Hello from sandbox!")
        """)
        
        print(f"✅ Success: {result.success}")
        print(f"✅ Exit code: {result.exit_code}")
        print(f"✅ Execution time: {result.execution_time}s")
        print(f"✅ Output:\n{result.stdout}")
        
        if result.stderr:
            print(f"⚠️  Stderr: {result.stderr}")
    
    print()


def code_with_env_vars():
    """Execute code with environment variables"""
    print("=" * 60)
    print("2. CODE EXECUTION WITH ENV VARS")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Pass environment variables (IMPORTANT: for secrets!)
        result = sandbox.run_code(
            """
import os

# These come from env parameter, NOT hardcoded!
api_key = os.environ.get('API_KEY')
debug = os.environ.get('DEBUG')

print(f"API Key: {api_key}")
print(f"Debug mode: {debug}")
            """,
            env={
                "API_KEY": "sk-test-secret-key-123",
                "DEBUG": "true"
            }
        )
        
        print(f"✅ Output:\n{result.stdout}")
    
    print()


def multiple_languages():
    """Execute code in multiple languages"""
    print("=" * 60)
    print("3. MULTIPLE LANGUAGES")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Python
        result_py = sandbox.run_code(
            'print("Hello from Python!")',
            language="python"
        )
        print(f"✅ Python: {result_py.stdout.strip()}")
        
        # JavaScript
        result_js = sandbox.run_code(
            'console.log("Hello from JavaScript!")',
            language="javascript"
        )
        print(f"✅ JavaScript: {result_js.stdout.strip()}")
        
        # Bash
        result_bash = sandbox.run_code(
            'echo "Hello from Bash!"',
            language="bash"
        )
        print(f"✅ Bash: {result_bash.stdout.strip()}")
        
        # Go
        result_go = sandbox.run_code(
            '''
package main
import "fmt"
func main() {
    fmt.Println("Hello from Go!")
}
            ''',
            language="go"
        )
        print(f"✅ Go: {result_go.stdout.strip()}")
    
    print()


def rich_outputs():
    """Execute code with rich outputs (images, plots, DataFrames)"""
    print("=" * 60)
    print("4. RICH OUTPUTS (Images, Plots, DataFrames)")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Generate plot and DataFrame
        result = sandbox.run_code("""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Create a plot
plt.figure(figsize=(8, 6))
x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x), label='sin(x)')
plt.plot(x, np.cos(x), label='cos(x)')
plt.legend()
plt.title('Trigonometric Functions')
plt.savefig('/tmp/plot.png')
print("Plot saved!")

# Create a DataFrame
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'Score': [95, 87, 92]
})
print(df)
        """)
        
        print(f"✅ Output:\n{result.stdout}")
        
        # Check for rich outputs
        if result.rich_outputs:
            print(f"✅ Rich outputs found: {len(result.rich_outputs)}")
            for i, output in enumerate(result.rich_outputs):
                print(f"   {i+1}. Type: {output.type}")
                print(f"      Data keys: {list(output.data.keys())}")
        else:
            print("ℹ️  No rich outputs captured")
    
    print()


async def async_execution():
    """Asynchronous code execution (non-blocking)"""
    print("=" * 60)
    print("5. ASYNC EXECUTION (NON-BLOCKING)")
    print("=" * 60)
    
    sandbox = Sandbox.create(template="code-interpreter", api_key=API_KEY)
    ensure_workspace(sandbox)
    
    try:
        # Start async execution (returns execution_id)
        execution_id = sandbox.run_code_async("""
import time
print("Starting long computation...")
time.sleep(3)
print("Computation complete!")
        """)
        
        print(f"✅ Execution started: {execution_id}")
        print("   (Non-blocking - can do other work)")
        
        # Do other work while code executes...
        await asyncio.sleep(1)
        print("   ...doing other work...")
        
        # Results are available via webhook or polling
        # (In production, use webhooks)
        print(f"✅ Execution ID for later retrieval: {execution_id}")
        
    finally:
        sandbox.kill()
    
    print()


def background_execution():
    """Background execution (fire and forget)"""
    print("=" * 60)
    print("6. BACKGROUND EXECUTION (FIRE & FORGET)")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Start background execution
        execution_id = sandbox.run_code_background("""
import time
with open('/workspace/background_task.txt', 'w') as f:
    for i in range(5):
        f.write(f"Step {i+1}\\n")
        f.flush()
        time.sleep(1)
    f.write("Done!\\n")
        """)
        
        print(f"✅ Background execution started: {execution_id}")
        print("   (Running in background)")
        
        # Can continue with other work immediately
        print("   ...continuing with other work...")
        
        # Check if file is being created
        import time
        time.sleep(2)
        if sandbox.files.exists("/workspace/background_task.txt"):
            content = sandbox.files.read("/workspace/background_task.txt")
            print(f"✅ Background task progress:\n{content}")
    
    print()


def ipython_execution():
    """IPython/Jupyter-style execution with rich display"""
    print("=" * 60)
    print("7. IPYTHON EXECUTION (JUPYTER-STYLE)")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # IPython supports rich display, last expression output, etc.
        result = sandbox.run_ipython("""
import pandas as pd
import numpy as np

# Last expression is automatically displayed
df = pd.DataFrame({
    'A': np.random.rand(5),
    'B': np.random.rand(5)
})

df.describe()  # This will be displayed
        """)
        
        print(f"✅ Success: {result.success}")
        print(f"✅ Output:\n{result.stdout}")
        
        if result.rich_outputs:
            print(f"✅ Rich outputs: {len(result.rich_outputs)}")
    
    print()


async def streaming_execution():
    """Stream code execution output in real-time (WebSocket)"""
    print("=" * 60)
    print("8. STREAMING EXECUTION (WEBSOCKET - REAL-TIME)")
    print("=" * 60)
    
    sandbox = Sandbox.create(template="code-interpreter", api_key=API_KEY)
    ensure_workspace(sandbox)
    
    try:
        # Stream output as it's generated
        code = """
import time
for i in range(5):
    print(f"Step {i+1}/5")
    time.sleep(1)
print("Complete!")
        """
        
        print("✅ Streaming output (real-time):")
        async for message in sandbox.run_code_stream(code):
            if message['type'] == 'stdout':
                print(f"   📤 {message['data']}", end='')
            elif message['type'] == 'stderr':
                print(f"   ⚠️  {message['data']}", end='')
            elif message['type'] == 'result':
                print(f"\n✅ Exit code: {message['exit_code']}")
                print(f"✅ Execution time: {message.get('execution_time', 0)}s")
            elif message['type'] == 'complete':
                print(f"✅ Streaming complete!")
                
    finally:
        sandbox.kill()
    
    print()


def timeout_handling():
    """Handle code execution timeouts"""
    print("=" * 60)
    print("9. TIMEOUT HANDLING")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # This will timeout
        try:
            result = sandbox.run_code(
                """
import time
time.sleep(100)  # Sleep longer than timeout
                """,
                timeout=2  # 2 second timeout
            )
        except Exception as e:
            print(f"✅ Caught timeout: {e}")
        
        # This will succeed
        result = sandbox.run_code(
            """
import time
time.sleep(1)
print("Done!")
            """,
            timeout=5
        )
        print(f"✅ Within timeout: {result.stdout.strip()}")
    
    print()


def working_directory():
    """Use custom working directory"""
    print("=" * 60)
    print("10. CUSTOM WORKING DIRECTORY")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        ensure_workspace(sandbox)
        # Create a directory
        sandbox.files.mkdir("/workspace/myproject")
        
        # Execute code in that directory
        result = sandbox.run_code(
            """
import os
print(f"Current dir: {os.getcwd()}")

# Create file in current dir
with open('data.txt', 'w') as f:
    f.write('Hello!')
            """,
            working_dir="/workspace/myproject"
        )
        
        print(f"✅ Output:\n{result.stdout}")
        
        # Verify file was created in correct directory
        assert sandbox.files.exists("/workspace/myproject/data.txt")
        print("✅ File created in correct directory!")
    
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("PYTHON SDK - CODE EXECUTION (ALL METHODS)")
    print("=" * 60 + "\n")
    
    # Synchronous examples
    basic_code_execution()
    code_with_env_vars()
    multiple_languages()
    rich_outputs()
    background_execution()
    ipython_execution()
    timeout_handling()
    working_directory()
    
    # Asynchronous examples
    print("Running async examples...")
    asyncio.run(async_execution())
    asyncio.run(streaming_execution())
    
    print("=" * 60)
    print("✅ ALL CODE EXECUTION METHODS DEMONSTRATED!")
    print("=" * 60)
    print("\nFeatures covered:")
    print("  ✅ Synchronous execution (run_code)")
    print("  ✅ Asynchronous execution (run_code_async)")
    print("  ✅ Background execution (run_code_background)")
    print("  ✅ IPython execution (run_ipython)")
    print("  ✅ Streaming execution (run_code_stream)")
    print("  ✅ Environment variables")
    print("  ✅ Rich outputs")
    print("  ✅ Multiple languages")
    print("  ✅ Timeouts")
    print("  ✅ Custom working directory")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

