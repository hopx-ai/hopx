"""
07. Desktop Automation - Python SDK

This example covers desktop automation features:
- VNC connection
- Mouse operations (click, move, drag, scroll)
- Keyboard input
- Clipboard operations
- Screenshots
- Screen recording
- Window management
- Display control
- OCR (text recognition)
- Element finding
- Wait for elements
- Drag and drop
- Get element bounds
- Capture specific windows
"""

from hopx_ai import Sandbox
import os
import base64

API_KEY = os.getenv("HOPX_API_KEY", "your-api-key-here")


def vnc_connection():
    """Get VNC connection for desktop access"""
    print("=" * 60)
    print("1. VNC CONNECTION")
    print("=" * 60)
    
    # Note: Desktop requires desktop-enabled template
    with Sandbox.create(template="desktop", api_key=API_KEY) as sandbox:
        # Get VNC URL
        vnc_info = sandbox.desktop.get_vnc_url()
        
        print(f"✅ VNC URL: {vnc_info['url']}")
        print(f"✅ Password: {vnc_info.get('password', 'N/A')}")
        print("✅ Connect with VNC viewer to control desktop remotely")
    
    print()


def mouse_operations():
    """Mouse click, move, drag, scroll"""
    print("=" * 60)
    print("2. MOUSE OPERATIONS")
    print("=" * 60)
    
    with Sandbox.create(template="desktop", api_key=API_KEY) as sandbox:
        # Click at coordinates
        sandbox.desktop.mouse_click(x=500, y=300, button="left")
        print("✅ Left click at (500, 300)")
        
        # Right click
        sandbox.desktop.mouse_click(x=500, y=300, button="right")
        print("✅ Right click at (500, 300)")
        
        # Double click
        sandbox.desktop.mouse_double_click(x=500, y=300)
        print("✅ Double click at (500, 300)")
        
        # Move mouse
        sandbox.desktop.mouse_move(x=600, y=400)
        print("✅ Moved mouse to (600, 400)")
        
        # Drag (press, move, release)
        sandbox.desktop.drag_drop(
            from_x=100, from_y=100,
            to_x=300, to_y=300
        )
        print("✅ Dragged from (100,100) to (300,300)")
        
        # Scroll
        sandbox.desktop.mouse_scroll(delta_y=-3)
        print("✅ Scrolled down")
    
    print()


def keyboard_operations():
    """Keyboard input and shortcuts"""
    print("=" * 60)
    print("3. KEYBOARD OPERATIONS")
    print("=" * 60)
    
    with Sandbox.create(template="desktop", api_key=API_KEY) as sandbox:
        # Type text
        sandbox.desktop.keyboard_type("Hello, World!")
        print("✅ Typed: Hello, World!")
        
        # Press key
        sandbox.desktop.keyboard_press("Return")
        print("✅ Pressed: Return")
        
        # Key combination (Ctrl+C)
        sandbox.desktop.keyboard_press("Control_L+c")
        print("✅ Pressed: Ctrl+C")
        
        # Alt+Tab
        sandbox.desktop.keyboard_press("Alt_L+Tab")
        print("✅ Pressed: Alt+Tab")
    
    print()


def clipboard_operations():
    """Clipboard get/set"""
    print("=" * 60)
    print("4. CLIPBOARD OPERATIONS")
    print("=" * 60)
    
    with Sandbox.create(template="desktop", api_key=API_KEY) as sandbox:
        # Set clipboard
        sandbox.desktop.clipboard_set("Hello from SDK!")
        print("✅ Clipboard set to: Hello from SDK!")
        
        # Get clipboard
        content = sandbox.desktop.clipboard_get()
        print(f"✅ Clipboard content: {content}")
    
    print()


def screenshot_operations():
    """Take screenshots"""
    print("=" * 60)
    print("5. SCREENSHOTS")
    print("=" * 60)
    
    with Sandbox.create(template="desktop", api_key=API_KEY) as sandbox:
        # Take full screenshot
        screenshot_data = sandbox.desktop.screenshot()
        
        print(f"✅ Screenshot taken: {len(screenshot_data)} bytes")
        
        # Save locally
        with open("/tmp/screenshot.png", "wb") as f:
            if isinstance(screenshot_data, str):
                # Base64 encoded
                f.write(base64.b64decode(screenshot_data))
            else:
                f.write(screenshot_data)
        
        print("✅ Screenshot saved to /tmp/screenshot.png")
        
        # Capture specific region
        region_screenshot = sandbox.desktop.screenshot(
            x=100, y=100,
            width=500, height=400
        )
        
        print(f"✅ Region screenshot: {len(region_screenshot)} bytes")
    
    print()


