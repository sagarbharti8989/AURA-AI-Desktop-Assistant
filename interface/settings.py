"""
Settings View for AURA.
Allows users to configure assistant preferences.
"""

import customtkinter as ctk
from config import config
from utils.logger import logger


class SettingsView(ctk.CTkFrame):
    """View panel for assistant configuration."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._build_ui()

    def _build_ui(self) -> None:
        title = ctk.CTkLabel(
            self,
            text="Settings & Preferences",
            font=("Segoe UI", 20, "bold"),
            text_color="#F8FAFC",
        )
        title.pack(anchor="w", pady=(10, 20))

        content = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=10)
        content.pack(fill="both", expand=True, padx=5, pady=5)

        # Voice Speech Rate
        row1 = ctk.CTkFrame(content, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=15)

        lbl1 = ctk.CTkLabel(
            row1, text="Speech Speed (WPM):", font=("Segoe UI", 13, "bold"), text_color="#F8FAFC"
        )
        lbl1.pack(side="left")

        self.rate_slider = ctk.CTkSlider(
            row1,
            from_=120,
            to=250,
            number_of_steps=13,
            width=200,
        )
        self.rate_slider.set(config.voice_rate)
        self.rate_slider.pack(side="right")

        # Whisper Model Selection
        row2 = ctk.CTkFrame(content, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=15)

        lbl2 = ctk.CTkLabel(
            row2, text="Speech Recognition Model:", font=("Segoe UI", 13, "bold"), text_color="#F8FAFC"
        )
        lbl2.pack(side="left")

        self.model_combo = ctk.CTkComboBox(
            row2,
            values=["tiny", "base", "small"],
            width=150,
        )
        self.model_combo.set(config.whisper_model)
        self.model_combo.pack(side="right")

        # Local AI Enable/Disable
        row3 = ctk.CTkFrame(content, fg_color="transparent")
        row3.pack(fill="x", padx=20, pady=15)

        lbl3 = ctk.CTkLabel(
            row3, text="Enable Local AI (Ollama):", font=("Segoe UI", 13, "bold"), text_color="#F8FAFC"
        )
        lbl3.pack(side="left")

        self.ai_switch = ctk.CTkSwitch(
            row3, text="", progress_color="#3B82F6"
        )
        if config.ai_enabled:
            self.ai_switch.select()
        else:
            self.ai_switch.deselect()
        self.ai_switch.pack(side="right")

        # Save Button
        save_btn = ctk.CTkButton(
            content,
            text="Save Settings",
            command=self._save_settings,
            fg_color="#3B82F6",
            hover_color="#2563EB",
            width=120,
        )
        save_btn.pack(pady=30)

        # Status Label
        self.status_lbl = ctk.CTkLabel(
            content, text="", font=("Segoe UI", 12), text_color="#10B981"
        )
        self.status_lbl.pack()

    def _save_settings(self) -> None:
        """Saves current settings."""
        rate = int(self.rate_slider.get())
        model = self.model_combo.get()
        ai_enabled = bool(self.ai_switch.get())

        config.settings["voice_rate"] = rate
        config.settings["whisper_model"] = model
        config.settings["ai_enabled"] = ai_enabled

        self.status_lbl.configure(text="Settings saved successfully!")
        self.after(3000, lambda: self.status_lbl.configure(text=""))
        logger.info(f"Updated settings: rate={rate}, model={model}, ai={ai_enabled}")

