"""
Windows Network Adapter for Wi-Fi management.
Interacts with Windows Wi-Fi interfaces via netsh.
"""

import subprocess
import re
from typing import Dict, Any
from utils.logger import logger
from utils.exceptions import ActionExecutionError
from utils.elevate import run_as_admin

class WindowsNetworkAdapter:
    """Manages Wi‑Fi adapter state."""

    def __init__(self) -> None:
        self._cached_interface: str | None = None

    def _detect_interface(self) -> str:
        """Detect the Wi‑Fi interface name (e.g., "Wi‑Fi" or "Wireless Network Connection")."""
        try:
            res = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                check=False,
            )
            m = re.search(r"Name\s*:\s*(.+)", res.stdout)
            iface = m.group(1).strip() if m else "Wi‑Fi"
            self._cached_interface = iface
            return iface
        except Exception as e:
            logger.error(f"Failed to detect Wi‑Fi interface: {e}")
            raise ActionExecutionError(f"Could not detect Wi‑Fi interface: {e}") from e

    def get_wifi_status(self) -> Dict[str, Any]:
        """Queries Wi‑Fi interface status."""
        try:
            res = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                check=False,
            )
            output = res.stdout

            if "There is no wireless interface on the system" in output:
                return {"available": False, "state": "No Wi‑Fi adapter found", "connected": False}

            state_match = re.search(r"State\s*:\s*(\w+)", output)
            ssid_match = re.search(r"SSID\s*:\s*(.+)", output)

            state = state_match.group(1) if state_match else "unknown"
            ssid = ssid_match.group(1).strip() if ssid_match else None
            connected = state.lower() == "connected"

            return {
                "available": True,
                "state": state,
                "connected": connected,
                "ssid": ssid,
            }
        except Exception as e:
            logger.error(f"Error checking Wi‑Fi status: {e}")
            raise ActionExecutionError(f"Could not retrieve Wi‑Fi status: {e}") from e

    def set_wifi_state(self, enable: bool) -> bool:
        """Enables or disables the detected Wi‑Fi interface."""
        try:
            interfaces = []
            if self._cached_interface:
                interfaces.append(self._cached_interface)
            else:
                res = subprocess.run(
                    ["netsh", "interface", "show", "interface"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                for match in re.finditer(r"^\s*([^\r\n]+?)\s+\w+\s*\|\s*Enabled|Disabled", res.stdout, re.MULTILINE):
                    iface = match.group(1).strip()
                    if iface:
                        interfaces.append(iface)
                if not interfaces:
                    interfaces.append(self._detect_interface())

            if not interfaces:
                raise ActionExecutionError("No Wi‑Fi interface was detected.")

            action = "enabled" if enable else "disabled"
            last_error = None
            for iface in interfaces:
                cmd = ["netsh", "interface", "set", "interface", f"name={iface}", f"admin={action}"]
                try:
                    res = run_as_admin(cmd)
                except PermissionError as e:
                    raise ActionExecutionError(str(e)) from e
                if res.returncode == 0:
                    self._cached_interface = iface
                    return True
                last_error = res.stderr.strip() or res.stdout.strip() or f"netsh failed for {iface}."

            logger.warning(f"Wi‑Fi toggle failed for all interfaces: {last_error}")
            raise ActionExecutionError(
                f"Could not {('enable' if enable else 'disable')} Wi‑Fi. {last_error}"
            )
        except ActionExecutionError:
            raise
        except Exception as e:
            logger.error(f"Failed to set Wi‑Fi state: {e}")
            raise ActionExecutionError(f"Wi‑Fi operation failed: {e}") from e

windows_network = WindowsNetworkAdapter()
