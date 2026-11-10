"""
Main Desktop Dashboard for AURA using CustomTkinter.
Provides a modern dark theme interface with push-to-talk button, status indicators,
real-time transcription and response display, and tab navigation.
"""

import time
import customtkinter as ctk
from typing import Optional
from config import config
from utils.constants import AssistantState
from core.assistant import assistant
from core.event_manager import event_manager
from interface.components import StatusBadge, Card
from interface.permissions_ui import PermissionsView
from interface.activity_history import ActivityHistoryView
from interface.settings import SettingsView
from voice.hotkey_manager import hotkey_manager
from utils.logger import logger


class AuraDashboard(ctk.CTk):
    """Main application window for AURA."""

    def __init__(self) -> None:
        super().__init__()

        # State tracking for dual-mode PTT / Click-to-Listen
        self._is_listening = False
        self._press_time = 0.0

        # Window configuration
        self.title("AURA – AI Desktop Assistant")
        self.geometry("900x600")
        self.minsize(800, 550)

        # Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color="#0F172A")

        self._build_layout()
        self._start_event_loop()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        hotkey_manager.register(on_press=self._on_ptt_press, on_release=self._on_ptt_release)

    def _build_layout(self) -> None:
        """Constructs sidebar and content panels."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1E293B")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        # Brand Logo / Title
        brand_label = ctk.CTkLabel(
            self.sidebar,
            text="AURA",
            font=("Segoe UI", 26, "bold"),
            text_color="#38BDF8",
        )
        brand_label.grid(row=0, column=0, padx=20, pady=(25, 5), sticky="w")

        tagline = ctk.CTkLabel(
            self.sidebar,
            text="Desktop Voice Assistant",
            font=("Segoe UI", 11),
            text_color="#94A3B8",
        )
        tagline.grid(row=1, column=0, padx=20, pady=(0, 25), sticky="w")

        # Navigation Buttons
        self.btn_dashboard = ctk.CTkButton(
            self.sidebar,
            text="Dashboard",
            font=("Segoe UI", 13, "bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            anchor="w",
            command=lambda: self._switch_view("dashboard"),
        )
        self.btn_dashboard.grid(row=2, column=0, padx=15, pady=6, sticky="ew")

        self.btn_permissions = ctk.CTkButton(
            self.sidebar,
            text="Permissions",
            font=("Segoe UI", 13),
            fg_color="transparent",
            hover_color="#334155",
            anchor="w",
            command=lambda: self._switch_view("permissions"),
        )
        self.btn_permissions.grid(row=3, column=0, padx=15, pady=6, sticky="ew")

        self.btn_history = ctk.CTkButton(
            self.sidebar,
            text="History",
            font=("Segoe UI", 13),
            fg_color="transparent",
            hover_color="#334155",
            anchor="w",
            command=lambda: self._switch_view("history"),
        )
        self.btn_history.grid(row=4, column=0, padx=15, pady=6, sticky="ew")

        self.btn_settings = ctk.CTkButton(
            self.sidebar,
            text="Settings",
            font=("Segoe UI", 13),
            fg_color="transparent",
            hover_color="#334155",
            anchor="w",
            command=lambda: self._switch_view("settings"),
        )
        self.btn_settings.grid(row=6, column=0, padx=15, pady=6, sticky="ew")

        version_lbl = ctk.CTkLabel(
            self.sidebar,
            text="v2.0 (Windows 11)",
            font=("Segoe UI", 10),
            text_color="#64748B",
        )
        version_lbl.grid(row=7, column=0, padx=20, pady=15, sticky="w")

        # --- Content Container ---
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=25, pady=20)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # Views
        self.view_dashboard = self._build_dashboard_view()
        self.view_permissions = PermissionsView(self.container)
        self.view_history = ActivityHistoryView(self.container)
        self.view_settings = SettingsView(self.container)

        self._switch_view("dashboard")

    def _build_dashboard_view(self) -> ctk.CTkFrame:
        """Constructs the primary dashboard panel."""
        panel = ctk.CTkFrame(self.container, fg_color="transparent")

        # Top Bar: Header and Status Badge
        top_bar = ctk.CTkFrame(panel, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 20))

        welcome_lbl = ctk.CTkLabel(
            top_bar,
            text="Voice Control Center",
            font=("Segoe UI", 20, "bold"),
            text_color="#F8FAFC",
        )
        welcome_lbl.pack(side="left")

        self.status_badge = StatusBadge(top_bar)
        self.status_badge.pack(side="right")

        # Central Push-to-Talk Button Area
        mic_card = Card(panel)
        mic_card.pack(fill="x", pady=10)

        mic_content = ctk.CTkFrame(mic_card, fg_color="transparent")
        mic_content.pack(pady=25)

        self.ptt_button = ctk.CTkButton(
            mic_content,
            text="START LISTENING",
            font=("Segoe UI", 15, "bold"),
            width=240,
            height=60,
            corner_radius=30,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
        )
        self.ptt_button.pack(pady=10)

        # Bind mouse events (supports both single click and press-and-hold)
        self.ptt_button.bind("<ButtonPress-1>", self._on_ptt_press)
        self.ptt_button.bind("<ButtonRelease-1>", self._on_ptt_release)

        self.ptt_hint = ctk.CTkLabel(
            mic_content,
            text="Click to start/stop listening (or hold and release). Shortcut: Ctrl+Shift+A",
            font=("Segoe UI", 11),
            text_color="#64748B",
        )
        self.ptt_hint.pack()

        # Command & Response Displays
        info_card = Card(panel, title="Active Interaction")
        info_card.pack(fill="both", expand=True, pady=10)

        # Recognized text
        rec_title = ctk.CTkLabel(
            info_card,
            text="Recognized Command:",
            font=("Segoe UI", 12, "bold"),
            text_color="#94A3B8",
        )
        rec_title.pack(anchor="w", padx=16, pady=(10, 2))

        self.rec_text = ctk.CTkLabel(
            info_card,
            text="Waiting for voice input...",
            font=("Segoe UI", 14),
            text_color="#F8FAFC",
            wraplength=600,
            justify="left",
        )
        self.rec_text.pack(anchor="w", padx=16, pady=(0, 15))

        # Assistant response
        res_title = ctk.CTkLabel(
            info_card,
            text="Assistant Response:",
            font=("Segoe UI", 12, "bold"),
            text_color="#94A3B8",
        )
        res_title.pack(anchor="w", padx=16, pady=(5, 2))

        self.res_text = ctk.CTkLabel(
            info_card,
            text="Ready.",
            font=("Segoe UI", 14, "bold"),
            text_color="#38BDF8",
            wraplength=600,
            justify="left",
        )
        self.res_text.pack(anchor="w", padx=16, pady=(0, 15))

        # Bottom Quick Text Input (for testing or silent mode)
        bottom_bar = ctk.CTkFrame(panel, fg_color="transparent")
        bottom_bar.pack(fill="x", pady=(10, 0))

        self.text_input = ctk.CTkEntry(
            bottom_bar,
            placeholder_text="Type a command (e.g. 'set volume to 40', 'open chrome')...",
            font=("Segoe UI", 13),
            height=40,
        )
        self.text_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.text_input.bind("<Return>", self._on_text_submit)

        send_btn = ctk.CTkButton(
            bottom_bar,
            text="Execute",
            width=90,
            height=40,
            fg_color="#334155",
            hover_color="#475569",
            command=self._on_text_submit,
        )
        send_btn.pack(side="right")

        return panel

    def _switch_view(self, view_name: str) -> None:
        """Switches displayed panel."""
        for v in (self.view_dashboard, self.view_permissions, self.view_history, self.view_settings):
            v.pack_forget()

        # Reset button styles
        nav_map = {
            "dashboard": (self.view_dashboard, self.btn_dashboard),
            "permissions": (self.view_permissions, self.btn_permissions),
            "history": (self.view_history, self.btn_history),
            "settings": (self.view_settings, self.btn_settings),
        }

        for name, (_, btn) in nav_map.items():
            if name == view_name:
                btn.configure(fg_color="#2563EB", font=("Segoe UI", 13, "bold"))
            else:
                btn.configure(fg_color="transparent", font=("Segoe UI", 13))

        target_view, _ = nav_map[view_name]
        target_view.pack(fill="both", expand=True)

        # Refresh dynamic views
        if view_name == "permissions":
            self.view_permissions.refresh()
        elif view_name == "history":
            self.view_history.refresh()

    def _start_voice(self) -> None:
        """Starts audio recording."""
        self._is_listening = True
        self.ptt_button.configure(text="LISTENING (CLICK TO FINISH)", fg_color="#EF4444")
        self.status_badge.set_status("LISTENING", "#EF4444")
        self.rec_text.configure(text="Listening for voice...")
        assistant.start_listening()

    def _stop_voice(self) -> None:
        """Stops audio recording and processes."""
        self._is_listening = False
        self.ptt_button.configure(text="PROCESSING...", fg_color="#F59E0B")
        self.status_badge.set_status("PROCESSING", "#F59E0B")
        assistant.stop_listening()

    def _on_ptt_press(self, event=None) -> None:
        """Handles mouse press on microphone button (toggle or press)."""
        self._press_time = time.time()
        if self._is_listening:
            self._stop_voice()
        else:
            self._start_voice()

    def _on_ptt_release(self, event=None) -> None:
        """Handles mouse release (supports press-and-hold)."""
        duration = time.time() - self._press_time
        if duration > 0.4 and self._is_listening:
            self._stop_voice()

    def _on_text_submit(self, event=None) -> None:
        """Dispatches typed command."""
        text = self.text_input.get().strip()
        if not text:
            return
        self.text_input.delete(0, "end")
        self.rec_text.configure(text=f'"{text}"')
        self.status_badge.set_status("EXECUTING", "#38BDF8")

        # Process command
        import threading
        threading.Thread(target=lambda: assistant.process_text_command(text), daemon=True).start()

    def _start_event_loop(self) -> None:
        """Periodically polls background event queue."""
        while True:
            evt = event_manager.poll()
            if not evt:
                break
            event_type, data = evt
            self._handle_event(event_type, data)

        self.after(50, self._start_event_loop)

    def _handle_event(self, event_type: str, data) -> None:
        """Processes events dispatched from background threads."""
        if event_type == "LISTENING_STARTED":
            self._is_listening = True
            self.status_badge.set_status("LISTENING", "#EF4444")
            self.ptt_button.configure(text="LISTENING (CLICK TO FINISH)", fg_color="#EF4444")
        elif event_type == "LISTENING_STOPPED":
            self.status_badge.set_status("PROCESSING", "#F59E0B")
            self.ptt_button.configure(text="PROCESSING...", fg_color="#F59E0B")
        elif event_type == "TRANSCRIPTION_COMPLETED":
            self.rec_text.configure(text=f'"{data}"')
        elif event_type == "TRANSCRIPTION_FAILED":
            self._is_listening = False
            self.status_badge.set_status("IDLE", "#10B981")
            self.ptt_button.configure(text="START LISTENING", fg_color="#2563EB")
            self.rec_text.configure(text="[No speech detected]")
            self.res_text.configure(text=str(data))
        elif event_type == "ACTION_COMPLETED":
            self._is_listening = False
            self.status_badge.set_status("IDLE", "#10B981")
            self.ptt_button.configure(text="START LISTENING", fg_color="#2563EB")
            self.res_text.configure(text=data.get("message", "Done."))
        elif event_type in ("COMMAND_REFUSED", "ACTION_UNAUTHORIZED"):
            self._is_listening = False
            self.status_badge.set_status("BLOCKED", "#EF4444")
            self.ptt_button.configure(text="START LISTENING", fg_color="#2563EB")
            self.res_text.configure(text=data.get("message", "Action blocked."))
        elif event_type == "COMMAND_UNKNOWN":
            self._is_listening = False
            self.status_badge.set_status("IDLE", "#10B981")
            self.ptt_button.configure(text="START LISTENING", fg_color="#2563EB")
            self.res_text.configure(text=data.get("message", "Unknown command."))
        elif event_type == "ERROR":
            self._is_listening = False
            self.status_badge.set_status("ERROR", "#EF4444")
            self.ptt_button.configure(text="START LISTENING", fg_color="#2563EB")
            self.res_text.configure(text=f"Error: {data}")

    def _on_close(self) -> None:
        """Cleans up background workers and closes dashboard."""
        hotkey_manager.unregister()
        self.destroy()

