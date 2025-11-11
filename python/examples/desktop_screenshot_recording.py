#!/usr/bin/env python3
"""
Desktop automation example - Screenshots and screen recording.

Demonstrates:
- Full screen screenshots
- Region screenshots
- Screen recording (start, stop, download)
"""

from hopx_ai import Sandbox, DesktopNotAvailableError
import time

def main():
    print("Creating desktop sandbox...")
    sandbox = Sandbox.create(template="desktop")
    
    print(f"✅ Sandbox created: {sandbox.sandbox_id}\n")
    
    try:
        # Screenshot operations
        print("📸 Screenshot operations:")
        
        # Full screen screenshot
        print("  - Capturing full screen...")
        img_bytes = sandbox.desktop.screenshot()
        print(f"  - Screenshot size: {len(img_bytes)} bytes")
        
        # Save to file
        with open('/tmp/fullscreen.png', 'wb') as f:
            f.write(img_bytes)
        print("  - Saved to /tmp/fullscreen.png")
        
        # Region screenshot
        print("  - Capturing region (100,100 500x300)...")
        region_bytes = sandbox.desktop.screenshot_region(100, 100, 500, 300)
        print(f"  - Region screenshot size: {len(region_bytes)} bytes")
        
        with open('/tmp/region.png', 'wb') as f:
            f.write(region_bytes)
        print("  - Saved to /tmp/region.png")
        
        print("✅ Screenshot operations completed\n")
        
        # Screen recording
        print("🎬 Screen recording:")
        
        # Start recording
        print("  - Starting recording...")
        rec_info = sandbox.desktop.start_recording(fps=30, quality="high")
        print(f"  - Recording ID: {rec_info.recording_id}")
        print(f"  - Status: {rec_info.status}")
        
        # Simulate some activity
        print("  - Simulating activity...")
        for i in range(5):
            sandbox.desktop.click(100 + i * 50, 100 + i * 50)
            time.sleep(0.5)
        
        # Stop recording
        print("  - Stopping recording...")
        final_rec = sandbox.desktop.stop_recording(rec_info.recording_id)
        print(f"  - Duration: {final_rec.duration:.2f}s")
        print(f"  - File size: {final_rec.file_size} bytes")
        print(f"  - Status: {final_rec.status}")
        
        # Check status
        print("  - Checking recording status...")
        status = sandbox.desktop.get_recording_status(rec_info.recording_id)
        print(f"  - Is ready: {status.is_ready}")
        
        if status.is_ready:
            # Download recording
            print("  - Downloading recording...")
            video_bytes = sandbox.desktop.download_recording(rec_info.recording_id)
            print(f"  - Video size: {len(video_bytes)} bytes")
            
            with open('/tmp/recording.mp4', 'wb') as f:
                f.write(video_bytes)
            print("  - Saved to /tmp/recording.mp4")
        
        print("✅ Recording operations completed\n")
        
    except DesktopNotAvailableError as e:
        print(f"\n❌ Desktop not available:")
        print(f"   {e.message}")
        print(f"\nTo enable desktop automation, add to your Dockerfile:")
        print(f"   {e.install_command}\n")
        
    finally:
        print("Cleaning up...")
        sandbox.kill()
        print("✅ Done!")


if __name__ == "__main__":
    main()

