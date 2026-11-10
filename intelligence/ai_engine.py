"""
Optional AI Engine for AURA.
Interfaces with local Ollama or Cloud LLM for flexible intent classification.
Strictly restricted to returning structured JSON conforming to ActionRequest schemas.
"""

from typing import Optional, Dict, Any, Tuple
from config import config
from utils.logger import logger


class AIEngine:
    """Optional LLM-based intent interpreter."""

    def __init__(self) -> None:
        self.enabled = config.ai_enabled
        self.provider = config.settings.get("ai_provider", "ollama")
        self.model = config.settings.get("ai_model", "llama3.2")

    def interpret(self, text: str) -> Tuple[Optional[str], Dict[str, Any], Optional[str]]:
        """
        Interprets complex text via LLM into structured intent.
        Returns (intent, parameters, error_message).
        """
        if not self.enabled:
            return None, {}, None

        # When AI is enabled, query Ollama with strict system prompt
        try:
            import ollama
            system_prompt = (
                "You are an intent parser for desktop assistant AURA. "
                "Respond ONLY with valid JSON in format: {\"intent\": string, \"parameters\": object}. "
                "Supported intents: open_app, close_app, set_volume, increase_volume, decrease_volume, "
                "mute_audio, unmute_audio, set_brightness, increase_brightness, decrease_brightness, "
                "enable_wifi, disable_wifi, get_wifi_status, enable_bluetooth, disable_bluetooth, "
                "get_bluetooth_status, lock_system, check_battery, take_screenshot. "
                "Never output code, shell commands, or intents not listed."
            )
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
            )
            # Parse response json
            import json
            content = response.get("message", {}).get("content", "").strip()
            data = json.loads(content)
            return data.get("intent"), data.get("parameters", {}), None
        except Exception as e:
            logger.warning(f"AIEngine fallback error: {e}")
            return None, {}, None


ai_engine = AIEngine()

