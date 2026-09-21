import logging
import os
from logging.handlers import RotatingFileHandler

_logger = None


def setup_logger(log_file: str = "logs/bot.log", level: str = "INFO") -> None:
    """Setup logger with rotating file handler."""
    global _logger

    # Create log directory
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create logger
    _logger = logging.getLogger("vacancy_bot")
    _logger.setLevel(getattr(logging, level.upper()))
    _logger.propagate = False

    # Clear existing handlers to avoid duplication and allow reconfiguration
    _logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # File handler with rotation
    file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)  # 10MB
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)


def get_logger() -> logging.Logger:
    """Get the logger instance."""
    global _logger
    if _logger is None:
        setup_logger()
    assert _logger is not None
    return _logger
