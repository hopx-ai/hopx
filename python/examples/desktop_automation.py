#!/usr/bin/env python3
"""
Desktop automation example - Mouse and keyboard control.

Demonstrates:
- Mouse clicks, moves, drags
- Keyboard typing and key presses
- Clipboard operations
"""

from hopx_ai import Sandbox, DesktopNotAvailableError
import time

def main():
    print("Creating desktop sandbox...")
    sandbox = Sandbox.create(template="desktop")
    
    print(f"✅ Sandbox created: {sandbox.sandbox_id}\n")
    
    try:
        # Mouse operations
        print("🖱️  Mouse operations:")
        
        # Click
        print("  - Clicking at (100, 100)...")
        sandbox.desktop.click(100, 100)
        
        # Move
        print("  - Moving to (200, 200)...")
        sandbox.desktop.move(200, 200)
        
        # Double click
        print("  - Double clicking at (150, 150)...")
        sandbox.desktop.click(150, 150, clicks=2)
        
        # Right click
        print("  - Right clicking at (175, 175)...")
        sandbox.desktop.click(175, 175, button="right")
        
        # Drag
        print("  - Dragging from (100, 100) to (300, 300)...")
        sandbox.desktop.drag(100, 100, 300, 300)
        
        # Scroll
        print("  - Scrolling down...")
        sandbox.desktop.scroll(5, "down")
        
        print("✅ Mouse operations completed\n")
        
        # Keyboard operations
        print("⌨️  Keyboard operations:")
        
        # Type text
        print("  - Typing 'Hello, Desktop!'...")
        sandbox.desktop.type("Hello, Desktop!")
        
        # Press key
        print("  - Pressing Return...")
        sandbox.desktop.press("Return")
        
        # Key combinations
        print("  - Pressing Ctrl+C...")
        sandbox.desktop.combination(['ctrl'], 'c')
        
        print("  - Pressing Ctrl+Shift+T...")
        sandbox.desktop.combination(['ctrl', 'shift'], 't')
        
        print("✅ Keyboard operations completed\n")
        
        # Clipboard operations
        print("📋 Clipboard operations:")
        
        # Set clipboard
        print("  - Setting clipboard...")
        sandbox.desktop.set_clipboard("Hello from clipboard!")
        
        # Get clipboard
        print("  - Reading clipboard...")
        content = sandbox.desktop.get_clipboard()
        print(f"  - Clipboard content: {content}")
        
        # Clipboard history
        print("  - Getting clipboard history...")
        history = sandbox.desktop.get_clipboard_history()
        print(f"  - History items: {len(history)}")
        
        print("✅ Clipboard operations completed\n")
        
    except DesktopNotAvailableError as e:
        print(f"\n❌ Desktop not available:")
        print(f"   {e.message}")
        print(f"\nInstall command:")
        print(f"   {e.install_command}\n")
        
    finally:
        print("Cleaning up...")
        sandbox.kill()
        print("✅ Done!")


if __name__ == "__main__":
    main()