def screen_recording():
    """Start/stop screen recording"""
    print("=" * 60)
    print("6. SCREEN RECORDING")
    print("=" * 60)
    
    with Sandbox.create(template="desktop", api_key=API_KEY) as sandbox:
        # Start recording
        sandbox.desktop.start_recording()
        print("✅ Recording started")
        
        # Do some actions
        sandbox.desktop.mouse_move(x=500, y=500)
        sandbox.desktop.keyboard_type("Recording in progress...")
        
        import time
        time.sleep(3)
        
        # Stop recording
        video_data = sandbox.desktop.stop_recording()
        print(f"✅ Recording stopped: {len(video_data)} bytes")
        
        # Save locally
        with open("/tmp/recording.webm", "wb") as f:
            f.write(video_data)
        
        print("✅ Recording saved to /tmp/recording.webm")
    
    print()


def window_management():
    """List, focus, resize windows"""
    print("=" * 60)
    print("7. WINDOW MANAGEMENT")
    print("=" * 60)
    
    with Sandbox.create(template="desktop", api_key=API_KEY) as sandbox:
        # List windows
        windows = sandbox.desktop.list_windows()
        
        print(f"✅ Open windows: {len(windows)}")
        for win in windows:
            print(f"   - {win['title']} (ID: {win['id']})")
        
        if windows:
            # Focus a window
            win_id = windows[0]['id']
            sandbox.desktop.focus_window(win_id)
            print(f"✅ Focused window: {win_id}")
            
            # Resize window
            sandbox.desktop.resize_window(win_id, width=800, height=600)
            print(f"✅ Resized window to 800x600")
            
            # Move window
            sandbox.desktop.move_window(win_id, x=100, y=100)
            print(f"✅ Moved window to (100, 100)")
            
            # Get window bounds
            bounds = sandbox.desktop.get_bounds(win_id)
            print(f"✅ Window bounds: {bounds}")
            
            # Capture window screenshot
            win_screenshot = sandbox.desktop.capture_window(win_id)
            print(f"✅ Window screenshot: {len(win_screenshot)} bytes")
    
    print()


def display_control():
    """Control display settings"""
    print("=" * 60)
    print("8. DISPLAY CONTROL")
    print("=" * 60)
    
    with Sandbox.create(template="desktop", api_key=API_KEY) as sandbox:
        # Set resolution
        sandbox.desktop.set_resolution(width=1920, height=1080)
        print("✅ Resolution set to 1920x1080")
        
        # Get display info
        info = sandbox.desktop.get_display_info()
        print(f"✅ Display info: {info}")
    
    print()


def ocr_operations():
    """OCR - Extract text from screen"""
    print("=" * 60)
    print("9. OCR (TEXT RECOGNITION)")
    print("=" * 60)
    
    with Sandbox.create(template="desktop", api_key=API_KEY) as sandbox:
        # Open a text editor and type something
        sandbox.desktop.keyboard_type("Hello, this is text on screen!")
        
        # Run OCR on full screen
        text = sandbox.desktop.ocr()
        print(f"✅ OCR text found: {text}")
        
        # Run OCR on specific region
        region_text = sandbox.desktop.ocr(
            x=100, y=100,
            width=500, height=200
        )
        print(f"✅ OCR region text: {region_text}")
    
    print()


def find_elements():
    """Find elements on screen"""
    print("=" * 60)
    print("10. FIND ELEMENTS")
    print("=" * 60)
    
    with Sandbox.create(template="desktop", api_key=API_KEY) as sandbox:
        # Find element by text
        element = sandbox.desktop.find_element(text="File")
        
        if element:
            print(f"✅ Found element at: ({element['x']}, {element['y']})")
            
            # Click on it
            sandbox.desktop.mouse_click(x=element['x'], y=element['y'])
            print("✅ Clicked on element")
        
        # Wait for element to appear
        try:
            element = sandbox.desktop.wait_for(
                text="Save",
                timeout_seconds=5
            )
            print(f"✅ Element appeared at: ({element['x']}, {element['y']})")
        except TimeoutError:
            print("⏱️  Element did not appear within timeout")
    
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("PYTHON SDK - DESKTOP AUTOMATION")
    print("=" * 60)
    print("\nNote: These examples require 'desktop' template")
    print("Some features may not be available in all environments")
    print("=" * 60 + "\n")
    
    try:
        vnc_connection()
        mouse_operations()
        keyboard_operations()
        clipboard_operations()
        screenshot_operations()
        screen_recording()
        window_management()
        display_control()
        ocr_operations()
        find_elements()
        
        print("=" * 60)
        print("✅ ALL DESKTOP AUTOMATION FEATURES DEMONSTRATED!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n⚠️  Desktop features require 'desktop' template")
        print(f"   Error: {e}")
        print("\n   To use desktop features:")
        print("   sandbox = Sandbox.create(template='desktop', ...)")


if __name__ == "__main__":
    main()

