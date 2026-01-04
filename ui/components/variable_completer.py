"""
Advanced Email Tool - Variable Completer
=========================================
Autocomplete popup for {Variable} insertion in text fields.
Shows column names when user types '{' and filters as they type.
"""

from typing import List, Optional
from PyQt5.QtWidgets import (
    QWidget, QListWidget, QListWidgetItem, QLineEdit, QTextEdit,
    QVBoxLayout, QFrame
)
from PyQt5.QtCore import Qt, QPoint, QEvent, QTimer
from PyQt5.QtGui import QKeyEvent, QFocusEvent


class VariableCompleterPopup(QFrame):
    """
    Popup widget showing variable suggestions.
    Appears when user types '{' and filters as they continue typing.
    """

    def __init__(self, parent=None):
        super().__init__(parent, Qt.Popup | Qt.FramelessWindowHint)
        self.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.setLineWidth(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.list_widget = QListWidget()
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)

        self._all_items: List[str] = []
        self._filter_text: str = ""
        self._callback = None

        # Styling
        self.setStyleSheet("""
            VariableCompleterPopup {
                background: white;
                border: 1px solid #0078D4;
            }
            QListWidget {
                border: none;
                background: white;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 4px 8px;
            }
            QListWidget::item:selected {
                background: #0078D4;
                color: white;
            }
            QListWidget::item:hover {
                background: #E5F3FF;
            }
        """)

        self.setMinimumWidth(200)
        self.setMaximumHeight(200)

    def set_items(self, items: List[str]) -> None:
        """Set the list of available variable names."""
        self._all_items = items.copy()

    def set_callback(self, callback) -> None:
        """Set callback function when item is selected."""
        self._callback = callback

    def show_popup(self, filter_text: str = "") -> None:
        """Show popup with filtered items."""
        self._filter_text = filter_text.lower()
        self._update_list()

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
            self.show()
            self.raise_()
        else:
            self.hide()

    def _update_list(self) -> None:
        """Update list based on filter."""
        self.list_widget.clear()

        for item in self._all_items:
            if self._filter_text == "" or self._filter_text in item.lower():
                list_item = QListWidgetItem(item)
                self.list_widget.addItem(list_item)

        # Adjust height based on item count
        item_count = min(self.list_widget.count(), 8)
        if item_count > 0:
            row_height = self.list_widget.sizeHintForRow(0)
            self.setFixedHeight(row_height * item_count + 4)

    def filter(self, text: str) -> None:
        """Filter items by text."""
        self._filter_text = text.lower()
        self._update_list()

        if self.list_widget.count() == 0:
            self.hide()

    def move_selection(self, delta: int) -> None:
        """Move selection up or down."""
        current = self.list_widget.currentRow()
        new_row = max(0, min(current + delta, self.list_widget.count() - 1))
        self.list_widget.setCurrentRow(new_row)

    def get_selected(self) -> Optional[str]:
        """Get currently selected item text."""
        current = self.list_widget.currentItem()
        if current:
            return current.text()
        return None

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        """Handle item click."""
        if self._callback and item:
            self._callback(item.text())
        self.hide()

    def select_current(self) -> None:
        """Select current item and trigger callback."""
        selected = self.get_selected()
        if selected and self._callback:
            self._callback(selected)
        self.hide()


class LineEditCompleter:
    """
    Attaches variable completion to a QLineEdit.
    Shows popup when user types '{' and inserts '{VariableName} ' on selection.
    """

    def __init__(self, line_edit: QLineEdit):
        self.line_edit = line_edit
        self.popup = VariableCompleterPopup()
        self._variables: List[str] = []
        self._trigger_pos: int = -1

        # Install event filter
        self.line_edit.installEventFilter(self)
        self.line_edit.textChanged.connect(self._on_text_changed)

        # Set callback
        self.popup.set_callback(self._insert_variable)

    def eventFilter(self, obj, event) -> bool:
        """Handle key events for the line edit."""
        if obj != self.line_edit:
            return False

        if event.type() == QEvent.KeyPress:
            key = event.key()

            if self.popup.isVisible():
                if key == Qt.Key_Escape:
                    self.popup.hide()
                    self._trigger_pos = -1
                    return True
                elif key == Qt.Key_Return or key == Qt.Key_Enter:
                    self.popup.select_current()
                    return True
                elif key == Qt.Key_Up:
                    self.popup.move_selection(-1)
                    return True
                elif key == Qt.Key_Down:
                    self.popup.move_selection(1)
                    return True

        elif event.type() == QEvent.FocusOut:
            # Delay hide to allow click on popup
            QTimer.singleShot(100, self._check_hide_popup)

        return False

    def _check_hide_popup(self) -> None:
        """Hide popup if line edit lost focus."""
        if not self.line_edit.hasFocus():
            self.popup.hide()
            self._trigger_pos = -1

    def set_variables(self, variables: List[str]) -> None:
        """Set available variables for completion."""
        self._variables = variables
        self.popup.set_items(variables)

    def _on_text_changed(self, text: str) -> None:
        """Handle text changes to detect '{' and filter."""
        cursor_pos = self.line_edit.cursorPosition()

        # Check if we're typing after '{'
        if self._trigger_pos >= 0:
            # Get text between { and cursor
            if cursor_pos > self._trigger_pos:
                filter_text = text[self._trigger_pos + 1:cursor_pos]

                # Check if user typed '}' or moved before '{'
                if '}' in filter_text or cursor_pos <= self._trigger_pos:
                    self.popup.hide()
                    self._trigger_pos = -1
                else:
                    self.popup.filter(filter_text)
                    self._position_popup()
            else:
                self.popup.hide()
                self._trigger_pos = -1

        # Check for new '{' trigger
        if cursor_pos > 0 and text[cursor_pos - 1] == '{':
            self._trigger_pos = cursor_pos - 1
            self.popup.show_popup("")
            self._position_popup()

    def _position_popup(self) -> None:
        """Position popup below the cursor."""
        if not self.popup.isVisible():
            return

        # Get cursor rectangle
        rect = self.line_edit.cursorRect()
        global_pos = self.line_edit.mapToGlobal(rect.bottomLeft())

        # Offset slightly
        global_pos.setY(global_pos.y() + 2)

        self.popup.move(global_pos)

    def _insert_variable(self, var_name: str) -> None:
        """Insert variable at trigger position."""
        if self._trigger_pos < 0:
            return

        text = self.line_edit.text()
        cursor_pos = self.line_edit.cursorPosition()

        # Replace from trigger position to cursor with {VarName}
        before = text[:self._trigger_pos]
        after = text[cursor_pos:]
        new_text = before + "{" + var_name + "} " + after

        self.line_edit.setText(new_text)
        self.line_edit.setCursorPosition(self._trigger_pos + len(var_name) + 3)

        self._trigger_pos = -1


