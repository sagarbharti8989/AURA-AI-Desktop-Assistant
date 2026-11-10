"""
SQLite database connection and schema management for AURA.
"""

import sqlite3
from typing import Optional
from config import config
from utils.logger import logger
from utils.exceptions import DatabaseError


class DatabaseManager:
    """Manages SQLite connection lifecycle and schema migrations."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or config.db_path
        self._initialize_schema()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a new sqlite3 connection with Row factory."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to SQLite at {self.db_path}: {e}")
            raise DatabaseError(f"Database connection error: {e}") from e

    def _initialize_schema(self) -> None:
        """Creates tables if they do not exist."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Execution logs table (append-only)
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS execution_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        request_id TEXT NOT NULL UNIQUE,
                        timestamp TEXT NOT NULL,
                        intent TEXT NOT NULL,
                        outcome TEXT NOT NULL,
                        verified INTEGER NOT NULL,
                        message TEXT
                    );
                    """
                )

                # Permissions table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS permissions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        permission_name TEXT NOT NULL UNIQUE,
                        enabled INTEGER NOT NULL,
                        requires_confirmation INTEGER NOT NULL DEFAULT 0
                    );
                    """
                )

                # App aliases table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS app_aliases (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alias TEXT NOT NULL UNIQUE,
                        executable_path TEXT NOT NULL,
                        enabled INTEGER NOT NULL DEFAULT 1
                    );
                    """
                )

                # User settings table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        setting_key TEXT NOT NULL UNIQUE,
                        setting_value TEXT
                    );
                    """
                )

                conn.commit()
                self._seed_default_data(conn)
        except Exception as e:
            logger.error(f"Error initializing SQLite schema: {e}")
            raise DatabaseError(f"Schema initialization failed: {e}") from e

    def _seed_default_data(self, conn: sqlite3.Connection) -> None:
        """Seeds initial default permissions and app aliases if table is empty."""
        cursor = conn.cursor()

        # Seed permissions
        cursor.execute("SELECT COUNT(*) FROM permissions;")
        if cursor.fetchone()[0] == 0:
            default_permissions = [
                ("app_launch", 1, 0),
                ("app_close", 1, 0),
                ("volume_control", 1, 0),
                ("brightness_control", 1, 0),
                ("wifi_control", 1, 0),
                ("bluetooth_control", 1, 0),
                ("system_control", 1, 0),
            ]
            cursor.executemany(
                """
                INSERT OR IGNORE INTO permissions (permission_name, enabled, requires_confirmation)
                VALUES (?, ?, ?);
                """,
                default_permissions,
            )

        # Seed app aliases from config
        cursor.execute("SELECT COUNT(*) FROM app_aliases;")
        if cursor.fetchone()[0] == 0 and config.app_aliases:
            aliases_data = [
                (alias, data.get("executable", alias), 1)
                for alias, data in config.app_aliases.items()
            ]
            cursor.executemany(
                """
                INSERT OR IGNORE INTO app_aliases (alias, executable_path, enabled)
                VALUES (?, ?, ?);
                """,
                aliases_data,
            )

        conn.commit()


db_manager = DatabaseManager()

