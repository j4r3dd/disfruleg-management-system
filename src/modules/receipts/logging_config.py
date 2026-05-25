# -*- coding: utf-8 -*-
"""
Logging Configuration
Centralized logging setup for the receipts module
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# ==================== CONFIGURATION ====================

# Log directory - use writable path for bundled executable
try:
    from src.utils.resource_path import get_writable_path
    LOG_DIR = get_writable_path("logs").parent
except ImportError:
    # Fallback for development
    LOG_DIR = Path(__file__).parent / "logs"

LOG_DIR.mkdir(exist_ok=True)

# Log levels
DEFAULT_LEVEL = logging.INFO
CONSOLE_LEVEL = logging.INFO
FILE_LEVEL = logging.DEBUG

# Log format
DETAILED_FORMAT = (
    '%(asctime)s | %(levelname)-8s | %(name)s | '
    '%(filename)s:%(lineno)d | %(funcName)s() | %(message)s'
)

SIMPLE_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'

CONSOLE_FORMAT = '%(levelname)-8s | %(name)s | %(message)s'

# Date format
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# File rotation settings
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Keep 5 backup files


# ==================== CUSTOM FORMATTER ====================

class ColoredFormatter(logging.Formatter):
    """
    Custom formatter with color support for console output
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def __init__(self, fmt=None, datefmt=None, use_color=True):
        super().__init__(fmt, datefmt)
        self.use_color = use_color

    def format(self, record):
        if self.use_color and record.levelname in self.COLORS:
            # Add color to level name
            levelname_color = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
            record.levelname = levelname_color

        return super().format(record)


# ==================== LOGGER SETUP ====================

def setup_logger(
    name: str,
    level: int = DEFAULT_LEVEL,
    log_to_file: bool = True,
    log_to_console: bool = True,
    use_colors: bool = True
) -> logging.Logger:
    """
    Setup and configure a logger

    Args:
        name: Logger name (usually __name__)
        level: Logging level
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        use_colors: Whether to use colors in console output

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False  # Don't propagate to root logger

    # ==================== CONSOLE HANDLER ====================
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(CONSOLE_LEVEL)

        if use_colors:
            console_formatter = ColoredFormatter(
                fmt=CONSOLE_FORMAT,
                datefmt=DATE_FORMAT,
                use_color=True
            )
        else:
            console_formatter = logging.Formatter(
                fmt=CONSOLE_FORMAT,
                datefmt=DATE_FORMAT
            )

        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # ==================== FILE HANDLER ====================
    if log_to_file:
        # Main log file with rotation
        log_file = LOG_DIR / f"receipts_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(FILE_LEVEL)

        file_formatter = logging.Formatter(
            fmt=DETAILED_FORMAT,
            datefmt=DATE_FORMAT
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Error-only log file
        error_log_file = LOG_DIR / f"receipts_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance (creates if doesn't exist)

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, set it up
    if not logger.handlers:
        logger = setup_logger(name)

    return logger


# ==================== UTILITY FUNCTIONS ====================

def set_global_level(level: int):
    """
    Set logging level for all receipts loggers

    Args:
        level: Logging level (e.g., logging.DEBUG)
    """
    for name, logger in logging.Logger.manager.loggerDict.items():
        if isinstance(logger, logging.Logger) and name.startswith('src.modules.receipts'):
            logger.setLevel(level)


def cleanup_old_logs(days: int = 30):
    """
    Clean up log files older than specified days

    Args:
        days: Number of days to keep logs
    """
    import time

    cutoff_time = time.time() - (days * 86400)

    for log_file in LOG_DIR.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
                print(f"Deleted old log file: {log_file.name}")
            except Exception as e:
                print(f"Error deleting {log_file.name}: {e}")


def log_exception(logger: logging.Logger, exc: Exception, message: Optional[str] = None):
    """
    Log an exception with full traceback

    Args:
        logger: Logger instance
        exc: Exception to log
        message: Optional custom message
    """
    if message:
        logger.error(f"{message}: {exc}", exc_info=True)
    else:
        logger.error(f"Exception occurred: {exc}", exc_info=True)


# ==================== CONTEXT MANAGER ====================

class LogContext:
    """
    Context manager for logging function entry/exit

    Usage:
        with LogContext(logger, "Processing order"):
            # ... code ...
    """

    def __init__(self, logger: logging.Logger, operation: str, level: int = logging.DEBUG):
        self.logger = logger
        self.operation = operation
        self.level = level
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log(self.level, f"Starting: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (datetime.now() - self.start_time).total_seconds()

        if exc_type is not None:
            self.logger.error(
                f"Failed: {self.operation} (after {elapsed:.2f}s)",
                exc_info=(exc_type, exc_val, exc_tb)
            )
            return False  # Re-raise exception
        else:
            self.logger.log(
                self.level,
                f"Completed: {self.operation} ({elapsed:.2f}s)"
            )
            return True


# ==================== PERFORMANCE LOGGER ====================

class PerformanceLogger:
    """
    Logger for tracking performance metrics
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.metrics = {}

    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.metrics[operation] = datetime.now()

    def end_timer(self, operation: str, log_level: int = logging.DEBUG):
        """End timing and log the duration"""
        if operation in self.metrics:
            elapsed = (datetime.now() - self.metrics[operation]).total_seconds()
            self.logger.log(
                log_level,
                f"Performance | {operation}: {elapsed:.3f}s"
            )
            del self.metrics[operation]
            return elapsed
        else:
            self.logger.warning(f"Timer for '{operation}' was not started")
            return None


# ==================== MODULE INITIALIZATION ====================

# Create default logger for the module
_module_logger = setup_logger('src.modules.receipts')


def get_module_logger() -> logging.Logger:
    """Get the default module logger"""
    return _module_logger


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Example usage
    logger = get_logger(__name__)

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # Test context manager
    with LogContext(logger, "Test operation"):
        logger.info("Inside context")

    # Test performance logger
    perf = PerformanceLogger(logger)
    perf.start_timer("test_operation")
    import time
    time.sleep(0.1)
    perf.end_timer("test_operation", logging.INFO)

    # Test exception logging
    try:
        raise ValueError("Test exception")
    except Exception as e:
        log_exception(logger, e, "Test error handling")

    print(f"\nLog files created in: {LOG_DIR}")
