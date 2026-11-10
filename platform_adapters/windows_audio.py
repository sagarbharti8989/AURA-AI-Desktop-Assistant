"""
Windows Audio Adapter using pycaw and Core Audio APIs.
"""

from typing import Tuple
from utils.logger import logger
from utils.exceptions import ActionExecutionError


class WindowsAudioAdapter:
    """Interfaces with Windows Core Audio endpoints."""

    def __init__(self) -> None:
        self._endpoint_volume = None

    def _get_volume_interface(self):
        """Retrieves and initializes the IAudioEndpointVolume interface."""
        import comtypes
        comtypes.CoInitialize()

        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from ctypes import cast, POINTER

        devices = AudioUtilities.GetSpeakers()
        if not devices:
            raise ActionExecutionError("No audio playback device found.")

        if hasattr(devices, "EndpointVolume"):
            return devices.EndpointVolume

        interface = devices.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))

    def get_volume(self) -> int:
        """Returns current master volume as an integer percentage (0-100)."""
        try:
            endpoint = self._get_volume_interface()
            scalar = endpoint.GetMasterVolumeLevelScalar()
            return int(round(scalar * 100))
        except Exception as e:
            logger.error(f"Failed to get audio volume: {e}")
            raise ActionExecutionError(f"Could not read volume: {e}") from e

    def set_volume(self, percentage: int) -> int:
        """Sets master volume percentage (0-100). Returns actual volume set."""
        try:
            percentage = max(0, min(100, percentage))
            endpoint = self._get_volume_interface()
            endpoint.SetMasterVolumeLevelScalar(percentage / 100.0, None)
            actual = int(round(endpoint.GetMasterVolumeLevelScalar() * 100))
            return actual
        except Exception as e:
            logger.error(f"Failed to set audio volume to {percentage}%: {e}")
            raise ActionExecutionError(f"Could not set volume: {e}") from e

    def get_mute(self) -> bool:
        """Returns True if master audio is muted."""
        try:
            endpoint = self._get_volume_interface()
            return bool(endpoint.GetMute())
        except Exception as e:
            logger.error(f"Failed to get mute status: {e}")
            raise ActionExecutionError(f"Could not read mute status: {e}") from e

    def set_mute(self, mute: bool) -> bool:
        """Mutes or unmutes master audio. Returns actual mute state."""
        try:
            endpoint = self._get_volume_interface()
            endpoint.SetMute(1 if mute else 0, None)
            return bool(endpoint.GetMute())
        except Exception as e:
            logger.error(f"Failed to set mute={mute}: {e}")
            raise ActionExecutionError(f"Could not set mute: {e}") from e


windows_audio = WindowsAudioAdapter()
