"""
Unit tests for Pydantic request validators.
"""

import pytest
from security.request_validator import (
    validate_intent_parameters,
    SetVolumeParams,
    SetBrightnessParams,
    AppParams,
)
from utils.exceptions import InvalidCommandError


def test_volume_validation_range():
    # Valid
    valid = validate_intent_parameters("set_volume", {"level": 50})
    assert valid["level"] == 50

    # Invalid range (> 100)
    with pytest.raises(InvalidCommandError):
        validate_intent_parameters("set_volume", {"level": 150})

    # Invalid range (< 0)
    with pytest.raises(InvalidCommandError):
        validate_intent_parameters("set_volume", {"level": -10})


def test_brightness_validation_range():
    valid = validate_intent_parameters("set_brightness", {"level": 75})
    assert valid["level"] == 75

    with pytest.raises(InvalidCommandError):
        validate_intent_parameters("set_brightness", {"level": 105})


def test_app_name_sanitization():
    valid = validate_intent_parameters("open_app", {"app_name": "Chrome"})
    assert valid["app_name"] == "chrome"

    # Directory traversal prevention
    valid_sanitized = validate_intent_parameters("open_app", {"app_name": "../../Notepad"})
    assert ".." not in valid_sanitized["app_name"]
    assert "/" not in valid_sanitized["app_name"]
    assert valid_sanitized["app_name"] == "notepad"

