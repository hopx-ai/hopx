#!/usr/bin/env python3
"""
Desktop automation example - VNC server.

Demonstrates:
- Starting VNC server
- Getting VNC connection info
- Stopping VNC server
"""

from hopx_ai import Sandbox, DesktopNotAvailableError

def main():
    # Create sandbox with desktop template
    print("Creating desktop sandbox...")
    sandbox = Sandbox.create(template="desktop")
    
    print(f"✅ Sandbox created: {sandbox.sandbox_id}\n")
    
    try:
        # Start VNC server
        print("Starting VNC server...")
        vnc_info = sandbox.desktop.start_vnc(display=1)
        
        print(f"✅ VNC server started!")
        print(f"   Display: {vnc_info.display}")
        print(f"   Port: {vnc_info.port}")
        print(f"   URL: {vnc_info.url}\n")
        
        # Get VNC status
        print("Checking VNC status...")
        status = sandbox.desktop.get_vnc_status()
        print(f"✅ VNC running: {status.running}\n")
        
        # Stop VNC
        print("Stopping VNC server...")
        sandbox.desktop.stop_vnc()
        print("✅ VNC stopped\n")
        
    except DesktopNotAvailableError as e:
        print(f"❌ Desktop not available:")
        print(f"   {e.message}")
        print(f"\n{e.install_command}\n")
        
    finally:
        # Cleanup
        print("Cleaning up...")
        sandbox.kill()
        print("✅ Done!")


if __name__ == "__main__":
    main()

