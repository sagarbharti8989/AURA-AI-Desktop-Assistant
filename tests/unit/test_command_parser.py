"""
Unit tests for deterministic CommandParser.
"""

import pytest
from intelligence.command_parser import command_parser


def test_parse_set_volume():
    intent, params, refusal = command_parser.parse("set volume to 40 percent")
    assert refusal is None
    assert intent == "set_volume"
    assert params == {"level": 40}


def test_parse_increase_volume():
    intent, params, refusal = command_parser.parse("increase volume by 15")
    assert refusal is None
    assert intent == "increase_volume"
    assert params == {"amount": 15}


def test_parse_mute_unmute():
    intent, params, refusal = command_parser.parse("mute my audio")
    assert refusal is None
    assert intent == "mute_audio"

    intent, params, refusal = command_parser.parse("unmute laptop")
    assert refusal is None
    assert intent == "unmute_audio"


def test_parse_set_brightness():
    intent, params, refusal = command_parser.parse("set brightness to 80")
    assert refusal is None
    assert intent == "set_brightness"
    assert params == {"level": 80}


def test_parse_open_app():
    intent, params, refusal = command_parser.parse("open chrome")
    assert refusal is None
    assert intent == "open_app"
    assert params == {"app_name": "chrome"}


def test_parse_lock_workstation():
    intent, params, refusal = command_parser.parse("lock my workstation")
    assert refusal is None
    assert intent == "lock_system"


def test_parse_check_battery():
    intent, params, refusal = command_parser.parse("how much is the battery")
    assert refusal is None
    assert intent == "check_battery"


def test_parse_wifi_and_bluetooth():
    intent, _, _ = command_parser.parse("turn on wifi")
    assert intent == "enable_wifi"

    intent, _, _ = command_parser.parse("check bluetooth status")
    assert intent == "get_bluetooth_status"

