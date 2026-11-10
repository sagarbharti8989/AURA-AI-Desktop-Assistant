"""
Unit tests for PermissionManager and SQLite repository toggles.
"""

import pytest
from security.permission_manager import permission_manager
from utils.constants import (
    SECURITY_REJECT_UNAUTHORIZED_MESSAGE,
    SECURITY_REJECT_UNKNOWN_MESSAGE,
)


def test_permission_toggle_enforcement():
    # Disable volume control
    permission_manager.set_permission("volume_control", False)
    authorized, msg, _ = permission_manager.validate_action("set_volume", {"level": 50})
    assert not authorized
    assert msg == SECURITY_REJECT_UNAUTHORIZED_MESSAGE

    # Re-enable volume control
    permission_manager.set_permission("volume_control", True)
    authorized, msg, params = permission_manager.validate_action("set_volume", {"level": 50})
    assert authorized
    assert msg is None
    assert params["level"] == 50


def test_reject_unknown_action():
    authorized, msg, _ = permission_manager.validate_action("format_hard_drive", {})
    assert not authorized
    assert msg == SECURITY_REJECT_UNKNOWN_MESSAGE

