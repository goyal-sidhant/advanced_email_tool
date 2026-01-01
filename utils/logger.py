"""
Advanced Email Tool - Logger
============================
Centralized logging configuration for the application.
Logs to both file and console with rotating file handler.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

import config

# Global logger instance
_logger: Optional[logging.Logger] = None


def setup_logger(name: str = "AdvancedEmailTool") -> logging.Logger:
    """
    Set up and configure the application logger.
    
    Creates a logger that writes to:
    - Console (INFO level and above)
    - Rotating file (DEBUG level and above)
    
    Args:
        name: Logger name (default: "AdvancedEmailTool")
        
    Returns:
        Configured logger instance
    """
    global _logger
    
    if _logger is not None:
        return _logger
    
    # Ensure log directory exists
    config.ensure_directories()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers if called multiple times
    if logger.handlers:
        return logger
    
    # Create formatters
    file_formatter = logging.Formatter(
        fmt=config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT
    )
    console_formatter = logging.Formatter(
        fmt="%(levelname)s: %(message)s"
    )
    
    # File handler (rotating)
    log_file = config.LOGS_DIR / config.LOG_FILE_NAME
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    _logger = logger
    
    logger.info(f"Logger initialized - Log file: {log_file}")
    
    return logger


def get_logger() -> logging.Logger:
    """
    Get the application logger instance.
    
    If logger hasn't been set up yet, sets it up with defaults.
    
    Returns:
        Logger instance
    """
    global _logger
    
    if _logger is None:
        return setup_logger()
    
    return _logger


def log_exception(message: str, exc: Exception) -> None:
    """
    Log an exception with full traceback.
    
    Args:
        message: Contextual message about what was happening
        exc: The exception that occurred
    """
    logger = get_logger()
    logger.error(f"{message}: {type(exc).__name__}: {exc}", exc_info=True)


def log_send_event(recipient: str, status: str, details: str = "") -> None:
    """
    Log an email send event with consistent formatting.
    
    Args:
        recipient: Email address of recipient
        status: "SUCCESS", "FAILED", or "SKIPPED"
        details: Additional details (optional)
    """
    logger = get_logger()
    
    if status == "SUCCESS":
        logger.info(f"✓ Email sent to {recipient}")
    elif status == "FAILED":
        logger.error(f"✗ Email failed for {recipient}: {details}")
    elif status == "SKIPPED":
        logger.warning(f"⚠ Email skipped for {recipient}: {details}")
    
    if details and status == "SUCCESS":
        logger.debug(f"  Details: {details}")


def log_matching_event(identifier: str, matched_count: int, files: list = None) -> None:
    """
    Log a file matching event.
    
    Args:
        identifier: Client identifier that was matched
        matched_count: Number of files matched
        files: List of matched filenames (optional)
    """
    logger = get_logger()
    
    if matched_count > 0:
        logger.debug(f"Matched {matched_count} file(s) for identifier '{identifier}'")
        if files:
            for f in files:
                logger.debug(f"  - {f}")
    else:
        logger.warning(f"No files matched for identifier '{identifier}'")
