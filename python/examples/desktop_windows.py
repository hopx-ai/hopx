#!/usr/bin/env python3
"""
Desktop automation example - Window management.

Demonstrates:
- Listing all windows
- Focusing windows
- Resizing windows
- Closing windows
- Display resolution management
"""

from hopx_ai import Sandbox, DesktopNotAvailableError

def main():
    print("Creating desktop sandbox...")
    sandbox = Sandbox.create(template="desktop")
    
    print(f"✅ Sandbox created: {sandbox.sandbox_id}\n")
    
    try:
        # Window management
        print("🪟 Window management:")
        
        # List windows
        print("  - Listing windows...")
        windows = sandbox.desktop.get_windows()
        print(f"  - Found {len(windows)} windows")
        
        for i, win in enumerate(windows[:5], 1):  # Show first 5
            print(f"  {i}. {win.title}")
            print(f"     ID: {win.id}")
            print(f"     Position: ({win.x}, {win.y})")
            print(f"     Size: {win.width}x{win.height}")
            if win.pid:
                print(f"     PID: {win.pid}")
        
        if windows:
            # Focus window
            print(f"\n  - Focusing first window...")
            sandbox.desktop.focus_window(windows[0].id)
            print("  ✅ Window focused")
            
            # Resize window
            print(f"\n  - Resizing window to 800x600...")
            sandbox.desktop.resize_window(windows[0].id, 800, 600)
            print("  ✅ Window resized")
            
            # Close window (commented out to not close important windows)
            # print(f"\n  - Closing window...")
            # sandbox.desktop.close_window(windows[0].id)
            # print("  ✅ Window closed")
        
        print("\n✅ Window operations completed\n")
        
        # Display management
        print("🖥️  Display management:")
        
        # Get current resolution
        print("  - Getting current resolution...")
        display = sandbox.desktop.get_display()
        print(f"  - Current: {display.resolution}")
        print(f"  - Width: {display.width}")
        print(f"  - Height: {display.height}")
        print(f"  - Depth: {display.depth}")
        
        # Get available resolutions
        print("\n  - Getting available resolutions...")
        resolutions = sandbox.desktop.get_available_resolutions()
        print(f"  - Available: {len(resolutions)} resolutions")
        for w, h in resolutions[:10]:  # Show first 10
            print(f"    - {w}x{h}")
        
        # Set resolution (commented out to not change display)
        # print("\n  - Setting resolution to 1920x1080...")
        # new_display = sandbox.desktop.set_resolution(1920, 1080)
        # print(f"  - New resolution: {new_display.resolution}")
        
        print("\n✅ Display operations completed\n")
        
    except DesktopNotAvailableError as e:
        print(f"\n❌ Desktop not available:")
        print(f"   {e.message}")
        print(f"\nMissing dependencies:")
        for dep in e.missing_dependencies:
            print(f"   - {dep}")
        print(f"\nInstall command:")
        print(f"   {e.install_command}")
        print(f"\nDocumentation: {e.docs_url}\n")
        
    finally:
        print("Cleaning up...")
        sandbox.kill()
        print("✅ Done!")


if __name__ == "__main__":
    main()

