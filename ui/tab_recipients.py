"""
Advanced Email Tool - Recipients Tab
====================================
Tab for selecting which recipients to send emails to.
"""

from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from ui.components.recipient_list import RecipientListWidget
from ui.components.dialogs import show_error, show_info, show_warning, InputDialog
from ui.components.tab_navigation import TabNavigationBar
from data.recipient_lists import RecipientListStorage
from utils import get_logger


class TabRecipients(QWidget):
    """
    Recipient selection tab.
    
    Features:
    - View all recipients from Excel
    - Select/deselect recipients
    - Save/load recipient lists
    - Search and filter
    """
    
    # Signals
    selection_changed = pyqtSignal(int)  # Emits selected count
    navigate_previous = pyqtSignal()
    navigate_next = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize the Recipients tab."""
        super().__init__(parent)
        
        self.logger = get_logger()
        self.list_storage = RecipientListStorage()
        self._email_column: Optional[str] = None
        self._identifier_column: Optional[str] = None
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Saved lists management
        lists_layout = QHBoxLayout()
        
        lists_label = QLabel("Saved Lists:")
        lists_layout.addWidget(lists_label)
        
        self.lists_combo = QComboBox()
        self.lists_combo.setMinimumWidth(200)
        self.lists_combo.addItem("-- Select Saved List --")
        self._refresh_lists()
        lists_layout.addWidget(self.lists_combo)
        
        self.load_list_btn = QPushButton("Load")
        self.load_list_btn.clicked.connect(self._load_list)
        lists_layout.addWidget(self.load_list_btn)
        
        self.save_list_btn = QPushButton("Save Selection...")
        self.save_list_btn.clicked.connect(self._save_list)
        lists_layout.addWidget(self.save_list_btn)
        
        self.delete_list_btn = QPushButton("Delete")
        self.delete_list_btn.clicked.connect(self._delete_list)
        lists_layout.addWidget(self.delete_list_btn)
        
        lists_layout.addStretch()
        
        layout.addLayout(lists_layout)
        
        # Recipient list widget
        self.recipient_list = RecipientListWidget()
        self.recipient_list.selection_changed.connect(self._on_selection_changed)
        layout.addWidget(self.recipient_list, stretch=1)
        
        # Summary bar
        summary_layout = QHBoxLayout()
        
        self.summary_label = QLabel("No data loaded")
        self.summary_label.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self.summary_label)
        
        summary_layout.addStretch()
        
        # Quick selection buttons
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.recipient_list.select_all)
        summary_layout.addWidget(self.select_all_btn)
        
        self.select_none_btn = QPushButton("Clear Selection")
        self.select_none_btn.clicked.connect(self.recipient_list.select_none)
        summary_layout.addWidget(self.select_none_btn)

        layout.addLayout(summary_layout)

        # Navigation bar
        self.nav_bar = TabNavigationBar(show_previous=True, show_next=True)
        self.nav_bar.previous_clicked.connect(self.navigate_previous.emit)
        self.nav_bar.next_clicked.connect(self.navigate_next.emit)
        layout.addWidget(self.nav_bar)

    def _refresh_lists(self) -> None:
        """Refresh saved lists dropdown."""
        current = self.lists_combo.currentText()
        
        self.lists_combo.blockSignals(True)
        self.lists_combo.clear()
        self.lists_combo.addItem("-- Select Saved List --")
        
        lists = self.list_storage.list_all()
        for lst in lists:
            self.lists_combo.addItem(f"{lst['name']} ({lst['count']})")
        
        # Restore selection
        idx = self.lists_combo.findText(current)
        if idx >= 0:
            self.lists_combo.setCurrentIndex(idx)
        
        self.lists_combo.blockSignals(False)
    
    def _load_list(self) -> None:
        """Load selected saved list."""
        text = self.lists_combo.currentText()
        if text == "-- Select Saved List --":
            return

        # Extract name (remove count part)
        name = text.rsplit(" (", 1)[0]

        list_data = self.list_storage.load_list(name)
        if list_data is not None:
            # Match saved recipients by email so the list follows the same
            # clients even if rows moved in the Excel file
            current_emails = self._current_email_values()
            if current_emails:
                indices, missing = RecipientListStorage.resolve_selection(
                    list_data, current_emails
                )
            else:
                # No email column mapped — fall back to raw indices
                max_idx = self.recipient_list.get_total_count() - 1
                indices = [
                    i for i in list_data.get('selected_indices', [])
                    if 0 <= i <= max_idx
                ]
                missing = []

            if missing:
                shown = "\n".join(f"• {email}" for email in missing[:10])
                if len(missing) > 10:
                    shown += f"\n… and {len(missing) - 10} more"
                show_warning(
                    self,
                    "Partial Load",
                    f"{len(missing)} saved recipient(s) are not in the "
                    f"current Excel data and were skipped:\n\n{shown}"
                )

            self.recipient_list.set_selected_indices(indices)
            self.logger.info(f"Loaded list '{name}' with {len(indices)} recipients")
        else:
            show_error(self, "Error", f"Could not load list '{name}'.")

    def _current_email_values(self) -> List[str]:
        """Email value of every loaded row, in display order."""
        if not self._email_column:
            return []
        return [
            str(row.get(self._email_column, '') or '')
            for row in self.recipient_list.get_all_data()
        ]

    def _status_message(self, message: str) -> None:
        """Show a transient message in the main window's status bar."""
        status_bar = getattr(self.window(), 'status_bar', None)
        if status_bar is not None:
            status_bar.showMessage(message, 4000)
    
    def _save_list(self) -> None:
        """Save current selection as a list."""
        selected = self.recipient_list.get_selected_indices()
        if not selected:
            show_error(self, "Error", "No recipients selected to save.")
            return
        
        name, ok = InputDialog.get_text(
            self,
            "Save Recipient List",
            "Enter list name:",
            ""
        )
        
        if ok and name:
            if self.list_storage.list_exists(name):
                reply = QMessageBox.question(
                    self,
                    "Overwrite?",
                    f"List '{name}' already exists. Overwrite?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            
            # Store emails alongside indices so the list follows the same
            # clients even after the Excel file changes
            emails = None
            if self._email_column:
                emails = [
                    str(row.get(self._email_column, '') or '')
                    for row in self.recipient_list.get_selected_data()
                ]

            success, msg = self.list_storage.save_list(
                name, selected, recipient_emails=emails
            )

            if success:
                self._refresh_lists()
                self._status_message(f"List '{name}' saved with {len(selected)} recipients")
            else:
                show_error(self, "Error", msg)
    
    def _delete_list(self) -> None:
        """Delete selected saved list."""
        text = self.lists_combo.currentText()
        if text == "-- Select Saved List --":
            return
        
        name = text.rsplit(" (", 1)[0]
        
        reply = QMessageBox.question(
            self,
            "Delete List?",
            f"Are you sure you want to delete '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, msg = self.list_storage.delete_list(name)
            if success:
                self._refresh_lists()
                self.lists_combo.setCurrentIndex(0)
                self._status_message(f"List '{name}' deleted")
            else:
                show_error(self, "Error", msg)
    
    def _on_selection_changed(self, count: int) -> None:
        """Handle selection changes."""
        total = self.recipient_list.get_total_count()
        self.summary_label.setText(f"{count} of {total} recipients selected")
        self.selection_changed.emit(count)
    
    def set_data(
        self,
        data: List[Dict[str, Any]],
        columns: List[str],
        email_column: Optional[str] = None,
        identifier_column: Optional[str] = None,
        preserve_selection: bool = False
    ) -> None:
        """
        Set recipient data.

        Args:
            data: List of row dictionaries
            columns: List of column names
            email_column: Name of email column
            identifier_column: Name of identifier column
            preserve_selection: Keep the current selection when the rows are
                unchanged (used when only the column mapping changed).
                Falls back to select-all if the row count differs.
        """
        previous_count = self.recipient_list.get_total_count()
        previous_selection = self.recipient_list.get_selected_indices()

        self._email_column = email_column
        self._identifier_column = identifier_column

        self.recipient_list.set_data(
            data, columns, email_column, identifier_column
        )

        if preserve_selection and previous_count == len(data) and previous_count > 0:
            self.recipient_list.set_selected_indices(previous_selection)
        else:
            # Auto-select all by default
            self.recipient_list.select_all()

        self._update_summary()
    
    def _update_summary(self) -> None:
        """Update summary label."""
        selected = self.recipient_list.get_selected_count()
        total = self.recipient_list.get_total_count()
        self.summary_label.setText(f"{selected} of {total} recipients selected")
    
    def get_selected_indices(self) -> List[int]:
        """Get list of selected row indices."""
        return self.recipient_list.get_selected_indices()
    
    def get_selected_data(self) -> List[Dict[str, Any]]:
        """Get data for selected rows."""
        return self.recipient_list.get_selected_data()
    
    def get_selected_count(self) -> int:
        """Get count of selected recipients."""
        return self.recipient_list.get_selected_count()
    
    def set_selected_indices(self, indices: List[int]) -> None:
        """Set selected indices (for session restore)."""
        self.recipient_list.set_selected_indices(indices)
    
    def clear(self) -> None:
        """Clear all data."""
        self.recipient_list.clear()
        self.summary_label.setText("No data loaded")
