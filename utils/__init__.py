"""
Advanced Email Tool - Utilities Package
=======================================
Common utility functions used across the application.
"""

from .logger import setup_logger, get_logger
from .file_utils import (
    check_path_accessible,
    check_network_drive,
    get_file_size,
    get_file_size_formatted,
    format_bytes,
    scan_directory,
    is_valid_path,
    ensure_extended_path,
)

__all__ = [
    # Logger
    'setup_logger',
    'get_logger',
    # File utilities
    'check_path_accessible',
    'check_network_drive',
    'get_file_size',
    'get_file_size_formatted',
    'format_bytes',
    'scan_directory',
    'is_valid_path',
    'ensure_extended_path',
]
