"""
Deterministic Command Parser for AURA.
Fast, rule-based intent recognition without requiring an LLM.
"""

import re
from typing import Optional, Dict, Any, Tuple
from security.security_policy import SecurityPolicy
from utils.logger import logger


class CommandParser:
    """Parses natural language text into structured ActionRequests."""

    def __init__(self) -> None:
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compiles regex patterns for supported intents."""
        self.patterns = [
            # Volume control
            (
                r"\b(?:set|change|put)\s+(?:the\s+)?volume\s+(?:to\s+)?(\d{1,3})(?:\s*%)?\b",
                "set_volume",
                lambda m: {"level": int(m.group(1))},
            ),
            (
                r"\b(?:turn|bring)\s+the\s+volume\s+(?:up\s+to|down\s+to|to)\s+(\d{1,3})(?:\s*%)?\b",
                "set_volume",
                lambda m: {"level": int(m.group(1))},
            ),
            (
                r"\b(?:increase|raise|turn\s+up|boost)\s+(?:the\s+)?volume(?:\s+by\s+(\d{1,3}))?\b",
                "increase_volume",
                lambda m: {"amount": int(m.group(1)) if m.group(1) else 10},
            ),
            (
                r"\b(?:decrease|lower|turn\s+down|reduce)\s+(?:the\s+)?volume(?:\s+by\s+(\d{1,3}))?\b",
                "decrease_volume",
                lambda m: {"amount": int(m.group(1)) if m.group(1) else 10},
            ),
            (
                r"\b(?:mute|silence)\s+(?:the\s+|my\s+)?(?:audio|sound|laptop|volume|speakers?)?\b",
                "mute_audio",
                lambda _: {},
            ),
            (
                r"\b(?:unmute)\s+(?:the\s+|my\s+)?(?:audio|sound|laptop|volume|speakers?)?\b",
                "unmute_audio",
                lambda _: {},
            ),
            # Brightness control
            (
                r"\b(?:set|change|adjust)\s+(?:the\s+)?(?:screen\s+|display\s+)?brightness\s+(?:to\s+)?(\d{1,3})(?:\s*%)?\b",
                "set_brightness",
                lambda m: {"level": int(m.group(1))},
            ),
            (
                r"\b(?:increase|raise|turn\s+up|boost)\s+(?:the\s+)?(?:screen\s+|display\s+)?brightness(?:\s+by\s+(\d{1,3}))?\b",
                "increase_brightness",
                lambda m: {"amount": int(m.group(1)) if m.group(1) else 10},
            ),
            (
                r"\b(?:make\s+(?:my\s+|the\s+)?screen\s+brighter)\b",
                "increase_brightness",
                lambda _: {"amount": 10},
            ),
            (
                r"\b(?:decrease|lower|turn\s+down|dim|reduce)\s+(?:the\s+)?(?:screen\s+|display\s+)?brightness(?:\s+by\s+(\d{1,3}))?\b",
                "decrease_brightness",
                lambda m: {"amount": int(m.group(1)) if m.group(1) else 10},
            ),
            (
                r"\b(?:dim\s+(?:my\s+|the\s+)?screen)\b",
                "decrease_brightness",
                lambda _: {"amount": 10},
            ),
            # Application Management
            (
                r"\b(?:open|launch|start|run)\s+([a-zA-Z0-9\s_\-\.]+)\b",
                "open_app",
                lambda m: {"app_name": m.group(1).strip()},
            ),
            (
                r"\b(?:close|quit|exit|terminate)\s+([a-zA-Z0-9\s_\-\.]+)\b",
                "close_app",
                lambda m: {"app_name": m.group(1).strip()},
            ),
            # Wi-Fi Management
            (
                r"\b(?:turn\s+on|enable|activate)\s+wi-?fi\b",
                "enable_wifi",
                lambda _: {},
            ),
            (
                r"\b(?:turn\s+off|disable|deactivate)\s+wi-?fi\b",
                "disable_wifi",
                lambda _: {},
            ),
            (
                r"\b(?:check|get|what\s+is\s+the|is)\s+wi-?fi(?:\s+status|\s+connected|\s+enabled)?\b",
                "get_wifi_status",
                lambda _: {},
            ),
            # Bluetooth Management
            (
                r"\b(?:turn\s+on|enable|activate)\s+bluetooth\b",
                "enable_bluetooth",
                lambda _: {},
            ),
            (
                r"\b(?:turn\s+off|disable|deactivate)\s+bluetooth\b",
                "disable_bluetooth",
                lambda _: {},
            ),
            (
                r"\b(?:check|get|what\s+is\s+the|is)\s+bluetooth(?:\s+status|\s+enabled)?\b",
                "get_bluetooth_status",
                lambda _: {},
            ),
            # System operations
            (
                r"\b(?:lock\s+(?:my\s+|the\s+)?(?:workstation|screen|laptop|computer|pc)|lock)\b",
                "lock_system",
                lambda _: {},
            ),
            (
                r"\b(?:check|get|how\s+much\s+is\s+(?:the\s+)?|what\s+is\s+(?:the\s+)?)\s*(?:battery|power|battery\s+status|battery\s+level)\b",
                "check_battery",
                lambda _: {},
            ),
            (
                r"\b(?:take\s+(?:a\s+)?screenshot|capture\s+(?:the\s+)?screen|screenshot)\b",
                "take_screenshot",
                lambda _: {},
            ),
        ]

    def parse(self, text: str) -> Tuple[Optional[str], Dict[str, Any], Optional[str]]:
        """
        Parses text input into (intent, parameters, security_violation_message).
        If a security policy is violated (power, files), returns (None, {}, refusal_message).
        """
        if not text or not text.strip():
            return None, {}, "Empty command received."

        # 1. Run security policy check
        is_allowed, policy_msg = SecurityPolicy.evaluate_text_input(text)
        if not is_allowed:
            return None, {}, policy_msg

        cleaned = text.strip()

        # 2. Match deterministic patterns
        for pattern, intent, extractor in self.patterns:
            match = re.search(pattern, cleaned, re.IGNORECASE)
            if match:
                try:
                    params = extractor(match)
                    logger.debug(f"CommandParser: Parsed '{cleaned}' -> {intent} {params}")
                    return intent, params, None
                except Exception as e:
                    logger.warning(f"Error extracting parameters for {intent}: {e}")
                    return None, {}, f"Invalid parameters for {intent}."

        logger.debug(f"CommandParser: No deterministic pattern matched '{cleaned}'.")
        return None, {}, None


command_parser = CommandParser()

