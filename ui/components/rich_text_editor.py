"""
Advanced Email Tool - Rich Text Editor
======================================
Visual HTML email editor with formatting toolbar.
No HTML knowledge needed - WYSIWYG editing.
"""

from typing import Optional, List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QToolBar, QAction, QFontComboBox, QComboBox,
    QColorDialog, QMenu, QPushButton, QLabel,
    QSplitter, QPlainTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import (
    QFont, QTextCharFormat, QColor, QTextCursor,
    QTextListFormat, QIcon, QKeySequence
)


class RichTextEditor(QWidget):
    """
    Rich text editor for email composition.
    
    Features:
    - Formatting toolbar (bold, italic, underline)
    - Font family and size selection
    - Text and highlight colors
    - Lists (bullet and numbered)
    - Variable insertion from Excel columns
    - HTML source view toggle
    """
    
    # Signals
    content_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the rich text editor."""
        super().__init__(parent)
        
        self._available_variables: List[str] = []
        self._show_source = False
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Formatting toolbar
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self._setup_toolbar()
        layout.addWidget(self.toolbar)
        
        # Editor area (splitter for source view)
        self.splitter = QSplitter(Qt.Vertical)
        
        # Rich text editor
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Segoe UI", 11))
        self.editor.setAcceptRichText(True)
        self.splitter.addWidget(self.editor)
        
        # HTML source view (hidden by default)
        self.source_view = QPlainTextEdit()
        self.source_view.setFont(QFont("Consolas", 10))
        self.source_view.setVisible(False)
        self.splitter.addWidget(self.source_view)
        
        layout.addWidget(self.splitter)
        
        # Variable insertion bar
        var_layout = QHBoxLayout()
        var_layout.setContentsMargins(0, 5, 0, 0)
        
        var_label = QLabel("Insert Variable:")
        var_layout.addWidget(var_label)
        
        self.var_combo = QComboBox()
        self.var_combo.setMinimumWidth(150)
        self.var_combo.addItem("-- Select Column --")
        var_layout.addWidget(self.var_combo)
        
        self.insert_var_btn = QPushButton("Insert")
        self.insert_var_btn.clicked.connect(self._insert_variable)
        var_layout.addWidget(self.insert_var_btn)
        
        var_layout.addStretch()
        
        # Toggle source view button
        self.source_toggle_btn = QPushButton("View HTML")
        self.source_toggle_btn.setCheckable(True)
        self.source_toggle_btn.clicked.connect(self._toggle_source_view)
        var_layout.addWidget(self.source_toggle_btn)
        
        layout.addLayout(var_layout)
    
    def _setup_toolbar(self) -> None:
        """Set up the formatting toolbar."""
        # Font family
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont("Segoe UI"))
        self.font_combo.currentFontChanged.connect(self._set_font_family)
        self.toolbar.addWidget(self.font_combo)
        
        # Font size
        self.size_combo = QComboBox()
        sizes = ["8", "9", "10", "11", "12", "14", "16", "18", "20", "24", "28", "36"]
        self.size_combo.addItems(sizes)
        self.size_combo.setCurrentText("11")
        self.size_combo.currentTextChanged.connect(self._set_font_size)
        self.size_combo.setFixedWidth(60)
        self.toolbar.addWidget(self.size_combo)
        
        self.toolbar.addSeparator()
        
        # Bold
        self.bold_action = QAction("B", self)
        self.bold_action.setFont(QFont("", -1, QFont.Bold))
        self.bold_action.setShortcut(QKeySequence.Bold)
        self.bold_action.setCheckable(True)
        self.bold_action.triggered.connect(self._toggle_bold)
        self.bold_action.setToolTip("Bold (Ctrl+B)")
        self.toolbar.addAction(self.bold_action)
        
        # Italic
        self.italic_action = QAction("I", self)
        font = QFont()
        font.setItalic(True)
        self.italic_action.setFont(font)
        self.italic_action.setShortcut(QKeySequence.Italic)
        self.italic_action.setCheckable(True)
        self.italic_action.triggered.connect(self._toggle_italic)
        self.italic_action.setToolTip("Italic (Ctrl+I)")
        self.toolbar.addAction(self.italic_action)
        
        # Underline
        self.underline_action = QAction("U", self)
        font = QFont()
        font.setUnderline(True)
        self.underline_action.setFont(font)
        self.underline_action.setShortcut(QKeySequence.Underline)
        self.underline_action.setCheckable(True)
        self.underline_action.triggered.connect(self._toggle_underline)
        self.underline_action.setToolTip("Underline (Ctrl+U)")
        self.toolbar.addAction(self.underline_action)
        
        self.toolbar.addSeparator()
        
        # Text color
        self.text_color_action = QAction("A", self)
        self.text_color_action.setToolTip("Text Color")
        self.text_color_action.triggered.connect(self._choose_text_color)
        self.toolbar.addAction(self.text_color_action)
        
        # Highlight color
        self.highlight_action = QAction("H", self)
        self.highlight_action.setToolTip("Highlight Color")
        self.highlight_action.triggered.connect(self._choose_highlight_color)
        self.toolbar.addAction(self.highlight_action)
        
        self.toolbar.addSeparator()
        
        # Bullet list
        self.bullet_action = QAction("•", self)
        self.bullet_action.setToolTip("Bullet List")
        self.bullet_action.triggered.connect(self._insert_bullet_list)
        self.toolbar.addAction(self.bullet_action)
        
        # Numbered list
        self.number_action = QAction("1.", self)
        self.number_action.setToolTip("Numbered List")
        self.number_action.triggered.connect(self._insert_numbered_list)
        self.toolbar.addAction(self.number_action)
        
        self.toolbar.addSeparator()
        
        # Alignment
        self.align_left_action = QAction("←", self)
        self.align_left_action.setToolTip("Align Left")
        self.align_left_action.triggered.connect(lambda: self._set_alignment(Qt.AlignLeft))
        self.toolbar.addAction(self.align_left_action)
        
        self.align_center_action = QAction("↔", self)
        self.align_center_action.setToolTip("Align Center")
        self.align_center_action.triggered.connect(lambda: self._set_alignment(Qt.AlignCenter))
        self.toolbar.addAction(self.align_center_action)
        
        self.align_right_action = QAction("→", self)
        self.align_right_action.setToolTip("Align Right")
        self.align_right_action.triggered.connect(lambda: self._set_alignment(Qt.AlignRight))
        self.toolbar.addAction(self.align_right_action)
    
    def _setup_connections(self) -> None:
        """Set up signal connections."""
        self.editor.textChanged.connect(self._on_text_changed)
        self.editor.cursorPositionChanged.connect(self._update_format_actions)
    
    def _on_text_changed(self) -> None:
        """Handle text changes."""
        self.content_changed.emit()
    
    def _update_format_actions(self) -> None:
        """Update toolbar buttons based on current cursor format."""
        cursor = self.editor.textCursor()
        char_format = cursor.charFormat()
        
        # Update bold/italic/underline states
        self.bold_action.setChecked(char_format.fontWeight() == QFont.Bold)
        self.italic_action.setChecked(char_format.fontItalic())
        self.underline_action.setChecked(char_format.fontUnderline())
        
        # Update font combo
        font = char_format.font()
        self.font_combo.blockSignals(True)
        self.font_combo.setCurrentFont(font)
        self.font_combo.blockSignals(False)
        
        # Update size combo
        size = int(char_format.fontPointSize()) if char_format.fontPointSize() > 0 else 11
        self.size_combo.blockSignals(True)
        self.size_combo.setCurrentText(str(size))
        self.size_combo.blockSignals(False)
    
    def _set_font_family(self, font: QFont) -> None:
        """Set font family for selection."""
        fmt = QTextCharFormat()
        fmt.setFontFamily(font.family())
        self._merge_format(fmt)
    
    def _set_font_size(self, size: str) -> None:
        """Set font size for selection."""
        try:
            point_size = float(size)
            fmt = QTextCharFormat()
            fmt.setFontPointSize(point_size)
            self._merge_format(fmt)
        except ValueError:
            pass
    
    def _toggle_bold(self) -> None:
        """Toggle bold formatting."""
        fmt = QTextCharFormat()
        weight = QFont.Normal if self.bold_action.isChecked() else QFont.Bold
        if self.bold_action.isChecked():
            weight = QFont.Bold
        else:
            weight = QFont.Normal
        fmt.setFontWeight(weight)
        self._merge_format(fmt)
    
    def _toggle_italic(self) -> None:
        """Toggle italic formatting."""
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.italic_action.isChecked())
        self._merge_format(fmt)
    
    def _toggle_underline(self) -> None:
        """Toggle underline formatting."""
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.underline_action.isChecked())
        self._merge_format(fmt)
    
    def _choose_text_color(self) -> None:
        """Show color dialog for text color."""
        color = QColorDialog.getColor(Qt.black, self, "Text Color")
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            self._merge_format(fmt)
    
    def _choose_highlight_color(self) -> None:
        """Show color dialog for highlight color."""
        color = QColorDialog.getColor(Qt.yellow, self, "Highlight Color")
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setBackground(color)
            self._merge_format(fmt)
    
    def _merge_format(self, fmt: QTextCharFormat) -> None:
        """Merge format into current selection."""
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(fmt)
        self.editor.mergeCurrentCharFormat(fmt)
    
    def _insert_bullet_list(self) -> None:
        """Insert or toggle bullet list."""
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        
        list_format = QTextListFormat()
        list_format.setStyle(QTextListFormat.ListDisc)
        cursor.createList(list_format)
        
        cursor.endEditBlock()
    
    def _insert_numbered_list(self) -> None:
        """Insert or toggle numbered list."""
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        
        list_format = QTextListFormat()
        list_format.setStyle(QTextListFormat.ListDecimal)
        cursor.createList(list_format)
        
        cursor.endEditBlock()
    
    def _set_alignment(self, alignment) -> None:
        """Set paragraph alignment."""
        self.editor.setAlignment(alignment)
    
    def _insert_variable(self) -> None:
        """Insert selected variable at cursor."""
        var_name = self.var_combo.currentText()
        if var_name and var_name != "-- Select Column --":
            self.editor.insertPlainText(f"{{{var_name}}}")
    
    def _toggle_source_view(self) -> None:
        """Toggle HTML source view."""
        self._show_source = self.source_toggle_btn.isChecked()
        
        if self._show_source:
            # Show HTML source
            html = self.editor.toHtml()
            self.source_view.setPlainText(html)
            self.source_view.setVisible(True)
            self.source_toggle_btn.setText("Hide HTML")
            self.editor.setReadOnly(True)
        else:
            # Apply changes from source and hide
            html = self.source_view.toPlainText()
            self.editor.setHtml(html)
            self.source_view.setVisible(False)
            self.source_toggle_btn.setText("View HTML")
            self.editor.setReadOnly(False)
    
    def set_available_variables(self, variables: List[str]) -> None:
        """
        Set available variables for insertion.
        
        Args:
            variables: List of column names
        """
        self._available_variables = variables
        self.var_combo.clear()
        self.var_combo.addItem("-- Select Column --")
        for var in variables:
            self.var_combo.addItem(var)
    
    def set_html(self, html: str) -> None:
        """
        Set the editor content from HTML.
        
        Args:
            html: HTML content
        """
        self.editor.setHtml(html)
    
    def get_html(self) -> str:
        """
        Get the editor content as HTML.
        
        Returns:
            HTML string
        """
        return self.editor.toHtml()
    
    def set_plain_text(self, text: str) -> None:
        """
        Set the editor content from plain text.
        
        Args:
            text: Plain text content
        """
        self.editor.setPlainText(text)
    
    def get_plain_text(self) -> str:
        """
        Get the editor content as plain text.
        
        Returns:
            Plain text string
        """
        return self.editor.toPlainText()
    
    def clear(self) -> None:
        """Clear the editor content."""
        self.editor.clear()
    
    def is_empty(self) -> bool:
        """
        Check if editor is empty.
        
        Returns:
            True if no content
        """
        return len(self.editor.toPlainText().strip()) == 0
    
    def insert_text(self, text: str) -> None:
        """
        Insert text at cursor position.
        
        Args:
            text: Text to insert
        """
        self.editor.insertPlainText(text)
    
    def insert_html(self, html: str) -> None:
        """
        Insert HTML at cursor position.
        
        Args:
            html: HTML to insert
        """
        self.editor.insertHtml(html)
