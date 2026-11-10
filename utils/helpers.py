"""
General helper functions for AURA.
"""

import uuid
from datetime import datetime, timezone


def generate_request_id() -> str:
    """Generates a unique request identifier."""
    return f"req_{uuid.uuid4().hex[:12]}"


def current_iso_timestamp() -> str:
    """Returns current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def clamp(value: int, min_val: int = 0, max_val: int = 100) -> int:
    """Clamps an integer value within specified range."""
    return max(min_val, min(max_val, value))