class TextEditCompleter:
    """
    Attaches variable completion to a QTextEdit.
    Shows popup when user types '{' and inserts '{VariableName} ' on selection.
    """

    def __init__(self, text_edit: QTextEdit):
        self.text_edit = text_edit
        self.popup = VariableCompleterPopup()
        self._variables: List[str] = []
        self._trigger_pos: int = -1
        self._active = False

        # Install event filter
        self.text_edit.installEventFilter(self)
        self.text_edit.textChanged.connect(self._on_text_changed)

        # Set callback
        self.popup.set_callback(self._insert_variable)

    def eventFilter(self, obj, event) -> bool:
        """Handle key events for the text edit."""
        if obj != self.text_edit:
            return False

        if event.type() == QEvent.KeyPress:
            key = event.key()

            if self.popup.isVisible():
                if key == Qt.Key_Escape:
                    self.popup.hide()
                    self._trigger_pos = -1
                    self._active = False
                    return True
                elif key == Qt.Key_Return or key == Qt.Key_Enter:
                    self.popup.select_current()
                    return True
                elif key == Qt.Key_Up:
                    self.popup.move_selection(-1)
                    return True
                elif key == Qt.Key_Down:
                    self.popup.move_selection(1)
                    return True

            # Detect { key press
            if event.text() == '{':
                self._active = True
                # Let the key be processed first, then show popup
                QTimer.singleShot(10, self._show_popup_after_brace)

        elif event.type() == QEvent.FocusOut:
            QTimer.singleShot(100, self._check_hide_popup)

        return False

    def _check_hide_popup(self) -> None:
        """Hide popup if text edit lost focus."""
        if not self.text_edit.hasFocus():
            self.popup.hide()
            self._trigger_pos = -1
            self._active = False

    def _show_popup_after_brace(self) -> None:
        """Show popup after { is inserted."""
        if not self._active:
            return

        cursor = self.text_edit.textCursor()
        self._trigger_pos = cursor.position() - 1
        self.popup.show_popup("")
        self._position_popup()

    def set_variables(self, variables: List[str]) -> None:
        """Set available variables for completion."""
        self._variables = variables
        self.popup.set_items(variables)

    def _on_text_changed(self) -> None:
        """Handle text changes to filter popup."""
        if not self._active or self._trigger_pos < 0:
            return

        cursor = self.text_edit.textCursor()
        cursor_pos = cursor.position()

        if cursor_pos <= self._trigger_pos:
            self.popup.hide()
            self._trigger_pos = -1
            self._active = False
            return

        # Get text from document
        doc = self.text_edit.document()
        full_text = doc.toPlainText()

        # Get filter text between { and cursor
        if self._trigger_pos < len(full_text):
            filter_text = full_text[self._trigger_pos + 1:cursor_pos]

            # Check if user typed '}' or newline
            if '}' in filter_text or '\n' in filter_text:
                self.popup.hide()
                self._trigger_pos = -1
                self._active = False
            else:
                self.popup.filter(filter_text)
                self._position_popup()

    def _position_popup(self) -> None:
        """Position popup below the cursor."""
        if not self.popup.isVisible():
            return

        cursor = self.text_edit.textCursor()
        rect = self.text_edit.cursorRect(cursor)
        global_pos = self.text_edit.mapToGlobal(rect.bottomLeft())

        # Offset slightly
        global_pos.setY(global_pos.y() + 2)

        self.popup.move(global_pos)

    def _insert_variable(self, var_name: str) -> None:
        """Insert variable at trigger position."""
        if self._trigger_pos < 0:
            return

        cursor = self.text_edit.textCursor()

        # Select from after { to current position
        cursor.setPosition(self._trigger_pos + 1)
        cursor.setPosition(
            self.text_edit.textCursor().position(),
            cursor.KeepAnchor
        )

        # Replace with variable name and closing brace + space
        cursor.insertText(var_name + "} ")

        self._trigger_pos = -1
        self._active = False
