"""
08. WebSocket Features - Python SDK

This example covers all WebSocket features:
- Interactive terminal (WebSocket)
- Code execution streaming (WebSocket)
- File watching (WebSocket)
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



async def interactive_terminal():
    """Interactive WebSocket terminal"""
    print("=" * 60)
    print("1. INTERACTIVE TERMINAL (WEBSOCKET)")
    print("=" * 60)
    
    sandbox = Sandbox.create(template="code-interpreter", api_key=API_KEY)
    ensure_workspace(sandbox)
    
    try:
        # Connect to terminal
        print("✅ Connecting to terminal...")
        
        async with await sandbox.terminal.connect() as term:
            print("✅ Terminal connected!")
            
            # Send commands
            await sandbox.terminal.send_input(term, "echo 'Hello from terminal!'\n")
            print("✅ Sent: echo 'Hello from terminal!'")
            
            await asyncio.sleep(0.5)
            
            await sandbox.terminal.send_input(term, "pwd\n")
            print("✅ Sent: pwd")
            
            await asyncio.sleep(0.5)
            
            await sandbox.terminal.send_input(term, "ls -la\n")
            print("✅ Sent: ls -la")
            
            # Receive output
            print("\n✅ Terminal output:")
            count = 0
            async for message in sandbox.terminal.iter_output(term):
                if message['type'] == 'output':
                    print(f"   {message['data']}", end='')
                
                count += 1
                if count >= 20:  # Limit output
                    break
            
            print("\n✅ Terminal session complete")
            
    finally:
        sandbox.kill()
    
    print()


async def terminal_resize():
    """Resize terminal"""
    print("=" * 60)
    print("2. TERMINAL RESIZE")
    print("=" * 60)
    
    sandbox = Sandbox.create(template="code-interpreter", api_key=API_KEY)
    ensure_workspace(sandbox)
    
    try:
        async with await sandbox.terminal.connect() as term:
            print("✅ Terminal connected (default size)")
            
            # Resize terminal
            await sandbox.terminal.resize(term, rows=40, cols=120)
            print("✅ Terminal resized to 40x120")
            
            # Send command to check size
            await sandbox.terminal.send_input(term, "echo $COLUMNS x $LINES\n")
            
            await asyncio.sleep(0.5)
            
            # Get output
            count = 0
            async for message in sandbox.terminal.iter_output(term):
                if message['type'] == 'output':
                    print(f"   {message['data']}", end='')
                count += 1
                if count >= 5:
                    break
            
            print()
            
    finally:
        sandbox.kill()
    
    print()


async def code_streaming():
    """Stream code execution output in real-time"""
    print("=" * 60)
    print("3. CODE EXECUTION STREAMING (WEBSOCKET)")
    print("=" * 60)
    
    sandbox = Sandbox.create(template="code-interpreter", api_key=API_KEY)
    ensure_workspace(sandbox)
    
    try:
        code = """
import time
import sys

for i in range(5):
    print(f"Step {i+1}/5", flush=True)
    sys.stderr.write(f"Progress: {(i+1)*20}%\\n")
    sys.stderr.flush()
    time.sleep(1)

print("Complete!", flush=True)
        """
        
        print("✅ Streaming code execution:")
        
        async for message in sandbox.run_code_stream(code):
            if message['type'] == 'stdout':
                print(f"   📤 stdout: {message['data']}", end='')
            elif message['type'] == 'stderr':
                print(f"   ⚠️  stderr: {message['data']}", end='')
            elif message['type'] == 'result':
                print(f"\n✅ Result:")
                print(f"   Exit code: {message.get('exit_code')}")
                print(f"   Execution time: {message.get('execution_time')}s")
            elif message['type'] == 'complete':
                print("✅ Streaming complete!")
        
    finally:
        sandbox.kill()
    
    print()


async def code_streaming_with_env():
    """Stream code execution with environment variables"""
    print("=" * 60)
    print("4. STREAMING WITH ENV VARS")
    print("=" * 60)
    
    sandbox = Sandbox.create(template="code-interpreter", api_key=API_KEY)
    ensure_workspace(sandbox)
    
    try:
        code = """
import os
import time

api_key = os.environ.get('API_KEY')
debug = os.environ.get('DEBUG')

print(f"API Key: {api_key}")
print(f"Debug: {debug}")

