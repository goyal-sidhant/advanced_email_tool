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
from ui.components.tab_navigation import TabNavigationBar
import time

from core.outlook_sender import OutlookSender, detect_new_outlook


def format_eta(elapsed_seconds: float, done: int, total: int) -> str:
    """Human-readable time remaining, from progress so far ('' if unknown)."""
    if done <= 0 or done >= total or elapsed_seconds <= 0:
        return ""

    remaining = elapsed_seconds / done * (total - done)
    if remaining < 90:
        return f"about {int(round(remaining))}s left"
    return f"about {int(round(remaining / 60))} min left"
from core.email_builder import EmailBuilder, Email
from data.checkpoint import CheckpointManager
from utils import get_logger

import config


class SendWorker(QThread):
    """Background worker for sending emails."""

    progress = pyqtSignal(int, int, str, bool, str)  # current, total, email, success, message
    sending = pyqtSignal(int, int, str)  # current, total, recipient (in flight)
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

            def before_send(current, total, email):
                to_str = "; ".join(email.to) if email.to else "Unknown"
                self.sending.emit(current, total, to_str)

            def cancel_check():
                return self._cancelled

            results = self.sender.send_emails_batch(
                self.emails,
                display_only=self.display_only,
                interval=self.interval,
                progress_callback=progress_callback,
                cancel_check=cancel_check,
                before_send_callback=before_send
            )

            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))
    
    def cancel(self):
        self._cancelled = True


class OutlookInitWorker(QThread):
    """Connects to Outlook off the UI thread so startup never freezes."""

    done = pyqtSignal(bool, str, bool)  # success, error, new_outlook_detected

    def __init__(self, sender: OutlookSender):
        super().__init__()
        self.sender = sender

    def run(self):
        try:
            ok, error = self.sender.initialize()
        except Exception as e:
            ok, error = False, str(e)

        new_outlook = False
        if not ok:
            try:
                new_outlook = detect_new_outlook()
            except Exception:
                pass

        self.done.emit(ok, error, new_outlook)


