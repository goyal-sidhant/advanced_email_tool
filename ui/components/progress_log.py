"""
Advanced Email Tool - Progress Log Widget
=========================================
Real-time log display for send operations.
Shows timestamped status messages with color coding.
"""

from datetime import datetime
from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat


class ProgressLog(QWidget):
    """
    Widget for displaying real-time progress logs.
    
    Features:
    - Timestamped log entries
    - Color-coded status (success/warning/error)
    - Auto-scroll with manual override
    - Copy and clear functionality
    - Progress summary bar
    """
    
    # Signals
    log_added = pyqtSignal(str)  # Emitted when new log entry added
    
    def __init__(self, parent=None):
        """Initialize the progress log widget."""
        super().__init__(parent)
        self._setup_ui()
        self._auto_scroll = True
        self._entry_count = 0
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Summary bar
        summary_layout = QHBoxLayout()
        
        self.summary_label = QLabel("Ready")
        summary_layout.addWidget(self.summary_label)
        
        summary_layout.addStretch()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setVisible(False)
        summary_layout.addWidget(self.progress_bar)
        
        layout.addLayout(summary_layout)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(self._get_monospace_font())
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)
        layout.addWidget(self.log_text)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.auto_scroll_btn = QPushButton("Auto-scroll: ON")
        self.auto_scroll_btn.setCheckable(True)
        self.auto_scroll_btn.setChecked(True)
        self.auto_scroll_btn.clicked.connect(self._toggle_auto_scroll)
        button_layout.addWidget(self.auto_scroll_btn)
        
        button_layout.addStretch()
        
        self.copy_btn = QPushButton("Copy Log")
        self.copy_btn.clicked.connect(self._copy_log)
        button_layout.addWidget(self.copy_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear)
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
    
    def _get_monospace_font(self):
        """Get a monospace font for the log."""
        from PyQt5.QtGui import QFont
        font = QFont("Consolas", 9)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
        return font
    
    def _toggle_auto_scroll(self) -> None:
        """Toggle auto-scroll behavior."""
        self._auto_scroll = self.auto_scroll_btn.isChecked()
        self.auto_scroll_btn.setText(
            f"Auto-scroll: {'ON' if self._auto_scroll else 'OFF'}"
        )
    
    def _copy_log(self) -> None:
        """Copy log contents to clipboard."""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.log_text.toPlainText())
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        return datetime.now().strftime("[%H:%M:%S]")
    
    def _append_colored(self, text: str, color: QColor) -> None:
        """Append colored text to the log."""
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Set color format
        format = QTextCharFormat()
        format.setForeground(color)
        
        cursor.insertText(text + "\n", format)
        
        # Auto-scroll if enabled
        if self._auto_scroll:
            self.log_text.setTextCursor(cursor)
            self.log_text.ensureCursorVisible()
        
        self._entry_count += 1
        self.log_added.emit(text)
    
    def log(self, message: str) -> None:
        """
        Add a regular log entry.
        
        Args:
            message: Log message
        """
        text = f"{self._get_timestamp()} {message}"
        self._append_colored(text, QColor("#333333"))
    
    def log_success(self, message: str) -> None:
        """
        Add a success log entry (green).
        
        Args:
            message: Success message
        """
        text = f"{self._get_timestamp()} ✓ {message}"
        self._append_colored(text, QColor("#28a745"))
    
    def log_warning(self, message: str) -> None:
        """
        Add a warning log entry (orange).
        
        Args:
            message: Warning message
        """
        text = f"{self._get_timestamp()} ⚠ {message}"
        self._append_colored(text, QColor("#fd7e14"))
    
    def log_error(self, message: str) -> None:
        """
        Add an error log entry (red).
        
        Args:
            message: Error message
        """
        text = f"{self._get_timestamp()} ✗ {message}"
        self._append_colored(text, QColor("#dc3545"))
    
    def log_info(self, message: str) -> None:
        """
        Add an info log entry (blue).
        
        Args:
            message: Info message
        """
        text = f"{self._get_timestamp()} ℹ {message}"
        self._append_colored(text, QColor("#007bff"))
    
    def set_summary(self, text: str) -> None:
        """
        Set the summary label text.
        
        Args:
            text: Summary text
        """
        self.summary_label.setText(text)
    
    def set_progress(self, current: int, total: int) -> None:
        """
        Set progress bar values.
        
        Args:
            current: Current progress value
            total: Total/maximum value
        """
        if not self.progress_bar.isVisible():
            self.progress_bar.setVisible(True)
        
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        
        # Update summary
        percent = (current / total * 100) if total > 0 else 0
        self.set_summary(f"Progress: {current}/{total} ({percent:.0f}%)")
    
    def hide_progress(self) -> None:
        """Hide the progress bar."""
        self.progress_bar.setVisible(False)
    
    def clear(self) -> None:
        """Clear all log entries."""
        self.log_text.clear()
        self._entry_count = 0
        self.set_summary("Ready")
        self.hide_progress()
    
    def get_log_text(self) -> str:
        """
        Get all log text.
        
        Returns:
            Complete log as string
        """
        return self.log_text.toPlainText()
    
    def get_entry_count(self) -> int:
        """
        Get number of log entries.
        
        Returns:
            Entry count
        """
        return self._entry_count
    
    def start_operation(self, operation_name: str, total: int = 0) -> None:
        """
        Mark the start of an operation.
        
        Args:
            operation_name: Name of the operation
            total: Total items (for progress bar)
        """
        self.log_info(f"Starting: {operation_name}")
        if total > 0:
            self.set_progress(0, total)
        else:
            self.set_summary(f"Running: {operation_name}")
    
    def end_operation(
        self,
        operation_name: str,
        success_count: int = 0,
        fail_count: int = 0
    ) -> None:
        """
        Mark the end of an operation.
        
        Args:
            operation_name: Name of the operation
            success_count: Number of successful items
            fail_count: Number of failed items
        """
        total = success_count + fail_count
        
        if fail_count == 0:
            self.log_success(
                f"Completed: {operation_name} ({success_count} successful)"
            )
        else:
            self.log_warning(
                f"Completed: {operation_name} "
                f"({success_count} successful, {fail_count} failed)"
            )
        
        self.set_summary(f"Done: {success_count}/{total}")
        self.hide_progress()
