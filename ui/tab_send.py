"""
Advanced Email Tool - Send Tab
==============================
Tab for executing the email send operation with progress tracking.
"""

from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QComboBox, QCheckBox,
    QMessageBox, QSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot

from ui.components.progress_log import ProgressLog
from ui.components.dialogs import show_error, show_info, show_warning, show_question
from core.outlook_sender import OutlookSender
from core.email_builder import EmailBuilder, Email
from data.checkpoint import CheckpointManager
from utils import get_logger

import config


class SendWorker(QThread):
    """Background worker for sending emails."""
    
    progress = pyqtSignal(int, int, str, bool, str)  # current, total, email, success, message
    finished = pyqtSignal(dict)  # results summary
    error = pyqtSignal(str)
    
    def __init__(
        self,
        sender: OutlookSender,
        emails: List[Email],
        checkpoint: CheckpointManager,
        interval: float,
        display_only: bool = False
    ):
        super().__init__()
        self.sender = sender
        self.emails = emails
        self.checkpoint = checkpoint
        self.interval = interval
        self.display_only = display_only
        self._cancelled = False
    
    def run(self):
        try:
            def progress_callback(current, total, email, success, message):
                to_str = "; ".join(email.to) if email.to else "Unknown"
                self.progress.emit(current, total, to_str, success, message)
                
                # Record in checkpoint
                if success:
                    self.checkpoint.record_success(email.row_index, to_str)
                else:
                    self.checkpoint.record_failure(email.row_index, to_str, message)
            
            def cancel_check():
                return self._cancelled
            
            results = self.sender.send_emails_batch(
                self.emails,
                display_only=self.display_only,
                interval=self.interval,
                progress_callback=progress_callback,
                cancel_check=cancel_check
            )
            
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def cancel(self):
        self._cancelled = True


