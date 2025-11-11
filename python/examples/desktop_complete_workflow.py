#!/usr/bin/env python3
"""
Desktop automation complete workflow.

Demonstrates a complete workflow:
1. Start VNC server
2. Open application
3. Automate UI interactions
4. Capture screenshots
5. Record demo video
"""

from hopx_ai import Sandbox, DesktopNotAvailableError
import time

def main():
    print("=" * 60)
    print("DESKTOP AUTOMATION - COMPLETE WORKFLOW")
    print("=" * 60)
    print()
    
    # Create sandbox
    print("1️⃣  Creating desktop sandbox...")
    sandbox = Sandbox.create(template="desktop")
    print(f"✅ Sandbox ID: {sandbox.sandbox_id}\n")
    
    try:
        # Start VNC for remote access
        print("2️⃣  Starting VNC server...")
        vnc_info = sandbox.desktop.start_vnc()
        print(f"✅ VNC running at: {vnc_info.url}")
        print(f"   Display: {vnc_info.display}\n")
        
        # Set optimal resolution
        print("3️⃣  Setting display resolution...")
        display = sandbox.desktop.set_resolution(1920, 1080)
        print(f"✅ Resolution: {display.resolution}\n")
        
        # Open application (Firefox example)
        print("4️⃣  Opening Firefox...")
        sandbox.commands.run('firefox &', background=True)
        time.sleep(3)  # Wait for Firefox to open
        print("✅ Firefox started\n")
        
        # Get window info
        print("5️⃣  Getting window information...")
        windows = sandbox.desktop.get_windows()
        firefox_window = next((w for w in windows if 'Firefox' in w.title), None)
        
        if firefox_window:
            print(f"✅ Found Firefox window:")
            print(f"   Title: {firefox_window.title}")
            print(f"   Size: {firefox_window.width}x{firefox_window.height}\n")
            
            # Focus Firefox
            print("6️⃣  Focusing Firefox window...")
            sandbox.desktop.focus_window(firefox_window.id)
            print("✅ Window focused\n")
        
        # Start recording
        print("7️⃣  Starting screen recording...")
        recording = sandbox.desktop.start_recording(fps=30, quality="high")
        print(f"✅ Recording ID: {recording.recording_id}\n")
        
        # Automate UI interactions
        print("8️⃣  Automating UI interactions...")
        
        # Type in address bar
        print("   - Opening address bar (Ctrl+L)...")
        sandbox.desktop.combination(['ctrl'], 'l')
        time.sleep(0.5)
        
        print("   - Typing URL...")
        sandbox.desktop.type("https://hopx_ai.com")
        time.sleep(0.5)
        
        print("   - Pressing Enter...")
        sandbox.desktop.press("Return")
        time.sleep(2)
        
        # Scroll page
        print("   - Scrolling down...")
        sandbox.desktop.scroll(3, "down")
        time.sleep(1)
        
        # Take screenshot
        print("\n9️⃣  Capturing screenshot...")
        screenshot = sandbox.desktop.screenshot()
        with open('/tmp/hopx_desktop.png', 'wb') as f:
            f.write(screenshot)
        print(f"✅ Screenshot saved ({len(screenshot)} bytes)\n")
        
        # Copy text
        print("🔟 Clipboard operations...")
        print("   - Selecting text (Ctrl+A)...")
        sandbox.desktop.combination(['ctrl'], 'a')
        time.sleep(0.3)
        
        print("   - Copying (Ctrl+C)...")
        sandbox.desktop.combination(['ctrl'], 'c')
        time.sleep(0.5)
        
        print("   - Reading clipboard...")
        clipboard_content = sandbox.desktop.get_clipboard()
        print(f"   - Clipboard: {clipboard_content[:100]}...\n")
        
        # Stop recording
        print("1️⃣1️⃣  Stopping screen recording...")
        final_recording = sandbox.desktop.stop_recording(recording.recording_id)
        print(f"✅ Recording stopped")
        print(f"   Duration: {final_recording.duration:.2f}s")
        print(f"   Size: {final_recording.file_size} bytes\n")
        
        # Download recording
        if final_recording.is_ready:
            print("1️⃣2️⃣  Downloading recording...")
            video = sandbox.desktop.download_recording(recording.recording_id)
            with open('/tmp/desktop_demo.mp4', 'wb') as f:
                f.write(video)
            print(f"✅ Video saved ({len(video)} bytes)\n")
        
        # Stop VNC
        print("1️⃣3️⃣  Stopping VNC server...")
        sandbox.desktop.stop_vnc()
        print("✅ VNC stopped\n")
        
        print("=" * 60)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("Output files:")
        print("  - /tmp/hopx_desktop.png (screenshot)")
        print("  - /tmp/desktop_demo.mp4 (recording)")
        print()
        
    except DesktopNotAvailableError as e:
        print("\n" + "=" * 60)
        print("❌ DESKTOP NOT AVAILABLE")
        print("=" * 60)
        print()
        print(f"Error: {e.message}")
        print()
        print("Missing dependencies:")
        for dep in e.missing_dependencies:
            print(f"  - {dep}")
        print()
        print("To enable desktop automation, add to your Dockerfile:")
        print(f"  RUN {e.install_command}")
        print()
        print(f"Documentation: {e.docs_url}")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        
    finally:
        print("Cleaning up...")
        sandbox.kill()
        print("✅ Sandbox destroyed\n")


if __name__ == "__main__":
    main()

