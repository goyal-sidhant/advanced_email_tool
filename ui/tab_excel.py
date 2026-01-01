"""
Advanced Email Tool - Excel Tab
===============================
Tab for loading Excel files and mapping columns to email fields.
"""

from typing import Optional, Dict, List, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog,
    QMessageBox, QSplitter, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal

from core.excel_handler import ExcelHandler
from ui.components.dialogs import show_error, show_info, show_file_dialog
from utils import get_logger

import config


class TabExcel(QWidget):
    """
    Excel file loading and column mapping tab.
    
    Features:
    - Load Excel file
    - Select worksheet
    - Preview data
    - Map columns to email fields (To, CC, BCC, Identifier)
    """
    
    # Signals
    data_loaded = pyqtSignal(list, list)  # Emits (columns, data)
    mapping_changed = pyqtSignal(dict)  # Emits column mapping
    
    def __init__(self, parent=None):
        """Initialize the Excel tab."""
        super().__init__(parent)
        
        self.logger = get_logger()
        self.excel_handler = ExcelHandler()
        self._file_path: Optional[str] = None
        self._columns: List[str] = []
        self._data: List[Dict[str, Any]] = []
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # File selection section
        file_group = QGroupBox("Excel File")
        file_layout = QVBoxLayout(file_group)
        
        # File path row
        path_layout = QHBoxLayout()
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: gray;")
        path_layout.addWidget(self.file_label, stretch=1)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_file)
        path_layout.addWidget(self.browse_btn)
        
        self.reload_btn = QPushButton("Reload")
        self.reload_btn.clicked.connect(self._reload_file)
        self.reload_btn.setEnabled(False)
        path_layout.addWidget(self.reload_btn)
        
        file_layout.addLayout(path_layout)
        
        # Sheet selection row
        sheet_layout = QHBoxLayout()
        
        sheet_label = QLabel("Worksheet:")
        sheet_layout.addWidget(sheet_label)
        
        self.sheet_combo = QComboBox()
        self.sheet_combo.setMinimumWidth(200)
        self.sheet_combo.currentIndexChanged.connect(self._on_sheet_changed)
        self.sheet_combo.setEnabled(False)
        sheet_layout.addWidget(self.sheet_combo)
        
        sheet_layout.addStretch()
        
        self.row_count_label = QLabel("")
        self.row_count_label.setStyleSheet("color: gray;")
        sheet_layout.addWidget(self.row_count_label)
        
        file_layout.addLayout(sheet_layout)
        
        layout.addWidget(file_group)
        
        # Splitter for mapping and preview
        splitter = QSplitter(Qt.Horizontal)
        
        # Column mapping section
        mapping_group = QGroupBox("Column Mapping")
        mapping_layout = QVBoxLayout(mapping_group)
        
        mapping_info = QLabel(
            "Map Excel columns to email fields.\n"
            "Only 'To Email' is required."
        )
        mapping_info.setStyleSheet("color: gray; font-size: 10px;")
        mapping_layout.addWidget(mapping_info)
        
        # To Email (required)
        to_layout = QHBoxLayout()
        to_label = QLabel("To Email *:")
        to_label.setFixedWidth(100)
        to_layout.addWidget(to_label)
        self.to_combo = QComboBox()
        self.to_combo.currentIndexChanged.connect(self._on_mapping_changed)
        to_layout.addWidget(self.to_combo)
        mapping_layout.addLayout(to_layout)
        
        # CC (optional)
        cc_layout = QHBoxLayout()
        cc_label = QLabel("CC:")
        cc_label.setFixedWidth(100)
        cc_layout.addWidget(cc_label)
        self.cc_combo = QComboBox()
        self.cc_combo.currentIndexChanged.connect(self._on_mapping_changed)
        cc_layout.addWidget(self.cc_combo)
        mapping_layout.addLayout(cc_layout)
        
        # BCC (optional)
        bcc_layout = QHBoxLayout()
        bcc_label = QLabel("BCC:")
        bcc_label.setFixedWidth(100)
        bcc_layout.addWidget(bcc_label)
        self.bcc_combo = QComboBox()
        self.bcc_combo.currentIndexChanged.connect(self._on_mapping_changed)
        bcc_layout.addWidget(self.bcc_combo)
        mapping_layout.addLayout(bcc_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #ddd;")
        mapping_layout.addWidget(separator)
        
        # Identifier (for attachment matching)
        id_layout = QHBoxLayout()
        id_label = QLabel("Identifier:")
        id_label.setFixedWidth(100)
        id_layout.addWidget(id_label)
        self.identifier_combo = QComboBox()
        self.identifier_combo.currentIndexChanged.connect(self._on_mapping_changed)
        id_layout.addWidget(self.identifier_combo)
        mapping_layout.addLayout(id_layout)
        
        id_help = QLabel(
            "Used to match files to recipients.\n"
            "e.g., Client Code, PAN, GSTIN"
        )
        id_help.setStyleSheet("color: gray; font-size: 10px;")
        mapping_layout.addWidget(id_help)
        
        mapping_layout.addStretch()
        
        # Validation button
        self.validate_btn = QPushButton("Validate Emails")
        self.validate_btn.clicked.connect(self._validate_emails)
        self.validate_btn.setEnabled(False)
        mapping_layout.addWidget(self.validate_btn)
        
        splitter.addWidget(mapping_group)
        
        # Data preview section
        preview_group = QGroupBox("Data Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.preview_table.horizontalHeader().setStretchLastSection(True)
        preview_layout.addWidget(self.preview_table)
        
        splitter.addWidget(preview_group)
        
        # Set splitter proportions
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter, stretch=1)
    
    def _browse_file(self) -> None:
        """Open file dialog to select Excel file."""
        file_path = show_file_dialog(
            self,
            title="Select Excel File",
            filter=config.EXCEL_FILTER
        )
        
        if file_path:
            self._load_file(file_path)
    
    def _load_file(self, file_path: str) -> None:
        """
        Load an Excel file.
        
        Args:
            file_path: Path to Excel file
        """
        self.logger.info(f"Loading file: {file_path}")
        
        success, error = self.excel_handler.load_file(file_path)
        
        if not success:
            show_error(self, "Error Loading File", error)
            return
        
        self._file_path = file_path
        self._update_ui_after_load()
    
    def _update_ui_after_load(self) -> None:
        """Update UI after successful file load."""
        # Update file label
        import os
        filename = os.path.basename(self._file_path)
        self.file_label.setText(filename)
        self.file_label.setToolTip(self._file_path)
        self.file_label.setStyleSheet("")
        
        # Update sheet combo
        sheets = self.excel_handler.get_sheet_names()
        self.sheet_combo.blockSignals(True)
        self.sheet_combo.clear()
        self.sheet_combo.addItems(sheets)
        self.sheet_combo.blockSignals(False)
        self.sheet_combo.setEnabled(True)
        
        # Enable buttons
        self.reload_btn.setEnabled(True)
        self.validate_btn.setEnabled(True)
        
        # Load data from first sheet
        self._load_sheet_data()
    
    def _on_sheet_changed(self, index: int) -> None:
        """Handle worksheet selection change."""
        if index < 0 or not self._file_path:
            return
        
        sheet_name = self.sheet_combo.currentText()
        success, error = self.excel_handler.load_file(self._file_path, sheet_name)
        
        if success:
            self._load_sheet_data()
        else:
            show_error(self, "Error Loading Sheet", error)
    
    def _load_sheet_data(self) -> None:
        """Load data from current sheet and update UI."""
        self._columns = self.excel_handler.get_columns()
        self._data = self.excel_handler.get_data(filtered=False)
        
        # Update row count
        count = len(self._data)
        self.row_count_label.setText(f"{count} row{'s' if count != 1 else ''}")
        
        # Update column mappings
        self._populate_column_combos()
        
        # Update preview table
        self._populate_preview_table()
        
        # Emit signal
        self.data_loaded.emit(self._columns, self._data)
    
    def _populate_column_combos(self) -> None:
        """Populate column mapping dropdowns."""
        # Block signals during population
        combos = [self.to_combo, self.cc_combo, self.bcc_combo, self.identifier_combo]
        for combo in combos:
            combo.blockSignals(True)
            combo.clear()
        
        # Add empty option for optional fields
        self.cc_combo.addItem("-- None --")
        self.bcc_combo.addItem("-- None --")
        self.identifier_combo.addItem("-- None --")
        
        # Add columns
        for col in self._columns:
            for combo in combos:
                combo.addItem(col)
        
        # Auto-detect email column
        self._auto_detect_columns()
        
        # Unblock signals
        for combo in combos:
            combo.blockSignals(False)
        
        # Trigger mapping changed
        self._on_mapping_changed()
    
    def _auto_detect_columns(self) -> None:
        """Try to auto-detect column mappings based on names."""
        columns_lower = {col.lower(): col for col in self._columns}
        
        # Detect email column
        email_patterns = ['email', 'e-mail', 'mail', 'to', 'recipient']
        for pattern in email_patterns:
            for col_lower, col in columns_lower.items():
                if pattern in col_lower:
                    idx = self._columns.index(col)
                    self.to_combo.setCurrentIndex(idx)
                    break
            else:
                continue
            break
        
        # Detect identifier column
        id_patterns = ['identifier', 'id', 'code', 'pan', 'gstin', 'client']
        for pattern in id_patterns:
            for col_lower, col in columns_lower.items():
                if pattern in col_lower:
                    idx = self._columns.index(col) + 1  # +1 for "-- None --"
                    self.identifier_combo.setCurrentIndex(idx)
                    break
            else:
                continue
            break
    
    def _populate_preview_table(self, max_rows: int = 100) -> None:
        """
        Populate the preview table with data.
        
        Args:
            max_rows: Maximum rows to show in preview
        """
        self.preview_table.clear()
        
        if not self._data:
            self.preview_table.setRowCount(0)
            self.preview_table.setColumnCount(0)
            return
        
        # Set up columns
        self.preview_table.setColumnCount(len(self._columns))
        self.preview_table.setHorizontalHeaderLabels(self._columns)
        
        # Limit rows for preview
        preview_data = self._data[:max_rows]
        self.preview_table.setRowCount(len(preview_data))
        
        # Populate cells
        for row_idx, row_data in enumerate(preview_data):
            for col_idx, col_name in enumerate(self._columns):
                value = str(row_data.get(col_name, ""))
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.preview_table.setItem(row_idx, col_idx, item)
        
        # Resize columns to content
        self.preview_table.resizeColumnsToContents()
    
    def _on_mapping_changed(self) -> None:
        """Handle column mapping changes."""
        mapping = self.get_column_mapping()
        self.mapping_changed.emit(mapping)
    
    def _validate_emails(self) -> None:
        """Validate email addresses in the mapped column."""
        email_column = self.to_combo.currentText()
        if not email_column:
            show_error(self, "Validation Error", "Please select an email column first.")
            return
        
        issues_idx, issues_msg = self.excel_handler.validate_email_column(email_column)
        
        if not issues_msg:
            show_info(
                self,
                "Validation Complete",
                f"All {len(self._data)} email addresses are valid!"
            )
        else:
            # Show issues (limit to first 20)
            display_issues = issues_msg[:20]
            if len(issues_msg) > 20:
                display_issues.append(f"... and {len(issues_msg) - 20} more issues")
            
            QMessageBox.warning(
                self,
                "Email Validation Issues",
                f"Found {len(issues_msg)} issue(s):\n\n" + "\n".join(display_issues)
            )
    
    def _reload_file(self) -> None:
        """Reload the current file."""
        if self._file_path:
            self._load_file(self._file_path)
    
    def get_column_mapping(self) -> Dict[str, Optional[str]]:
        """
        Get the current column mapping.
        
        Returns:
            Dictionary with mapping for each field
        """
        def get_value(combo: QComboBox) -> Optional[str]:
            text = combo.currentText()
            if text and text != "-- None --":
                return text
            return None
        
        return {
            'to': get_value(self.to_combo),
            'cc': get_value(self.cc_combo),
            'bcc': get_value(self.bcc_combo),
            'identifier': get_value(self.identifier_combo),
        }
    
    def set_column_mapping(self, mapping: Dict[str, Optional[str]]) -> None:
        """
        Set the column mapping.
        
        Args:
            mapping: Dictionary with column mappings
        """
        def set_combo(combo: QComboBox, value: Optional[str], has_none: bool = False):
            if value and value in self._columns:
                idx = combo.findText(value)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            elif has_none:
                combo.setCurrentIndex(0)  # "-- None --"
        
        set_combo(self.to_combo, mapping.get('to'))
        set_combo(self.cc_combo, mapping.get('cc'), has_none=True)
        set_combo(self.bcc_combo, mapping.get('bcc'), has_none=True)
        set_combo(self.identifier_combo, mapping.get('identifier'), has_none=True)
    
    def get_columns(self) -> List[str]:
        """
        Get list of column names.
        
        Returns:
            List of column names
        """
        return self._columns.copy()
    
    def get_data(self) -> List[Dict[str, Any]]:
        """
        Get the loaded data.
        
        Returns:
            List of row dictionaries
        """
        return self._data.copy()
    
    def get_excel_handler(self) -> ExcelHandler:
        """
        Get the Excel handler instance.
        
        Returns:
            ExcelHandler instance
        """
        return self.excel_handler
    
    def get_file_path(self) -> Optional[str]:
        """
        Get the loaded file path.
        
        Returns:
            File path or None
        """
        return self._file_path
    
    def is_data_loaded(self) -> bool:
        """
        Check if data is loaded.
        
        Returns:
            True if data is loaded
        """
        return len(self._data) > 0
    
    def load_file_path(self, file_path: str) -> bool:
        """
        Load a specific file path (for session restore).
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            True if loaded successfully
        """
        import os
        if os.path.exists(file_path):
            self._load_file(file_path)
            return self.is_data_loaded()
        return False
