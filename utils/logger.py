"""
Structured logging module for AURA.
Writes to both standard output and rotating log file.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config import BASE_DIR, config

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "aura.log"


def setup_logger(name: str = "AURA") -> logging.Logger:
    """Configures and returns a logger instance."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        level_str = config.log_level.upper()
        level = getattr(logging, level_str, logging.INFO)
        logger.setLevel(level)

        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # File handler (max 5MB, keep 3 backups)
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


logger = setup_logger()

