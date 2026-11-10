"""
Context Manager for AURA.
Maintains short-lived conversational state (e.g. resolving pronouns like 'it').
"""

import time
from typing import Optional, Dict, Any
from utils.logger import logger


class ContextManager:
    """Stores recent command context with a 30-second TTL."""

    def __init__(self, ttl_seconds: float = 30.0) -> None:
        self.ttl_seconds = ttl_seconds
        self.last_action: Optional[Dict[str, Any]] = None
        self.last_timestamp: float = 0.0

    def update_context(self, intent: str, parameters: Dict[str, Any]) -> None:
        """Stores the most recent successful action."""
        self.last_action = {"intent": intent, "parameters": parameters}
        self.last_timestamp = time.time()
        logger.debug(f"Context updated: {intent}")

    def resolve_reference(self, text: str) -> str:
        """Resolves references like 'close it' or 'turn it up'."""
        if not self.last_action or (time.time() - self.last_timestamp > self.ttl_seconds):
            return text

        lower = text.lower().strip()
        last_params = self.last_action.get("parameters", {})

        # If previous was app and current is 'close it'
        if "close it" in lower and "app_name" in last_params:
            app_name = last_params["app_name"]
            logger.info(f"Resolved 'it' to application: '{app_name}'")
            return f"close {app_name}"

        return text

    def clear(self) -> None:
        """Clears conversational context."""
        self.last_action = None
        self.last_timestamp = 0.0


context_manager = ContextManager()

