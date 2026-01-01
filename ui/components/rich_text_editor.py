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
    QSplitter, QPlainTextEdit, QApplication, QFileDialog,
    QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData, QUrl, QByteArray
from PyQt5.QtGui import (
    QFont, QTextCharFormat, QColor, QTextCursor,
    QTextListFormat, QIcon, QKeySequence, QImage,
    QImageReader, QTextDocumentFragment
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
        self.editor.setAcceptDrops(True)
        self.splitter.addWidget(self.editor)
        
        # Install event filter for drag-drop
        self.editor.installEventFilter(self)
        
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
        
        self.toolbar.addSeparator()
        
        # Paste Table from Excel
        self.paste_table_action = QAction("📋 Table", self)
        self.paste_table_action.setToolTip("Paste Table from Excel (Ctrl+Shift+V)")
        self.paste_table_action.setShortcut("Ctrl+Shift+V")
        self.paste_table_action.triggered.connect(self._paste_table_from_clipboard)
        self.toolbar.addAction(self.paste_table_action)
        
        # Insert Image
        self.insert_image_btn = QPushButton("🖼️ Image")
        self.insert_image_btn.setToolTip("Insert Image")
        self.insert_image_btn.setFlat(True)
        
        image_menu = QMenu(self)
        image_menu.addAction("From File...", self._insert_image_from_file)
        image_menu.addAction("From Clipboard", self._insert_image_from_clipboard)
        self.insert_image_btn.setMenu(image_menu)
        self.toolbar.addWidget(self.insert_image_btn)
    
    def _setup_connections(self) -> None:
        """Set up signal connections."""
        self.editor.textChanged.connect(self._on_text_changed)
        self.editor.cursorPositionChanged.connect(self._update_format_actions)
    
    def eventFilter(self, obj, event):
        """Handle drag-drop events for images."""
        from PyQt5.QtCore import QEvent
        
        if obj == self.editor:
            if event.type() == QEvent.DragEnter:
                mime_data = event.mimeData()
                if mime_data.hasUrls() or mime_data.hasImage():
                    # Check if any URL is an image
                    if mime_data.hasUrls():
                        for url in mime_data.urls():
                            path = url.toLocalFile().lower()
                            if path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                                event.acceptProposedAction()
                                return True
                    if mime_data.hasImage():
                        event.acceptProposedAction()
                        return True
            
            elif event.type() == QEvent.Drop:
                mime_data = event.mimeData()
                
                # Handle dropped image file
                if mime_data.hasUrls():
                    for url in mime_data.urls():
                        path = url.toLocalFile()
                        if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                            self._insert_image(path)
                            event.acceptProposedAction()
                            return True
                
                # Handle dropped image data
                if mime_data.hasImage():
                    image = QImage(mime_data.imageData())
                    if not image.isNull():
                        self._insert_qimage(image)
                        event.acceptProposedAction()
                        return True
        
        return super().eventFilter(obj, event)
    
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
    
    # ========== TABLE METHODS ==========
    
    def _paste_table_from_clipboard(self) -> None:
        """Paste table from clipboard (Excel, Google Sheets, etc.)."""
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        html_table = None
        
        # Try HTML format first (Excel copies as HTML)
        if mime_data.hasHtml():
            html = mime_data.html()
            # Check if it contains a table
            if '<table' in html.lower():
                html_table = self._extract_and_style_table(html)
        
        # Fallback to plain text (tab-separated)
        if not html_table and mime_data.hasText():
            text = mime_data.text()
            if '\t' in text:  # Tab-separated = likely from spreadsheet
                html_table = self._convert_tsv_to_table(text)
        
        if html_table:
            self.editor.insertHtml(html_table)
            self.editor.insertHtml("<p></p>")  # Add paragraph after table
            self.content_changed.emit()
        else:
            QMessageBox.information(
                self,
                "No Table Found",
                "No table data found in clipboard.\n\n"
                "Copy cells from Excel or Google Sheets first,\n"
                "then click 'Paste Table'."
            )
    
    def _extract_and_style_table(self, html: str) -> str:
        """
        Extract table from HTML and apply consistent styling.
        
        Args:
            html: Raw HTML from clipboard
            
        Returns:
            Styled HTML table
        """
        import re
        
        # Find table content
        table_match = re.search(r'<table[^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
        if not table_match:
            return ""
        
        table_content = table_match.group(1)
        
        # Clean up the content - remove excessive styling
        # Keep only tr and td/th tags
        table_content = re.sub(r'<colgroup[^>]*>.*?</colgroup>', '', table_content, flags=re.DOTALL | re.IGNORECASE)
        table_content = re.sub(r'style="[^"]*"', '', table_content, flags=re.IGNORECASE)
        table_content = re.sub(r'class="[^"]*"', '', table_content, flags=re.IGNORECASE)
        table_content = re.sub(r'width="[^"]*"', '', table_content, flags=re.IGNORECASE)
        table_content = re.sub(r'height="[^"]*"', '', table_content, flags=re.IGNORECASE)
        
        # Build styled table
        styled_table = '''
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; border: 1px solid #333;">
{content}
</table>
'''.format(content=table_content)
        
        # Style first row as header (bold, background)
        styled_table = re.sub(
            r'(<tr[^>]*>)(.*?)(</tr>)',
            lambda m: m.group(1) + self._style_first_row(m.group(2)) + m.group(3),
            styled_table,
            count=1,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        return styled_table
    
    def _style_first_row(self, row_content: str) -> str:
        """Style first row cells as headers."""
        import re
        # Add background and bold to first row cells
        row_content = re.sub(
            r'<td([^>]*)>',
            r'<td\1 style="background-color: #4472C4; color: white; font-weight: bold;">',
            row_content,
            flags=re.IGNORECASE
        )
        row_content = re.sub(
            r'<th([^>]*)>',
            r'<th\1 style="background-color: #4472C4; color: white; font-weight: bold;">',
            row_content,
            flags=re.IGNORECASE
        )
        return row_content
    
    def _convert_tsv_to_table(self, text: str) -> str:
        """
        Convert tab-separated text to HTML table.
        
        Args:
            text: Tab-separated text from clipboard
            
        Returns:
            HTML table string
        """
        lines = text.strip().split('\n')
        if not lines:
            return ""
        
        rows_html = []
        for i, line in enumerate(lines):
            cells = line.split('\t')
            if i == 0:
                # Header row
                cells_html = ''.join(
                    f'<td style="background-color: #4472C4; color: white; font-weight: bold; padding: 6px; border: 1px solid #333;">{cell}</td>'
                    for cell in cells
                )
            else:
                # Data rows
                cells_html = ''.join(
                    f'<td style="padding: 6px; border: 1px solid #333;">{cell}</td>'
                    for cell in cells
                )
            rows_html.append(f'<tr>{cells_html}</tr>')
        
        table_html = f'''
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; border: 1px solid #333;">
{''.join(rows_html)}
</table>
'''
        return table_html
    
    # ========== IMAGE METHODS ==========
    
    def _insert_image_from_file(self) -> None:
        """Insert image from file picker."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*.*)"
        )
        
        if file_path:
            self._insert_image(file_path)
    
    def _insert_image_from_clipboard(self) -> None:
        """Insert image from clipboard."""
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        if mime_data.hasImage():
            image = clipboard.image()
            if not image.isNull():
                self._insert_qimage(image)
            else:
                QMessageBox.information(
                    self,
                    "No Image",
                    "No image found in clipboard.\n\n"
                    "Copy an image or take a screenshot first."
                )
        else:
            QMessageBox.information(
                self,
                "No Image",
                "No image found in clipboard.\n\n"
                "Copy an image or take a screenshot first."
            )
    
    def _insert_image(self, file_path: str) -> None:
        """
        Insert image from file path.
        
        Args:
            file_path: Path to image file
        """
        import os
        import base64
        
        # Read and encode image
        try:
            with open(file_path, 'rb') as f:
                image_data = f.read()
            
            # Determine mime type
            ext = os.path.splitext(file_path)[1].lower()
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
            }
            mime_type = mime_types.get(ext, 'image/png')
            
            # Encode to base64
            b64_data = base64.b64encode(image_data).decode('utf-8')
            
            # Insert as base64 data URI (for editor preview)
            # Note: On send, this will be converted to CID attachment
            img_html = f'<img src="data:{mime_type};base64,{b64_data}" style="max-width: 100%;" />'
            self.editor.insertHtml(img_html)
            self.content_changed.emit()
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Image Error",
                f"Could not insert image:\n{str(e)}"
            )
    
    def _insert_qimage(self, image: QImage) -> None:
        """
        Insert QImage (from clipboard).
        
        Args:
            image: QImage object
        """
        import base64
        from PyQt5.QtCore import QBuffer, QIODevice
        
        # Convert to PNG bytes
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        image_data = buffer.data()
        
        # Encode to base64
        b64_data = base64.b64encode(bytes(image_data)).decode('utf-8')
        
        # Insert as base64 data URI
        img_html = f'<img src="data:image/png;base64,{b64_data}" style="max-width: 100%;" />'
        self.editor.insertHtml(img_html)
        self.content_changed.emit()
    
    def get_embedded_images(self) -> List[dict]:
        """
        Extract embedded base64 images from HTML for conversion to CID.
        
        Returns:
            List of dicts with 'data', 'mime_type', 'cid'
        """
        import re
        import uuid
        
        html = self.get_html()
        images = []
        
        # Find all base64 images
        pattern = r'<img[^>]+src="data:([^;]+);base64,([^"]+)"[^>]*>'
        
        for match in re.finditer(pattern, html):
            mime_type = match.group(1)
            b64_data = match.group(2)
            cid = f"image_{uuid.uuid4().hex[:8]}"
            
            images.append({
                'mime_type': mime_type,
                'data': b64_data,
                'cid': cid,
                'original_tag': match.group(0),
            })
        
        return images
    
    def convert_images_to_cid(self, images: List[dict]) -> str:
        """
        Convert base64 images to CID references in HTML.
        
        Args:
            images: List from get_embedded_images()
            
        Returns:
            HTML with CID references instead of base64
        """
        html = self.get_html()
        
        for img in images:
            cid_tag = f'<img src="cid:{img["cid"]}" />'
            html = html.replace(img['original_tag'], cid_tag)
        
        return html
