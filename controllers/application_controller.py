"""
Application Controller for AURA.
Manages whitelisted desktop application launching and safe closing.
"""

from typing import Tuple
from platform_adapters.windows_process import windows_process
from utils.logger import logger


class ApplicationController:
    """Controls whitelisted applications."""

    def __init__(self, adapter=windows_process) -> None:
        self.adapter = adapter

    def open_app(self, app_name: str) -> Tuple[bool, str, str, str]:
        """Launches an approved application."""
        success = self.adapter.launch_app(app_name)
        msg = f"Opening {app_name.capitalize()}."
        return success, app_name, app_name, msg

    def close_app(self, app_name: str) -> Tuple[bool, str, str, str]:
        """Gracefully closes an approved application."""
        success = self.adapter.close_app_gracefully(app_name)
        msg = f"Closed {app_name.capitalize()}."
        return success, app_name, app_name, msg


application_controller = ApplicationController()