class TestSendWorker(QThread):
    """Background worker for the single test email — keeps the UI responsive."""

    finished_with_result = pyqtSignal(bool, str, str)  # success, message, recipient

    def __init__(self, sender: OutlookSender, email: Email):
        super().__init__()
        self.sender = sender
        self.email = email

    def run(self):
        try:
            success, message = self.sender.send_email(self.email)
        except Exception as e:
            success, message = False, str(e)

        recipient = self.email.to[0] if self.email.to else ""
        self.finished_with_result.emit(success, message, recipient)


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
    navigate_previous = pyqtSignal()
    navigate_next = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the Send tab."""
        super().__init__(parent)
        
        self.logger = get_logger()
        self.outlook_sender = OutlookSender()
        self.checkpoint_manager = CheckpointManager()
        self._email_builder: Optional[EmailBuilder] = None
        self._emails: List[Email] = []
        self._send_worker: Optional[SendWorker] = None
        self._init_worker: Optional[OutlookInitWorker] = None
        self._is_sending = False

        self._setup_ui()

        # Outlook connection is deferred: main.py calls start_outlook_init()
        # after the window is shown, so startup never blocks on COM
        self.start_btn.setEnabled(False)
        self.online_label.setText("Not connected")
        self.online_label.setStyleSheet("color: gray;")
    
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
        interval_label.setToolTip("Wait time between sending each email")
        options_layout.addWidget(interval_label)
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 30)
        self.interval_spin.setValue(int(config.SEND_INTERVAL))
        self.interval_spin.setSuffix(" seconds")
        self.interval_spin.setToolTip(
            "Delay between sending emails.\n"
            "Helps avoid triggering spam filters.\n"
            "Recommended: 2-5 seconds."
        )
        options_layout.addWidget(self.interval_spin)
        
        options_layout.addSpacing(20)
        
        self.preview_check = QCheckBox("Preview mode (display in Outlook, don't send)")
        self.preview_check.setToolTip(
            "Opens each email in Outlook for review.\n"
            "You can then send manually or close.\n"
            "Useful for testing before bulk send."
        )
        options_layout.addWidget(self.preview_check)
        
        options_layout.addStretch()
        
        config_layout.addLayout(options_layout)
        
        layout.addWidget(config_group)
        
        # Pre-Send Summary section
        summary_group = QGroupBox("Pre-Send Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        # Summary stats
        stats_layout = QHBoxLayout()
        
        self.summary_recipients = QLabel("Recipients: 0")
        self.summary_recipients.setStyleSheet("font-weight: bold;")
        stats_layout.addWidget(self.summary_recipients)
        
        stats_layout.addSpacing(30)
        
        self.summary_attachments = QLabel("With attachments: 0")
        stats_layout.addWidget(self.summary_attachments)
        
        stats_layout.addSpacing(30)
        
        self.summary_no_attachments = QLabel("")
        self.summary_no_attachments.setStyleSheet("color: #856404;")
        stats_layout.addWidget(self.summary_no_attachments)
        
        stats_layout.addStretch()
        
        summary_layout.addLayout(stats_layout)
        
        # Warning section
        self.warning_frame = QWidget()
        warning_layout = QHBoxLayout(self.warning_frame)
        warning_layout.setContentsMargins(0, 5, 0, 5)
        
        self.warning_icon = QLabel("⚠")
        self.warning_icon.setStyleSheet("color: #dc3545; font-size: 16px;")
        warning_layout.addWidget(self.warning_icon)
        
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: #dc3545;")
        warning_layout.addWidget(self.warning_label)
        
        self.view_warnings_btn = QPushButton("View List")
        self.view_warnings_btn.setFixedWidth(80)
        self.view_warnings_btn.clicked.connect(self._show_warning_details)
        warning_layout.addWidget(self.view_warnings_btn)
        
        warning_layout.addStretch()
        
        self.warning_frame.setVisible(False)
        summary_layout.addWidget(self.warning_frame)
        
        # Test send button
        test_layout = QHBoxLayout()
        
        self.test_btn = QPushButton("📧 Send Test Email First")
        self.test_btn.setToolTip("Send first email to yourself for verification")
        self.test_btn.clicked.connect(self._send_test_email)
        test_layout.addWidget(self.test_btn)
        
        test_layout.addStretch()
        
        summary_layout.addLayout(test_layout)
        
        layout.addWidget(summary_group)
        
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
        
        self.retry_btn = QPushButton()
        self.retry_btn.setToolTip("Send again only to the recipients that failed")
        self.retry_btn.clicked.connect(self._retry_failed)
        self.retry_btn.setVisible(False)
        controls_layout.addWidget(self.retry_btn)

        self.resume_btn = QPushButton("Resume Previous")
        self.resume_btn.clicked.connect(self._resume_sending)
        self.resume_btn.setVisible(False)
        controls_layout.addWidget(self.resume_btn)

        layout.addLayout(controls_layout)

        # Navigation bar (last tab - no Next button)
        self.nav_bar = TabNavigationBar(show_previous=True, show_next=False)
        self.nav_bar.previous_clicked.connect(self.navigate_previous.emit)
        layout.addWidget(self.nav_bar)

    def start_outlook_init(self) -> None:
        """Connect to Outlook in a worker thread (called after window show)."""
        if self.outlook_sender.is_initialized():
            return
        if self._init_worker and self._init_worker.isRunning():
            return

        self.online_label.setText("⏳ Connecting to Outlook…")
        self.online_label.setStyleSheet("color: gray;")
        self.start_btn.setEnabled(False)

        self._init_worker = OutlookInitWorker(self.outlook_sender)
        self._init_worker.done.connect(self._on_outlook_init_done)
        self._init_worker.start()

    @pyqtSlot(bool, str, bool)
    def _on_outlook_init_done(self, success: bool, error: str, new_outlook: bool) -> None:
        """Handle Outlook connection result on the UI thread."""
        if success:
            self._populate_accounts()
            self._update_online_status()
            self.start_btn.setEnabled(True)
            self.progress_log.log_success("Outlook connected")
        else:
            self.progress_log.log_error(f"Outlook not available: {error}")
            self.start_btn.setEnabled(False)
            self.online_label.setText("⚠ Outlook not available — click Refresh to retry")
            self.online_label.setStyleSheet("color: #dc3545;")

            if new_outlook:
                show_warning(
                    self,
                    "New Outlook Detected",
                    "This app requires Outlook Classic — New Outlook cannot "
                    "be automated.\n\n"
                    "To switch back:\n"
                    "1. Open Outlook\n"
                    "2. Go to Settings (gear icon)\n"
                    "3. Toggle OFF 'New Outlook'\n\n"
                    "Then click Refresh on the Send tab to reconnect."
                )

    def _refresh_accounts(self) -> None:
        """Refresh accounts — doubles as reconnect if Outlook wasn't available."""
        if not self.outlook_sender.is_initialized():
            self.start_outlook_init()
            return

        self.outlook_sender.refresh_accounts()
        self._populate_accounts()

    def _populate_accounts(self) -> None:
        """Fill the account dropdown from the sender's account list."""
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
        
        # Update pre-send summary
        self._update_summary()
        
        # Check for incomplete session
        if self.checkpoint_manager.has_incomplete_session():
            info = self.checkpoint_manager.get_incomplete_session_info()
            if info:
                self.resume_btn.setVisible(True)
                self.progress_log.log_warning(
                    f"Found incomplete session: {info['completed_count']}/{info['total_recipients']} sent"
                )
    
    def _update_summary(self) -> None:
        """Update the pre-send summary display."""
        if not self._emails:
            self.summary_recipients.setText("Recipients: 0")
            self.summary_attachments.setText("With attachments: 0")
            self.summary_no_attachments.setText("")
            self.warning_frame.setVisible(False)
            return
        
        total = len(self._emails)
        with_attachments = sum(1 for e in self._emails if e.attachments)
        without_attachments = total - with_attachments
        
        self.summary_recipients.setText(f"Recipients: {total}")
        self.summary_attachments.setText(f"With attachments: {with_attachments}")
        
        # Show warning for emails without attachments
        self._no_attachment_emails = [e for e in self._emails if not e.attachments]
        
        if without_attachments > 0:
            self.summary_no_attachments.setText(f"⚠ {without_attachments} without attachments")
            self.warning_label.setText(f"{without_attachments} recipient(s) have no attachments")
            self.warning_frame.setVisible(True)
        else:
            self.summary_no_attachments.setText("✓ All have attachments")
            self.summary_no_attachments.setStyleSheet("color: #28a745;")
            self.warning_frame.setVisible(False)
    
    def _show_warning_details(self) -> None:
        """Show details about warnings (emails without attachments)."""
        if not hasattr(self, '_no_attachment_emails') or not self._no_attachment_emails:
            return
        
        details = "Recipients without attachments:\n\n"
        for i, email in enumerate(self._no_attachment_emails[:50], 1):  # Limit to 50
            to_str = email.to[0] if email.to else "Unknown"
            details += f"{i}. {to_str}\n"
        
        if len(self._no_attachment_emails) > 50:
            details += f"\n... and {len(self._no_attachment_emails) - 50} more"
        
        QMessageBox.information(
            self,
            "Recipients Without Attachments",
            details
        )
    
    def _send_test_email(self) -> None:
        """Send a test email (first email to logged-in user)."""
        if not self._emails:
            show_error(self, "Error", "No emails to test.")
            return

        # Apply the account chosen in the dropdown — the test must verify
        # the same sender identity the real send will use
        account_email = self.account_combo.currentData()
        if account_email:
            self.outlook_sender.select_account(account_email)

        # Get the logged-in user's email
        account = self.outlook_sender.get_selected_account()
        if not account:
            show_error(self, "Error", "No Outlook account selected.")
            return

        my_email = account.email

        # Confirm
        reply = QMessageBox.question(
            self,
            "Send Test Email",
            f"This will send the FIRST email to yourself:\n\n"
            f"To: {my_email}\n"
            f"Subject: [TEST] {self._emails[0].subject[:50]}...\n\n"
            f"Continue?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Create test email (copy of first email, sent to self)
        from copy import deepcopy
        test_email = deepcopy(self._emails[0])
        test_email.to = [my_email]
        test_email.cc = []
        test_email.bcc = []
        test_email.subject = f"[TEST] {test_email.subject}"

        # Send in the background so the window stays responsive
        self.test_btn.setEnabled(False)
        self.status_label.setText("Sending test email...")

        self._test_worker = TestSendWorker(self.outlook_sender, test_email)
        self._test_worker.finished_with_result.connect(self._on_test_send_done)
        self._test_worker.start()

    @pyqtSlot(bool, str, str)
    def _on_test_send_done(self, success: bool, message: str, recipient: str) -> None:
        """Handle test send completion."""
        self.test_btn.setEnabled(True)
        self.status_label.setText(f"Ready: {len(self._emails)} emails to send")

        if success:
            show_info(self, "Test Sent", f"Test email sent to {recipient}\n\nCheck your inbox!")
            self.progress_log.log_success(f"Test email sent to {recipient}")
        else:
            self.progress_log.log_error(f"Test email failed: {message}")
            show_error(self, "Test Failed", f"Could not send test email:\n{message}")
    
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

        # Start checkpoint with the actual row indexes being sent, so a
        # resume matches emails by row even when a subset was selected
        self.checkpoint_manager.start_session(
            [e.row_index for e in self._emails],
            sending_account=account_email or ""
        )

        self._launch_send(self._emails)

    def _launch_send(self, emails: List[Email]) -> None:
        """Start the send worker for the given emails (checkpoint already set up)."""
        preview_mode = self.preview_check.isChecked()

        # Update UI
        self._is_sending = True
        self._send_started_at = time.monotonic()
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.account_combo.setEnabled(False)
        self.interval_spin.setEnabled(False)
        self.preview_check.setEnabled(False)
        self.retry_btn.setVisible(False)
        self.resume_btn.setVisible(False)

        self.progress_log.clear()
        self.progress_log.start_operation(
            f"{'Displaying' if preview_mode else 'Sending'} emails",
            len(emails)
        )

        self.send_started.emit()

        # Start worker
        self._send_worker = SendWorker(
            self.outlook_sender,
            emails,
            self.checkpoint_manager,
            self.interval_spin.value(),
            preview_mode
        )
        self._send_worker.progress.connect(self._on_progress)
        self._send_worker.sending.connect(self._on_sending)
        self._send_worker.finished.connect(self._on_finished)
        self._send_worker.error.connect(self._on_error)
        self._send_worker.start()

    def _cancel_sending(self) -> None:
        """
        Cancel the send operation immediately.

        No confirmation dialog: every second spent reading one is another
        email going out, and a cancelled run is fully resumable.
        """
        if self._send_worker:
            self._send_worker.cancel()
            self.cancel_btn.setEnabled(False)
            self.progress_log.log_warning(
                "Cancelling — finishing the email currently being sent…"
            )
    
    def _resume_sending(self) -> None:
        """Resume an incomplete session, continuing its existing checkpoint."""
        success, msg, remaining = self.checkpoint_manager.resume_session()

        if not success:
            show_error(self, "Resume Failed", msg)
            return

        # Send only the rows the checkpoint says are still pending,
        # without starting a new checkpoint session
        remaining_set = set(remaining)
        resume_emails = [e for e in self._emails if e.row_index in remaining_set]

        if not resume_emails:
            self.checkpoint_manager.suspend_session()
            show_error(
                self,
                "Resume Failed",
                "The remaining recipients are not in the current email list.\n\n"
                "Reload the same Excel file and select the same recipients, "
                "then try Resume again."
            )
            return

        account_email = self.account_combo.currentData()
        if account_email:
            self.outlook_sender.select_account(account_email)

        self.progress_log.log_info(msg)
        self._launch_send(resume_emails)
    
    @pyqtSlot(int, int, str)
    def _on_sending(self, current: int, total: int, recipient: str) -> None:
        """Show the in-flight recipient while the send happens."""
        self.status_label.setText(f"Sending to {recipient} ({current}/{total})…")

    @pyqtSlot(int, int, str, bool, str)
    def _on_progress(self, current: int, total: int, email: str, success: bool, message: str) -> None:
        """Handle progress updates."""
        self.progress_log.set_progress(current, total)

        if success:
            self.progress_log.log_success(f"Sent to: {email}")
        else:
            self.progress_log.log_error(f"Failed: {email} - {message}")

        elapsed = time.monotonic() - getattr(self, '_send_started_at', time.monotonic())
        eta = format_eta(elapsed, current, total)
        suffix = f" — {eta}" if eta else ""
        self.status_label.setText(f"Sending: {current}/{total}{suffix}")

    @pyqtSlot(dict)
    def _on_finished(self, results: dict) -> None:
        """Handle send completion."""
        self._is_sending = False

        sent = results.get('sent', 0)
        failed = results.get('failed', 0)
        cancelled = results.get('cancelled', False)
        aborted_reason = results.get('aborted_reason', '')

        # A cancelled or self-aborted run stays resumable; only a run that
        # actually reached the end is finalized
        if cancelled or aborted_reason:
            self.checkpoint_manager.suspend_session()
        else:
            self.checkpoint_manager.complete_session(success=True)

        # Update UI
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.account_combo.setEnabled(True)
        self.interval_spin.setEnabled(True)
        self.preview_check.setEnabled(True)
        self.resume_btn.setVisible(False)

        self.progress_log.end_operation("Email sending", sent, failed)

        if cancelled:
            self.status_label.setText(f"Cancelled: {sent} sent, {failed} failed")
            self.progress_log.log_warning("Operation cancelled by user")
            self.resume_btn.setVisible(True)
        elif aborted_reason:
            self.status_label.setText(f"Stopped: {sent} sent, {failed} failed")
            self.progress_log.log_error(aborted_reason)
            self.resume_btn.setVisible(True)
            show_warning(self, "Sending Stopped", aborted_reason)
        else:
            self.status_label.setText(f"Complete: {sent} sent, {failed} failed")
            if failed == 0:
                show_info(self, "Complete", f"Successfully sent {sent} emails!")
            else:
                show_warning(
                    self,
                    "Complete with Errors",
                    f"Sent: {sent}\nFailed: {failed}\n\n"
                    f"Use 'Retry {failed} Failed' to send again to just "
                    f"those recipients."
                )

        # Failed rows can be retried on their own
        if failed > 0:
            failed_rows = set(self.checkpoint_manager.failed)
            retryable = [e for e in self._emails if e.row_index in failed_rows]
            if retryable:
                self.retry_btn.setText(f"↻ Retry {len(retryable)} Failed")
                self.retry_btn.setVisible(True)

        self.send_completed.emit(results)

    def _retry_failed(self) -> None:
        """Send again to only the recipients that failed in the last run."""
        failed_rows = set(self.checkpoint_manager.failed)
        retry_emails = [e for e in self._emails if e.row_index in failed_rows]

        if not retry_emails:
            show_error(self, "Nothing to Retry", "No failed recipients found.")
            self.retry_btn.setVisible(False)
            return

        account_email = self.account_combo.currentData()
        if account_email:
            self.outlook_sender.select_account(account_email)

        # Fresh checkpoint session covering just the failed rows
        self.checkpoint_manager.start_session(
            [e.row_index for e in retry_emails],
            sending_account=account_email or ""
        )

        self.progress_log.log_info(
            f"Retrying {len(retry_emails)} failed recipient(s)…"
        )
        self._launch_send(retry_emails)
    
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
