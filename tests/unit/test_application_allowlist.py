"""Tests for configured application aliases and safe argument-based launches."""

from config import config
from intelligence.command_parser import command_parser
from platform_adapters.windows_process import WindowsProcessAdapter


def test_added_applications_are_approved_and_parseable():
    expected_aliases = {
        "paint",
        "windows terminal",
        "terminal",
        "vlc",
        "vlc media player",
        "settings",
        "windows settings",
    }

    assert expected_aliases <= config.app_aliases.keys()
    for alias in ("Paint", "Windows Terminal", "VLC media player", "Settings"):
        intent, params, refusal = command_parser.parse(f"open {alias}")
        assert intent == "open_app"
        assert params["app_name"].lower() == alias.lower()
        assert refusal is None


def test_settings_launch_uses_allowlisted_arguments(monkeypatch):
    adapter = WindowsProcessAdapter()
    launched = {}

    monkeypatch.setattr(adapter, "resolve_executable", lambda _app_name: "explorer.exe")
    monkeypatch.setattr(
        "platform_adapters.windows_process.subprocess.Popen",
        lambda command, **kwargs: launched.update(command=command, kwargs=kwargs),
    )

    assert adapter.launch_app("settings")
    assert launched["command"] == ["explorer.exe", "ms-settings:"]
    assert launched["kwargs"] == {"close_fds": True}
