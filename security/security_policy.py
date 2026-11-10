"""
Strict security policy interceptors for AURA.
Enforces prohibitions on power termination and personal file access.
"""

import re
from typing import Optional, Tuple
from utils.constants import (
    SECURITY_REJECT_POWER_MESSAGE,
    SECURITY_REJECT_FILE_MESSAGE,
)
from utils.logger import logger

# Blocked power-related keywords
POWER_PATTERNS = [
    r"\b(shut\s*down|shutdown)\b",
    r"\b(restart|reboot)\b",
    r"\b(power\s*off)\b",
    r"\b(hibernate|sleep\s+pc|sleep\s+laptop)\b",
    r"\b(log\s*off|sign\s*out)\b",
]

# Blocked personal file access patterns
FILE_ACCESS_PATTERNS = [
    r"\b(read|open|show|display|find|search|delete|edit|view)\s+(my\s+)?(files?|documents?|folders?|desktop|downloads?|pictures?|photos?|videos?)\b",
    r"\b(read|open|show|display|search|edit)\s+.*?\.(txt|pdf|docx?|xlsx?|pptx?|csv|json|env|key|log|password|db)\b",
    r"\b(personal\s+files?|personal\s+data|credentials?|passwords?|browser\s+history)\b",
    r"\b(browse\s+(folder|directory|files?))\b",
]


class SecurityPolicy:
    """Evaluates text and intents against fundamental security rules."""

    @classmethod
    def evaluate_text_input(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        Inspects raw user text input.
        Returns (is_allowed, rejection_reason).
        """
        lower = text.lower().strip()

        # 1. Check power commands
        for pattern in POWER_PATTERNS:
            if re.search(pattern, lower):
                logger.warning(f"Security Policy: Intercepted blocked power command: '{text}'")
                return False, SECURITY_REJECT_POWER_MESSAGE

        # 2. Check personal file access
        for pattern in FILE_ACCESS_PATTERNS:
            if re.search(pattern, lower):
                logger.warning(f"Security Policy: Intercepted blocked personal file request: '{text}'")
                return False, SECURITY_REJECT_FILE_MESSAGE

        return True, None

    @classmethod
    def evaluate_intent(cls, intent: str) -> Tuple[bool, Optional[str]]:
        """
        Inspects intent identifier.
        Guarantees shutdown/restart/file intents can never pass.
        """
        lower = intent.lower().strip()
        if any(term in lower for term in ("shutdown", "restart", "reboot", "power_off")):
            return False, SECURITY_REJECT_POWER_MESSAGE

        if any(term in lower for term in ("file", "document", "folder", "read_dir")):
            return False, SECURITY_REJECT_FILE_MESSAGE

        return True, None

