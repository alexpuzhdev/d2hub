from __future__ import annotations

from typing import Callable, Optional

from PySide6 import QtCore, QtGui, QtWidgets

from ..base import HudBase
from ..hud_style import HudStyle
from .app import QtApp
from .styles import HudColors, default_colors


class HudQt(QtWidgets.QWidget, HudBase):
    def __init__(self, style: HudStyle, app: QtApp | None = None) -> None:
        self._qt_app = app or QtApp()
        super().__init__()

        self._style = style
        self._colors = default_colors()
        self._warning_level = ""
        self._locked = False
        self._drag_enabled = True
        self._drag_offset = QtCore.QPoint()
        self._on_close: Optional[Callable[[], None]] = None
        self._closing = False
        self._fade_animation: Optional[QtCore.QPropertyAnimation] = None
        self._scale = self._resolve_scale()

        self._configure_window()
        self._build_layout()
        self._apply_theme()

    def _resolve_scale(self) -> float:
        screen = QtGui.QGuiApplication.primaryScreen()
        if not screen:
            return 1.0
        height = screen.availableGeometry().height()
        return max(0.9, min(1.35, height / 1080.0))

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
        self.setWindowOpacity(1.0)

    def _build_layout(self) -> None:
        layout = QtWidgets.QVBoxLayout()
        margin = int(18 * self._scale)
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(int(10 * self._scale))

        header = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(int(10 * self._scale))

        self.timer = QtWidgets.QLabel("0:00")
        self.timer.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.timer.setFont(self._font(self._style.font_size + 12, "bold"))

        self.backend_badge = QtWidgets.QLabel("PYSide6 HUD")
        self.backend_badge.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.backend_badge.setFont(self._font(max(9, self._style.font_size - 4), "bold"))

        header_layout.addWidget(self.timer, 1)
        header_layout.addWidget(self.backend_badge, 0)

        self.now_card, self.now_accent, self.now_title, self.now = self._build_card(
            "NOW",
            "READY  |  F8 START  F9 STOP  F10 RESET  F7 LOCK",
        )
        self.next_card, self.next_accent, self.next_title, self.next = self._build_card(
            "NEXT",
            "NEXT: —",
        )
        self.after_card, self.after_accent, self.after_title, self.after = self._build_card(
            "AFTER",
            "AFTER: —",
            muted=True,
        )

        layout.addWidget(header)
        layout.addWidget(self.now_card)
        layout.addWidget(self.next_card)
        layout.addWidget(self.after_card)
        layout.addStretch(1)

        self.setLayout(layout)

    def _build_card(
        self,
        title: str,
        body: str,
        muted: bool = False,
    ) -> tuple[QtWidgets.QFrame, QtWidgets.QFrame, QtWidgets.QLabel, QtWidgets.QLabel]:
        card = QtWidgets.QFrame()
        card.setObjectName("hudCard")
        card_layout = QtWidgets.QHBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(int(10 * self._scale))

        accent = QtWidgets.QFrame()
        accent.setFixedWidth(max(3, int(4 * self._scale)))
        accent.setObjectName("hudAccent")

        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(
            int(12 * self._scale),
            int(10 * self._scale),
            int(12 * self._scale),
            int(10 * self._scale),
        )
        content_layout.setSpacing(int(6 * self._scale))

        title_label = QtWidgets.QLabel(title)
        title_label.setFont(self._font(max(9, self._style.font_size - 4), "bold"))
        title_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        body_label = QtWidgets.QLabel(body)
        body_label.setWordWrap(True)
        body_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        body_label.setFont(self._font(self._style.font_size + (0 if muted else 1), "bold"))

        content_layout.addWidget(title_label)
        content_layout.addWidget(body_label)

        card_layout.addWidget(accent)
        card_layout.addWidget(content, 1)

        return card, accent, title_label, body_label

    def _font(self, size: int, weight: str | None = None) -> QtGui.QFont:
        font = QtGui.QFont()
        font.setFamilies(
            [
                self._style.font_family,
                "Rajdhani",
                "Exo 2",
                "Segoe UI",
                "Arial",
            ]
        )
        font.setPointSize(max(8, int(size * self._scale)))
        weight_value = self._weight_from_string(weight or self._style.font_weight)
        font.setWeight(weight_value)
        return font

    @staticmethod
    def _weight_from_string(weight: str) -> int:
        if weight.lower() == "bold":
            return QtGui.QFont.Weight.Bold
        return QtGui.QFont.Weight.Normal

    def _apply_theme(self) -> None:
        accent = self._accent_color()
        muted = self._colors.text_muted
        primary = self._colors.text_primary

        self.timer.setStyleSheet(self._label_style(primary))
        self.backend_badge.setStyleSheet(
            "QLabel {"
            f"color: {self._rgba(primary, 0.92)};"
            f"background-color: {self._rgba(self._colors.panel_alt, 0.9)};"
            f"border: 1px solid {self._rgba(accent, 0.6)};"
            f"border-radius: {int(10 * self._scale)}px;"
            f"padding: {int(4 * self._scale)}px {int(10 * self._scale)}px;"
            "letter-spacing: 1px;"
            "}"
        )

        for title in (self.now_title, self.next_title, self.after_title):
            title.setStyleSheet(self._label_style(muted))
        self.now.setStyleSheet(self._label_style(primary))
        self.next.setStyleSheet(self._label_style(primary))
        self.after.setStyleSheet(self._label_style(muted))

        for card, accent_bar in (
            (self.now_card, self.now_accent),
            (self.next_card, self.next_accent),
            (self.after_card, self.after_accent),
        ):
            card.setStyleSheet(self._card_style(accent))
            accent_bar.setStyleSheet(
                "QFrame {"
                f"background-color: {self._rgba(accent, 0.95)};"
                f"border-radius: {int(6 * self._scale)}px;"
                "}"
            )

        self.update()

    def _card_style(self, accent: QtGui.QColor) -> str:
        return (
            "QFrame#hudCard {"
            f"background-color: {self._rgba(self._colors.panel, 0.9)};"
            f"border: 1px solid {self._rgba(accent, 0.25)};"
            f"border-radius: {int(12 * self._scale)}px;"
            "}"
        )

    @staticmethod
    def _rgba(color: QtGui.QColor, alpha: float) -> str:
        return f"rgba({color.red()}, {color.green()}, {color.blue()}, {int(alpha * 255)})"

    def _accent_color(self) -> QtGui.QColor:
        if self._warning_level == "danger":
            return self._colors.accent_danger
        if self._warning_level == "warn":
            return self._colors.accent_warn
        return self._colors.accent_info

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        rect = self.rect()
        top_color = self._colors.background_top
        bottom_color = self._colors.background_bottom

        if self._warning_level == "danger":
            top_color = self._mix(top_color, self._colors.accent_danger, 0.18)
            bottom_color = self._mix(bottom_color, self._colors.accent_danger, 0.1)
        elif self._warning_level == "warn":
            top_color = self._mix(top_color, self._colors.accent_warn, 0.16)
            bottom_color = self._mix(bottom_color, self._colors.accent_warn, 0.08)

        max_alpha = max(0, min(255, int(255 * self._style.alpha)))
        top = QtGui.QColor(top_color)
        bottom = QtGui.QColor(bottom_color)
        top.setAlpha(max_alpha)
        bottom.setAlpha(max(0, min(255, int(max_alpha * 0.95))))

        gradient = QtGui.QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
        gradient.setColorAt(0.0, top)
        gradient.setColorAt(1.0, bottom)

        path = QtGui.QPainterPath()
        radius = int(16 * self._scale)
        path.addRoundedRect(rect.adjusted(1, 1, -1, -1), radius, radius)
        painter.fillPath(path, gradient)
        painter.end()
        super().paintEvent(event)

    @staticmethod
    def _mix(color: QtGui.QColor, accent: QtGui.QColor, ratio: float) -> QtGui.QColor:
        ratio = max(0.0, min(1.0, ratio))
        red = int(color.red() + (accent.red() - color.red()) * ratio)
        green = int(color.green() + (accent.green() - color.green()) * ratio)
        blue = int(color.blue() + (accent.blue() - color.blue()) * ratio)
        return QtGui.QColor(red, green, blue)

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
        level = ""
        if isinstance(is_warn, str):
            level = is_warn.strip().lower()
            if level not in {"danger", "warn", "info"}:
                level = "warn" if level else ""
        elif is_warn:
            level = "warn"
        self._warning_level = level
        self._apply_theme()

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

    def _animate_opacity(self, start: float, end: float, duration: int) -> None:
        animation = QtCore.QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self._fade_animation = animation
        animation.start()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self._closing:
            event.accept()
            return
        if self._on_close:
            self._on_close()
        event.ignore()

    def run(self) -> None:
        self.setWindowOpacity(0.0)
        self.show()
        self._animate_opacity(0.0, 1.0, int(220 * self._scale))
        self._qt_app.exec()

    def close(self) -> None:
        if self._closing:
            return
        self._closing = True

        def finalize() -> None:
            self._qt_app.quit()
            super().close()

        animation = QtCore.QPropertyAnimation(self, b"windowOpacity")
        animation.setDuration(int(180 * self._scale))
        animation.setStartValue(self.windowOpacity())
        animation.setEndValue(0.0)
        animation.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        animation.finished.connect(finalize)
        self._fade_animation = animation
        animation.start()
