"""
Pydantic data models for database records and requests/responses.
"""

from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field


class ExecutionLogRecord(BaseModel):
    """Execution log entity stored in SQLite."""
    id: Optional[int] = None
    request_id: str
    timestamp: str
    intent: str
    outcome: str
    verified: bool
    message: Optional[str] = None


class PermissionRecord(BaseModel):
    """User capability permission entity."""
    id: Optional[int] = None
    permission_name: str
    enabled: bool
    requires_confirmation: bool = False


class AppAliasRecord(BaseModel):
    """Whitelisted application alias entity."""
    id: Optional[int] = None
    alias: str
    executable_path: str
    enabled: bool = True


class UserSettingRecord(BaseModel):
    """General configuration setting entity."""
    id: Optional[int] = None
    setting_key: str
    setting_value: str

