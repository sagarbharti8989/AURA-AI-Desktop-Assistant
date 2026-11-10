"""
AURA – AI Desktop Assistant
Main Application Entry Point.
"""

import sys
from utils.logger import logger
from database.database import db_manager
from interface.dashboard import AuraDashboard


def main() -> None:
    """Initializes and runs AURA."""
    logger.info("Starting AURA – AI Desktop Assistant v2.0...")
    try:
        # 1. Initialize SQLite schema and repositories
        _ = db_manager

        # 2. Start Desktop UI
        app = AuraDashboard()
        app.mainloop()
    except KeyboardInterrupt:
        logger.info("AURA terminated by user.")
    except Exception as e:
        logger.critical(f"Fatal error during AURA execution: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

