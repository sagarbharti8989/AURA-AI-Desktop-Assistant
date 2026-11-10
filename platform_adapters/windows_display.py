"""
Windows Display Brightness Adapter using screen-brightness-control.
"""

from typing import Optional
from utils.logger import logger
from utils.exceptions import ActionExecutionError


class WindowsDisplayAdapter:
    """Interfaces with Windows display brightness controls."""

    def get_brightness(self) -> int:
        """Returns current brightness of primary display as integer percentage (0-100)."""
        try:
            import screen_brightness_control as sbc
            levels = sbc.get_brightness(display=0)
            if levels is not None:
                if isinstance(levels, list) and levels:
                    return int(levels[0])
                elif isinstance(levels, (int, float)):
                    return int(levels)
            raise ActionExecutionError("No supported display detected for brightness control.")
        except Exception as e:
            logger.warning(f"Failed to read display brightness: {e}")
            raise ActionExecutionError("Display brightness cannot be queried on this screen.") from e

    def set_brightness(self, percentage: int) -> int:
        """Sets display brightness (0-100). Returns verified brightness."""
        try:
            import screen_brightness_control as sbc
            percentage = max(0, min(100, percentage))
            sbc.set_brightness(percentage, display=0)
            return self.get_brightness()
        except Exception as e:
            logger.warning(f"Failed to set display brightness to {percentage}%: {e}")
            raise ActionExecutionError("Display brightness cannot be adjusted on this screen.") from e


windows_display = WindowsDisplayAdapter()
