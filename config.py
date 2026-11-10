"""
AURA Configuration Loader
Loads settings, application aliases, and authorized actions from JSON files and environment variables.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)


def _load_json(file_path: Path, default_data: dict) -> dict:
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_data
    return default_data


class Config:
    """Application configuration container."""

    def __init__(self) -> None:
        self.settings: Dict[str, Any] = _load_json(
            CONFIG_DIR / "settings.json",
            {
                "assistant_name": "AURA",
                "theme": "dark",
                "voice_rate": 175,
                "voice_volume": 1.0,
                "whisper_model": "base",
                "whisper_device": "cpu",
                "whisper_compute_type": "int8",
                "ai_enabled": False,
                "ai_provider": "ollama",
                "ai_model": "llama3.2",
                "ollama_host": "http://localhost:11434",
                "db_path": "aura.db",
                "log_level": "INFO",
            },
        )
        self.app_aliases: Dict[str, Any] = _load_json(CONFIG_DIR / "app_aliases.json", {})
        self.authorized_actions: Dict[str, Any] = _load_json(
            CONFIG_DIR / "authorized_actions.json", {}
        )

    @property
    def assistant_name(self) -> str:
        return self.settings.get("assistant_name", "AURA")

    @property
    def db_path(self) -> str:
        return str(BASE_DIR / self.settings.get("db_path", "aura.db"))

    @property
    def log_level(self) -> str:
        return self.settings.get("log_level", "INFO")

    @property
    def voice_rate(self) -> int:
        return int(self.settings.get("voice_rate", 175))

    @property
    def voice_volume(self) -> float:
        return float(self.settings.get("voice_volume", 1.0))

    @property
    def whisper_model(self) -> str:
        return self.settings.get("whisper_model", "base")

    @property
    def whisper_device(self) -> str:
        return self.settings.get("whisper_device", "cpu")

    @property
    def whisper_compute_type(self) -> str:
        return self.settings.get("whisper_compute_type", "int8")

    @property
    def ai_enabled(self) -> bool:
        return bool(self.settings.get("ai_enabled", False))


config = Config()

