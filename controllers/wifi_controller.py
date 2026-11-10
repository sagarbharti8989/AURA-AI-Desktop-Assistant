"""
Wi-Fi Controller for AURA.
Manages Wi-Fi status and adapter toggling.
"""

from typing import Tuple, Dict, Any
from platform_adapters.windows_network import windows_network
from utils.logger import logger


class WifiController:
    """Controls Wi-Fi operations."""

    def __init__(self, adapter=windows_network) -> None:
        self.adapter = adapter

    def get_status(self) -> Tuple[bool, None, Dict[str, Any], str]:
        """Queries Wi-Fi status."""
        status = self.adapter.get_wifi_status()
        if not status.get("available"):
            return True, None, status, "No Wi-Fi adapter detected."
        if status.get("connected"):
            return True, None, status, f"Wi-Fi is connected to {status.get('ssid')}."
        return True, None, status, f"Wi-Fi is {status.get('state')}."

    def enable(self) -> Tuple[bool, bool, bool, str]:
        """Enables Wi-Fi adapter."""
        success = self.adapter.set_wifi_state(True)
        return success, True, True, "Wi-Fi enabled."

    def disable(self) -> Tuple[bool, bool, bool, str]:
        """Disables Wi-Fi adapter."""
        success = self.adapter.set_wifi_state(False)
        return success, False, False, "Wi-Fi disabled."


wifi_controller = WifiController()
