from pathlib import Path
import os
import sys
from loguru import logger

def setup_logging():
    logger.remove()
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_file = os.environ.get("LOG_FILE", "").strip()

    logger.add(
        sys.stdout,
        colorize=True,
        level=level,
        backtrace=False,
        diagnose=False,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <7}</level> | "
               "<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>"
    )
    if log_file:
        p = Path(log_file).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(p),
            level=level,
            rotation="20 MB",
            retention="10 files",
            compression="zip",
            encoding="utf-8",
            backtrace=False,
            diagnose=False,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <7} | {function}:{line} - {message}",
        )