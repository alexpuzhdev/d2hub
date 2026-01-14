from __future__ import annotations

from typing import Callable, Optional

from PySide6 import QtCore, QtGui, QtWidgets

from ..hud_style import HudStyle
from .styles import default_colors


class HudQt(QtWidgets.QWidget):
    def __init__(self, style: HudStyle) -> None:
        self._app = QtWidgets.QApplication.instance()
        if self._app is None:
            self._app = QtWidgets.QApplication([])

        super().__init__()

        self._style = style
        self._colors = default_colors()
        self._is_warn = False
        self._locked = False
        self._drag_enabled = True
        self._drag_offset = QtCore.QPoint()
        self._on_close: Optional[Callable[[], None]] = None
        self._closing = False

        self._configure_window()
        self._build_layout()

    def _configure_window(self) -> None:
        self.setWindowTitle(self._style.title)
        flags = (
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.Tool
        )
        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.resize(self._style.width, self._style.height)
        self.move(self._style.x, self._style.y)

    def _build_layout(self) -> None:
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        self.timer = QtWidgets.QLabel("0:00")
        self.timer.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.timer.setFont(self._font(self._style.font_size + 10, "bold"))
        self.timer.setStyleSheet(self._label_style(self._colors.text_primary))

        self.now = QtWidgets.QLabel(
            "READY  |  F8 START  F9 STOP  F10 RESET  F7 LOCK"
        )
        self._configure_block_label(self.now, self._colors.text_muted, self._style.font_size)

        self.next = QtWidgets.QLabel("NEXT: —")
        self._configure_block_label(self.next, self._colors.text_primary, self._style.font_size)

        self.after = QtWidgets.QLabel("AFTER: —")
        self._configure_block_label(
            self.after,
            self._colors.text_muted,
            max(10, self._style.font_size - 1),
            weight="normal",
        )

        layout.addWidget(self.timer)
        layout.addWidget(self.now)
        layout.addWidget(self.next)
        layout.addWidget(self.after)
        layout.addStretch(1)

        self.setLayout(layout)

    def _font(self, size: int, weight: str | None = None) -> QtGui.QFont:
        font = QtGui.QFont(self._style.font_family)
        font.setPointSize(size)
        weight_value = self._weight_from_string(weight or self._style.font_weight)
        font.setWeight(weight_value)
        return font

    @staticmethod
    def _weight_from_string(weight: str) -> int:
        if weight.lower() == "bold":
            return QtGui.QFont.Weight.Bold
        return QtGui.QFont.Weight.Normal

    @staticmethod
    def _label_style(color: QtGui.QColor) -> str:
        return (
            "QLabel {"
            f"color: rgba({color.red()}, {color.green()}, {color.blue()}, 255);"
            "background: transparent;"
            "}"
        )

    def _configure_block_label(
        self,
        label: QtWidgets.QLabel,
        color: QtGui.QColor,
        size: int,
        weight: str | None = None,
    ) -> None:
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        label.setFont(self._font(size, weight))
        label.setStyleSheet(self._label_style(color))
        label.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        rect = self.rect()
        base_color = (
            self._colors.background_warn if self._is_warn else self._colors.background_normal
        )
        max_alpha = max(0, min(255, int(255 * self._style.alpha)))
        left_alpha = max(0, min(255, int(max_alpha * 0.4)))
        right_alpha = max(0, min(255, int(max_alpha * 0.9)))

        left = QtGui.QColor(base_color)
        right = QtGui.QColor(base_color)
        left.setAlpha(left_alpha)
        right.setAlpha(right_alpha)

        gradient = QtGui.QLinearGradient(rect.left(), rect.top(), rect.right(), rect.top())
        gradient.setColorAt(0.0, left)
        gradient.setColorAt(1.0, right)

        painter.fillRect(rect, gradient)
        painter.end()
        super().paintEvent(event)

    def _set_clickthrough(self, enabled: bool) -> None:
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, enabled)
        self.setWindowFlag(QtCore.Qt.WindowTransparentForInput, enabled)
        self.show()

    def set_drag_enabled(self, enabled: bool) -> None:
        self._drag_enabled = bool(enabled)

    def toggle_lock(self) -> None:
        self.set_lock(not self._locked)

    def set_lock(self, enabled: bool) -> None:
        enabled = bool(enabled)
        self._locked = enabled
        self.set_drag_enabled(not enabled)
        self._set_clickthrough(enabled)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if not self._drag_enabled or event.button() != QtCore.Qt.LeftButton:
            super().mousePressEvent(event)
            return
        self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        event.accept()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if not self._drag_enabled or not (event.buttons() & QtCore.Qt.LeftButton):
            super().mouseMoveEvent(event)
            return
        self.move(event.globalPosition().toPoint() - self._drag_offset)
        event.accept()

    def set_warning(self, is_warn: bool | str) -> None:
        self._is_warn = bool(is_warn)
        self.update()

    def set_timer(self, text: str) -> None:
        self.timer.setText(text)

    def set_now(self, text: str) -> None:
        self.now.setText(text)

    def set_next(self, text: str) -> None:
        self.next.setText(text)

    def set_after(self, text: str) -> None:
        self.after.setText(text)

    def every(self, ms: int, fn: Callable[[], None]) -> None:
        QtCore.QTimer.singleShot(ms, fn)

    def set_on_close(self, callback: Callable[[], None]) -> None:
        self._on_close = callback

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self._closing:
            event.accept()
            return
        if self._on_close:
            self._on_close()
        event.ignore()

    def run(self) -> None:
        self.show()
        self._app.exec()

    def close(self) -> None:
        self._closing = True
        self._app.quit()
        super().close()
