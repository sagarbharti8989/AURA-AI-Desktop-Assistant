"""
Event Manager for AURA.
Thread-safe queue for UI updates and decouple worker communication.
"""

import queue
from typing import Any, Tuple, Optional


class EventManager:
    """Thread-safe event queue."""

    def __init__(self) -> None:
        self._queue: queue.Queue = queue.Queue()

    def emit(self, event_type: str, data: Any = None) -> None:
        """Pushes an event into the queue."""
        self._queue.put((event_type, data))

    def poll(self) -> Optional[Tuple[str, Any]]:
        """Pops an event without blocking."""
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None


event_manager = EventManager()

