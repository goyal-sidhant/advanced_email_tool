"""
Advanced Email Tool - Data Package
==================================
Data persistence layer for sessions, templates, and recipient lists.
Handles saving and loading user data to disk.
"""

from .session_manager import SessionManager
from .template_storage import TemplateStorage
from .recipient_lists import RecipientListStorage
from .checkpoint import CheckpointManager

__all__ = [
    'SessionManager',
    'TemplateStorage',
    'RecipientListStorage',
    'CheckpointManager',
]
