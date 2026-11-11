"""
Windows Process and Application Management Adapter.
Ensures application launch uses strictly whitelisted paths and safe subprocess invocation.
Application closing uses graceful Win32 WM_CLOSE rather than force-killing.
"""

import subprocess
import os
import shutil
import ctypes
from typing import Optional, List
from config import config
from utils.logger import logger
from utils.exceptions import ActionExecutionError


class WindowsProcessAdapter:
    """Safely manages application process lifecycle."""

    def resolve_executable(self, app_name: str) -> Optional[str]:
        """
        Resolves app_name to a validated executable from the whitelist config.
        Never inspects user personal files.
        """
        key = app_name.lower().strip()
        aliases = config.app_aliases

        if key in aliases:
            entry = aliases[key]
            # Check executable in PATH
            exe = entry.get("executable")
            resolved = shutil.which(exe)
            if resolved:
                return resolved

            # Check fallback paths
            for path_template in entry.get("fallback_paths", []):
                expanded = os.path.expandvars(path_template)
                if os.path.isfile(expanded):
                    return expanded

        # Fallback: check standard safe system executables (e.g. notepad, calc)
        safe_system_apps = {"notepad": "notepad.exe", "calculator": "calc.exe", "calc": "calc.exe", "explorer": "explorer.exe", "task manager": "taskmgr.exe"}
        if key in safe_system_apps:
            resolved = shutil.which(safe_system_apps[key])
            if resolved:
                return resolved

        return None

    def launch_app(self, app_name: str) -> bool:
        """Launches a whitelisted application."""
        key = app_name.lower().strip()
        entry = config.app_aliases.get(key, {})
        exe_path = self.resolve_executable(app_name)
        if not exe_path:
            raise ActionExecutionError(
                f"Application '{app_name}' is not in the approved application list or not installed."
            )

        arguments = entry.get("arguments", [])
        if not isinstance(arguments, list) or not all(isinstance(arg, str) for arg in arguments):
            raise ActionExecutionError(f"Invalid launch arguments configured for '{app_name}'.")

        try:
            logger.info(f"Launching approved executable: {exe_path}")
            # Launch without shell=True to prevent shell injection
            subprocess.Popen([exe_path, *arguments], close_fds=True)
            return True
        except Exception as e:
            logger.error(f"Failed to launch '{app_name}': {e}")
            raise ActionExecutionError(f"Could not launch {app_name}: {e}") from e

    def close_app_gracefully(self, app_name: str) -> bool:
        """
        Finds top-level windows matching the application name and posts WM_CLOSE.
        Does NOT use taskkill /F to avoid losing unsaved data.
        """
        key = app_name.lower().strip()
        entry = config.app_aliases.get(key, {})
        exe_path = self.resolve_executable(app_name)
        target_name = str(
            entry.get("window_title")
            or (os.path.basename(exe_path) if exe_path else app_name)
        ).lower()
        if target_name.endswith(".exe"):
            target_name = target_name[:-4]

        WM_CLOSE = 0x0010
        user32 = ctypes.windll.user32

        closed_any = False

        def enum_windows_callback(hwnd, extra):
            nonlocal closed_any
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value.lower()
                    if target_name in title or app_name.lower() in title:
                        logger.info(f"Posting WM_CLOSE to window: '{buff.value}'")
                        user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
                        closed_any = True
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)

        if not closed_any:
            # Fallback: graceful taskkill without /F flag
            if not entry.get("arguments"):
                try:
                    proc_name = f"{target_name}.exe"
                    res = subprocess.run(["taskkill", "/IM", proc_name], capture_output=True, text=True, check=False)
                    if res.returncode == 0:
                        return True
                except Exception:
                    pass
            raise ActionExecutionError(f"No running window found for application '{app_name}'.")

        return True


windows_process = WindowsProcessAdapter()
