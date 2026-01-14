"""
Advanced Email Tool - Recipient List Widget
==========================================
Widget for displaying and selecting email recipients from Excel data.
Supports filtering, selection, and saved list management.
"""

from typing import List, Dict, Any, Optional, Set
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QCheckBox, QComboBox, QHeaderView, QMenu, QAction,
    QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal


class RecipientListWidget(QWidget):
    """
    Widget for displaying and selecting recipients.
    
    Features:
    - Table view of recipient data
    - Search/filter functionality
    - Select all/none/invert
    - Save/load recipient lists
    - Column visibility toggle
    """
    
    # Signals
    selection_changed = pyqtSignal(int)  # Emits count of selected
    
    def __init__(self, parent=None):
        """Initialize recipient list widget."""
        super().__init__(parent)
        
        self._data: List[Dict[str, Any]] = []
        self._columns: List[str] = []
        self._email_column: str = ""
        self._identifier_column: str = ""
        self._selected_indices: Set[int] = set()
        self._filtered_indices: List[int] = []
        
        self._setup_ui()

    def _find_column(self, column_name: str) -> Optional[str]:
        """Find actual column name using case-insensitive match."""
        if not column_name:
            return None
        col_lower = column_name.lower()
        for col in self._columns:
            if col.lower() == col_lower:
                return col
        return None

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Search bar
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search recipients...")
        self.search_input.textChanged.connect(self._apply_filter)
        search_layout.addWidget(self.search_input)
        
        self.filter_column = QComboBox()
        self.filter_column.addItem("All Columns")
        self.filter_column.currentIndexChanged.connect(self._apply_filter)
        self.filter_column.setFixedWidth(150)
        search_layout.addWidget(self.filter_column)
        
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.table)
        
        # Selection controls
        controls_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all)
        controls_layout.addWidget(self.select_all_btn)
        
        self.select_none_btn = QPushButton("Select None")
        self.select_none_btn.clicked.connect(self.select_none)
        controls_layout.addWidget(self.select_none_btn)
        
        self.invert_btn = QPushButton("Invert")
        self.invert_btn.clicked.connect(self.invert_selection)
        controls_layout.addWidget(self.invert_btn)
        
        controls_layout.addStretch()
        
        self.selection_label = QLabel("0 of 0 selected")
        controls_layout.addWidget(self.selection_label)
        
        layout.addLayout(controls_layout)
    
    def set_data(
        self,
        data: List[Dict[str, Any]],
        columns: List[str],
        email_column: str = "",
        identifier_column: str = ""
    ) -> None:
        """
        Set the recipient data.
        
        Args:
            data: List of row dictionaries
            columns: List of column names
            email_column: Name of email column (for display priority)
            identifier_column: Name of identifier column
        """
        self._data = data
        self._columns = columns
        self._email_column = email_column
        self._identifier_column = identifier_column
        self._selected_indices = set()
        self._filtered_indices = list(range(len(data)))
        
        # Update filter column dropdown
        self.filter_column.clear()
        self.filter_column.addItem("All Columns")
        for col in columns:
            self.filter_column.addItem(col)
        
        self._rebuild_table()
        self._update_selection_label()
    
    def _rebuild_table(self) -> None:
        """Rebuild the table with current data and filters."""
        self.table.clear()
        self.table.setRowCount(0)
        
        if not self._data:
            return
        
        # Determine visible columns (prioritize email and identifier)
        visible_columns = self._get_visible_columns()
        
        # Set up columns (+1 for checkbox)
        self.table.setColumnCount(len(visible_columns) + 1)
        
        headers = [""] + visible_columns
        self.table.setHorizontalHeaderLabels(headers)
        
        # Set checkbox column width
        self.table.setColumnWidth(0, 30)
        
        # Add rows
        self.table.setRowCount(len(self._filtered_indices))
        
        for row_idx, data_idx in enumerate(self._filtered_indices):
            row_data = self._data[data_idx]
            
            # Checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(data_idx in self._selected_indices)
            checkbox.stateChanged.connect(
                lambda state, idx=data_idx: self._on_checkbox_changed(idx, state)
            )
            self.table.setCellWidget(row_idx, 0, checkbox)
            
            # Data columns
            for col_idx, col_name in enumerate(visible_columns):
                value = str(row_data.get(col_name, ""))
                item = QTableWidgetItem(value)
                item.setData(Qt.UserRole, data_idx)  # Store original index
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, col_idx + 1, item)
        
        # Resize columns to content
        self.table.resizeColumnsToContents()
    
    def _get_visible_columns(self) -> List[str]:
        """Get columns to display (prioritize important ones)."""
        visible = []

        # Prioritize email and identifier columns (case-insensitive)
        actual_email = self._find_column(self._email_column)
        if actual_email:
            visible.append(actual_email)

        actual_identifier = self._find_column(self._identifier_column)
        if actual_identifier and actual_identifier not in visible:
            visible.append(actual_identifier)

        # Add remaining columns (up to 5 total)
        for col in self._columns:
            if col not in visible and len(visible) < 5:
                visible.append(col)

        return visible
    
    def _on_checkbox_changed(self, data_idx: int, state: int) -> None:
        """Handle checkbox state change."""
        if state == Qt.Checked:
            self._selected_indices.add(data_idx)
        else:
            self._selected_indices.discard(data_idx)
        
        self._update_selection_label()
        self.selection_changed.emit(len(self._selected_indices))
    
    def _apply_filter(self) -> None:
        """Apply search filter to the table."""
        search_text = self.search_input.text().lower().strip()
        filter_col = self.filter_column.currentText()
        
        if not search_text:
            self._filtered_indices = list(range(len(self._data)))
        else:
            self._filtered_indices = []
            
            for idx, row in enumerate(self._data):
                if filter_col == "All Columns":
                    # Search all columns
                    match = any(
                        search_text in str(v).lower()
                        for v in row.values()
                    )
                else:
                    # Search specific column
                    match = search_text in str(row.get(filter_col, "")).lower()
                
                if match:
                    self._filtered_indices.append(idx)
        
        self._rebuild_table()
        self._update_selection_label()
    
    def _update_selection_label(self) -> None:
        """Update the selection count label."""
        selected = len(self._selected_indices)
        total = len(self._data)
        filtered = len(self._filtered_indices)
        
        if filtered == total:
            self.selection_label.setText(f"{selected} of {total} selected")
        else:
            self.selection_label.setText(
                f"{selected} of {total} selected (showing {filtered})"
            )
    
    def _show_context_menu(self, position) -> None:
        """Show context menu."""
        menu = QMenu(self)
        
        select_visible = QAction("Select All Visible", self)
        select_visible.triggered.connect(self._select_visible)
        menu.addAction(select_visible)
        
        deselect_visible = QAction("Deselect All Visible", self)
        deselect_visible.triggered.connect(self._deselect_visible)
        menu.addAction(deselect_visible)
        
        menu.addSeparator()
        
        copy_emails = QAction("Copy Selected Emails", self)
        copy_emails.triggered.connect(self._copy_selected_emails)
        menu.addAction(copy_emails)
        
        menu.exec_(self.table.mapToGlobal(position))
    
    def _select_visible(self) -> None:
        """Select all visible (filtered) rows."""
        for idx in self._filtered_indices:
            self._selected_indices.add(idx)
        
        self._rebuild_table()
        self._update_selection_label()
        self.selection_changed.emit(len(self._selected_indices))
    
    def _deselect_visible(self) -> None:
        """Deselect all visible (filtered) rows."""
        for idx in self._filtered_indices:
            self._selected_indices.discard(idx)
        
        self._rebuild_table()
        self._update_selection_label()
        self.selection_changed.emit(len(self._selected_indices))
    
    def _copy_selected_emails(self) -> None:
        """Copy selected email addresses to clipboard."""
        if not self._email_column:
            return
        
        emails = []
        for idx in self._selected_indices:
            email = str(self._data[idx].get(self._email_column, ""))
            if email:
                emails.append(email)
        
        if emails:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText("; ".join(emails))
    
    def select_all(self) -> None:
        """Select all recipients."""
        self._selected_indices = set(range(len(self._data)))
        self._rebuild_table()
        self._update_selection_label()
        self.selection_changed.emit(len(self._selected_indices))
    
    def select_none(self) -> None:
        """Deselect all recipients."""
        self._selected_indices.clear()
        self._rebuild_table()
        self._update_selection_label()
        self.selection_changed.emit(0)
    
    def invert_selection(self) -> None:
        """Invert the current selection."""
        all_indices = set(range(len(self._data)))
        self._selected_indices = all_indices - self._selected_indices
        self._rebuild_table()
        self._update_selection_label()
        self.selection_changed.emit(len(self._selected_indices))
    
    def get_selected_indices(self) -> List[int]:
        """
        Get list of selected row indices.
        
        Returns:
            List of selected indices (0-based)
        """
        return sorted(list(self._selected_indices))
    
    def set_selected_indices(self, indices: List[int]) -> None:
        """
        Set the selected indices.
        
        Args:
            indices: List of indices to select
        """
        self._selected_indices = set(indices)
        self._rebuild_table()
        self._update_selection_label()
        self.selection_changed.emit(len(self._selected_indices))
    
    def get_selected_data(self) -> List[Dict[str, Any]]:
        """
        Get data for selected rows.
        
        Returns:
            List of row dictionaries
        """
        return [self._data[i] for i in sorted(self._selected_indices)]
    
    def get_selected_count(self) -> int:
        """
        Get count of selected recipients.
        
        Returns:
            Number of selected recipients
        """
        return len(self._selected_indices)
    
    def get_total_count(self) -> int:
        """
        Get total recipient count.
        
        Returns:
            Total number of recipients
        """
        return len(self._data)
    
    def clear(self) -> None:
        """Clear all data and selections."""
        self._data = []
        self._columns = []
        self._selected_indices.clear()
        self._filtered_indices = []
        self.table.clear()
        self.table.setRowCount(0)
        self.search_input.clear()
        self._update_selection_label()
