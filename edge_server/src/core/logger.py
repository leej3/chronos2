import sys
from loguru import logger
from .config import settings

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL
)
logger.add(
    settings.LOG_FILE,
    rotation="500 MB",
    retention="10 days",
    level=settings.LOG_LEVEL
)

def get_logs(n_lines: int = 100) -> list:
    """Get last n lines from log file"""
    try:
        with open(settings.LOG_FILE, 'r') as f:
            lines = f.readlines()
            return lines[-n_lines:]
    except Exception as e:
        logger.error(f"Error reading log file: {e}")
        return []