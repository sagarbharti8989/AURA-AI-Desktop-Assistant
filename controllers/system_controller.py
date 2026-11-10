"""
System Controller for AURA.
Manages safe system utilities: workstation lock, battery query, screenshot.
Power termination operations (shutdown, restart) are strictly excluded.
"""

from typing import Tuple, Dict, Any
from platform_adapters.windows_system import windows_system
from utils.logger import logger


class SystemController:
    """Controls safe system utilities."""

    def __init__(self, adapter=windows_system) -> None:
        self.adapter = adapter

    def lock_system(self) -> Tuple[bool, None, None, str]:
        """Locks the workstation."""
        success = self.adapter.lock_workstation()
        return success, None, None, "Workstation locked."

    def check_battery(self) -> Tuple[bool, None, Dict[str, Any], str]:
        """Queries battery status."""
        status = self.adapter.get_battery_status()
        return True, None, status, status.get("message", "Battery query completed.")

    def take_screenshot(self) -> Tuple[bool, None, str, str]:
        """Takes a screenshot to application screenshot directory."""
        path = self.adapter.take_screenshot()
        return True, None, path, "Screenshot saved."


system_controller = SystemController()
