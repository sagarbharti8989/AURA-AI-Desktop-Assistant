"""
Security Policy Tests for AURA.
Verifies strict refusal of power termination and personal file access.
"""

import pytest
from security.security_policy import SecurityPolicy
from utils.constants import (
    SECURITY_REJECT_POWER_MESSAGE,
    SECURITY_REJECT_FILE_MESSAGE,
)
from core.assistant import assistant


def test_refuse_shutdown_commands():
    power_commands = [
        "shut down my computer",
        "shutdown",
        "restart the laptop",
        "reboot windows",
        "power off immediately",
        "hibernate my pc",
    ]
    for cmd in power_commands:
        allowed, msg = SecurityPolicy.evaluate_text_input(cmd)
        assert not allowed, f"Command '{cmd}' should have been blocked!"
        assert msg == SECURITY_REJECT_POWER_MESSAGE


def test_refuse_file_access_commands():
    file_commands = [
        "open my documents",
        "read files in downloads",
        "show my desktop files",
        "find passwords.txt",
        "read resume.pdf",
        "search files for bank statement",
        "delete my files",
        "browse directory",
    ]
    for cmd in file_commands:
        allowed, msg = SecurityPolicy.evaluate_text_input(cmd)
        assert not allowed, f"Command '{cmd}' should have been blocked!"
        assert msg == SECURITY_REJECT_FILE_MESSAGE


def test_assistant_intercepts_blocked_power_command():
    resp = assistant.process_text_command("shut down my laptop")
    assert not resp.success
    assert resp.message == SECURITY_REJECT_POWER_MESSAGE


def test_assistant_intercepts_blocked_file_access():
    resp = assistant.process_text_command("open my secret document.docx")
    assert not resp.success
    assert resp.message == SECURITY_REJECT_FILE_MESSAGE

