"""
utils/logger.py
───────────────
Centralised logging factory for the Telesurgery-LangChain system.
Every module calls setup_logger(__name__) to get a named logger
that writes to both stdout and a rotating log file under results/.
"""

import logging
import sys
from pathlib import Path

# Import lazily to avoid circular dependency at module load time
def _get_settings():
    from config import settings
    return settings


def setup_logger(name: str) -> logging.Logger:
    """
    Return a named logger configured for both console and file output.
    Safe to call multiple times — won't add duplicate handlers.

    Args:
        name: Typically __name__ of the calling module.

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    cfg = _get_settings()
    level = getattr(logging, cfg.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-24s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Console handler ───────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    # ── File handler ──────────────────────────────────────────────
    log_path: Path = cfg.RESULTS_DIR / cfg.LOG_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(fmt)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)

    # Prevent messages from propagating to the root logger
    logger.propagate = False

    return logger
