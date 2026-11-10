"""
Custom exception hierarchy for AURA.
"""


class AuraException(Exception):
    """Base exception for all AURA domain errors."""
    pass


class MicrophoneError(AuraException):
    """Raised when audio capture device fails or is unavailable."""
    pass


class SpeechRecognitionError(AuraException):
    """Raised when transcription fails."""
    pass


class InvalidCommandError(AuraException):
    """Raised when input command does not match supported schemas or is invalid."""
    pass


class SecurityViolationError(AuraException):
    """Raised when an attempt to bypass security policies or unauthorized action occurs."""
    pass


class PermissionDeniedError(AuraException):
    """Raised when an action is blocked due to disabled user permission."""
    pass


class ActionExecutionError(AuraException):
    """Raised when an OS controller function fails during execution."""
    pass


class VerificationError(AuraException):
    """Raised when post-execution state does not match requested state."""
    pass


class DatabaseError(AuraException):
    """Raised for SQLite persistence failures."""
    pass

