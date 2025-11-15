"""Desktop automation resource for Hopx Sandboxes."""

from typing import Optional, List, Tuple
import logging
from ._agent_client import AgentHTTPClient
from .models import VNCInfo, WindowInfo, RecordingInfo, DisplayInfo
from .errors import DesktopNotAvailableError

logger = logging.getLogger(__name__)


class Desktop:
    """
    Desktop automation resource.
    
    Provides methods for controlling GUI applications, VNC access, mouse/keyboard input,
    screenshots, screen recording, and window management.
    
    Features:
    - VNC server management
    - Mouse control (click, move, drag, scroll)
    - Keyboard control (type, press, combinations)
    - Clipboard operations
    - Screenshot capture
    - Screen recording
    - Window management
    - Display configuration
    
    Note:
        Desktop automation requires specific dependencies in your template.
        If not available, methods will raise DesktopNotAvailableError with
        installation instructions.
    
    Example:
        >>> sandbox = Sandbox.create(template="desktop")
        >>> 
        >>> # Start VNC
        >>> vnc_info = sandbox.desktop.start_vnc()
        >>> print(f"VNC at: {vnc_info.url}")
        >>> 
        >>> # Mouse control
        >>> sandbox.desktop.click(100, 100)
        >>> sandbox.desktop.type("Hello World")
        >>> 
        >>> # Screenshot
        >>> img_bytes = sandbox.desktop.screenshot()
        >>> with open('screen.png', 'wb') as f:
        ...     f.write(img_bytes)
    """
    
    def __init__(self, client: AgentHTTPClient):
        """
        Initialize Desktop resource.
        
        Args:
            client: Shared agent HTTP client
        """
        self._client = client
        self._available: Optional[bool] = None
        self._checked = False
        logger.debug("Desktop resource initialized")
    
    def _check_availability(self) -> None:
        """
        Check if desktop automation is available.
        
        Raises:
            DesktopNotAvailableError: If desktop features not available
        """
        if self._checked:
            if not self._available:
                raise DesktopNotAvailableError(
                    message=(
                        "Desktop automation is not available in this sandbox. "
                        "Your template may be missing required dependencies."
                    )
                )
            return
        
        self._checked = True
        
        try:
            # Try to get VNC status (simple desktop endpoint check)
            response = self._client.get(
                "/desktop/vnc/status",
                operation="check desktop availability",
                timeout=5
            )
            self._available = True
            logger.debug("Desktop automation available")
            
        except Exception as e:
            # Desktop not available
            self._available = False
            logger.warning(f"Desktop automation not available: {e}")
            
            raise DesktopNotAvailableError(
                message=(
                    "Desktop automation is not available in this sandbox. "
                    "Your template may be missing required dependencies."
                ),
                missing_dependencies=[
                    "xdotool",
                    "xvfb",
                    "tigervnc-standalone-server",
                    "wmctrl",
                    "imagemagick"
                ],
                request_id=getattr(e, 'request_id', None)
            )
    
    # =============================================================================
    # VNC SERVER
    # =============================================================================
    
    def start_vnc(self, display: int = 1, password: Optional[str] = None) -> VNCInfo:
        """
        Start VNC server.
        
        Args:
            display: Display number (default: 1, creates :1)
            password: VNC password (optional)
        
        Returns:
            VNC server information with URL and port
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> vnc_info = sandbox.desktop.start_vnc()
            >>> print(f"Connect to: {vnc_info.url}")
            >>> print(f"Display: {vnc_info.display}")
        """
        self._check_availability()
        
        logger.debug(f"Starting VNC server on display :{display}")
        
        payload = {"display": display}
        if password:
            payload["password"] = password
        
        response = self._client.post(
            "/desktop/vnc/start",
            json=payload,
            operation="start VNC server"
        )
        
        data = response.json()
        return VNCInfo(
            running=data.get("running", True),
            display=data.get("display"),
            port=data.get("port"),
            url=data.get("url"),
            password=password
        )
    
    def stop_vnc(self) -> None:
        """
        Stop VNC server.
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> sandbox.desktop.stop_vnc()
        """
        self._check_availability()
        
        logger.debug("Stopping VNC server")
        
        self._client.post(
            "/desktop/vnc/stop",
            json={},
            operation="stop VNC server"
        )
    
    def get_vnc_status(self) -> VNCInfo:
        """
        Get VNC server status.
        
        Returns:
            VNC server information
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> vnc = sandbox.desktop.get_vnc_status()
            >>> if vnc.running:
            ...     print(f"VNC running at {vnc.url}")
        """
        self._check_availability()
        
        response = self._client.get(
            "/desktop/vnc/status",
            operation="get VNC status"
        )
        
        data = response.json()
        return VNCInfo(
            running=data.get("running", False),
            display=data.get("display"),
            port=data.get("port"),
            url=data.get("url")
        )
    
    def get_vnc_url(self) -> str:
        """
        Get VNC URL (convenience method).
        
        This is a convenience method that returns just the URL string
        instead of the full VNCInfo object.
        
        Returns:
            VNC URL string
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> url = sandbox.desktop.get_vnc_url()
            >>> print(f"Connect to: {url}")
        """
        vnc_info = self.get_vnc_status()
        return vnc_info.url or ""
    
    # =============================================================================
    # MOUSE CONTROL
    # =============================================================================
    
    def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> None:
        """
        Click at position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks (1 for single, 2 for double)
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> # Single click
            >>> sandbox.desktop.click(100, 100)
            >>> 
            >>> # Right click
            >>> sandbox.desktop.click(200, 200, button="right")
            >>> 
            >>> # Double click
            >>> sandbox.desktop.click(150, 150, clicks=2)
        """
        self._check_availability()
        
        logger.debug(f"Mouse click at ({x}, {y}), button={button}, clicks={clicks}")
        
        self._client.post(
            "/desktop/mouse/click",
            json={
                "x": x,
                "y": y,
                "button": button,
                "clicks": clicks
            },
            operation="mouse click"
        )
    
    def move(self, x: int, y: int) -> None:
        """
        Move mouse cursor to position.
        
        Args:
            x: X coordinate
            y: Y coordinate
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> sandbox.desktop.move(300, 400)
        """
        self._check_availability()
        
        logger.debug(f"Mouse move to ({x}, {y})")
        
        self._client.post(
            "/desktop/mouse/move",
            json={"x": x, "y": y},
            operation="mouse move"
        )
    
    def drag(self, from_x: int, from_y: int, to_x: int, to_y: int, button: str = "left") -> None:
        """
        Drag from one position to another.
        
        Args:
            from_x: Starting X coordinate
            from_y: Starting Y coordinate
            to_x: Ending X coordinate
            to_y: Ending Y coordinate
            button: Mouse button to hold ('left', 'right', 'middle')
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> # Drag from (100, 100) to (200, 200)
            >>> sandbox.desktop.drag(100, 100, 200, 200)
        """
        self._check_availability()
        
        logger.debug(f"Mouse drag from ({from_x}, {from_y}) to ({to_x}, {to_y})")
        
        self._client.post(
            "/desktop/mouse/drag",
            json={
                "from_x": from_x,
                "from_y": from_y,
                "to_x": to_x,
                "to_y": to_y,
                "button": button
            },
            operation="mouse drag"
        )
    
    def scroll(self, amount: int, direction: str = "down") -> None:
        """
        Scroll mouse wheel.
        
        Args:
            amount: Scroll amount (positive integer)
            direction: Scroll direction ('up', 'down', 'left', 'right')
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> # Scroll down 5 clicks
            >>> sandbox.desktop.scroll(5, "down")
            >>> 
            >>> # Scroll up 3 clicks
            >>> sandbox.desktop.scroll(3, "up")
        """
        self._check_availability()
        
        logger.debug(f"Mouse scroll {direction} by {amount}")
        
        self._client.post(
            "/desktop/mouse/scroll",
            json={
                "amount": amount,
                "direction": direction
            },
            operation="mouse scroll"
        )
    
    # =============================================================================
    # KEYBOARD CONTROL
    # =============================================================================
    
    def type(self, text: str, delay_ms: int = 10) -> None:
        """
        Type text.
        
        Args:
            text: Text to type
            delay_ms: Delay between keystrokes in milliseconds
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> sandbox.desktop.type("Hello, World!")
            >>> 
            >>> # Slower typing
            >>> sandbox.desktop.type("Slow typing", delay_ms=50)
        """
        self._check_availability()
        
        logger.debug(f"Keyboard type: {text[:50]}... (delay={delay_ms}ms)")
        
        self._client.post(
            "/desktop/keyboard/type",
            json={
                "text": text,
                "delay_ms": delay_ms
            },
            operation="keyboard type"
        )
    
    def press(self, key: str) -> None:
        """
        Press a key.
        
        Args:
            key: Key name (e.g., 'Return', 'Escape', 'Tab', 'F1', etc.)
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> sandbox.desktop.press("Return")
            >>> sandbox.desktop.press("Escape")
            >>> sandbox.desktop.press("Tab")
        """
        self._check_availability()
        
        logger.debug(f"Keyboard press: {key}")
        
        self._client.post(
            "/desktop/keyboard/press",
            json={"key": key},
            operation="keyboard press"
        )
    
    def combination(self, modifiers: List[str], key: str) -> None:
        """
        Press key combination.
        
        Args:
            modifiers: Modifier keys (e.g., ['ctrl'], ['ctrl', 'shift'])
            key: Main key
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> # Ctrl+C
            >>> sandbox.desktop.combination(['ctrl'], 'c')
            >>> 
            >>> # Ctrl+Shift+T
            >>> sandbox.desktop.combination(['ctrl', 'shift'], 't')
            >>> 
            >>> # Alt+F4
            >>> sandbox.desktop.combination(['alt'], 'F4')
        """
        self._check_availability()
        
        logger.debug(f"Keyboard combination: {'+'.join(modifiers)}+{key}")
        
        self._client.post(
            "/desktop/keyboard/combination",
            json={
                "modifiers": modifiers,
                "key": key
            },
            operation="keyboard combination"
        )
    
    # =============================================================================
    # CLIPBOARD
    # =============================================================================
    
    def set_clipboard(self, text: str) -> None:
        """
        Set clipboard content.
        
        Args:
            text: Text to set in clipboard
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> sandbox.desktop.set_clipboard("Hello from clipboard!")
        """
        self._check_availability()
        
        logger.debug(f"Set clipboard: {text[:50]}...")
        
        self._client.post(
            "/desktop/clipboard/set",
            json={"text": text},
            operation="set clipboard"
        )
    
    def get_clipboard(self) -> str:
        """
        Get clipboard content.
        
        Returns:
            Current clipboard text
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> text = sandbox.desktop.get_clipboard()
            >>> print(text)
        """
        self._check_availability()
        
        logger.debug("Get clipboard")
        
        response = self._client.get(
            "/desktop/clipboard/get",
            operation="get clipboard"
        )
        
        data = response.json()
        return data.get("text", "")
    
    def get_clipboard_history(self) -> List[str]:
        """
        Get clipboard history.
        
        Returns:
            List of recent clipboard contents
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> history = sandbox.desktop.get_clipboard_history()
            >>> for item in history:
            ...     print(item)
        """
        self._check_availability()
        
        logger.debug("Get clipboard history")
        
        response = self._client.get(
            "/desktop/clipboard/history",
            operation="get clipboard history"
        )
        
        data = response.json()
        return data.get("history", [])
    
    # =============================================================================
    # SCREENSHOT
    # =============================================================================
    
    def screenshot(self) -> bytes:
        """
        Capture full screen screenshot.
        
        Returns:
            Screenshot image as PNG bytes
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> img_bytes = sandbox.desktop.screenshot()
            >>> with open('screenshot.png', 'wb') as f:
            ...     f.write(img_bytes)
        """
        self._check_availability()
        
        logger.debug("Capture screenshot")
        
        response = self._client.get(
            "/desktop/screenshot",
            operation="capture screenshot"
        )
        
        return response.content
    
    def screenshot_region(self, x: int, y: int, width: int, height: int) -> bytes:
        """
        Capture screenshot of specific region.
        
        Args:
            x: Starting X coordinate
            y: Starting Y coordinate
            width: Region width
            height: Region height
        
        Returns:
            Screenshot image as PNG bytes
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> # Capture 500x300 region starting at (100, 100)
            >>> img_bytes = sandbox.desktop.screenshot_region(100, 100, 500, 300)
            >>> with open('region.png', 'wb') as f:
            ...     f.write(img_bytes)
        """
        self._check_availability()
        
        logger.debug(f"Capture screenshot region: ({x}, {y}) {width}x{height}")
        
        response = self._client.post(
            "/desktop/screenshot/region",
            json={
                "x": x,
                "y": y,
                "width": width,
                "height": height
            },
            operation="capture screenshot region"
        )
        
        return response.content
    
    # =============================================================================
    # SCREEN RECORDING
    # =============================================================================
    
    def start_recording(
        self,
        fps: int = 10,
        format: str = "mp4",
        quality: str = "medium"
    ) -> RecordingInfo:
        """
        Start screen recording.
        
        Args:
            fps: Frames per second (default: 10)
            format: Video format ('mp4', 'webm')
            quality: Video quality ('low', 'medium', 'high')
        
        Returns:
            Recording information with recording_id
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> rec = sandbox.desktop.start_recording(fps=30, quality="high")
            >>> print(f"Recording ID: {rec.recording_id}")
            >>> # ... do stuff ...
            >>> sandbox.desktop.stop_recording(rec.recording_id)
        """
        self._check_availability()
        
        logger.debug(f"Start recording: fps={fps}, format={format}, quality={quality}")
        
        response = self._client.post(
            "/desktop/recording/start",
            json={
                "fps": fps,
                "format": format,
                "quality": quality
            },
            operation="start recording"
        )
        
        data = response.json()
        return RecordingInfo(
            recording_id=data.get("recording_id", ""),
            status=data.get("status", "recording"),
            fps=fps,
            format=format
        )
    
    def stop_recording(self, recording_id: str) -> RecordingInfo:
        """
        Stop screen recording.
        
        Args:
            recording_id: Recording ID from start_recording()
        
        Returns:
            Recording information with status and file size
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> rec = sandbox.desktop.start_recording()
            >>> # ... do stuff ...
            >>> final_rec = sandbox.desktop.stop_recording(rec.recording_id)
            >>> print(f"Duration: {final_rec.duration}s")
            >>> print(f"Size: {final_rec.file_size} bytes")
        """
        self._check_availability()
        
        logger.debug(f"Stop recording: {recording_id}")
        
        response = self._client.post(
            "/desktop/recording/stop",
            json={"recording_id": recording_id},
            operation="stop recording"
        )
        
        data = response.json()
        return RecordingInfo(
            recording_id=recording_id,
            status=data.get("status", "stopped"),
            duration=data.get("duration", 0.0),
            file_size=data.get("file_size", 0),
            format=data.get("format", "mp4")
        )
    
    def get_recording_status(self, recording_id: str) -> RecordingInfo:
        """
        Get recording status.
        
        Args:
            recording_id: Recording ID
        
        Returns:
            Recording information
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> status = sandbox.desktop.get_recording_status(rec.recording_id)
            >>> if status.is_ready:
            ...     video = sandbox.desktop.download_recording(rec.recording_id)
        """
        self._check_availability()
        
        response = self._client.get(
            "/desktop/recording/status",
            params={"id": recording_id},
            operation="get recording status"
        )
        
        data = response.json()
        return RecordingInfo(
            recording_id=recording_id,
            status=data.get("status", "unknown"),
            duration=data.get("duration", 0.0),
            file_size=data.get("file_size", 0)
        )
    
    def download_recording(self, recording_id: str) -> bytes:
        """
        Download recorded video.
        
        Args:
            recording_id: Recording ID
        
        Returns:
            Video file bytes
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> video_bytes = sandbox.desktop.download_recording(rec.recording_id)
            >>> with open('recording.mp4', 'wb') as f:
            ...     f.write(video_bytes)
        """
        self._check_availability()
        
        logger.debug(f"Download recording: {recording_id}")
        
        response = self._client.get(
            "/desktop/recording/download",
            params={"id": recording_id},
            operation="download recording",
            timeout=120  # Longer timeout for video download
        )
        
        return response.content
    
    # =============================================================================
    # WINDOW MANAGEMENT
    # =============================================================================
    
    def get_windows(self) -> List[WindowInfo]:
        """
        Get list of all windows.
        
        Returns:
            List of window information
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> windows = sandbox.desktop.get_windows()
            >>> for w in windows:
            ...     print(f"{w.title}: {w.width}x{w.height} at ({w.x}, {w.y})")
        """
        self._check_availability()
        
        logger.debug("Get windows list")
        
        response = self._client.get(
            "/desktop/windows",
            operation="get windows"
        )
        
        data = response.json()
        windows = []
        for win in data.get("windows", []):
            windows.append(WindowInfo(
                id=win.get("id", ""),
                title=win.get("title", ""),
                x=win.get("x", 0),
                y=win.get("y", 0),
                width=win.get("width", 0),
                height=win.get("height", 0),
                desktop=win.get("desktop"),
                pid=win.get("pid")
            ))
        
        return windows
    
    def focus_window(self, window_id: str) -> None:
        """
        Focus (activate) window.
        
        Args:
            window_id: Window ID from get_windows()
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> windows = sandbox.desktop.get_windows()
            >>> if windows:
            ...     sandbox.desktop.focus_window(windows[0].id)
        """
        self._check_availability()
        
        logger.debug(f"Focus window: {window_id}")
        
        self._client.post(
            "/desktop/windows/focus",
            json={"window_id": window_id},
            operation="focus window"
        )
    
    def close_window(self, window_id: str) -> None:
        """
        Close window.
        
        Args:
            window_id: Window ID from get_windows()
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> windows = sandbox.desktop.get_windows()
            >>> for w in windows:
            ...     if "Firefox" in w.title:
            ...         sandbox.desktop.close_window(w.id)
        """
        self._check_availability()
        
        logger.debug(f"Close window: {window_id}")
        
        self._client.post(
            "/desktop/windows/close",
            json={"window_id": window_id},
            operation="close window"
        )
    
    def resize_window(self, window_id: str, width: int, height: int) -> None:
        """
        Resize window.
        
        Args:
            window_id: Window ID from get_windows()
            width: New width
            height: New height
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> windows = sandbox.desktop.get_windows()
            >>> if windows:
            ...     sandbox.desktop.resize_window(windows[0].id, 800, 600)
        """
        self._check_availability()
        
        logger.debug(f"Resize window {window_id}: {width}x{height}")
        
        self._client.post(
            "/desktop/windows/resize",
            json={
                "window_id": window_id,
                "width": width,
                "height": height
            },
            operation="resize window"
        )
    
    def minimize_window(self, window_id: str) -> None:
        """
        Minimize window.
        
        Args:
            window_id: Window ID from get_windows()
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> windows = sandbox.desktop.get_windows()
            >>> if windows:
            ...     sandbox.desktop.minimize_window(windows[0].id)
        """
        self._check_availability()
        
        logger.debug(f"Minimize window {window_id}")
        
        self._client.post(
            "/desktop/windows/minimize",
            json={"window_id": window_id},
            operation="minimize window"
        )
    
    # =============================================================================
    # DISPLAY
    # =============================================================================
    
    def get_display(self) -> DisplayInfo:
        """
        Get current display resolution.
        
        Returns:
            Display information
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> display = sandbox.desktop.get_display()
            >>> print(f"Resolution: {display.resolution}")
            >>> print(f"Size: {display.width}x{display.height}")
        """
        self._check_availability()
        
        response = self._client.get(
            "/desktop/display",
            operation="get display info"
        )
        
        data = response.json()
        return DisplayInfo(
            width=data.get("width", 1920),
            height=data.get("height", 1080),
            depth=data.get("depth", 24)
        )
    
    def get_available_resolutions(self) -> List[Tuple[int, int]]:
        """
        Get available display resolutions.
        
        Returns:
            List of (width, height) tuples
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> resolutions = sandbox.desktop.get_available_resolutions()
            >>> for w, h in resolutions:
            ...     print(f"{w}x{h}")
        """
        self._check_availability()
        
        response = self._client.get(
            "/desktop/display/available",
            operation="get available resolutions"
        )
        
        data = response.json()
        resolutions = []
        for res in data.get("resolutions", []):
            if isinstance(res, dict):
                resolutions.append((res.get("width", 0), res.get("height", 0)))
            elif isinstance(res, (list, tuple)) and len(res) >= 2:
                resolutions.append((res[0], res[1]))
        
        return resolutions
    
    def set_resolution(self, width: int, height: int) -> DisplayInfo:
        """
        Set display resolution.
        
        Args:
            width: Screen width
            height: Screen height
        
        Returns:
            New display information
        
        Raises:
            DesktopNotAvailableError: If desktop not available
        
        Example:
            >>> display = sandbox.desktop.set_resolution(1920, 1080)
            >>> print(f"New resolution: {display.resolution}")
        """
        self._check_availability()
        
        logger.debug(f"Set resolution: {width}x{height}")
        
        response = self._client.post(
            "/desktop/display/set",
            json={
                "width": width,
                "height": height
            },
            operation="set display resolution"
        )
        
        data = response.json()
        return DisplayInfo(
            width=data.get("width", width),
            height=data.get("height", height),
            depth=data.get("depth", 24)
        )
    
    # =============================================================================
    # X11 ADVANCED FEATURES
    # =============================================================================
    
    def ocr(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        *,
        language: str = "eng",
        timeout: Optional[int] = None
    ) -> str:
        """
        Perform OCR on a screen region.
        
        Args:
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of region
            height: Height of region
            language: OCR language (default: "eng")
            timeout: Request timeout in seconds
        
        Returns:
            Extracted text from the region
        
        Example:
            >>> text = sandbox.desktop.ocr(100, 100, 400, 200)
            >>> print(f"Extracted: {text}")
        """
        self._check_availability()
        
        response = self._client.post(
            "/desktop/x11/ocr",
            json={"x": x, "y": y, "width": width, "height": height, "language": language},
            operation="OCR screen region",
            timeout=timeout
        )
        
        data = response.json()
        return data.get("text", "")
    
    def find_element(
        self,
        text: str,
        *,
        timeout: Optional[int] = None
    ) -> Optional[dict]:
        """
        Find UI element by text.
        
        Args:
            text: Text to search for
            timeout: Request timeout in seconds
        
        Returns:
            Dict with element coordinates (x, y, width, height) or None
        
        Example:
            >>> element = sandbox.desktop.find_element("Submit")
            >>> if element:
            ...     sandbox.desktop.click(element['x'], element['y'])
        """
        self._check_availability()
        
        response = self._client.post(
            "/desktop/x11/find_element",
            json={"text": text},
            operation="find UI element",
            timeout=timeout
        )
        
        data = response.json()
        return data.get("element")
    
    def wait_for(
        self,
        text: str,
        *,
        timeout: int = 30
    ) -> dict:
        """
        Wait for UI element to appear.
        
        Args:
            text: Text to wait for
            timeout: Max wait time in seconds
        
        Returns:
            Dict with element coordinates when found
        
        Example:
            >>> element = sandbox.desktop.wait_for("Loading complete", timeout=60)
            >>> print(f"Found at: {element['x']}, {element['y']}")
        """
        self._check_availability()
        
        response = self._client.post(
            "/desktop/x11/wait_for",
            json={"text": text, "timeout": timeout},
            operation="wait for element",
            timeout=timeout + 5
        )
        
        data = response.json()
        return data.get("element", {})
    
    def drag_drop(
        self,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        *,
        timeout: Optional[int] = None
    ) -> None:
        """
        Drag and drop from one point to another.
        
        Args:
            from_x: Starting X coordinate
            from_y: Starting Y coordinate
            to_x: Ending X coordinate
            to_y: Ending Y coordinate
            timeout: Request timeout in seconds
        
        Example:
            >>> # Drag file to folder
            >>> sandbox.desktop.drag_drop(100, 200, 500, 300)
        """
        self._check_availability()
        
        self._client.post(
            "/desktop/x11/drag_drop",
            json={"from_x": from_x, "from_y": from_y, "to_x": to_x, "to_y": to_y},
            operation="drag and drop",
            timeout=timeout
        )
    
    def get_bounds(
        self,
        text: str,
        *,
        timeout: Optional[int] = None
    ) -> dict:
        """
        Get bounding box of UI element.
        
        Args:
            text: Text to search for
            timeout: Request timeout in seconds
        
        Returns:
            Dict with x, y, width, height
        
        Example:
            >>> bounds = sandbox.desktop.get_bounds("OK Button")
            >>> print(f"Button at: {bounds['x']}, {bounds['y']}")
            >>> print(f"Size: {bounds['width']}x{bounds['height']}")
        """
        self._check_availability()
        
        response = self._client.post(
            "/desktop/x11/get_bounds",
            json={"text": text},
            operation="get element bounds",
            timeout=timeout
        )
        
        return response.json()
    
    def capture_window(
        self,
        window_id: Optional[str] = None,
        *,
        timeout: Optional[int] = None
    ) -> bytes:
        """
        Capture screenshot of specific window.
        
        Args:
            window_id: Window ID (None for active window)
            timeout: Request timeout in seconds
        
        Returns:
            PNG image bytes
        
        Example:
            >>> # Capture active window
            >>> img = sandbox.desktop.capture_window()
            >>> with open('window.png', 'wb') as f:
            ...     f.write(img)
            >>> 
            >>> # Capture specific window
            >>> img = sandbox.desktop.capture_window(window_id="0x1234567")
        """
        self._check_availability()
        
        params = {}
        if window_id:
            params['window_id'] = window_id
        
        response = self._client.get(
            "/desktop/x11/capture_window",
            params=params,
            operation="capture window",
            timeout=timeout
        )
        
        return response.content

    def hotkey(
        self,
        modifiers: List[str],
        key: str,
        *,
        timeout: Optional[int] = None
    ) -> None:
        """
        Execute hotkey combination (e.g., Ctrl+C, Alt+Tab).

        Args:
            modifiers: List of modifier keys (e.g., ["ctrl", "shift"])
            key: Main key to press (e.g., "c", "tab")
            timeout: Request timeout in seconds

        Example:
            >>> # Copy: Ctrl+C
            >>> sandbox.desktop.hotkey(["ctrl"], "c")
            >>>
            >>> # Paste: Ctrl+V
            >>> sandbox.desktop.hotkey(["ctrl"], "v")
            >>>
            >>> # Switch window: Alt+Tab
            >>> sandbox.desktop.hotkey(["alt"], "tab")
            >>>
            >>> # Screenshot: Ctrl+Shift+P
            >>> sandbox.desktop.hotkey(["ctrl", "shift"], "p")
        """
        self._check_availability()

        response = self._client.post(
            "/desktop/x11/hotkey",
            json={"modifiers": modifiers, "key": key},
            operation="execute hotkey",
            timeout=timeout
        )

        logger.debug(f"Hotkey executed: {modifiers}+{key}")

    def get_debug_logs(self) -> List[str]:
        """
        Get desktop automation debug logs.

        Returns debug logs from the desktop automation system, useful for
        troubleshooting automation issues.

        Returns:
            List of log lines

        Example:
            >>> logs = sandbox.desktop.get_debug_logs()
            >>> for log in logs[-10:]:  # Last 10 lines
            ...     print(log)

        Note:
            Requires Agent v3.2.0+. GET /desktop/debug/logs endpoint.
        """
        self._check_availability()

        response = self._client.get(
            "/desktop/debug/logs",
            operation="get desktop debug logs"
        )

        data = response.json()
        return data.get("logs", [])

    def get_debug_processes(self) -> List[Dict[str, Any]]:
        """
        Get desktop-related processes for debugging.

        Returns information about X11 and desktop-related processes.

        Returns:
            List of dicts with process information:
            - pid: Process ID
            - name: Process name
            - command: Full command line

        Example:
            >>> processes = sandbox.desktop.get_debug_processes()
            >>> for proc in processes:
            ...     print(f"{proc['pid']}: {proc['name']}")

        Note:
            Requires Agent v3.2.0+. GET /desktop/debug/processes endpoint.
        """
        self._check_availability()

        response = self._client.get(
            "/desktop/debug/processes",
            operation="get desktop debug processes"
        )

        data = response.json()
        return data.get("processes", [])

    def __repr__(self) -> str:
        status = "available" if self._available else "unknown" if not self._checked else "unavailable"
        return f"<Desktop status={status}>"

