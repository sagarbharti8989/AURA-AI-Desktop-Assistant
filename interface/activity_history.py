"""
Activity History View for AURA.
Displays past voice commands, execution outcomes, and provides a clear history control.
"""

import customtkinter as ctk
from database.repositories import ExecutionLogRepository


class ActivityHistoryView(ctk.CTkFrame):
    """View panel for execution history logs."""

    def __init__(self, master, log_repo: ExecutionLogRepository = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.repo = log_repo or ExecutionLogRepository()
        self._build_ui()

    def _build_ui(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(10, 15))

        title = ctk.CTkLabel(
            header,
            text="Activity History",
            font=("Segoe UI", 20, "bold"),
            text_color="#F8FAFC",
        )
        title.pack(side="left")

        btn_box = ctk.CTkFrame(header, fg_color="transparent")
        btn_box.pack(side="right")

        refresh_btn = ctk.CTkButton(
            btn_box,
            text="Refresh",
            width=80,
            command=self.refresh,
            fg_color="#334155",
            hover_color="#475569",
        )
        refresh_btn.pack(side="left", padx=5)

        clear_btn = ctk.CTkButton(
            btn_box,
            text="Clear History",
            width=100,
            command=self._clear_history,
            fg_color="#EF4444",
            hover_color="#DC2626",
        )
        clear_btn.pack(side="left", padx=5)

        self.list_frame = ctk.CTkScrollableFrame(
            self, fg_color="#1E293B", corner_radius=10
        )
        self.list_frame.pack(fill="both", expand=True)

        self.refresh()

    def refresh(self) -> None:
        """Reloads records from database."""
        for child in self.list_frame.winfo_children():
            child.destroy()

        records = self.repo.get_recent(50)

        if not records:
            empty_lbl = ctk.CTkLabel(
                self.list_frame,
                text="No execution activity recorded yet.",
                font=("Segoe UI", 13),
                text_color="#64748B",
            )
            empty_lbl.pack(pady=40)
            return

        for r in records:
            item = ctk.CTkFrame(self.list_frame, fg_color="#0F172A", corner_radius=8)
            item.pack(fill="x", padx=10, pady=5)

            # Left side: Intent & message
            left = ctk.CTkFrame(item, fg_color="transparent")
            left.pack(side="left", fill="both", expand=True, padx=12, pady=10)

            title_row = ctk.CTkFrame(left, fg_color="transparent")
            title_row.pack(fill="x")

            intent_lbl = ctk.CTkLabel(
                title_row,
                text=r.intent.replace("_", " ").upper(),
                font=("Segoe UI", 12, "bold"),
                text_color="#38BDF8",
            )
            intent_lbl.pack(side="left")

            time_lbl = ctk.CTkLabel(
                title_row,
                text=r.timestamp.replace("T", " ").replace("Z", ""),
                font=("Segoe UI", 10),
                text_color="#64748B",
            )
            time_lbl.pack(side="left", padx=(10, 0))

            msg_lbl = ctk.CTkLabel(
                left,
                text=r.message or "",
                font=("Segoe UI", 12),
                text_color="#E2E8F0",
                wraplength=450,
                justify="left",
            )
            msg_lbl.pack(anchor="w", pady=(3, 0))

            # Right side: Status badge
            color = "#10B981" if r.outcome == "SUCCESS" else "#EF4444"
            status_lbl = ctk.CTkLabel(
                item,
                text=r.outcome,
                font=("Segoe UI", 11, "bold"),
                text_color=color,
            )
            status_lbl.pack(side="right", padx=16)

    def _clear_history(self) -> None:
        """Clears execution history."""
        self.repo.clear()
        self.refresh()

