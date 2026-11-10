"""
Windows System Utilities Adapter.
Handles workstation lock, battery queries, and screenshots.
Strictly excludes any power-off, shutdown, or restart capabilities.
"""

import ctypes
import os
import psutil
from typing import Dict, Any
from config import BASE_DIR
from utils.logger import logger
from utils.exceptions import ActionExecutionError


class WindowsSystemAdapter:
    """Safe Windows system-level utility operations."""

    def lock_workstation(self) -> bool:
        """Locks the Windows user session via LockWorkStation API."""
        try:
            logger.info("Locking Windows workstation.")
            result = ctypes.windll.user32.LockWorkStation()
            if result == 0:
                raise ActionExecutionError("Windows API LockWorkStation failed.")
            return True
        except Exception as e:
            logger.error(f"Failed to lock workstation: {e}")
            raise ActionExecutionError(f"Could not lock workstation: {e}") from e

    def get_battery_status(self) -> Dict[str, Any]:
        """Queries current battery percentage and power plugged state."""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return {
                    "has_battery": False,
                    "percent": 100,
                    "power_plugged": True,
                    "message": "Desktop system or no battery detected.",
                }

            return {
                "has_battery": True,
                "percent": int(battery.percent),
                "power_plugged": bool(battery.power_plugged),
                "secs_left": battery.secsleft,
                "message": f"Battery is at {int(battery.percent)}%, {'plugged in' if battery.power_plugged else 'on battery'}.",
            }
        except Exception as e:
            logger.error(f"Failed to read battery: {e}")
            raise ActionExecutionError(f"Could not retrieve battery status: {e}") from e

    def take_screenshot(self) -> str:
        """
        Captures the screen and stores it in the isolated application screenshots folder.
        Never accesses user personal folders.
        """
        try:
            from PIL import ImageGrab
            screenshot_dir = BASE_DIR / "screenshots"
            screenshot_dir.mkdir(exist_ok=True)

            from datetime import datetime
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            target_path = screenshot_dir / filename

            img = ImageGrab.grab()
            img.save(str(target_path), "PNG")
            logger.info(f"Screenshot saved to isolated app path: {target_path}")
            return str(target_path)
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            raise ActionExecutionError(f"Could not capture screenshot: {e}") from e


windows_system = WindowsSystemAdapter()
