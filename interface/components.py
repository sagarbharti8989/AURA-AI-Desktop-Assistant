"""
Reusable UI component helpers for CustomTkinter.
"""

import customtkinter as ctk
from typing import Optional


class StatusBadge(ctk.CTkFrame):
    """Visual status pill badge with indicator color."""

    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=12, fg_color="#1E293B", **kwargs)

        self.dot = ctk.CTkLabel(
            self, text="●", font=("Arial", 14), text_color="#10B981"
        )
        self.dot.pack(side="left", padx=(10, 4), pady=4)

        self.label = ctk.CTkLabel(
            self,
            text="IDLE",
            font=("Segoe UI", 12, "bold"),
            text_color="#F8FAFC",
        )
        self.label.pack(side="left", padx=(0, 10), pady=4)

    def set_status(self, text: str, color: str = "#10B981") -> None:
        """Updates text and dot color."""
        self.label.configure(text=text.upper())
        self.dot.configure(text_color=color)


class Card(ctk.CTkFrame):
    """Modern dark theme content card."""

    def __init__(self, master, title: Optional[str] = None, **kwargs):
        super().__init__(master, corner_radius=10, fg_color="#1E293B", **kwargs)
        if title:
            header = ctk.CTkLabel(
                self,
                text=title,
                font=("Segoe UI", 14, "bold"),
                text_color="#94A3B8",
            )
            header.pack(anchor="w", padx=16, pady=(12, 6))

