"""
Advanced Email Tool - Session Manager
=====================================
Handles auto-save and crash recovery for application state.
Saves the complete session state to JSON for restoration.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from utils import get_logger

import config


class SessionManager:
    """
    Manages application session persistence.
    
    Saves and restores:
    - Excel file path
    - Column mappings
    - Email templates
    - Attachment settings
    - Recipient selections
    - Selected Outlook account
    """
    
    def __init__(self):
        """Initialize the session manager."""
        self.logger = get_logger()
        self.session_file = config.SESSIONS_DIR / config.SESSION_FILE
        self._ensure_directory()
    
    def _ensure_directory(self) -> None:
        """Ensure session directory exists."""
        config.ensure_directories()
    
    def save_session(self, state: Dict[str, Any]) -> bool:
        """
        Save current session state to disk.
        
        Args:
            state: Dictionary containing all session state
            
        Returns:
            True if saved successfully
        """
        try:
            # Add metadata
            state['_metadata'] = {
                'saved_at': datetime.now().isoformat(),
                'version': config.APP_VERSION,
            }
            
            # Save to file (atomically — a crash mid-write must never
            # destroy the previous session, this IS the crash-recovery file)
            from utils.file_utils import write_json_atomic
            write_json_atomic(
                self.session_file, state,
                indent=2, ensure_ascii=False, default=str
            )

            self.logger.debug(f"Session saved to {self.session_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving session: {e}", exc_info=True)
            return False
    
    def load_session(self) -> Optional[Dict[str, Any]]:
        """
        Load session state from disk.
        
        Returns:
            Session state dictionary, or None if no session found
        """
        try:
            if not self.session_file.exists():
                return None
            
            with open(self.session_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.logger.info("Session loaded from disk")
            return state
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid session file format: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading session: {e}", exc_info=True)
            return None
    
    @staticmethod
    def has_meaningful_content(state: Optional[Dict[str, Any]]) -> bool:
        """
        Check whether a session snapshot contains anything worth restoring.

        After 'New Session' the auto-save timer keeps running and saves an
        empty snapshot; without this check the next launch would offer to
        restore a blank session.
        """
        if not state:
            return False

        text_keys = ('excel_file_path', 'subject_template',
                     'attachment_folder', 'universal_bcc')
        if any(str(state.get(key) or '').strip() for key in text_keys):
            return True

        if state.get('static_attachments'):
            return True

        # The rich text editor emits boilerplate HTML even when empty —
        # only visible text counts as content
        body = str(state.get('body_template') or '')
        body_text = re.sub(r'<[^>]+>', '', body).replace('&nbsp;', '')
        return bool(body_text.strip())

    def has_saved_session(self) -> bool:
        """
        Check if a saved session exists.
        
        Returns:
            True if session file exists
        """
        return self.session_file.exists()
    
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """
        Get basic info about saved session without loading it fully.
        
        Returns:
            Dictionary with session metadata, or None
        """
        try:
            if not self.session_file.exists():
                return None
            
            with open(self.session_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Count selected recipients
            selected_indices = state.get('selected_indices', [])
            selected_count = len(selected_indices) if selected_indices else 0
            
            return {
                'saved_at': state.get('_metadata', {}).get('saved_at', 'Unknown'),
                'version': state.get('_metadata', {}).get('version', 'Unknown'),
                'excel_file': state.get('excel_file_path', 'Not set'),
                'has_template': bool(state.get('subject_template') or state.get('body_template')),
                'template_name': state.get('template_name', 'Custom'),
                'selected_count': selected_count,
            }
            
        except Exception:
            return None
    
    def clear_session(self) -> bool:
        """
        Delete the saved session file.
        
        Returns:
            True if cleared successfully
        """
        try:
            if self.session_file.exists():
                os.remove(self.session_file)
                self.logger.info("Session cleared")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing session: {e}")
            return False
    
    def create_state_snapshot(
        self,
        excel_file_path: str = "",
        column_mapping: Dict[str, str] = None,
        subject_template: str = "",
        body_template: str = "",
        static_attachments: list = None,
        attachment_folder: str = "",
        attachment_recursive: bool = False,
        selected_recipients: list = None,
        selected_account: str = "",
        universal_bcc: str = ""
    ) -> Dict[str, Any]:
        """
        Create a state snapshot dictionary from individual values.
        
        This is a helper method to ensure consistent state structure.
        
        Returns:
            State dictionary ready for saving
        """
        return {
            'excel_file_path': excel_file_path,
            'column_mapping': column_mapping or {},
            'subject_template': subject_template,
            'body_template': body_template,
            'static_attachments': static_attachments or [],
            'attachment_folder': attachment_folder,
            'attachment_recursive': attachment_recursive,
            'selected_recipients': selected_recipients or [],
            'selected_account': selected_account,
            'universal_bcc': universal_bcc,
        }
    
    def export_session(self, export_path: str) -> bool:
        """
        Export current session to a specific file.
        
        Args:
            export_path: Path to export file
            
        Returns:
            True if exported successfully
        """
        try:
            state = self.load_session()
            if not state:
                self.logger.warning("No session to export")
                return False
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Session exported to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting session: {e}")
            return False
    
    def import_session(self, import_path: str) -> bool:
        """
        Import session from a specific file.
        
        Args:
            import_path: Path to import file
            
        Returns:
            True if imported successfully
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Validate basic structure
            if not isinstance(state, dict):
                self.logger.error("Invalid session file structure")
                return False
            
            # Save as current session
            return self.save_session(state)
            
        except Exception as e:
            self.logger.error(f"Error importing session: {e}")
            return False


