"""
Advanced Email Tool - Attachments Tab
=====================================
Tab for configuring static and variable (identifier-matched) attachments.
"""

from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QLineEdit, QCheckBox,
    QSplitter, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot

from ui.components.file_list import FileListWidget, MatchedFileListWidget
from ui.components.dialogs import show_error, show_info, show_folder_dialog, show_save_dialog
from core.attachment_matcher import AttachmentMatcher
from utils import get_logger, format_bytes

import config


class ScanWorker(QThread):
    """Background worker for scanning directories."""
    
    finished = pyqtSignal(int, str)  # count, message
    error = pyqtSignal(str)
    
    def __init__(self, matcher: AttachmentMatcher, extensions: List[str] = None):
        super().__init__()
        self.matcher = matcher
        self.extensions = extensions
    
    def run(self):
        try:
            count, msg = self.matcher.scan(self.extensions)
            self.finished.emit(count, msg)
        except Exception as e:
            self.error.emit(str(e))


class TabAttachments(QWidget):
    """
    Attachments configuration tab.
    
    Features:
    - Static attachments (sent to everyone)
    - Variable attachments (matched by identifier)
    - Folder scanning with progress
    - Match statistics and report generation
    """
    
    # Signals
    attachments_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the Attachments tab."""
        super().__init__(parent)
        
        self.logger = get_logger()
        self.attachment_matcher = AttachmentMatcher()
        self._identifiers: List[str] = []
        self._scan_worker: Optional[ScanWorker] = None
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Splitter for static and variable sections
        splitter = QSplitter(Qt.Horizontal)
        
        # Static attachments section
        static_group = QGroupBox("Static Attachments (sent to all recipients)")
        static_layout = QVBoxLayout(static_group)
        
        static_info = QLabel(
            "These files will be attached to every email.\n"
            "e.g., Cover letter, Instructions, Forms"
        )
        static_info.setStyleSheet("color: gray; font-size: 10px;")
        static_layout.addWidget(static_info)
        
        self.static_file_list = FileListWidget(
            title="Static Files",
            show_add_remove=True,
            show_size=True,
            file_filter=config.ALL_FILES_FILTER
        )
        self.static_file_list.files_changed.connect(self._on_attachments_changed)
        static_layout.addWidget(self.static_file_list)
        
        splitter.addWidget(static_group)
        
        # Variable attachments section
        variable_group = QGroupBox("Variable Attachments (matched by identifier)")
        variable_layout = QVBoxLayout(variable_group)
        
        variable_info = QLabel(
            "Files matched using the Identifier column from Excel.\n"
            "Exact substring match in filename (case-sensitive)."
        )
        variable_info.setStyleSheet("color: gray; font-size: 10px;")
        variable_layout.addWidget(variable_info)
        
        # Folder selection
        folder_layout = QHBoxLayout()
        
        folder_label = QLabel("Folder:")
        folder_layout.addWidget(folder_label)
        
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select folder containing client files...")
        self.folder_input.setReadOnly(True)
        folder_layout.addWidget(self.folder_input)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_folder)
        folder_layout.addWidget(self.browse_btn)
        
        variable_layout.addLayout(folder_layout)
        
        # Options row
        options_layout = QHBoxLayout()
        
        self.recursive_check = QCheckBox("Include subfolders")
        self.recursive_check.setChecked(False)
        options_layout.addWidget(self.recursive_check)
        
        options_layout.addStretch()
        
        self.scan_btn = QPushButton("Scan Folder")
        self.scan_btn.clicked.connect(self._scan_folder)
        self.scan_btn.setEnabled(False)
        options_layout.addWidget(self.scan_btn)
        
        variable_layout.addLayout(options_layout)
        
        # Scan progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        variable_layout.addWidget(self.progress_bar)
        
        # Scan status
        self.scan_status_label = QLabel("No folder selected")
        self.scan_status_label.setStyleSheet("color: gray;")
        variable_layout.addWidget(self.scan_status_label)
        
        # Match statistics
        stats_layout = QHBoxLayout()
        
        self.stats_label = QLabel("")
        stats_layout.addWidget(self.stats_label)
        
        stats_layout.addStretch()
        
        self.report_btn = QPushButton("Generate Report")
        self.report_btn.clicked.connect(self._generate_report)
        self.report_btn.setEnabled(False)
        stats_layout.addWidget(self.report_btn)
        
        variable_layout.addLayout(stats_layout)
        
        # Test matching section
        test_group = QGroupBox("Test Matching")
        test_layout = QVBoxLayout(test_group)
        
        test_input_layout = QHBoxLayout()
        
        self.test_input = QLineEdit()
        self.test_input.setPlaceholderText("Enter identifier to test...")
        test_input_layout.addWidget(self.test_input)
        
        self.test_btn = QPushButton("Test")
        self.test_btn.clicked.connect(self._test_matching)
        test_input_layout.addWidget(self.test_btn)
        
        test_layout.addLayout(test_input_layout)
        
        self.matched_files_list = MatchedFileListWidget()
        test_layout.addWidget(self.matched_files_list)
        
        variable_layout.addWidget(test_group)
        
        splitter.addWidget(variable_group)
        
        # Set splitter proportions
        splitter.setSizes([350, 450])
        
        layout.addWidget(splitter)
        
        # Size warning
        self.size_warning_label = QLabel("")
        self.size_warning_label.setStyleSheet("color: #fd7e14;")
        layout.addWidget(self.size_warning_label)
    
    def _browse_folder(self) -> None:
        """Open folder selection dialog."""
        folder = show_folder_dialog(self, "Select Attachments Folder")
        
        if folder:
            self.folder_input.setText(folder)
            self.folder_input.setToolTip(folder)
            
            success, error = self.attachment_matcher.set_directory(
                folder,
                self.recursive_check.isChecked()
            )
            
            if success:
                self.scan_btn.setEnabled(True)
                self.scan_status_label.setText("Folder selected. Click 'Scan Folder' to index files.")
            else:
                show_error(self, "Error", error)
                self.scan_btn.setEnabled(False)
    
    def _scan_folder(self) -> None:
        """Scan the selected folder for files."""
        if self._scan_worker and self._scan_worker.isRunning():
            return
        
        # Update recursive setting
        self.attachment_matcher.recursive = self.recursive_check.isChecked()
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.scan_btn.setEnabled(False)
        self.scan_status_label.setText("Scanning...")
        
        # Start worker thread
        self._scan_worker = ScanWorker(self.attachment_matcher)
        self._scan_worker.finished.connect(self._on_scan_finished)
        self._scan_worker.error.connect(self._on_scan_error)
        self._scan_worker.start()
    
    @pyqtSlot(int, str)
    def _on_scan_finished(self, count: int, message: str) -> None:
        """Handle scan completion."""
        self.progress_bar.setVisible(False)
        self.scan_btn.setEnabled(True)
        self.scan_status_label.setText(message)
        self.report_btn.setEnabled(count > 0)
        
        # Update match statistics if identifiers available
        if self._identifiers:
            self._update_match_statistics()
        
        self._on_attachments_changed()
    
    @pyqtSlot(str)
    def _on_scan_error(self, error: str) -> None:
        """Handle scan error."""
        self.progress_bar.setVisible(False)
        self.scan_btn.setEnabled(True)
        self.scan_status_label.setText(f"Error: {error}")
        show_error(self, "Scan Error", error)
    
    def _update_match_statistics(self) -> None:
        """Update match statistics display."""
        if not self._identifiers:
            self.stats_label.setText("")
            return
        
        stats = self.attachment_matcher.get_match_statistics(self._identifiers)
        
        matched = stats['matched_count']
        total = stats['total_identifiers']
        percent = stats['match_percentage']
        unmatched = stats['unmatched_count']
        
        if unmatched > 0:
            self.stats_label.setText(
                f"<b>{matched}/{total}</b> identifiers matched ({percent:.0f}%) | "
                f"<span style='color: #dc3545;'>{unmatched} unmatched</span>"
            )
        else:
            self.stats_label.setText(
                f"<b>{matched}/{total}</b> identifiers matched ({percent:.0f}%) ✓"
            )
    
    def _test_matching(self) -> None:
        """Test matching for entered identifier."""
        identifier = self.test_input.text().strip()
        if not identifier:
            show_error(self, "Error", "Please enter an identifier to test.")
            return
        
        if not self.attachment_matcher.total_files:
            show_error(self, "Error", "Please scan a folder first.")
            return
        
        matches = self.attachment_matcher.match_identifier(identifier)
        self.matched_files_list.set_matched_files(matches, identifier)
        
        if not matches:
            show_info(
                self,
                "No Matches",
                f"No files found containing '{identifier}' in filename."
            )
    
    def _generate_report(self) -> None:
        """Generate and save match report."""
        if not self._identifiers:
            show_error(self, "Error", "No identifiers available. Load Excel data first.")
            return
        
        save_path = show_save_dialog(
            self,
            "Save Match Report",
            "Excel Files (*.xlsx)",
            default_name="match_report.xlsx"
        )
        
        if save_path:
            report = self.attachment_matcher.generate_match_report(
                self._identifiers,
                save_path
            )
            show_info(self, "Report Generated", f"Match report saved to:\n{save_path}")
    
    def _on_attachments_changed(self) -> None:
        """Handle attachment configuration changes."""
        self._update_size_warning()
        self.attachments_changed.emit()
    
    def _update_size_warning(self) -> None:
        """Update attachment size warning."""
        static_size = self.static_file_list.get_total_size()
        
        if static_size > config.MAX_ATTACHMENT_SIZE_BYTES:
            self.size_warning_label.setText(
                f"⚠ Static attachments ({format_bytes(static_size)}) exceed "
                f"{config.MAX_ATTACHMENT_SIZE_MB}MB limit!"
            )
        elif static_size > config.MAX_ATTACHMENT_SIZE_BYTES * 0.8:
            self.size_warning_label.setText(
                f"⚠ Static attachments ({format_bytes(static_size)}) approaching "
                f"{config.MAX_ATTACHMENT_SIZE_MB}MB limit"
            )
        else:
            self.size_warning_label.setText("")
    
    def set_identifiers(self, identifiers: List[str]) -> None:
        """
        Set identifiers for matching statistics.
        
        Args:
            identifiers: List of identifier values from Excel
        """
        self._identifiers = [str(i).strip() for i in identifiers if i]
        
        if self.attachment_matcher.total_files > 0:
            self._update_match_statistics()
    
    def get_static_attachments(self) -> List[str]:
        """Get list of static attachment paths."""
        return self.static_file_list.get_files()
    
    def set_static_attachments(self, files: List[str]) -> None:
        """Set static attachment files."""
        self.static_file_list.set_files(files)
    
    def get_attachment_folder(self) -> Optional[str]:
        """Get the attachment folder path."""
        return self.attachment_matcher.directory
    
    def get_attachment_matcher(self) -> AttachmentMatcher:
        """Get the attachment matcher instance."""
        return self.attachment_matcher
    
    def is_recursive(self) -> bool:
        """Check if recursive scanning is enabled."""
        return self.recursive_check.isChecked()
    
    def set_folder(self, folder: str, recursive: bool = False) -> bool:
        """
        Set the attachment folder (for session restore).
        
        Args:
            folder: Folder path
            recursive: Whether to scan recursively
            
        Returns:
            True if successful
        """
        import os
        if not os.path.exists(folder):
            return False
        
        self.folder_input.setText(folder)
        self.recursive_check.setChecked(recursive)
        
        success, _ = self.attachment_matcher.set_directory(folder, recursive)
        if success:
            self.scan_btn.setEnabled(True)
            self._scan_folder()
            return True
        return False
