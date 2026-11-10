"""
Volume Controller for AURA.
Manages system volume and mute controls through platform adapter.
"""

from typing import Tuple, Optional
from platform_adapters.windows_audio import windows_audio
from utils.helpers import clamp
from utils.logger import logger


class VolumeController:
    """Controls master audio volume."""

    def __init__(self, adapter=windows_audio) -> None:
        self.adapter = adapter

    def set_volume(self, level: int) -> Tuple[bool, int, int, str]:
        """
        Sets master volume to target level (0-100).
        Returns (success, requested_level, actual_level, message).
        """
        target = clamp(level, 0, 100)
        actual = self.adapter.set_volume(target)
        return True, target, actual, f"Volume set to {actual}%."

    def increase_volume(self, amount: int = 10) -> Tuple[bool, int, int, str]:
        """Increases volume by amount."""
        current = self.adapter.get_volume()
        target = clamp(current + amount, 0, 100)
        actual = self.adapter.set_volume(target)
        return True, target, actual, f"Volume increased to {actual}%."

    def decrease_volume(self, amount: int = 10) -> Tuple[bool, int, int, str]:
        """Decreases volume by amount."""
        current = self.adapter.get_volume()
        target = clamp(current - amount, 0, 100)
        actual = self.adapter.set_volume(target)
        return True, target, actual, f"Volume decreased to {actual}%."

    def mute(self) -> Tuple[bool, bool, bool, str]:
        """Mutes audio."""
        actual = self.adapter.set_mute(True)
        return True, True, actual, "Audio muted."

    def unmute(self) -> Tuple[bool, bool, bool, str]:
        """Unmutes audio."""
        actual = self.adapter.set_mute(False)
        return True, False, actual, "Audio unmuted."

    def get_volume(self) -> int:
        """Reads current volume."""
        return self.adapter.get_volume()


volume_controller = VolumeController()