class TabSend(QWidget):
    """
    Email sending tab.
    
    Features:
    - Outlook account selection
    - Send interval configuration
    - Preview mode (display only)
    - Real-time progress log
    - Pause/resume/cancel
    - Checkpoint recovery
    """
    
    # Signals
    send_started = pyqtSignal()
    send_completed = pyqtSignal(dict)  # results
    
    def __init__(self, parent=None):
        """Initialize the Send tab."""
        super().__init__(parent)
        
        self.logger = get_logger()
        self.outlook_sender = OutlookSender()
        self.checkpoint_manager = CheckpointManager()
        self._email_builder: Optional[EmailBuilder] = None
        self._emails: List[Email] = []
        self._send_worker: Optional[SendWorker] = None
        self._is_sending = False
        
        self._setup_ui()
        self._initialize_outlook()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Configuration section
        config_group = QGroupBox("Send Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Account selection
        account_layout = QHBoxLayout()
        
        account_label = QLabel("Send from:")
        account_layout.addWidget(account_label)
        
        self.account_combo = QComboBox()
        self.account_combo.setMinimumWidth(300)
        account_layout.addWidget(self.account_combo)
        
        self.refresh_accounts_btn = QPushButton("Refresh")
        self.refresh_accounts_btn.clicked.connect(self._refresh_accounts)
        account_layout.addWidget(self.refresh_accounts_btn)
        
        account_layout.addStretch()
        
        config_layout.addLayout(account_layout)
        
        # Options row
        options_layout = QHBoxLayout()
        
        interval_label = QLabel("Delay between emails:")
        options_layout.addWidget(interval_label)
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 30)
        self.interval_spin.setValue(int(config.SEND_INTERVAL))
        self.interval_spin.setSuffix(" seconds")
        options_layout.addWidget(self.interval_spin)
        
        options_layout.addSpacing(20)
        
        self.preview_check = QCheckBox("Preview mode (display in Outlook, don't send)")
        options_layout.addWidget(self.preview_check)
        
        options_layout.addStretch()
        
        config_layout.addLayout(options_layout)
        
        layout.addWidget(config_group)
        
        # Status section
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.online_label = QLabel("")
        status_layout.addWidget(self.online_label)
        
        layout.addLayout(status_layout)
        
        # Progress log
        log_group = QGroupBox("Progress")
        log_layout = QVBoxLayout(log_group)
        
        self.progress_log = ProgressLog()
        log_layout.addWidget(self.progress_log)
        
        layout.addWidget(log_group, stretch=1)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Start Sending")
        self.start_btn.setStyleSheet("font-weight: bold; padding: 10px 20px;")
        self.start_btn.clicked.connect(self._start_sending)
        controls_layout.addWidget(self.start_btn)
        
        self.cancel_btn = QPushButton("⬛ Cancel")
        self.cancel_btn.clicked.connect(self._cancel_sending)
        self.cancel_btn.setEnabled(False)
        controls_layout.addWidget(self.cancel_btn)
        
        controls_layout.addStretch()
        
        self.resume_btn = QPushButton("Resume Previous")
        self.resume_btn.clicked.connect(self._resume_sending)
        self.resume_btn.setVisible(False)
        controls_layout.addWidget(self.resume_btn)
        
        layout.addLayout(controls_layout)
    
    def _initialize_outlook(self) -> None:
        """Initialize Outlook connection."""
        success, error = self.outlook_sender.initialize()
        
        if success:
            self._refresh_accounts()
            self._update_online_status()
            self.progress_log.log_success("Outlook connected")
        else:
            self.progress_log.log_error(f"Outlook not available: {error}")
            self.start_btn.setEnabled(False)
            self.online_label.setText("⚠ Outlook not available")
            self.online_label.setStyleSheet("color: #dc3545;")
    
    def _refresh_accounts(self) -> None:
        """Refresh Outlook accounts list."""
        self.account_combo.clear()
        
        accounts = self.outlook_sender.get_accounts()
        for account in accounts:
            self.account_combo.addItem(
                f"{account.email} ({account.name})",
                account.email
            )
        
        if not accounts:
            self.account_combo.addItem("No accounts found")
    
    def _update_online_status(self) -> None:
        """Update Outlook online status."""
        is_online, status = self.outlook_sender.is_online()
        
        if is_online:
            self.online_label.setText("✓ Online")
            self.online_label.setStyleSheet("color: #28a745;")
        else:
            self.online_label.setText(f"⚠ {status}")
            self.online_label.setStyleSheet("color: #fd7e14;")
    
    def set_email_builder(self, builder: EmailBuilder) -> None:
        """Set the email builder."""
        self._email_builder = builder
    
    def set_emails(self, emails: List[Email]) -> None:
        """
        Set emails to send.
        
        Args:
            emails: List of Email objects
        """
        self._emails = emails
        self.status_label.setText(f"Ready: {len(emails)} emails to send")
        
        # Check for incomplete session
        if self.checkpoint_manager.has_incomplete_session():
            info = self.checkpoint_manager.get_incomplete_session_info()
            if info:
                self.resume_btn.setVisible(True)
                self.progress_log.log_warning(
                    f"Found incomplete session: {info['completed_count']}/{info['total_recipients']} sent"
                )
    
    def _start_sending(self) -> None:
        """Start the send operation."""
        if not self._emails:
            show_error(self, "Error", "No emails to send.")
            return
        
        # Confirm
        preview_mode = self.preview_check.isChecked()
        action = "display" if preview_mode else "send"
        
        reply = QMessageBox.question(
            self,
            f"Confirm {action.title()}",
            f"Are you sure you want to {action} {len(self._emails)} emails?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Select account
        account_email = self.account_combo.currentData()
        if account_email:
            self.outlook_sender.select_account(account_email)
        
        # Start checkpoint
        self.checkpoint_manager.start_session(
            len(self._emails),
            sending_account=account_email or ""
        )
        
        # Update UI
        self._is_sending = True
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.account_combo.setEnabled(False)
        self.interval_spin.setEnabled(False)
        self.preview_check.setEnabled(False)
        
        self.progress_log.clear()
        self.progress_log.start_operation(
            f"{'Displaying' if preview_mode else 'Sending'} emails",
            len(self._emails)
        )
        
        self.send_started.emit()
        
        # Start worker
        self._send_worker = SendWorker(
            self.outlook_sender,
            self._emails,
            self.checkpoint_manager,
            self.interval_spin.value(),
            preview_mode
        )
        self._send_worker.progress.connect(self._on_progress)
        self._send_worker.finished.connect(self._on_finished)
        self._send_worker.error.connect(self._on_error)
        self._send_worker.start()
    
    def _cancel_sending(self) -> None:
        """Cancel the send operation."""
        if self._send_worker:
            reply = QMessageBox.question(
                self,
                "Cancel Sending?",
                "Are you sure you want to cancel? Progress will be saved.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self._send_worker.cancel()
                self.progress_log.log_warning("Cancelling... (waiting for current email)")
    
    def _resume_sending(self) -> None:
        """Resume an incomplete session."""
        success, msg, remaining = self.checkpoint_manager.resume_session()
        
        if success:
            # Filter emails to only remaining ones
            remaining_set = set(remaining)
            self._emails = [e for e in self._emails if e.row_index in remaining_set]
            
            self.progress_log.log_info(msg)
            self._start_sending()
        else:
            show_error(self, "Resume Failed", msg)
    
    @pyqtSlot(int, int, str, bool, str)
    def _on_progress(self, current: int, total: int, email: str, success: bool, message: str) -> None:
        """Handle progress updates."""
        self.progress_log.set_progress(current, total)
        
        if success:
            self.progress_log.log_success(f"Sent to: {email}")
        else:
            self.progress_log.log_error(f"Failed: {email} - {message}")
        
        self.status_label.setText(f"Sending: {current}/{total}")
    
    @pyqtSlot(dict)
    def _on_finished(self, results: dict) -> None:
        """Handle send completion."""
        self._is_sending = False
        
        # Complete checkpoint
        self.checkpoint_manager.complete_session(
            success=not results.get('cancelled', False)
        )
        
        # Update UI
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.account_combo.setEnabled(True)
        self.interval_spin.setEnabled(True)
        self.preview_check.setEnabled(True)
        self.resume_btn.setVisible(False)
        
        sent = results.get('sent', 0)
        failed = results.get('failed', 0)
        cancelled = results.get('cancelled', False)
        
        self.progress_log.end_operation("Email sending", sent, failed)
        
        if cancelled:
            self.status_label.setText(f"Cancelled: {sent} sent, {failed} failed")
            self.progress_log.log_warning("Operation cancelled by user")
            self.resume_btn.setVisible(True)
        else:
            self.status_label.setText(f"Complete: {sent} sent, {failed} failed")
            if failed == 0:
                show_info(self, "Complete", f"Successfully sent {sent} emails!")
            else:
                show_warning(
                    self,
                    "Complete with Errors",
                    f"Sent: {sent}\nFailed: {failed}\n\nCheck the log for details."
                )
        
        self.send_completed.emit(results)
    
    @pyqtSlot(str)
    def _on_error(self, error: str) -> None:
        """Handle send error."""
        self._is_sending = False
        
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.account_combo.setEnabled(True)
        self.interval_spin.setEnabled(True)
        self.preview_check.setEnabled(True)
        
        self.progress_log.log_error(f"Error: {error}")
        self.status_label.setText("Error occurred")
        
        show_error(self, "Send Error", error)
    
    def get_selected_account(self) -> Optional[str]:
        """Get selected account email."""
        return self.account_combo.currentData()
    
    def is_sending(self) -> bool:
        """Check if currently sending."""
        return self._is_sending
