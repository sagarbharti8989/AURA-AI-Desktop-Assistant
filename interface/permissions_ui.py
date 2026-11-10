"""
Permissions Management View for AURA.
Allows users to toggle capabilities dynamically in SQLite.
"""

import customtkinter as ctk
from database.repositories import PermissionRepository
from utils.logger import logger


class PermissionsView(ctk.CTkFrame):
    """View panel for managing individual capability permissions."""

    def __init__(self, master, permission_repo: PermissionRepository = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.repo = permission_repo or PermissionRepository()
        self._build_ui()

    def _build_ui(self) -> None:
        title = ctk.CTkLabel(
            self,
            text="Capability Permissions",
            font=("Segoe UI", 20, "bold"),
            text_color="#F8FAFC",
        )
        title.pack(anchor="w", pady=(10, 5))

        desc = ctk.CTkLabel(
            self,
            text="Enable or disable specific laptop operations. Disabling an operation blocks all subsequent voice commands immediately.",
            font=("Segoe UI", 12),
            text_color="#94A3B8",
            wraplength=600,
            justify="left",
        )
        desc.pack(anchor="w", pady=(0, 20))

        self.switches_frame = ctk.CTkScrollableFrame(
            self, fg_color="#1E293B", corner_radius=10
        )
        self.switches_frame.pack(fill="both", expand=True)

        self.refresh()

    def refresh(self) -> None:
        """Reloads permission toggles from database."""
        for child in self.switches_frame.winfo_children():
            child.destroy()

        permissions_meta = [
            ("app_launch", "Application Launching", "Allow AURA to launch whitelisted desktop applications."),
            ("app_close", "Application Closing", "Allow AURA to gracefully close supported applications."),
            ("volume_control", "Audio Volume Control", "Allow AURA to adjust volume, mute, and unmute system audio."),
            ("brightness_control", "Screen Brightness Control", "Allow AURA to adjust primary display brightness."),
            ("wifi_control", "Wi-Fi Management", "Allow AURA to check status and toggle Wi-Fi adapter."),
            ("bluetooth_control", "Bluetooth Management", "Allow AURA to check status and toggle Bluetooth radio."),
            ("system_control", "Safe System Utilities", "Allow workstation locking, battery checks, and screenshots."),
        ]

        all_perms = self.repo.get_all()

        for key, name, hint in permissions_meta:
            row = ctk.CTkFrame(self.switches_frame, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=12)

            text_col = ctk.CTkFrame(row, fg_color="transparent")
            text_col.pack(side="left", fill="both", expand=True)

            label = ctk.CTkLabel(
                text_col, text=name, font=("Segoe UI", 14, "bold"), text_color="#F8FAFC"
            )
            label.pack(anchor="w")

            hint_label = ctk.CTkLabel(
                text_col, text=hint, font=("Segoe UI", 11), text_color="#64748B"
            )
            hint_label.pack(anchor="w")

            is_enabled = all_perms.get(key, True)
            switch = ctk.CTkSwitch(
                row,
                text="",
                command=lambda k=key: self._on_toggle(k),
                progress_color="#3B82F6",
            )
            if is_enabled:
                switch.select()
            else:
                switch.deselect()

            switch.pack(side="right", padx=10)

    def _on_toggle(self, permission_key: str) -> None:
        """Handles switch toggle event."""
        current = self.repo.is_enabled(permission_key)
        new_state = not current
        self.repo.set_enabled(permission_key, new_state)
        logger.info(f"User toggled permission '{permission_key}' -> {new_state}")

