"""
Windows Bluetooth Adapter.
Interacts with Windows Radio Management and Bluetooth interfaces.
"""

import subprocess
from typing import Dict, Any
from utils.logger import logger
from utils.exceptions import ActionExecutionError


class WindowsBluetoothAdapter:
    """Manages Bluetooth radio state on Windows 11."""

    def get_bluetooth_status(self) -> Dict[str, Any]:
        """Queries Bluetooth service and radio state."""
        try:
            # Query Bluetooth support service status
            cmd = ["powershell", "-NoProfile", "-Command", "Get-Service -Name bthserv | Select-Object -ExpandProperty Status"]
            res = subprocess.run(cmd, capture_output=True, text=True, check=False)
            status_str = res.stdout.strip().lower()

            is_running = (status_str == "running")
            return {
                "available": bool(status_str),
                "state": "enabled" if is_running else "disabled",
                "service_status": status_str or "unavailable",
            }
        except Exception as e:
            logger.error(f"Error querying Bluetooth: {e}")
            raise ActionExecutionError(f"Could not retrieve Bluetooth status: {e}") from e

    def set_bluetooth_state(self, enable: bool) -> bool:
        """Toggles Bluetooth radio or service."""
        try:
            action = "start" if enable else "stop"
            cmd = ["powershell", "-NoProfile", "-Command", f"{action.capitalize()}-Service -Name bthserv"]
            res = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if res.returncode != 0:
                raise ActionExecutionError("Bluetooth toggle requires elevated privileges or unsupported radio.")

            return True
        except Exception as e:
            logger.error(f"Bluetooth toggle error: {e}")
            raise ActionExecutionError(f"Could not modify Bluetooth state: {e}") from e


windows_bluetooth = WindowsBluetoothAdapter()
