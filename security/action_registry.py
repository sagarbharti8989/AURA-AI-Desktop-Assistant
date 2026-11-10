"""
Defines the strictly authorized action registry for AURA.
Any action outside this registry is rejected immediately.
"""

from typing import Dict, Any

ACTION_REGISTRY: Dict[str, Dict[str, Any]] = {
    "open_app": {
        "controller": "application",
        "permission": "app_launch",
        "confirmation": False,
        "description": "Launch a whitelisted application",
    },
    "close_app": {
        "controller": "application",
        "permission": "app_close",
        "confirmation": False,
        "description": "Gracefully close an application window",
    },
    "set_volume": {
        "controller": "volume",
        "permission": "volume_control",
        "confirmation": False,
        "description": "Set master volume percentage",
    },
    "increase_volume": {
        "controller": "volume",
        "permission": "volume_control",
        "confirmation": False,
        "description": "Increase master volume",
    },
    "decrease_volume": {
        "controller": "volume",
        "permission": "volume_control",
        "confirmation": False,
        "description": "Decrease master volume",
    },
    "mute_audio": {
        "controller": "volume",
        "permission": "volume_control",
        "confirmation": False,
        "description": "Mute master audio",
    },
    "unmute_audio": {
        "controller": "volume",
        "permission": "volume_control",
        "confirmation": False,
        "description": "Unmute master audio",
    },
    "set_brightness": {
        "controller": "brightness",
        "permission": "brightness_control",
        "confirmation": False,
        "description": "Set primary display brightness percentage",
    },
    "increase_brightness": {
        "controller": "brightness",
        "permission": "brightness_control",
        "confirmation": False,
        "description": "Increase primary display brightness",
    },
    "decrease_brightness": {
        "controller": "brightness",
        "permission": "brightness_control",
        "confirmation": False,
        "description": "Decrease primary display brightness",
    },
    "get_wifi_status": {
        "controller": "wifi",
        "permission": "wifi_control",
        "confirmation": False,
        "description": "Query Wi-Fi adapter status",
    },
    "enable_wifi": {
        "controller": "wifi",
        "permission": "wifi_control",
        "confirmation": False,
        "description": "Enable Wi-Fi adapter",
    },
    "disable_wifi": {
        "controller": "wifi",
        "permission": "wifi_control",
        "confirmation": False,
        "description": "Disable Wi-Fi adapter",
    },
    "get_bluetooth_status": {
        "controller": "bluetooth",
        "permission": "bluetooth_control",
        "confirmation": False,
        "description": "Query Bluetooth radio status",
    },
    "enable_bluetooth": {
        "controller": "bluetooth",
        "permission": "bluetooth_control",
        "confirmation": False,
        "description": "Enable Bluetooth radio",
    },
    "disable_bluetooth": {
        "controller": "bluetooth",
        "permission": "bluetooth_control",
        "confirmation": False,
        "description": "Disable Bluetooth radio",
    },
    "lock_system": {
        "controller": "system",
        "permission": "system_control",
        "confirmation": False,
        "description": "Lock Windows session",
    },
    "check_battery": {
        "controller": "system",
        "permission": "system_control",
        "confirmation": False,
        "description": "Check battery percentage and power source",
    },
    "take_screenshot": {
        "controller": "system",
        "permission": "system_control",
        "confirmation": False,
        "description": "Capture screen to clipboard or app directory",
    },
}

