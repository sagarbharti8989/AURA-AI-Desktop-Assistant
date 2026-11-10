"""
Repository layer providing clean CRUD abstractions over SQLite tables.
"""

from typing import List, Optional, Dict
from database.database import db_manager
from database.models import (
    ExecutionLogRecord,
    PermissionRecord,
    AppAliasRecord,
    UserSettingRecord,
)
from utils.logger import logger


class ExecutionLogRepository:
    """Repository for execution logs."""

    def __init__(self, manager=db_manager) -> None:
        self.manager = manager

    def log(self, record: ExecutionLogRecord) -> None:
        """Appends a new execution record."""
        try:
            with self.manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO execution_logs (request_id, timestamp, intent, outcome, verified, message)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        record.request_id,
                        record.timestamp,
                        record.intent,
                        record.outcome,
                        1 if record.verified else 0,
                        record.message,
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to write execution log: {e}")

    def get_recent(self, limit: int = 50) -> List[ExecutionLogRecord]:
        """Fetches recent execution logs ordered newest first."""
        records: List[ExecutionLogRecord] = []
        try:
            with self.manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, request_id, timestamp, intent, outcome, verified, message
                    FROM execution_logs
                    ORDER BY id DESC
                    LIMIT ?;
                    """,
                    (limit,),
                )
                for row in cursor.fetchall():
                    records.append(
                        ExecutionLogRecord(
                            id=row["id"],
                            request_id=row["request_id"],
                            timestamp=row["timestamp"],
                            intent=row["intent"],
                            outcome=row["outcome"],
                            verified=bool(row["verified"]),
                            message=row["message"],
                        )
                    )
        except Exception as e:
            logger.error(f"Failed to fetch execution logs: {e}")
        return records

    def clear(self) -> None:
        """Clears all execution logs."""
        try:
            with self.manager.get_connection() as conn:
                conn.execute("DELETE FROM execution_logs;")
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to clear execution logs: {e}")


class PermissionRepository:
    """Repository for user capability permissions."""

    def __init__(self, manager=db_manager) -> None:
        self.manager = manager

    def is_enabled(self, permission_name: str) -> bool:
        """Returns True if the permission is enabled in the database."""
        try:
            with self.manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT enabled FROM permissions WHERE permission_name = ?;",
                    (permission_name,),
                )
                row = cursor.fetchone()
                if row:
                    return bool(row["enabled"])
        except Exception as e:
            logger.error(f"Failed to query permission {permission_name}: {e}")
        return False

    def set_enabled(self, permission_name: str, enabled: bool) -> None:
        """Enables or disables a permission."""
        try:
            with self.manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO permissions (permission_name, enabled, requires_confirmation)
                    VALUES (?, ?, 0)
                    ON CONFLICT(permission_name) DO UPDATE SET enabled = excluded.enabled;
                    """,
                    (permission_name, 1 if enabled else 0),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to set permission {permission_name}: {e}")

    def get_all(self) -> Dict[str, bool]:
        """Returns a dictionary of all permissions and their boolean status."""
        permissions: Dict[str, bool] = {}
        try:
            with self.manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT permission_name, enabled FROM permissions;")
                for row in cursor.fetchall():
                    permissions[row["permission_name"]] = bool(row["enabled"])
        except Exception as e:
            logger.error(f"Failed to fetch all permissions: {e}")
        return permissions


class AppAliasRepository:
    """Repository for approved application aliases."""

    def __init__(self, manager=db_manager) -> None:
        self.manager = manager

    def get_executable(self, alias: str) -> Optional[str]:
        """Resolves alias to an executable reference if enabled."""
        try:
            with self.manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT executable_path FROM app_aliases WHERE alias = ? AND enabled = 1;",
                    (alias.lower().strip(),),
                )
                row = cursor.fetchone()
                if row:
                    return str(row["executable_path"])
        except Exception as e:
            logger.error(f"Failed to lookup alias {alias}: {e}")
        return None

    def get_all(self) -> List[AppAliasRecord]:
        """Returns all configured app aliases."""
        aliases: List[AppAliasRecord] = []
        try:
            with self.manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, alias, executable_path, enabled FROM app_aliases;")
                for row in cursor.fetchall():
                    aliases.append(
                        AppAliasRecord(
                            id=row["id"],
                            alias=row["alias"],
                            executable_path=row["executable_path"],
                            enabled=bool(row["enabled"]),
                        )
                    )
        except Exception as e:
            logger.error(f"Failed to get app aliases: {e}")
        return aliases


class SettingsRepository:
    """Repository for key-value user settings."""

    def __init__(self, manager=db_manager) -> None:
        self.manager = manager

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieves a setting by key."""
        try:
            with self.manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT setting_value FROM user_settings WHERE setting_key = ?;", (key,))
                row = cursor.fetchone()
                if row:
                    return str(row["setting_value"])
        except Exception as e:
            logger.error(f"Failed to get setting {key}: {e}")
        return default

    def set(self, key: str, value: str) -> None:
        """Inserts or updates a setting key."""
        try:
            with self.manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO user_settings (setting_key, setting_value)
                    VALUES (?, ?)
                    ON CONFLICT(setting_key) DO UPDATE SET setting_value = excluded.setting_value;
                    """,
                    (key, value),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to set setting {key}: {e}")

