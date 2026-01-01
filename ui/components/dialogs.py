"""
Advanced Email Tool - Dialogs
============================
Common dialog boxes and popup windows.
Provides consistent UI for messages, file selection, and user input.
"""

from typing import Optional, Tuple, List
from PyQt5.QtWidgets import (
    QMessageBox, QFileDialog, QInputDialog, QDialog,
    QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QLineEdit, QTextEdit, QDialogButtonBox
)
from PyQt5.QtCore import Qt


def show_info(parent, title: str, message: str) -> None:
    """
    Show an information message box.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Message to display
    """
    QMessageBox.information(parent, title, message)


def show_warning(parent, title: str, message: str) -> None:
    """
    Show a warning message box.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Warning message
    """
    QMessageBox.warning(parent, title, message)


def show_error(parent, title: str, message: str) -> None:
    """
    Show an error message box.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Error message
    """
    QMessageBox.critical(parent, title, message)


def show_question(
    parent,
    title: str,
    message: str,
    buttons: QMessageBox.StandardButtons = None
) -> bool:
    """
    Show a yes/no question dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Question message
        buttons: Button configuration
        
    Returns:
        True if user clicked Yes
    """
    if buttons is None:
        buttons = QMessageBox.Yes | QMessageBox.No
    
    result = QMessageBox.question(parent, title, message, buttons)
    return result == QMessageBox.Yes


def show_question_cancel(
    parent,
    title: str,
    message: str
) -> Optional[bool]:
    """
    Show a yes/no/cancel question dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Question message
        
    Returns:
        True for Yes, False for No, None for Cancel
    """
    result = QMessageBox.question(
        parent, title, message,
        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
    )
    
    if result == QMessageBox.Yes:
        return True
    elif result == QMessageBox.No:
        return False
    else:
        return None


def show_file_dialog(
    parent,
    title: str = "Select File",
    filter: str = "All Files (*.*)",
    directory: str = ""
) -> Optional[str]:
    """
    Show a file open dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        filter: File type filter (e.g., "Excel Files (*.xlsx)")
        directory: Starting directory
        
    Returns:
        Selected file path or None if cancelled
    """
    file_path, _ = QFileDialog.getOpenFileName(
        parent, title, directory, filter
    )
    return file_path if file_path else None


def show_files_dialog(
    parent,
    title: str = "Select Files",
    filter: str = "All Files (*.*)",
    directory: str = ""
) -> List[str]:
    """
    Show a multi-file open dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        filter: File type filter
        directory: Starting directory
        
    Returns:
        List of selected file paths (empty if cancelled)
    """
    files, _ = QFileDialog.getOpenFileNames(
        parent, title, directory, filter
    )
    return files if files else []


def show_folder_dialog(
    parent,
    title: str = "Select Folder",
    directory: str = ""
) -> Optional[str]:
    """
    Show a folder selection dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        directory: Starting directory
        
    Returns:
        Selected folder path or None if cancelled
    """
    folder_path = QFileDialog.getExistingDirectory(
        parent, title, directory
    )
    return folder_path if folder_path else None


def show_save_dialog(
    parent,
    title: str = "Save File",
    filter: str = "All Files (*.*)",
    directory: str = "",
    default_name: str = ""
) -> Optional[str]:
    """
    Show a file save dialog.
    
    Args:
        parent: Parent widget
        title: Dialog title
        filter: File type filter
        directory: Starting directory
        default_name: Default filename
        
    Returns:
        Selected save path or None if cancelled
    """
    if default_name:
        import os
        directory = os.path.join(directory, default_name)
    
    file_path, _ = QFileDialog.getSaveFileName(
        parent, title, directory, filter
    )
    return file_path if file_path else None


class InputDialog(QDialog):
    """
    Custom input dialog with validation support.
    
    Provides a text input with optional validation.
    """
    
    def __init__(
        self,
        parent,
        title: str,
        label: str,
        default_value: str = "",
        placeholder: str = ""
    ):
        """
        Initialize input dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            label: Input label text
            default_value: Default input value
            placeholder: Placeholder text
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # Label
        self.label = QLabel(label)
        layout.addWidget(self.label)
        
        # Input field
        self.input = QLineEdit()
        self.input.setText(default_value)
        if placeholder:
            self.input.setPlaceholderText(placeholder)
        layout.addWidget(self.input)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.input.setFocus()
    
    def get_value(self) -> str:
        """Get the input value."""
        return self.input.text().strip()
    
    @staticmethod
    def get_text(
        parent,
        title: str,
        label: str,
        default_value: str = ""
    ) -> Tuple[str, bool]:
        """
        Static method to show dialog and get result.
        
        Returns:
            Tuple of (text, ok_pressed)
        """
        dialog = InputDialog(parent, title, label, default_value)
        result = dialog.exec_()
        return dialog.get_value(), result == QDialog.Accepted


class ProgressDialog(QDialog):
    """
    Progress dialog with cancel support.
    
    Shows a progress bar with status text and cancel button.
    """
    
    def __init__(
        self,
        parent,
        title: str,
        message: str = "",
        maximum: int = 100,
        cancelable: bool = True
    ):
        """
        Initialize progress dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Initial status message
            maximum: Maximum progress value
            cancelable: Whether cancel button is shown
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setModal(True)
        
        # Don't allow closing via X button
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowCloseButtonHint
        )
        
        self._cancelled = False
        
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel(message)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Detail label
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("color: gray;")
        layout.addWidget(self.detail_label)
        
        # Cancel button
        if cancelable:
            self.cancel_button = QPushButton("Cancel")
            self.cancel_button.clicked.connect(self._on_cancel)
            layout.addWidget(self.cancel_button, alignment=Qt.AlignRight)
        else:
            self.cancel_button = None
    
    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self._cancelled = True
        if self.cancel_button:
            self.cancel_button.setEnabled(False)
            self.cancel_button.setText("Cancelling...")
    
    def was_cancelled(self) -> bool:
        """Check if cancel was requested."""
        return self._cancelled
    
    def set_progress(self, value: int) -> None:
        """Set progress bar value."""
        self.progress_bar.setValue(value)
    
    def set_maximum(self, value: int) -> None:
        """Set progress bar maximum."""
        self.progress_bar.setMaximum(value)
    
    def set_status(self, message: str) -> None:
        """Set main status message."""
        self.status_label.setText(message)
    
    def set_detail(self, message: str) -> None:
        """Set detail message (smaller, gray text)."""
        self.detail_label.setText(message)
    
    def finish(self) -> None:
        """Close the dialog."""
        self.accept()


class MultiLineInputDialog(QDialog):
    """
    Dialog for multi-line text input.
    
    Useful for entering longer text like descriptions.
    """
    
    def __init__(
        self,
        parent,
        title: str,
        label: str,
        default_value: str = ""
    ):
        """
        Initialize multi-line input dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            label: Input label
            default_value: Default text
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Label
        self.label = QLabel(label)
        layout.addWidget(self.label)
        
        # Text edit
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(default_value)
        layout.addWidget(self.text_edit)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_value(self) -> str:
        """Get the text value."""
        return self.text_edit.toPlainText()
    
    @staticmethod
    def get_text(
        parent,
        title: str,
        label: str,
        default_value: str = ""
    ) -> Tuple[str, bool]:
        """
        Static method to show dialog and get result.
        
        Returns:
            Tuple of (text, ok_pressed)
        """
        dialog = MultiLineInputDialog(parent, title, label, default_value)
        result = dialog.exec_()
        return dialog.get_value(), result == QDialog.Accepted
