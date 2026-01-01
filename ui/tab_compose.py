"""
Advanced Email Tool - Compose Tab
=================================
Tab for composing email subject and body with template support.
"""

from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QLineEdit, QComboBox,
    QMessageBox, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal

from ui.components.rich_text_editor import RichTextEditor
from ui.components.dialogs import show_error, show_info, show_warning, InputDialog
from data.template_storage import TemplateStorage
from core.template_engine import TemplateEngine
from utils import get_logger


class TabCompose(QWidget):
    """
    Email composition tab.
    
    Features:
    - Subject line with variable support
    - Rich text body editor
    - Template save/load
    - Variable insertion from Excel columns
    - Preview with sample data
    """
    
    # Signals
    template_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the Compose tab."""
        super().__init__(parent)
        
        self.logger = get_logger()
        self.template_storage = TemplateStorage()
        self.template_engine = TemplateEngine()
        self._available_columns: List[str] = []
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Template management bar
        template_layout = QHBoxLayout()
        
        template_label = QLabel("Template:")
        template_layout.addWidget(template_label)
        
        self.template_combo = QComboBox()
        self.template_combo.setMinimumWidth(200)
        self.template_combo.addItem("-- New Template --")
        self._refresh_template_list()
        template_layout.addWidget(self.template_combo)
        
        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(self._load_template)
        template_layout.addWidget(self.load_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_template)
        template_layout.addWidget(self.save_btn)
        
        self.save_as_btn = QPushButton("Save As...")
        self.save_as_btn.clicked.connect(self._save_template_as)
        template_layout.addWidget(self.save_as_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._delete_template)
        template_layout.addWidget(self.delete_btn)
        
        template_layout.addSpacing(20)
        
        self.import_btn = QPushButton("Import File...")
        self.import_btn.setToolTip("Import content from Word (.docx) or Text (.txt) file")
        self.import_btn.clicked.connect(self._import_file)
        template_layout.addWidget(self.import_btn)
        
        template_layout.addStretch()
        
        layout.addLayout(template_layout)
        
        # Subject line
        subject_group = QGroupBox("Subject Line")
        subject_layout = QVBoxLayout(subject_group)
        
        subject_input_layout = QHBoxLayout()
        
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Enter subject with {Variables} from Excel columns...")
        self.subject_input.textChanged.connect(self._on_content_changed)
        subject_input_layout.addWidget(self.subject_input)
        
        self.subject_var_combo = QComboBox()
        self.subject_var_combo.setFixedWidth(150)
        self.subject_var_combo.addItem("Insert Variable")
        subject_input_layout.addWidget(self.subject_var_combo)
        
        self.subject_insert_btn = QPushButton("Insert")
        self.subject_insert_btn.clicked.connect(self._insert_subject_variable)
        subject_input_layout.addWidget(self.subject_insert_btn)
        
        subject_layout.addLayout(subject_input_layout)
        
        layout.addWidget(subject_group)
        
        # Body editor
        body_group = QGroupBox("Email Body")
        body_layout = QVBoxLayout(body_group)
        
        self.body_editor = RichTextEditor()
        self.body_editor.content_changed.connect(self._on_content_changed)
        body_layout.addWidget(self.body_editor)
        
        layout.addWidget(body_group, stretch=1)
        
        # Universal BCC
        bcc_layout = QHBoxLayout()
        
        bcc_label = QLabel("Universal BCC (added to all emails):")
        bcc_layout.addWidget(bcc_label)
        
        self.universal_bcc_input = QLineEdit()
        self.universal_bcc_input.setPlaceholderText("e.g., records@yourfirm.com")
        bcc_layout.addWidget(self.universal_bcc_input)
        
        layout.addLayout(bcc_layout)
        
        # Variable usage info
        self.var_info_label = QLabel("")
        self.var_info_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.var_info_label)
    
    def _refresh_template_list(self) -> None:
        """Refresh the template dropdown list."""
        current = self.template_combo.currentText()
        
        self.template_combo.blockSignals(True)
        self.template_combo.clear()
        self.template_combo.addItem("-- New Template --")
        
        templates = self.template_storage.list_templates()
        for template in templates:
            self.template_combo.addItem(template['name'])
        
        # Restore selection if possible
        idx = self.template_combo.findText(current)
        if idx >= 0:
            self.template_combo.setCurrentIndex(idx)
        
        self.template_combo.blockSignals(False)
    
    def _load_template(self) -> None:
        """Load selected template."""
        name = self.template_combo.currentText()
        if name == "-- New Template --":
            self._clear_content()
            return
        
        template = self.template_storage.load_template(name)
        if template:
            self.subject_input.setText(template.get('subject', ''))
            self.body_editor.set_html(template.get('body', ''))
            self.logger.info(f"Template loaded: {name}")
            show_info(self, "Template Loaded", f"Template '{name}' loaded successfully.")
        else:
            show_error(self, "Error", f"Could not load template '{name}'.")
    
    def _save_template(self) -> None:
        """Save current content to selected template."""
        name = self.template_combo.currentText()
        if name == "-- New Template --":
            self._save_template_as()
            return
        
        success, msg = self.template_storage.save_template(
            name,
            self.subject_input.text(),
            self.body_editor.get_html()
        )
        
        if success:
            show_info(self, "Saved", f"Template '{name}' saved.")
        else:
            show_error(self, "Error", msg)
    
    def _save_template_as(self) -> None:
        """Save current content as new template."""
        name, ok = InputDialog.get_text(
            self,
            "Save Template",
            "Enter template name:",
            ""
        )
        
        if ok and name:
            if self.template_storage.template_exists(name):
                reply = QMessageBox.question(
                    self,
                    "Overwrite?",
                    f"Template '{name}' already exists. Overwrite?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            
            success, msg = self.template_storage.save_template(
                name,
                self.subject_input.text(),
                self.body_editor.get_html()
            )
            
            if success:
                self._refresh_template_list()
                self.template_combo.setCurrentText(name)
                show_info(self, "Saved", f"Template saved as '{name}'.")
            else:
                show_error(self, "Error", msg)
    
    def _delete_template(self) -> None:
        """Delete selected template."""
        name = self.template_combo.currentText()
        if name == "-- New Template --":
            return
        
        reply = QMessageBox.question(
            self,
            "Delete Template?",
            f"Are you sure you want to delete '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, msg = self.template_storage.delete_template(name)
            if success:
                self._refresh_template_list()
                self.template_combo.setCurrentIndex(0)
                show_info(self, "Deleted", f"Template '{name}' deleted.")
            else:
                show_error(self, "Error", msg)
    
    def _clear_content(self) -> None:
        """Clear subject and body."""
        self.subject_input.clear()
        self.body_editor.clear()
    
    def _insert_subject_variable(self) -> None:
        """Insert selected variable into subject line."""
        var_name = self.subject_var_combo.currentText()
        if var_name and var_name != "Insert Variable":
            cursor_pos = self.subject_input.cursorPosition()
            current_text = self.subject_input.text()
            new_text = current_text[:cursor_pos] + f"{{{var_name}}}" + current_text[cursor_pos:]
            self.subject_input.setText(new_text)
            self.subject_input.setCursorPosition(cursor_pos + len(var_name) + 2)
    
    def _on_content_changed(self) -> None:
        """Handle content changes."""
        self._update_variable_info()
        self.template_changed.emit()
    
    def _update_variable_info(self) -> None:
        """Update variable usage information."""
        subject = self.subject_input.text()
        body = self.body_editor.get_html()
        
        report = self.template_engine.get_variable_usage_report(
            subject, body, self._available_columns
        )
        
        used = len(report['used_columns'])
        missing = report['missing_variables']
        
        if missing:
            self.var_info_label.setText(
                f"⚠ Missing columns: {', '.join(missing)}"
            )
            self.var_info_label.setStyleSheet("color: #dc3545; font-size: 10px;")
        elif used > 0:
            self.var_info_label.setText(
                f"✓ Using {used} variable(s): {', '.join(report['used_columns'])}"
            )
            self.var_info_label.setStyleSheet("color: #28a745; font-size: 10px;")
        else:
            self.var_info_label.setText("No variables used (static email)")
            self.var_info_label.setStyleSheet("color: gray; font-size: 10px;")
    
    def set_available_columns(self, columns: List[str]) -> None:
        """
        Set available columns for variable insertion.
        
        Args:
            columns: List of column names from Excel
        """
        self._available_columns = columns
        
        # Update subject variable dropdown
        self.subject_var_combo.clear()
        self.subject_var_combo.addItem("Insert Variable")
        for col in columns:
            self.subject_var_combo.addItem(col)
        
        # Update body editor
        self.body_editor.set_available_variables(columns)
        
        # Update info
        self._update_variable_info()
    
    def get_subject_template(self) -> str:
        """Get the subject template."""
        return self.subject_input.text()
    
    def get_body_template(self) -> str:
        """Get the body HTML template."""
        return self.body_editor.get_html()
    
    def get_universal_bcc(self) -> Optional[str]:
        """Get the universal BCC address."""
        bcc = self.universal_bcc_input.text().strip()
        return bcc if bcc else None
    
    def set_subject_template(self, subject: str) -> None:
        """Set the subject template."""
        self.subject_input.setText(subject)
    
    def set_body_template(self, body: str) -> None:
        """Set the body HTML template."""
        self.body_editor.set_html(body)
    
    def set_universal_bcc(self, bcc: str) -> None:
        """Set the universal BCC address."""
        self.universal_bcc_input.setText(bcc or "")
    
    def is_valid(self) -> tuple:
        """
        Check if composition is valid.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.subject_input.text().strip():
            return False, "Subject line is empty"
        
        if self.body_editor.is_empty():
            return False, "Email body is empty"
        
        # Check for missing variables
        subject = self.subject_input.text()
        body = self.body_editor.get_html()
        report = self.template_engine.get_variable_usage_report(
            subject, body, self._available_columns
        )
        
        if report['missing_variables']:
            return False, f"Missing columns: {', '.join(report['missing_variables'])}"
        
        return True, ""
    
    def _import_file(self) -> None:
        """Import content from Word (.docx) or Text (.txt) file."""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import File",
            "",
            "Supported Files (*.docx *.txt *.html *.htm);;Word Documents (*.docx);;Text Files (*.txt);;HTML Files (*.html *.htm);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            import os
            ext = os.path.splitext(file_path)[1].lower()
            
            content = ""
            
            if ext == '.docx':
                content = self._read_docx(file_path)
            elif ext == '.txt':
                content = self._read_txt(file_path)
            elif ext in ['.html', '.htm']:
                content = self._read_html(file_path)
            else:
                show_warning(self, "Unsupported", f"File type '{ext}' is not supported.")
                return
            
            if content:
                # Ask how to import
                reply = QMessageBox.question(
                    self,
                    "Import Content",
                    "How would you like to import this content?\n\n"
                    "Yes = Replace current body\n"
                    "No = Append to current body",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Yes:
                    self.body_editor.set_html(content)
                elif reply == QMessageBox.No:
                    current = self.body_editor.get_html()
                    self.body_editor.set_html(current + "<br><br>" + content)
                # Cancel = do nothing
                
                if reply != QMessageBox.Cancel:
                    self.logger.info(f"Imported content from: {file_path}")
                    show_info(self, "Imported", "Content imported successfully.")
            
        except Exception as e:
            show_error(self, "Import Error", f"Could not import file:\n{e}")
            self.logger.error(f"Import error: {e}")
    
    def _read_docx(self, file_path: str) -> str:
        """Read content from a Word document."""
        try:
            # Try using python-docx
            import docx
            doc = docx.Document(file_path)
            
            html_parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    html_parts.append(f"<p>{para.text}</p>")
            
            return "\n".join(html_parts)
        except ImportError:
            # python-docx not installed, try basic extraction
            show_warning(
                self, 
                "Limited Support",
                "python-docx not installed. Install it for better Word support:\n"
                "pip install python-docx"
            )
            return ""
    
    def _read_txt(self, file_path: str) -> str:
        """Read content from a text file."""
        # Try different encodings
        encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    text = f.read()
                # Convert plain text to HTML paragraphs
                paragraphs = text.split('\n\n')
                html_parts = []
                for para in paragraphs:
                    para = para.strip()
                    if para:
                        # Replace single newlines with <br>
                        para = para.replace('\n', '<br>')
                        html_parts.append(f"<p>{para}</p>")
                return "\n".join(html_parts)
            except UnicodeDecodeError:
                continue
        
        raise ValueError("Could not decode file with any supported encoding")
    
    def _read_html(self, file_path: str) -> str:
        """Read content from an HTML file."""
        encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                # Try to extract just the body content
                import re
                body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
                if body_match:
                    return body_match.group(1)
                return content
            except UnicodeDecodeError:
                continue
        
        raise ValueError("Could not decode file with any supported encoding")
