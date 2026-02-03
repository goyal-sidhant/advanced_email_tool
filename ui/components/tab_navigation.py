"""
Advanced Email Tool - Tab Navigation Component
==============================================
Reusable Previous/Next navigation buttons for tab pages.
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal


class TabNavigationBar(QWidget):
    """
    Navigation bar with Previous and Next buttons.

    Emits signals that can be connected to main window navigation.
    Place at the bottom of each tab for consistent navigation.
    """

    previous_clicked = pyqtSignal()
    next_clicked = pyqtSignal()

    def __init__(self, show_previous: bool = True, show_next: bool = True, parent=None):
        """
        Initialize navigation bar.

        Args:
            show_previous: Whether to show the Previous button
            show_next: Whether to show the Next button
            parent: Parent widget
        """
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 0)  # Top margin for spacing

        self.prev_btn = QPushButton("< Previous")
        self.prev_btn.setToolTip("Go to previous tab (Ctrl+Shift+Tab)")
        self.prev_btn.clicked.connect(self.previous_clicked.emit)
        self.prev_btn.setVisible(show_previous)
        layout.addWidget(self.prev_btn)

        layout.addStretch()

        self.next_btn = QPushButton("Next >")
        self.next_btn.setToolTip("Go to next tab (Ctrl+Tab)")
        self.next_btn.clicked.connect(self.next_clicked.emit)
        self.next_btn.setVisible(show_next)
        layout.addWidget(self.next_btn)

    def set_previous_enabled(self, enabled: bool) -> None:
        """Enable or disable the Previous button."""
        self.prev_btn.setEnabled(enabled)

    def set_next_enabled(self, enabled: bool) -> None:
        """Enable or disable the Next button."""
        self.next_btn.setEnabled(enabled)

    def set_previous_text(self, text: str) -> None:
        """Change the Previous button text."""
        self.prev_btn.setText(text)

    def set_next_text(self, text: str) -> None:
        """Change the Next button text."""
        self.next_btn.setText(text)

    def set_previous_visible(self, visible: bool) -> None:
        """Show or hide the Previous button."""
        self.prev_btn.setVisible(visible)

    def set_next_visible(self, visible: bool) -> None:
        """Show or hide the Next button."""
        self.next_btn.setVisible(visible)
