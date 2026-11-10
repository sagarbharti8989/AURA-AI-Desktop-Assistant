"""
State Manager for AURA.
Maintains operational state and enforces valid state transitions.
"""

import threading
from typing import Callable, List
from utils.constants import AssistantState
from utils.logger import logger


class StateManager:
    """Thread-safe state machine."""

    def __init__(self) -> None:
        self._state = AssistantState.IDLE
        self._lock = threading.Lock()
        self._listeners: List[Callable[[AssistantState], None]] = []

    @property
    def current_state(self) -> AssistantState:
        with self._lock:
            return self._state

    def set_state(self, new_state: AssistantState) -> None:
        """Transitions to new state and notifies subscribers."""
        with self._lock:
            if self._state == new_state:
                return
            prev_state = self._state
            self._state = new_state
            logger.debug(f"State transition: {prev_state.value} -> {new_state.value}")
            listeners_copy = list(self._listeners)

        for listener in listeners_copy:
            try:
                listener(new_state)
            except Exception as e:
                logger.error(f"Error in state listener: {e}")

    def subscribe(self, callback: Callable[[AssistantState], None]) -> None:
        """Registers a listener for state changes."""
        with self._lock:
            if callback not in self._listeners:
                self._listeners.append(callback)

    def is_listening(self) -> bool:
        return self.current_state == AssistantState.LISTENING

    def can_listen(self) -> bool:
        """User can initiate listening unless microphone capture is already active."""
        return self.current_state != AssistantState.LISTENING


state_manager = StateManager()

