"""
Global Keyboard Shortcut Manager for AURA.
Enables Push-to-Talk or toggle activation via keyboard shortcuts.
"""

from typing import Optional, Callable
from utils.logger import logger


class HotkeyManager:
    """Manages global keyboard hotkeys for assistant activation."""

    def __init__(self, default_hotkey: str = "ctrl+shift+a") -> None:
        self.hotkey = default_hotkey
        self.is_registered = False

    def register(self, on_press: Callable[[], None], on_release: Optional[Callable[[], None]] = None) -> bool:
        """Registers global hotkey with fallback handling."""
        try:
            import keyboard
            keyboard.add_hotkey(self.hotkey, on_press)
            self.is_registered = True
            logger.info(f"Global hotkey registered: {self.hotkey}")
            return True
        except Exception as e:
            logger.warning(f"Could not register global hotkey '{self.hotkey}': {e}")
            return False

    def unregister(self) -> None:
        """Unregisters hotkey."""
        if self.is_registered:
            try:
                import keyboard
                keyboard.remove_hotkey(self.hotkey)
                self.is_registered = False
            except Exception:
                pass


hotkey_manager = HotkeyManager()

