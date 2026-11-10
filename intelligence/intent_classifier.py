"""
Intent Classifier for AURA.
Coordinates deterministic parsing and optional AI fallback.
"""

from typing import Tuple, Optional, Dict, Any
from intelligence.command_parser import command_parser
from security.action_registry import ACTION_REGISTRY
from utils.constants import SECURITY_REJECT_UNKNOWN_MESSAGE
from utils.logger import logger


class IntentClassifier:
    """Classifies user input into validated intents."""

    def __init__(self, parser=command_parser) -> None:
        self.parser = parser

    def classify(self, text: str) -> Tuple[Optional[str], Dict[str, Any], Optional[str]]:
        """
        Processes command string:
        Returns (intent, parameters, refusal_or_error_message).
        """
        # Deterministic parsing first
        intent, params, refusal = self.parser.parse(text)

        if refusal:
            # Policy refusal or syntax error
            return None, {}, refusal

        if intent:
            if intent in ACTION_REGISTRY:
                return intent, params, None
            else:
                return None, {}, SECURITY_REJECT_UNKNOWN_MESSAGE

        # If deterministic parser didn't match:
        logger.info(f"IntentClassifier: Unrecognized instruction '{text}'")
        return None, {}, SECURITY_REJECT_UNKNOWN_MESSAGE


intent_classifier = IntentClassifier()

