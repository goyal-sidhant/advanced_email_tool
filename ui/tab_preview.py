"""
Advanced Email Tool - Preview Tab
=================================
Tab for previewing emails before sending.
Shows how each email will look with data substituted.
"""

from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QComboBox, QTextBrowser,
    QSplitter, QListWidget, QListWidgetItem, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal

from ui.components.file_list import MatchedFileListWidget
from ui.components.variable_completer import LineEditCompleter
from ui.components.tab_navigation import TabNavigationBar
from core.template_engine import TemplateEngine
from core.email_builder import EmailBuilder
from utils import get_logger, format_bytes


class TabPreview(QWidget):
    """
    Email preview tab.

    Features:
    - Preview email for each recipient
    - Navigate between recipients
    - View substituted subject and body
    - View attachments per recipient
    - Validate before sending
    """

    # Signals
    navigate_previous = pyqtSignal()
    navigate_next = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize the Preview tab."""
        super().__init__(parent)
        
        self.logger = get_logger()
        self.template_engine = TemplateEngine()
        self._data: List[Dict[str, Any]] = []
        self._selected_indices: List[int] = []
        self._email_builder: Optional[EmailBuilder] = None
        self._current_index: int = 0
        self._columns: List[str] = []
        self._email_column: str = ""
        self._name_column: Optional[str] = None
        self._identifier_column: Optional[str] = None
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Navigation bar
        nav_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.clicked.connect(self._prev_recipient)
        nav_layout.addWidget(self.prev_btn)
        
        self.recipient_combo = QComboBox()
        self.recipient_combo.setMinimumWidth(300)
        self.recipient_combo.currentIndexChanged.connect(self._on_recipient_selected)
        nav_layout.addWidget(self.recipient_combo, stretch=1)
        
        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self._next_recipient)
        nav_layout.addWidget(self.next_btn)
        
        nav_layout.addSpacing(20)
        
        self.position_label = QLabel("0 / 0")
        nav_layout.addWidget(self.position_label)
        
        layout.addLayout(nav_layout)
        
        # Display format row
        format_layout = QHBoxLayout()
        
        format_label = QLabel("Display as:")
        format_layout.addWidget(format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.addItem("Email only", "email")
        self.format_combo.addItem("Name (Email)", "name_email")
        self.format_combo.addItem("Identifier - Email", "id_email")
        self.format_combo.addItem("Custom...", "custom")
        self.format_combo.currentIndexChanged.connect(self._on_format_changed)
        format_layout.addWidget(self.format_combo)
        
        format_layout.addSpacing(10)
        
        self.custom_format_label = QLabel("Format:")
        self.custom_format_label.setVisible(False)
        format_layout.addWidget(self.custom_format_label)
        
        self.custom_format_input = QLineEdit()
        self.custom_format_input.setPlaceholderText("e.g., {Name} <{Email}> - Type '{' for suggestions")
        self.custom_format_input.setVisible(False)
        self.custom_format_input.setMinimumWidth(200)
        self.custom_format_input.editingFinished.connect(self._refresh_recipient_list)
        format_layout.addWidget(self.custom_format_input)

        # Variable autocomplete for custom format (shows popup when typing '{')
        self._format_completer = LineEditCompleter(self.custom_format_input)
        
        format_layout.addStretch()
        
        self.refresh_btn = QPushButton("Refresh Preview")
        self.refresh_btn.clicked.connect(self._refresh_current)
        format_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(format_layout)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Email preview section
        preview_group = QGroupBox("Email Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        # Subject display
        subject_layout = QHBoxLayout()
        subject_label = QLabel("<b>Subject:</b>")
        subject_layout.addWidget(subject_label)
        self.subject_display = QLabel("")
        self.subject_display.setWordWrap(True)
        self.subject_display.setStyleSheet("background: #f5f5f5; padding: 5px;")
        subject_layout.addWidget(self.subject_display, stretch=1)
        preview_layout.addLayout(subject_layout)
        
        # Recipients display
        recipients_layout = QHBoxLayout()
        to_label = QLabel("<b>To:</b>")
        recipients_layout.addWidget(to_label)
        self.to_display = QLabel("")
        self.to_display.setWordWrap(True)
        recipients_layout.addWidget(self.to_display, stretch=1)
        preview_layout.addLayout(recipients_layout)
        
        # CC/BCC display (if applicable)
        self.cc_display = QLabel("")
        self.cc_display.setVisible(False)
        preview_layout.addWidget(self.cc_display)
        
        # Body preview
        body_label = QLabel("<b>Body:</b>")
        preview_layout.addWidget(body_label)
        
        self.body_browser = QTextBrowser()
        self.body_browser.setOpenExternalLinks(True)
        preview_layout.addWidget(self.body_browser, stretch=1)
        
        splitter.addWidget(preview_group)
        
        # Attachments section
        attachments_group = QGroupBox("Attachments")
        attachments_layout = QVBoxLayout(attachments_group)
        
        self.attachment_summary = QLabel("No attachments")
        attachments_layout.addWidget(self.attachment_summary)
        
        self.attachment_list = QListWidget()
        attachments_layout.addWidget(self.attachment_list)
        
        self.size_warning = QLabel("")
        self.size_warning.setStyleSheet("color: #fd7e14;")
        attachments_layout.addWidget(self.size_warning)
        
        splitter.addWidget(attachments_group)
        
        # Set splitter proportions
        splitter.setSizes([600, 300])
        
        layout.addWidget(splitter, stretch=1)
        
        # Validation summary
        validation_layout = QHBoxLayout()
        
        self.validation_label = QLabel("")
        validation_layout.addWidget(self.validation_label, stretch=1)
        
        self.refresh_btn = QPushButton("Refresh Preview")
        self.refresh_btn.clicked.connect(self.refresh_preview)
        validation_layout.addWidget(self.refresh_btn)

        layout.addLayout(validation_layout)

        # Tab navigation bar (separate from recipient navigation)
        self.tab_nav_bar = TabNavigationBar(show_previous=True, show_next=True)
        self.tab_nav_bar.previous_clicked.connect(self.navigate_previous.emit)
        self.tab_nav_bar.next_clicked.connect(self.navigate_next.emit)
        layout.addWidget(self.tab_nav_bar)

    def set_email_builder(self, builder: EmailBuilder) -> None:
        """
        Set the email builder for preview generation.
        
        Args:
            builder: Configured EmailBuilder instance
        """
        self._email_builder = builder
    
    def set_preview_data(
        self,
        data: List[Dict[str, Any]],
        selected_indices: List[int],
        email_column: str,
        columns: List[str] = None,
        name_column: str = None,
        identifier_column: str = None
    ) -> None:
        """
        Set data for preview.
        
        Args:
            data: All data rows
            selected_indices: Indices of selected recipients
            email_column: Name of email column for display
            columns: All available columns
            name_column: Column containing name
            identifier_column: Column containing identifier
        """
        self._data = data
        self._selected_indices = selected_indices
        self._current_index = 0
        self._email_column = email_column
        self._columns = columns or []
        self._name_column = name_column
        self._identifier_column = identifier_column

        # Update custom format autocomplete with available columns
        self._format_completer.set_variables(self._columns)

        # Auto-detect name column if not provided
        if not self._name_column and columns:
            for col in columns:
                if col.lower() in ['name', 'client name', 'customer', 'party', 'party name']:
                    self._name_column = col
                    break
        
        # Populate recipient dropdown
        self._refresh_recipient_list()
        
        # Update display
        if selected_indices:
            self._show_preview(0)
        else:
            self._clear_preview()
        
        self._update_navigation()
    
    def _on_format_changed(self, index: int) -> None:
        """Handle display format change."""
        format_type = self.format_combo.itemData(index)
        
        # Show/hide custom format input
        is_custom = (format_type == "custom")
        self.custom_format_label.setVisible(is_custom)
        self.custom_format_input.setVisible(is_custom)
        
        if not is_custom:
            self._refresh_recipient_list()
    
    def _refresh_recipient_list(self) -> None:
        """Refresh the recipient dropdown with current format."""
        current_idx = self._current_index
        
        self.recipient_combo.blockSignals(True)
        self.recipient_combo.clear()
        
        format_type = self.format_combo.currentData()
        
        for idx in self._selected_indices:
            if idx < len(self._data):
                row = self._data[idx]
                display_text = self._format_recipient(row, idx, format_type)
                self.recipient_combo.addItem(display_text, idx)
        
        # Restore selection
        if current_idx < self.recipient_combo.count():
            self.recipient_combo.setCurrentIndex(current_idx)
        
        self.recipient_combo.blockSignals(False)
    
    def _format_recipient(self, row: Dict[str, Any], idx: int, format_type: str) -> str:
        """Format a recipient for display in dropdown."""
        email = str(row.get(self._email_column, f"Row {idx + 1}"))
        
        if format_type == "email":
            return f"{idx + 1}. {email}"
        
        elif format_type == "name_email":
            name = ""
            if self._name_column:
                name = str(row.get(self._name_column, "")).strip()
            if name:
                return f"{idx + 1}. {name} ({email})"
            return f"{idx + 1}. {email}"
        
        elif format_type == "id_email":
            identifier = ""
            if self._identifier_column:
                identifier = str(row.get(self._identifier_column, "")).strip()
            if identifier:
                return f"{idx + 1}. {identifier} - {email}"
            return f"{idx + 1}. {email}"
        
        elif format_type == "custom":
            custom_fmt = self.custom_format_input.text().strip()
            if custom_fmt:
                # Replace {ColumnName} with values
                result = custom_fmt
                for col in self._columns:
                    placeholder = "{" + col + "}"
                    value = str(row.get(col, "")).strip()
                    result = result.replace(placeholder, value)
                return f"{idx + 1}. {result}"
            return f"{idx + 1}. {email}"
        
        return f"{idx + 1}. {email}"
    
    def _refresh_current(self) -> None:
        """Refresh the current preview."""
        if self._current_index >= 0 and self._current_index < self.recipient_combo.count():
            self._show_preview(self._current_index)
    
    def _show_preview(self, combo_index: int) -> None:
        """
        Show preview for recipient at combo index.
        
        Args:
            combo_index: Index in the combo box
        """
        if combo_index < 0 or combo_index >= self.recipient_combo.count():
            return
        
        self._current_index = combo_index
        data_idx = self.recipient_combo.itemData(combo_index)
        
        if data_idx is None or data_idx >= len(self._data):
            return
        
        row_data = self._data[data_idx]
        
        if self._email_builder:
            preview = self._email_builder.get_preview_data(row_data)
            
            # Update subject
            self.subject_display.setText(preview.get('subject', ''))
            
            # Update recipients
            to_list = preview.get('to', [])
            self.to_display.setText("; ".join(to_list) if to_list else "(no recipients)")
            
            # Update body
            self.body_browser.setHtml(preview.get('body_html', ''))
            
            # Update attachments
            attachments = preview.get('attachments', [])
            self._update_attachments_display(attachments)
        else:
            self.subject_display.setText("(Email builder not configured)")
            self.body_browser.setHtml("")
            self.attachment_list.clear()
        
        self._update_navigation()
    
    def _update_attachments_display(self, attachments: List[Dict]) -> None:
        """Update attachments list display."""
        self.attachment_list.clear()
        
        if not attachments:
            self.attachment_summary.setText("No attachments")
            self.size_warning.setText("")
            return
        
        total_size = 0
        static_count = 0
        variable_count = 0
        
        for att in attachments:
            filename = att.get('filename', 'Unknown')
            size = att.get('size', '0 B')
            att_type = att.get('type', 'static')
            
            prefix = "📎" if att_type == 'static' else "🔗"
            item = QListWidgetItem(f"{prefix} {filename}  ({size})")
            item.setToolTip(att.get('path', ''))
            self.attachment_list.addItem(item)
            
            if att_type == 'static':
                static_count += 1
            else:
                variable_count += 1
        
        # Update summary
        parts = []
        if static_count:
            parts.append(f"{static_count} static")
        if variable_count:
            parts.append(f"{variable_count} matched")
        
        self.attachment_summary.setText(
            f"{len(attachments)} attachment(s): {', '.join(parts)}"
        )
        
        # Size warning would need actual size calculation
        self.size_warning.setText("")
    
    def _clear_preview(self) -> None:
        """Clear preview display."""
        self.subject_display.setText("")
        self.to_display.setText("")
        self.cc_display.setText("")
        self.body_browser.setHtml("")
        self.attachment_list.clear()
        self.attachment_summary.setText("No attachments")
        self.position_label.setText("0 / 0")
    
    def _update_navigation(self) -> None:
        """Update navigation buttons and position label."""
        total = self.recipient_combo.count()
        current = self._current_index + 1 if total > 0 else 0
        
        self.position_label.setText(f"{current} / {total}")
        self.prev_btn.setEnabled(self._current_index > 0)
        self.next_btn.setEnabled(self._current_index < total - 1)
    
    def _prev_recipient(self) -> None:
        """Navigate to previous recipient."""
        if self._current_index > 0:
            self._current_index -= 1
            self.recipient_combo.setCurrentIndex(self._current_index)
    
    def _next_recipient(self) -> None:
        """Navigate to next recipient."""
        if self._current_index < self.recipient_combo.count() - 1:
            self._current_index += 1
            self.recipient_combo.setCurrentIndex(self._current_index)
    
    def _on_recipient_selected(self, index: int) -> None:
        """Handle recipient selection from dropdown."""
        self._show_preview(index)
    
    def refresh_preview(self) -> None:
        """Refresh the current preview."""
        self._show_preview(self._current_index)
    
    def validate_all(self) -> tuple:
        """
        Validate all selected recipients.
        
        Returns:
            Tuple of (is_valid, issues_list)
        """
        issues = []
        
        if not self._email_builder:
            return False, ["Email builder not configured"]
        
        if not self._selected_indices:
            return False, ["No recipients selected"]
        
        # Check for recipients without email
        for idx in self._selected_indices:
            if idx >= len(self._data):
                issues.append(f"Invalid index: {idx}")
                continue
            
            row = self._data[idx]
            preview = self._email_builder.get_preview_data(row)
            
            if not preview.get('to'):
                issues.append(f"Row {idx + 1}: No email address")
        
        is_valid = len(issues) == 0
        
        if is_valid:
            self.validation_label.setText(
                f"✓ {len(self._selected_indices)} emails ready to send"
            )
            self.validation_label.setStyleSheet("color: #28a745;")
        else:
            self.validation_label.setText(
                f"⚠ {len(issues)} issue(s) found"
            )
            self.validation_label.setStyleSheet("color: #dc3545;")
        
        return is_valid, issues
