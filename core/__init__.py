"""
Advanced Email Tool - Core Package
==================================
Core business logic for email operations.
This package contains no UI code - purely logic.
"""

from .validators import (
    validate_email_address,
    validate_email_list,
    suggest_email_correction,
    validate_template_variables,
    check_attachment_size,
)

from .excel_handler import ExcelHandler
from .template_engine import TemplateEngine
from .attachment_matcher import AttachmentMatcher
from .email_builder import EmailBuilder
from .outlook_sender import OutlookSender

__all__ = [
    # Validators
    'validate_email_address',
    'validate_email_list',
    'suggest_email_correction',
    'validate_template_variables',
    'check_attachment_size',
    # Classes
    'ExcelHandler',
    'TemplateEngine',
    'AttachmentMatcher',
    'EmailBuilder',
    'OutlookSender',
]
