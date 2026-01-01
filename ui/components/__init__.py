"""
Advanced Email Tool - UI Components Package
===========================================
Reusable UI widgets and components.
"""

from .dialogs import (
    show_info,
    show_warning,
    show_error,
    show_question,
    show_file_dialog,
    show_folder_dialog,
    show_save_dialog,
    InputDialog,
    ProgressDialog,
)

from .progress_log import ProgressLog
from .file_list import FileListWidget
from .recipient_list import RecipientListWidget

from .rich_text_editor import RichTextEditor

__all__ = [
    # Dialogs
    'show_info',
    'show_warning',
    'show_error',
    'show_question',
    'show_file_dialog',
    'show_folder_dialog',
    'show_save_dialog',
    'InputDialog',
    'ProgressDialog',
    # Widgets
    'ProgressLog',
    'FileListWidget',
    'RecipientListWidget',
    'RichTextEditor',
]
