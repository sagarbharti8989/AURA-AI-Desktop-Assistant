"""
Brightness Controller for AURA.
Controls primary display brightness through platform adapter.
"""

from typing import Tuple
from platform_adapters.windows_display import windows_display
from utils.helpers import clamp
from utils.logger import logger


class BrightnessController:
    """Controls primary display brightness."""

    def __init__(self, adapter=windows_display) -> None:
        self.adapter = adapter

    def set_brightness(self, level: int) -> Tuple[bool, int, int, str]:
        """Sets brightness to percentage (0-100)."""
        target = clamp(level, 0, 100)
        actual = self.adapter.set_brightness(target)
        return True, target, actual, f"Brightness set to {actual}%."

    def increase_brightness(self, amount: int = 10) -> Tuple[bool, int, int, str]:
        """Increases brightness by amount."""
        current = self.adapter.get_brightness()
        target = clamp(current + amount, 0, 100)
        actual = self.adapter.set_brightness(target)
        return True, target, actual, f"Brightness increased to {actual}%."

    def decrease_brightness(self, amount: int = 10) -> Tuple[bool, int, int, str]:
        """Decreases brightness by amount."""
        current = self.adapter.get_brightness()
        target = clamp(current - amount, 0, 100)
        actual = self.adapter.set_brightness(target)
        return True, target, actual, f"Brightness decreased to {actual}%."

    def get_brightness(self) -> int:
        """Reads current brightness level."""
        return self.adapter.get_brightness()


brightness_controller = BrightnessController()
