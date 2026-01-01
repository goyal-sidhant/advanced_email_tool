"""
Advanced Email Tool - Checkpoint Manager
========================================
Handles send progress checkpointing for resume functionality.
Saves progress during batch sends so they can be resumed after interruption.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from utils import get_logger

import config


class CheckpointManager:
    """
    Manages send operation checkpoints.
    
    Saves:
    - Session ID
    - Total recipients
    - Completed indices
    - Timestamp
    - Source file info
    
    Allows resuming interrupted batch sends.
    """
    
    def __init__(self):
        """Initialize checkpoint manager."""
        self.logger = get_logger()
        self.checkpoints_dir = config.CHECKPOINTS_DIR
        self.checkpoint_file = self.checkpoints_dir / config.CHECKPOINT_FILE
        self._ensure_directory()
        
        # Current session tracking
        self.session_id: Optional[str] = None
        self.total: int = 0
        self.completed: List[int] = []
        self.failed: List[int] = []
        self.is_active: bool = False
    
    def _ensure_directory(self) -> None:
        """Ensure checkpoints directory exists."""
        config.ensure_directories()
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def start_session(
        self,
        total_recipients: int,
        excel_file: str = "",
        sending_account: str = ""
    ) -> str:
        """
        Start a new send session.
        
        Args:
            total_recipients: Total number of emails to send
            excel_file: Path to source Excel file
            sending_account: Email account being used
            
        Returns:
            Session ID
        """
        self.session_id = self._generate_session_id()
        self.total = total_recipients
        self.completed = []
        self.failed = []
        self.is_active = True
        
        checkpoint_data = {
            'session_id': self.session_id,
            'started_at': datetime.now().isoformat(),
            'total_recipients': total_recipients,
            'excel_file': excel_file,
            'sending_account': sending_account,
            'completed_indices': [],
            'failed_indices': [],
            'last_updated': datetime.now().isoformat(),
            'status': 'in_progress',
        }
        
        self._save_checkpoint(checkpoint_data)
        self.logger.info(f"Send session started: {self.session_id}")
        
        return self.session_id
    
    def record_success(self, index: int, email: str = "") -> None:
        """
        Record a successful send.
        
        Args:
            index: Index of the recipient row
            email: Email address (for logging)
        """
        if not self.is_active:
            return
        
        self.completed.append(index)
        self._update_checkpoint()
        
        self.logger.debug(f"Checkpoint: sent #{index + 1} to {email}")
    
    def record_failure(self, index: int, email: str = "", reason: str = "") -> None:
        """
        Record a failed send.
        
        Args:
            index: Index of the recipient row
            email: Email address
            reason: Failure reason
        """
        if not self.is_active:
            return
        
        self.failed.append(index)
        self._update_checkpoint()
        
        self.logger.warning(f"Checkpoint: failed #{index + 1} ({email}): {reason}")
    
    def _update_checkpoint(self) -> None:
        """Update the checkpoint file with current progress."""
        try:
            # Load existing checkpoint
            checkpoint_data = self._load_checkpoint()
            if not checkpoint_data:
                return
            
            checkpoint_data['completed_indices'] = self.completed.copy()
            checkpoint_data['failed_indices'] = self.failed.copy()
            checkpoint_data['last_updated'] = datetime.now().isoformat()
            checkpoint_data['progress_percent'] = (
                len(self.completed) + len(self.failed)
            ) / self.total * 100 if self.total > 0 else 0
            
            self._save_checkpoint(checkpoint_data)
            
        except Exception as e:
            self.logger.error(f"Error updating checkpoint: {e}")
    
    def _save_checkpoint(self, data: Dict[str, Any]) -> None:
        """Save checkpoint data to file."""
        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving checkpoint: {e}")
    
    def _load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """Load checkpoint data from file."""
        try:
            if not self.checkpoint_file.exists():
                return None
            
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading checkpoint: {e}")
            return None
    
    def complete_session(self, success: bool = True) -> Dict[str, Any]:
        """
        Mark current session as complete.
        
        Args:
            success: Whether the batch completed successfully
            
        Returns:
            Summary dictionary
        """
        if not self.is_active:
            return {}
        
        # Update final status
        checkpoint_data = self._load_checkpoint()
        if checkpoint_data:
            checkpoint_data['status'] = 'completed' if success else 'interrupted'
            checkpoint_data['completed_at'] = datetime.now().isoformat()
            checkpoint_data['final_completed'] = len(self.completed)
            checkpoint_data['final_failed'] = len(self.failed)
            self._save_checkpoint(checkpoint_data)
        
        summary = {
            'session_id': self.session_id,
            'total': self.total,
            'completed': len(self.completed),
            'failed': len(self.failed),
            'success': success,
        }
        
        self.is_active = False
        self.logger.info(
            f"Session complete: {len(self.completed)}/{self.total} sent, "
            f"{len(self.failed)} failed"
        )
        
        return summary
    
    def has_incomplete_session(self) -> bool:
        """
        Check if there's an incomplete session to resume.
        
        Returns:
            True if incomplete session exists
        """
        checkpoint_data = self._load_checkpoint()
        if not checkpoint_data:
            return False
        
        return checkpoint_data.get('status') == 'in_progress'
    
    def get_incomplete_session_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about incomplete session.
        
        Returns:
            Session info dictionary or None
        """
        checkpoint_data = self._load_checkpoint()
        if not checkpoint_data or checkpoint_data.get('status') != 'in_progress':
            return None
        
        completed = checkpoint_data.get('completed_indices', [])
        failed = checkpoint_data.get('failed_indices', [])
        total = checkpoint_data.get('total_recipients', 0)
        
        return {
            'session_id': checkpoint_data.get('session_id'),
            'started_at': checkpoint_data.get('started_at'),
            'last_updated': checkpoint_data.get('last_updated'),
            'excel_file': checkpoint_data.get('excel_file'),
            'sending_account': checkpoint_data.get('sending_account'),
            'total_recipients': total,
            'completed_count': len(completed),
            'failed_count': len(failed),
            'remaining_count': total - len(completed) - len(failed),
            'progress_percent': checkpoint_data.get('progress_percent', 0),
        }
    
    def get_remaining_indices(self) -> List[int]:
        """
        Get indices that haven't been processed yet.
        
        Returns:
            List of remaining indices
        """
        checkpoint_data = self._load_checkpoint()
        if not checkpoint_data:
            return []
        
        total = checkpoint_data.get('total_recipients', 0)
        completed = set(checkpoint_data.get('completed_indices', []))
        failed = set(checkpoint_data.get('failed_indices', []))
        processed = completed | failed
        
        return [i for i in range(total) if i not in processed]
    
    def resume_session(self) -> Tuple[bool, str, List[int]]:
        """
        Resume an incomplete session.
        
        Returns:
            Tuple of (success, message, remaining_indices)
        """
        checkpoint_data = self._load_checkpoint()
        if not checkpoint_data:
            return False, "No checkpoint found", []
        
        if checkpoint_data.get('status') != 'in_progress':
            return False, "No incomplete session to resume", []
        
        # Restore state
        self.session_id = checkpoint_data.get('session_id')
        self.total = checkpoint_data.get('total_recipients', 0)
        self.completed = checkpoint_data.get('completed_indices', [])
        self.failed = checkpoint_data.get('failed_indices', [])
        self.is_active = True
        
        remaining = self.get_remaining_indices()
        
        self.logger.info(
            f"Resuming session {self.session_id}: "
            f"{len(remaining)} emails remaining"
        )
        
        return True, f"Resuming with {len(remaining)} remaining", remaining
    
    def clear_checkpoint(self) -> bool:
        """
        Clear the checkpoint file.
        
        Returns:
            True if cleared successfully
        """
        try:
            if self.checkpoint_file.exists():
                os.remove(self.checkpoint_file)
            
            self.session_id = None
            self.total = 0
            self.completed = []
            self.failed = []
            self.is_active = False
            
            self.logger.info("Checkpoint cleared")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing checkpoint: {e}")
            return False
    
    def get_progress(self) -> Dict[str, Any]:
        """
        Get current progress information.
        
        Returns:
            Progress dictionary
        """
        if not self.is_active:
            return {
                'active': False,
                'completed': 0,
                'failed': 0,
                'total': 0,
                'percent': 0,
            }
        
        processed = len(self.completed) + len(self.failed)
        percent = (processed / self.total * 100) if self.total > 0 else 0
        
        return {
            'active': True,
            'session_id': self.session_id,
            'completed': len(self.completed),
            'failed': len(self.failed),
            'total': self.total,
            'remaining': self.total - processed,
            'percent': percent,
        }
