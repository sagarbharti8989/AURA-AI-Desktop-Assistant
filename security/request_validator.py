"""
Pydantic schemas for validating action requests, parameters, and responses.
"""

from __future__ import annotations
from typing import Any, Optional, Dict
from pydantic import BaseModel, Field, field_validator
from utils.exceptions import InvalidCommandError


class SetVolumeParams(BaseModel):
    level: int = Field(..., ge=0, le=100, description="Volume level from 0 to 100")


class AdjustVolumeParams(BaseModel):
    amount: int = Field(default=10, ge=1, le=100, description="Relative volume change delta")


class SetBrightnessParams(BaseModel):
    level: int = Field(..., ge=0, le=100, description="Brightness level from 0 to 100")


class AdjustBrightnessParams(BaseModel):
    amount: int = Field(default=10, ge=1, le=100, description="Relative brightness change delta")


class AppParams(BaseModel):
    app_name: str = Field(..., min_length=1, max_length=100, description="Name or alias of application")

    @field_validator("app_name")
    @classmethod
    def sanitize_app_name(cls, v: str) -> str:
        # Strip path traversal characters
        cleaned = v.strip().replace("..", "").replace("/", "").replace("\\", "")
        if not cleaned:
            raise ValueError("Application name cannot be empty or contain invalid path characters.")
        return cleaned.lower()


class ActionRequest(BaseModel):
    """Structured action request object passed through the security layer."""
    request_id: str
    intent: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    source: str = "voice"


class ActionResponse(BaseModel):
    """Structured response returned by controllers and verifier."""
    request_id: str
    intent: str
    success: bool
    verified: bool
    requested_value: Optional[Any] = None
    actual_value: Optional[Any] = None
    message: str


def validate_intent_parameters(intent: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Validates parameters for known intents against specific Pydantic models."""
    try:
        if intent == "set_volume":
            return SetVolumeParams(**parameters).model_dump()
        elif intent in ("increase_volume", "decrease_volume"):
            return AdjustVolumeParams(**parameters).model_dump()
        elif intent == "set_brightness":
            return SetBrightnessParams(**parameters).model_dump()
        elif intent in ("increase_brightness", "decrease_brightness"):
            return AdjustBrightnessParams(**parameters).model_dump()
        elif intent in ("open_app", "close_app"):
            return AppParams(**parameters).model_dump()
        return parameters
    except Exception as e:
        raise InvalidCommandError(f"Parameter validation failed for intent '{intent}': {e}") from e

