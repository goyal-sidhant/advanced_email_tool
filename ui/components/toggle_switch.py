"""
Advanced Email Tool - iOS-Style Toggle Switch Components
========================================================
Custom toggle switch widgets with smooth animations.
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty, QSize
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush


class ToggleSwitch(QWidget):
    """
    iOS-style toggle switch widget.

    A sliding toggle that changes between ON (green) and OFF (gray) states
    with smooth animation.
    """

    toggled = pyqtSignal(bool)

    # Colors
    COLOR_ON = QColor("#34C759")  # iOS green
    COLOR_OFF = QColor("#E9E9EB")  # iOS gray
    COLOR_THUMB = QColor("#FFFFFF")  # White thumb
    COLOR_DISABLED = QColor("#CCCCCC")

    def __init__(self, parent=None):
        """Initialize the toggle switch."""
        super().__init__(parent)

        self._checked = False
        self._thumb_position = 0.0  # 0.0 = left (off), 1.0 = right (on)

        # Size
        self._width = 50
        self._height = 26
        self._thumb_margin = 2

        self.setFixedSize(self._width, self._height)
        self.setCursor(Qt.PointingHandCursor)

        # Animation
        self._animation = QPropertyAnimation(self, b"thumbPosition", self)
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.InOutCubic)

    def sizeHint(self) -> QSize:
        """Return the preferred size."""
        return QSize(self._width, self._height)

    def minimumSizeHint(self) -> QSize:
        """Return the minimum size."""
        return QSize(self._width, self._height)

    @pyqtProperty(float)
    def thumbPosition(self) -> float:
        """Get thumb position (0.0 to 1.0)."""
        return self._thumb_position

    @thumbPosition.setter
    def thumbPosition(self, pos: float) -> None:
        """Set thumb position and trigger repaint."""
        self._thumb_position = pos
        self.update()

    def isChecked(self) -> bool:
        """Return whether the switch is checked (ON)."""
        return self._checked

    def setChecked(self, checked: bool) -> None:
        """Set the checked state with animation."""
        if self._checked != checked:
            self._checked = checked
            self._animate_thumb()
            self.toggled.emit(self._checked)

    def setCheckedNoSignal(self, checked: bool) -> None:
        """Set the checked state without emitting signal (for restore)."""
        if self._checked != checked:
            self._checked = checked
            # Set position directly without animation for instant restore
            self._thumb_position = 1.0 if checked else 0.0
            self.update()

    def toggle(self) -> None:
        """Toggle the switch state."""
        self.setChecked(not self._checked)

    def _animate_thumb(self) -> None:
        """Animate the thumb to the new position."""
        self._animation.stop()
        self._animation.setStartValue(self._thumb_position)
        self._animation.setEndValue(1.0 if self._checked else 0.0)
        self._animation.start()

    def mousePressEvent(self, event) -> None:
        """Handle mouse press to toggle."""
        if event.button() == Qt.LeftButton and self.isEnabled():
            self.toggle()

    def paintEvent(self, event) -> None:
        """Paint the toggle switch."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate dimensions
        rect_height = self._height
        rect_width = self._width
        radius = rect_height / 2

        # Background color interpolation
        if self.isEnabled():
            # Interpolate between off and on colors based on thumb position
            r = int(self.COLOR_OFF.red() + (self.COLOR_ON.red() - self.COLOR_OFF.red()) * self._thumb_position)
            g = int(self.COLOR_OFF.green() + (self.COLOR_ON.green() - self.COLOR_OFF.green()) * self._thumb_position)
            b = int(self.COLOR_OFF.blue() + (self.COLOR_ON.blue() - self.COLOR_OFF.blue()) * self._thumb_position)
            bg_color = QColor(r, g, b)
        else:
            bg_color = self.COLOR_DISABLED

        # Draw background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(0, 0, rect_width, rect_height, radius, radius)

        # Calculate thumb position
        thumb_diameter = rect_height - (self._thumb_margin * 2)
        max_x = rect_width - thumb_diameter - self._thumb_margin
        thumb_x = self._thumb_margin + (max_x - self._thumb_margin) * self._thumb_position
        thumb_y = self._thumb_margin

        # Draw thumb shadow
        if self.isEnabled():
            shadow_color = QColor(0, 0, 0, 30)
            painter.setBrush(QBrush(shadow_color))
            painter.drawEllipse(int(thumb_x) + 1, int(thumb_y) + 1, thumb_diameter, thumb_diameter)

        # Draw thumb
        thumb_color = self.COLOR_THUMB if self.isEnabled() else QColor("#F0F0F0")
        painter.setBrush(QBrush(thumb_color))
        painter.drawEllipse(int(thumb_x), int(thumb_y), thumb_diameter, thumb_diameter)

        painter.end()


class LabeledToggleSwitch(QWidget):
    """
    Toggle switch with labels on both sides for binary choices.

    Example: "OR (Either)" [toggle] "AND (Both)"
    When unchecked: left option selected
    When checked: right option selected
    """

    toggled = pyqtSignal(bool)

    def __init__(self, left_label: str, right_label: str, parent=None):
        """
        Initialize labeled toggle switch.

        Args:
            left_label: Text for left/unchecked option
            right_label: Text for right/checked option
        """
        super().__init__(parent)

        self._left_label = left_label
        self._right_label = right_label

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Left label
        self._left_widget = QLabel(self._left_label)
        self._left_widget.setStyleSheet("font-weight: bold;")
        layout.addWidget(self._left_widget)

        # Toggle switch
        self._toggle = ToggleSwitch()
        self._toggle.toggled.connect(self._on_toggled)
        layout.addWidget(self._toggle)

        # Right label
        self._right_widget = QLabel(self._right_label)
        self._right_widget.setStyleSheet("color: gray;")
        layout.addWidget(self._right_widget)

        layout.addStretch()

        # Update label styles
        self._update_label_styles()

    def _on_toggled(self, checked: bool) -> None:
        """Handle toggle state change."""
        self._update_label_styles()
        self.toggled.emit(checked)

    def _update_label_styles(self) -> None:
        """Update label styles based on toggle state."""
        if self._toggle.isChecked():
            # Right option selected
            self._left_widget.setStyleSheet("color: gray;")
            self._right_widget.setStyleSheet("font-weight: bold;")
        else:
            # Left option selected
            self._left_widget.setStyleSheet("font-weight: bold;")
            self._right_widget.setStyleSheet("color: gray;")

    def isChecked(self) -> bool:
        """Return whether right option is selected."""
        return self._toggle.isChecked()

    def setChecked(self, checked: bool) -> None:
        """Set toggle state (True = right option)."""
        self._toggle.setChecked(checked)

    def setCheckedNoSignal(self, checked: bool) -> None:
        """Set toggle state without emitting signal."""
        self._toggle.setCheckedNoSignal(checked)
        self._update_label_styles()

    def setEnabled(self, enabled: bool) -> None:
        """Enable or disable the widget."""
        super().setEnabled(enabled)
        self._toggle.setEnabled(enabled)
        self._left_widget.setEnabled(enabled)
        self._right_widget.setEnabled(enabled)
