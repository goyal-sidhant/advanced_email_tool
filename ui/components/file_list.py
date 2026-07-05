"""
Advanced Email Tool - File List Widget
=====================================
Widget for displaying and managing lists of files.
Used for static attachments and matched file display.
"""

import os
from typing import List, Optional, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QListWidgetItem, QPushButton, QLabel, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

from utils import get_file_size_formatted, format_bytes


class FileListWidget(QWidget):
    """
    Widget for displaying a list of files.
    
    Features:
    - Add/remove files
    - Display file size
    - Context menu actions
    - Total size calculation
    - Drag and drop support (optional)
    """
    
    # Signals
    files_changed = pyqtSignal()  # Emitted when file list changes
    file_double_clicked = pyqtSignal(str)  # Emitted with file path
    
    def __init__(
        self,
        parent=None,
        title: str = "Files",
        show_add_remove: bool = True,
        show_size: bool = True,
        file_filter: str = "All Files (*.*)"
    ):
        """
        Initialize file list widget.
        
        Args:
            parent: Parent widget
            title: Widget title
            show_add_remove: Whether to show add/remove buttons
            show_size: Whether to show file sizes
            file_filter: File type filter for add dialog
        """
        super().__init__(parent)
        
        self._files: List[str] = []
        self._show_size = show_size
        self._file_filter = file_filter

        self._setup_ui(title, show_add_remove)

        # Files can be dragged in from Explorer
        self.setAcceptDrops(True)
    
    def _setup_ui(self, title: str, show_add_remove: bool) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel(f"<b>{title}</b>")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.count_label = QLabel("0 files")
        self.count_label.setStyleSheet("color: gray;")
        header_layout.addWidget(self.count_label)
        
        layout.addLayout(header_layout)
        
        # File list
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.list_widget.itemDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self.list_widget)
        
        # Size display
        if self._show_size:
            self.size_label = QLabel("Total: 0 B")
            self.size_label.setStyleSheet("color: gray;")
            layout.addWidget(self.size_label)
        
        # Buttons
        if show_add_remove:
            button_layout = QHBoxLayout()
            
            self.add_btn = QPushButton("Add Files...")
            self.add_btn.clicked.connect(self._add_files)
            button_layout.addWidget(self.add_btn)
            
            self.remove_btn = QPushButton("Remove")
            self.remove_btn.clicked.connect(self._remove_selected)
            self.remove_btn.setEnabled(False)
            button_layout.addWidget(self.remove_btn)
            
            button_layout.addStretch()
            
            self.clear_btn = QPushButton("Clear All")
            self.clear_btn.clicked.connect(self.clear)
            button_layout.addWidget(self.clear_btn)
            
            layout.addLayout(button_layout)
            
            # Connect selection change
            self.list_widget.itemSelectionChanged.connect(
                lambda: self.remove_btn.setEnabled(
                    len(self.list_widget.selectedItems()) > 0
                )
            )
    
    def _add_files(self) -> None:
        """Show file dialog to add files."""
        from ui.components.dialogs import show_files_dialog

        files = show_files_dialog(
            self,
            title="Select Files to Add",
            filter=self._file_filter,
            remember_key="attachment_files"
        )

        if files:
            self.add_files(files)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        """Add dropped files to the list."""
        import os

        paths = [
            url.toLocalFile()
            for url in event.mimeData().urls()
            if url.toLocalFile() and os.path.isfile(url.toLocalFile())
        ]
        if paths:
            event.acceptProposedAction()
            self.add_files(paths)
    
    def _remove_selected(self) -> None:
        """Remove selected files from list."""
        selected = self.list_widget.selectedItems()
        for item in selected:
            idx = self.list_widget.row(item)
            self.list_widget.takeItem(idx)
            if idx < len(self._files):
                del self._files[idx]
        
        self._update_counts()
        self.files_changed.emit()
    
    def _show_context_menu(self, position) -> None:
        """Show context menu at position."""
        item = self.list_widget.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        # Open file location
        open_action = QAction("Open File Location", self)
        open_action.triggered.connect(
            lambda: self._open_file_location(item.data(Qt.UserRole))
        )
        menu.addAction(open_action)
        
        # Copy path
        copy_action = QAction("Copy Path", self)
        copy_action.triggered.connect(
            lambda: self._copy_path(item.data(Qt.UserRole))
        )
        menu.addAction(copy_action)
        
        menu.addSeparator()
        
        # Remove
        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(self._remove_selected)
        menu.addAction(remove_action)
        
        menu.exec_(self.list_widget.mapToGlobal(position))
    
    def _open_file_location(self, path: str) -> None:
        """Open file location in explorer."""
        if not path:
            return
        
        import subprocess
        folder = os.path.dirname(path)
        if os.path.exists(folder):
            subprocess.Popen(f'explorer /select,"{path}"')
    
    def _copy_path(self, path: str) -> None:
        """Copy file path to clipboard."""
        if not path:
            return
        
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(path)
    
    def _on_double_click(self, item: QListWidgetItem) -> None:
        """Handle double-click on item."""
        path = item.data(Qt.UserRole)
        if path:
            self.file_double_clicked.emit(path)
    
    def _update_counts(self) -> None:
        """Update count and size labels."""
        count = len(self._files)
        self.count_label.setText(f"{count} file{'s' if count != 1 else ''}")
        
        if self._show_size:
            total_size = sum(
                os.path.getsize(f) for f in self._files
                if os.path.exists(f)
            )
            self.size_label.setText(f"Total: {format_bytes(total_size)}")
    
    def add_file(self, file_path: str) -> bool:
        """
        Add a single file to the list.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if added (False if already exists)
        """
        if file_path in self._files:
            return False
        
        self._files.append(file_path)
        self._add_list_item(file_path)
        self._update_counts()
        self.files_changed.emit()
        
        return True
    
    def add_files(self, file_paths: List[str]) -> int:
        """
        Add multiple files to the list.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            Number of files added
        """
        added = 0
        for path in file_paths:
            if path not in self._files:
                self._files.append(path)
                self._add_list_item(path)
                added += 1
        
        if added > 0:
            self._update_counts()
            self.files_changed.emit()
        
        return added
    
    def _add_list_item(self, file_path: str) -> None:
        """Add a list item for a file."""
        filename = os.path.basename(file_path)
        
        if self._show_size and os.path.exists(file_path):
            size = get_file_size_formatted(file_path)
            text = f"{filename}  ({size})"
        else:
            text = filename
        
        item = QListWidgetItem(text)
        item.setData(Qt.UserRole, file_path)
        item.setToolTip(file_path)
        
        # Color based on existence
        if not os.path.exists(file_path):
            item.setForeground(Qt.red)
        
        self.list_widget.addItem(item)
    
    def remove_file(self, file_path: str) -> bool:
        """
        Remove a file from the list.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if removed
        """
        if file_path not in self._files:
            return False
        
        idx = self._files.index(file_path)
        self._files.remove(file_path)
        self.list_widget.takeItem(idx)
        self._update_counts()
        self.files_changed.emit()
        
        return True
    
    def clear(self) -> None:
        """Clear all files from list."""
        self._files.clear()
        self.list_widget.clear()
        self._update_counts()
        self.files_changed.emit()
    
    def get_files(self) -> List[str]:
        """
        Get list of file paths.
        
        Returns:
            List of file paths
        """
        return self._files.copy()
    
    def set_files(self, file_paths: List[str]) -> None:
        """
        Set the file list (replaces existing).
        
        Args:
            file_paths: List of file paths
        """
        self._files.clear()
        self.list_widget.clear()
        
        for path in file_paths:
            self._files.append(path)
            self._add_list_item(path)
        
        self._update_counts()
        self.files_changed.emit()
    
    def get_total_size(self) -> int:
        """
        Get total size of all files in bytes.
        
        Returns:
            Total size in bytes
        """
        return sum(
            os.path.getsize(f) for f in self._files
            if os.path.exists(f)
        )
    
    def get_file_count(self) -> int:
        """
        Get number of files.
        
        Returns:
            File count
        """
        return len(self._files)
    
    def set_title(self, title: str) -> None:
        """
        Set the widget title.
        
        Args:
            title: New title
        """
        self.title_label.setText(f"<b>{title}</b>")


class MatchedFileListWidget(FileListWidget):
    """
    Specialized file list for showing matched attachments.
    
    Displays files matched by identifier with status indicators.
    """
    
    def __init__(self, parent=None):
        """Initialize matched file list widget."""
        super().__init__(
            parent,
            title="Matched Files",
            show_add_remove=False,
            show_size=True
        )
    
    def set_matched_files(
        self,
        matches: List[Tuple[str, str, int]],
        identifier: str = ""
    ) -> None:
        """
        Set matched files display.
        
        Args:
            matches: List of (full_path, filename, size) tuples
            identifier: The identifier used for matching
        """
        self._files.clear()
        self.list_widget.clear()
        
        if identifier:
            self.set_title(f"Matched Files for: {identifier}")
        
        for full_path, filename, size in matches:
            self._files.append(full_path)
            
            size_str = format_bytes(size)
            text = f"{filename}  ({size_str})"
            
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, full_path)
            item.setToolTip(full_path)
            
            self.list_widget.addItem(item)
        
        self._update_counts()
