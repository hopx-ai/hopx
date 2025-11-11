"""
06. Process Management - Python SDK

This example covers:
- List processes
- Kill processes
- Monitor process resource usage
"""

from hopx_ai import Sandbox
import os
import time

API_KEY = os.getenv("HOPX_API_KEY", "your-api-key-here")


def list_processes():
    """List all running processes"""
    print("=" * 60)
    print("1. LIST PROCESSES")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        # Start some background processes
        sandbox.run_code_background('import time; time.sleep(60)')
        sandbox.run_code_background('import time; time.sleep(60)')
        
        time.sleep(1)  # Let them start
        
        # List processes
        processes = sandbox.list_processes()
        
        print(f"✅ Total processes: {len(processes)}")
        print(f"\n{'Process ID':<25} {'Status':<12} {'Language':<12} {'Start Time':<25}")
        print("=" * 75)
        
        for proc in processes[:10]:  # Show first 10  
            # Processes are dicts, not objects
            pid = proc.get('process_id', 'N/A')
            status = proc.get('status', 'N/A')
            language = proc.get('language', 'N/A')
            start_time = proc.get('start_time', 'N/A')
            print(f"{pid:<25} {status:<12} {language:<12} {start_time:<25}")
    
    print()


def kill_process():
    """Kill a specific process"""
    print("=" * 60)
    print("2. KILL PROCESS")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        # Start a long-running process
        exec_id = sandbox.run_code_background("""
import time
print("Starting long process...")
for i in range(100):
    print(f"Step {i}")
    time.sleep(1)
        """)
        
        print(f"✅ Started background process: {exec_id}")
        time.sleep(2)
        
        # List processes to find Python processes
        processes = sandbox.list_processes()
        python_procs = [p for p in processes if 'python' in p.get('name', '').lower()]
        
        print(f"✅ Python processes: {len(python_procs)}")
        
        # Kill one of them
        if python_procs:
            pid_to_kill = python_procs[0].get('pid')
            print(f"✅ Killing process: {pid_to_kill}")
            
            sandbox.kill_process(pid_to_kill)
            print(f"✅ Process {pid_to_kill} killed")
            
            # Verify it's gone
            time.sleep(1)
            processes_after = sandbox.list_processes()
            still_exists = any(p.get('pid') == pid_to_kill for p in processes_after)
            print(f"✅ Process still exists: {still_exists}")
    
    print()


def monitor_resources():
    """Monitor process resource usage"""
    print("=" * 60)
    print("3. MONITOR PROCESS RESOURCES")
    print("=" * 60)
    
    with Sandbox.create(template="code-interpreter", api_key=API_KEY) as sandbox:
        # Start a memory-intensive process
        sandbox.run_code_background("""
import time
# Allocate some memory
data = [list(range(1000000)) for _ in range(10)]
time.sleep(30)
        """)
        
        time.sleep(2)
        
        # Monitor processes
        processes = sandbox.list_processes()
        
        # Find processes using most CPU
        cpu_sorted = sorted(processes, key=lambda p: p.get('cpu_percent', 0), reverse=True)
        print("✅ Top 5 CPU consumers:")
        for proc in cpu_sorted[:5]:
            print(f"   {proc.get('name', 'N/A')}: {proc.get('cpu_percent', 0):.1f}%")
        
        # Find processes using most memory
        mem_sorted = sorted(processes, key=lambda p: p.get('memory_percent', 0), reverse=True)
        print("\n✅ Top 5 Memory consumers:")
        for proc in mem_sorted[:5]:
            print(f"   {proc.get('name', 'N/A')}: {proc.get('memory_percent', 0):.1f}%")
    
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("PYTHON SDK - PROCESS MANAGEMENT")
    print("=" * 60 + "\n")
    
    list_processes()
    kill_process()
    monitor_resources()
    
    print("=" * 60)
    print("✅ ALL PROCESS MANAGEMENT OPERATIONS DEMONSTRATED!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

