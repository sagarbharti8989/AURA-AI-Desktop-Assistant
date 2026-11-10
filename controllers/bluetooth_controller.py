"""
Bluetooth Controller for AURA.
Manages Bluetooth radio state through platform adapter.
"""

from typing import Tuple, Dict, Any
from platform_adapters.windows_bluetooth import windows_bluetooth
from utils.logger import logger


class BluetoothController:
    """Controls Bluetooth operations."""

    def __init__(self, adapter=windows_bluetooth) -> None:
        self.adapter = adapter

    def get_status(self) -> Tuple[bool, None, Dict[str, Any], str]:
        """Queries Bluetooth status."""
        status = self.adapter.get_bluetooth_status()
        state = status.get("state", "unknown")
        return True, None, status, f"Bluetooth is {state}."

    def enable(self) -> Tuple[bool, bool, bool, str]:
        """Enables Bluetooth radio."""
        success = self.adapter.set_bluetooth_state(True)
        return success, True, True, "Bluetooth enabled."

    def disable(self) -> Tuple[bool, bool, bool, str]:
        """Disables Bluetooth radio."""
        success = self.adapter.set_bluetooth_state(False)
        return success, False, False, "Bluetooth disabled."


bluetooth_controller = BluetoothController()
