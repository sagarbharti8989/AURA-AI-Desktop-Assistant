"""
Unit tests for database repositories.
"""

import pytest
from database.repositories import (
    ExecutionLogRepository,
    PermissionRepository,
    AppAliasRepository,
    SettingsRepository,
)
from database.models import ExecutionLogRecord
from utils.helpers import current_iso_timestamp, generate_request_id


def test_execution_log_repository():
    repo = ExecutionLogRepository()
    req_id = generate_request_id()

    record = ExecutionLogRecord(
        request_id=req_id,
        timestamp=current_iso_timestamp(),
        intent="set_volume",
        outcome="SUCCESS",
        verified=True,
        message="Volume set to 40%.",
    )
    repo.log(record)

    recent = repo.get_recent(5)
    assert any(r.request_id == req_id for r in recent)


def test_settings_repository():
    repo = SettingsRepository()
    repo.set("test_key", "test_value_123")
    val = repo.get("test_key")
    assert val == "test_value_123"


def test_app_alias_repository():
    repo = AppAliasRepository()
    exe = repo.get_executable("notepad")
    assert exe is not None