for i in range(3):
    print(f"Processing {i+1}...")
    time.sleep(1)
        """
        
        print("✅ Streaming with env vars:")
        
        async for message in sandbox.run_code_stream(
            code,
            env={
                "API_KEY": "sk-test-123",
                "DEBUG": "true"
            }
        ):
            if message['type'] == 'stdout':
                print(f"   {message['data']}", end='')
            elif message['type'] == 'complete':
                print("✅ Complete!")
        
    finally:
        sandbox.kill()
    
    print()


async def file_watching():
    """Watch filesystem for changes"""
    print("=" * 60)
    print("5. FILE WATCHING (WEBSOCKET)")
    print("=" * 60)
    
    sandbox = Sandbox.create(template="code-interpreter", api_key=API_KEY)
    ensure_workspace(sandbox)
    
    try:
        print("✅ Starting file watcher on /workspace...")
        
        async def watch_files():
            """Watch for file changes"""
            event_count = 0
            async for event in sandbox.files.watch("/workspace"):
                if event['type'] == 'change':
                    print(f"   📂 {event['event'].upper()}: {event['path']}")
                    event_count += 1
                    if event_count >= 10:  # Stop after 10 events
                        break
        
        async def make_file_changes():
            """Make some file changes"""
            await asyncio.sleep(1)  # Wait for watcher to start
            
            print("✅ Making file changes...")
            
            sandbox.files.write("/workspace/test1.txt", "Content 1")
            await asyncio.sleep(0.5)
            
            sandbox.files.write("/workspace/test2.txt", "Content 2")
            await asyncio.sleep(0.5)
            
            sandbox.files.write("/workspace/test1.txt", "Updated content")
            await asyncio.sleep(0.5)
            
            sandbox.files.mkdir("/workspace/newdir")
            await asyncio.sleep(0.5)
            
            sandbox.files.remove("/workspace/test2.txt")
            await asyncio.sleep(0.5)
        
        # Run watcher and file changes concurrently
        await asyncio.gather(
            watch_files(),
            make_file_changes()
        )
        
        print("✅ File watching complete!")
        
    finally:
        sandbox.kill()
    
    print()


async def file_watching_specific_path():
    """Watch specific directory"""
    print("=" * 60)
    print("6. WATCH SPECIFIC DIRECTORY")
    print("=" * 60)
    
    sandbox = Sandbox.create(template="code-interpreter", api_key=API_KEY)
    ensure_workspace(sandbox)
    
    try:
        # Create a specific directory to watch
        sandbox.files.mkdir("/workspace/monitored")
        
        print("✅ Watching /workspace/monitored...")
        
        async def watch():
            event_count = 0
            async for event in sandbox.files.watch("/workspace/monitored"):
                if event['type'] == 'change':
                    print(f"   📂 {event['event']}: {event['path']}")
                    event_count += 1
                    if event_count >= 5:
                        break
        
        async def make_changes():
            await asyncio.sleep(1)
            
            # These will be detected
            sandbox.files.write("/workspace/monitored/file1.txt", "Test")
            await asyncio.sleep(0.5)
            
            sandbox.files.write("/workspace/monitored/file2.txt", "Test")
            await asyncio.sleep(0.5)
            
            # This won't be detected (different directory)
            sandbox.files.write("/workspace/other.txt", "Test")
        
        await asyncio.gather(watch(), make_changes())
        
        print("✅ Specific directory watching complete!")
        
    finally:
        sandbox.kill()
    
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("PYTHON SDK - WEBSOCKET FEATURES")
    print("=" * 60)
    print("\nNote: WebSocket features require async/await")
    print("      Install: pip install websockets")
    print("=" * 60 + "\n")
    
    # Run all async examples
    asyncio.run(interactive_terminal())
    asyncio.run(terminal_resize())
    asyncio.run(code_streaming())
    asyncio.run(code_streaming_with_env())
    asyncio.run(file_watching())
    asyncio.run(file_watching_specific_path())
    
    print("=" * 60)
    print("✅ ALL WEBSOCKET FEATURES DEMONSTRATED!")
    print("=" * 60)
    print("\nFeatures covered:")
    print("  ✅ Interactive terminal")
    print("  ✅ Terminal resize")
    print("  ✅ Code execution streaming")
    print("  ✅ Streaming with env vars")
    print("  ✅ File watching")
    print("  ✅ Directory-specific watching")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

