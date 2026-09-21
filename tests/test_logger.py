import logging
import os

from utils.logger import get_logger, setup_logger


def _cleanup_logger(log_file: str) -> None:
    """Close all handlers and remove log file."""
    logger = get_logger()
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    if os.path.exists(log_file):
        os.remove(log_file)


def test_setup_logger_creates_log_file():
    """Test that setup_logger creates log directory and file."""
    log_file = "logs/test.log"

    # Clean up
    _cleanup_logger(log_file)

    setup_logger(log_file=log_file)
    logger = get_logger()

    assert os.path.exists(log_file)
    assert logger is not None
    assert logger.level == logging.INFO

    # Cleanup
    _cleanup_logger(log_file)


def test_logger_writes_to_file():
    """Test that logger actually writes to file."""
    log_file = "logs/test_write.log"

    _cleanup_logger(log_file)

    setup_logger(log_file=log_file)
    logger = get_logger()

    logger.info("Test message")

    # Force flush
    for handler in logger.handlers:
        handler.flush()

    with open(log_file) as f:
        content = f.read()
        assert "Test message" in content

    # Cleanup
    _cleanup_logger(log_file)
