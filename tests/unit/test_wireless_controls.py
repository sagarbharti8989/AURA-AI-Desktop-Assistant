"""Regression tests for Wi‑Fi and Bluetooth control permission handling."""

import pytest

from platform_adapters.windows_bluetooth import WindowsBluetoothAdapter
from platform_adapters.windows_network import WindowsNetworkAdapter
from utils.elevate import run_as_admin
from utils.exceptions import ActionExecutionError


def test_run_as_admin_requires_elevation(monkeypatch):
    monkeypatch.setattr(
        __import__("ctypes").windll.shell32,
        "IsUserAnAdmin",
        lambda: False,
    )
    with pytest.raises(PermissionError, match="Administrator privileges"):
        run_as_admin(["netsh", "interface", "show", "interface"])


def test_wifi_toggle_raises_clear_admin_error(monkeypatch):
    adapter = WindowsNetworkAdapter()

    monkeypatch.setattr(adapter, "_detect_interface", lambda: "Wi‑Fi")

    def _raise_permission(_cmd):
        raise PermissionError("Administrator privileges are required to change Wi‑Fi or Bluetooth settings.")

    monkeypatch.setattr("platform_adapters.windows_network.run_as_admin", _raise_permission)

    with pytest.raises(ActionExecutionError, match="Administrator privileges"):
        adapter.set_wifi_state(True)


def test_bluetooth_toggle_raises_clear_admin_error(monkeypatch):
    adapter = WindowsBluetoothAdapter()

    def _raise_permission(_cmd):
        raise PermissionError("Administrator privileges are required to change Wi‑Fi or Bluetooth settings.")

    monkeypatch.setattr("platform_adapters.windows_bluetooth.run_as_admin", _raise_permission)

    with pytest.raises(ActionExecutionError, match="Administrator privileges"):
        adapter.set_bluetooth_state(True)
