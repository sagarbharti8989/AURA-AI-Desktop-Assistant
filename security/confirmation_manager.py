"""
Confirmation Manager for sensitive user operations.
Tracks pending confirmations with expiration windows.
"""

import time
from typing import Optional, Dict, Any
from utils.logger import logger


class ConfirmationManager:
    """Manages short-lived confirmation states."""

    def __init__(self, timeout_seconds: float = 15.0) -> None:
        self.timeout_seconds = timeout_seconds
        self.pending_confirmation: Optional[Dict[str, Any]] = None

    def request_confirmation(self, intent: str, parameters: Dict[str, Any]) -> str:
        """Stores a pending confirmation."""
        self.pending_confirmation = {
            "intent": intent,
            "parameters": parameters,
            "timestamp": time.time(),
        }
        logger.info(f"Confirmation requested for intent: {intent}")
        return f"Are you sure you want to proceed with {intent.replace('_', ' ')}?"

    def is_awaiting_confirmation(self) -> bool:
        """Checks if a valid, unexpired confirmation is pending."""
        if not self.pending_confirmation:
            return False
        if time.time() - self.pending_confirmation["timestamp"] > self.timeout_seconds:
            self.clear()
            return False
        return True

    def validate_confirmation(self, user_response: str) -> Optional[Dict[str, Any]]:
        """
        Validates affirmative response ("yes", "confirm", "proceed").
        Returns the pending action if approved, else None.
        """
        if not self.is_awaiting_confirmation():
            return None

        cleaned = user_response.lower().strip()
        affirmatives = {"yes", "yeah", "yep", "sure", "confirm", "proceed", "do it"}

        if cleaned in affirmatives:
            action = self.pending_confirmation
            self.clear()
            return action

        self.clear()
        return None

    def clear(self) -> None:
        """Clears any pending confirmation."""
        self.pending_confirmation = None


confirmation_manager = ConfirmationManager()

