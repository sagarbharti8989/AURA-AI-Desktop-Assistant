"""
System-wide constants and enumerations for AURA.
"""

from enum import Enum


class AssistantState(str, Enum):
    """Operational states of AURA."""
    INACTIVE = "INACTIVE"
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    RESPONDING = "RESPONDING"
    ERROR = "ERROR"


class PermissionKey(str, Enum):
    """Predefined capability permission identifiers."""
    APP_LAUNCH = "app_launch"
    APP_CLOSE = "app_close"
    VOLUME_CONTROL = "volume_control"
    BRIGHTNESS_CONTROL = "brightness_control"
    WIFI_CONTROL = "wifi_control"
    BLUETOOTH_CONTROL = "bluetooth_control"
    SYSTEM_CONTROL = "system_control"


# Security Constants
SECURITY_REJECT_POWER_MESSAGE = "I am not authorized to shut down or restart the system."
SECURITY_REJECT_FILE_MESSAGE = "I do not have access to personal files."
SECURITY_REJECT_UNAUTHORIZED_MESSAGE = "This operation is not authorized in your permissions."
SECURITY_REJECT_UNKNOWN_MESSAGE = "I could not find a supported action for that instruction."