class AutoSaveManager:
    """
    Manages automatic saving of session state.

    Runs on a QTimer so the state getter (which reads Qt widgets) always
    executes on the GUI thread — the old threading.Timer read widget
    state from a background thread, which is undefined behavior in Qt.
    """

    def __init__(self, session_manager: SessionManager):
        """
        Initialize auto-save manager.

        Args:
            session_manager: SessionManager instance to use
        """
        self.session_manager = session_manager
        self.logger = get_logger()
        self._timer = None
        self._state_getter = None
        self._pause_check = None
        self._interval = config.AUTO_SAVE_INTERVAL

    def set_state_getter(self, getter_func) -> None:
        """
        Set the function that returns current state.

        Args:
            getter_func: Function that returns state dictionary
        """
        self._state_getter = getter_func

    def set_pause_check(self, pause_func) -> None:
        """
        Set a predicate that pauses auto-save while true (e.g. mid-send,
        when tabs are being mutated by the send worker).
        """
        self._pause_check = pause_func

    def start(self, interval: float = None) -> None:
        """
        Start auto-save timer.

        Must be called from the GUI thread.

        Args:
            interval: Save interval in seconds (default from config)
        """
        if interval:
            self._interval = interval

        from PyQt5.QtCore import QTimer

        if self._timer is None:
            self._timer = QTimer()
            self._timer.timeout.connect(self._do_save)

        self._timer.start(int(self._interval * 1000))
        self.logger.info(f"Auto-save started (interval: {self._interval}s)")

    def stop(self) -> None:
        """Stop auto-save timer."""
        if self._timer:
            self._timer.stop()
        self.logger.info("Auto-save stopped")

    def _do_save(self) -> None:
        """Perform auto-save (skipped while paused)."""
        try:
            if self._pause_check and self._pause_check():
                return
            if self._state_getter:
                state = self._state_getter()
                if state:
                    self.session_manager.save_session(state)
        except Exception as e:
            self.logger.error(f"Auto-save error: {e}")

    def save_now(self) -> bool:
        """
        Trigger immediate save.

        Returns:
            True if saved successfully
        """
        if self._state_getter:
            state = self._state_getter()
            if state:
                return self.session_manager.save_session(state)
        return False
