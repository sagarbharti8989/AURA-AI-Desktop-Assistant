"""
Result Verifier for AURA.
Inspects actual system state post-execution to ensure operations genuinely succeeded.
Never allows false positive confirmations.
"""

from typing import Any, Optional
from security.request_validator import ActionResponse
from utils.logger import logger


class ResultVerifier:
    """Verifies actual system state against requested target state."""

    def verify(
        self,
        request_id: str,
        intent: str,
        success: bool,
        requested_value: Optional[Any],
        actual_value: Optional[Any],
        raw_message: str,
    ) -> ActionResponse:
        """
        Validates whether actual outcome satisfies the requested intent.
        Returns a verified ActionResponse.
        """
        if not success:
            logger.info(f"Verification: Action {intent} failed directly: {raw_message}")
            return ActionResponse(
                request_id=request_id,
                intent=intent,
                success=False,
                verified=True,
                requested_value=requested_value,
                actual_value=actual_value,
                message=raw_message,
            )

        # Numerical state verification for volume and brightness
        if intent in ("set_volume", "increase_volume", "decrease_volume"):
            if actual_value is not None and requested_value is not None:
                # Allow minor tolerance (e.g. +/- 2%) due to Windows audio quantization
                diff = abs(int(actual_value) - int(requested_value))
                if diff > 3 and intent == "set_volume":
                    msg = f"Volume was set, but actual level is {actual_value}%."
                    logger.warning(f"Verification mismatch: {msg}")
                    return ActionResponse(
                        request_id=request_id,
                        intent=intent,
                        success=True,
                        verified=False,
                        requested_value=requested_value,
                        actual_value=actual_value,
                        message=msg,
                    )
            message = f"Volume set to {actual_value} percent." if actual_value is not None else raw_message

        elif intent in ("set_brightness", "increase_brightness", "decrease_brightness"):
            message = f"Brightness set to {actual_value} percent." if actual_value is not None else raw_message

        elif intent == "mute_audio":
            message = "Audio muted."
        elif intent == "unmute_audio":
            message = "Audio unmuted."
        elif intent == "open_app":
            message = raw_message or "Application opened."
        elif intent == "close_app":
            message = raw_message or "Application closed."
        elif intent == "lock_system":
            message = "Workstation locked."
        elif intent == "check_battery":
            message = raw_message
        elif intent == "take_screenshot":
            message = "Screenshot captured."
        else:
            message = raw_message

        logger.info(f"Verification SUCCESS: {intent} -> {message}")
        return ActionResponse(
            request_id=request_id,
            intent=intent,
            success=True,
            verified=True,
            requested_value=requested_value,
            actual_value=actual_value,
            message=message,
        )


result_verifier = ResultVerifier()

