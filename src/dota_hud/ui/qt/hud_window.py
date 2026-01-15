from __future__ import annotations

from typing import Callable, Optional

from PySide6 import QtCore, QtGui, QtWidgets

from ..hud_style import HudStyle
from .styles import default_colors


class HudQt(QtWidgets.QWidget):
    """Окно HUD на базе PySide6."""

    def __init__(self, style: HudStyle) -> None:
        """Создаёт окно HUD."""
        self._app = QtWidgets.QApplication.instance()
        if self._app is None:
            self._app = QtWidgets.QApplication([])

        super().__init__()

        self._style = style
        self._colors = default_colors()
        self._warning_level = ""
        self._warning_overlay_strength = 0.0
        self._warning_anim: Optional[QtCore.QPropertyAnimation] = None
        self._locked = False
        self._drag_enabled = True
        self._drag_offset = QtCore.QPoint()
        self._on_close: Optional[Callable[[], None]] = None
        self._closing = False

        self._configure_window()
        self._build_layout()
        self._apply_text_colors()

    def _configure_window(self) -> None:
        self.setWindowTitle(self._style.title)
        flags = (
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.Tool
            | QtCore.Qt.WindowDoesNotAcceptFocus
        )
        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.resize(self._style.width, self._style.height)
        self.move(self._style.x, self._style.y)

    def _build_layout(self) -> None:
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        self.timer = QtWidgets.QLabel("0:00")
        self.timer.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.timer.setFont(self._font(self._style.font_size + 12, "bold"))

        self.warning = QtWidgets.QLabel("")
        self._configure_block_label(self.warning, self._style.font_size)

        self.now = QtWidgets.QLabel("ГОТОВО  |  F7 LOCK")
        self._configure_block_label(self.now, self._style.font_size)

        self.next = QtWidgets.QLabel("ДАЛЕЕ: —")
        self._configure_block_label(self.next, self._style.font_size)

        self.macro = QtWidgets.QLabel("MACRO: —")
        self._configure_block_label(self.macro, self._style.font_size)

        layout.addWidget(self.timer)
        layout.addWidget(self.warning)
        layout.addWidget(self.now)
        layout.addWidget(self.next)
        layout.addWidget(self.macro)
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
    def _rgba(color: QtGui.QColor, alpha: int | None = None) -> str:
        alpha_value = color.alpha() if alpha is None else alpha
        return f"rgba({color.red()}, {color.green()}, {color.blue()}, {alpha_value})"

    def _label_style(
        self,
        color: QtGui.QColor,
        background: QtGui.QColor | None = None,
        background_alpha: int | None = None,
        padding: int = 0,
    ) -> str:
        background_style = ""
        if background is not None:
            background_style = (
                f"background-color: {self._rgba(background, background_alpha)};"
                "border-radius: 4px;"
            )
        padding_style = f"padding: {padding}px;" if padding else ""
        return (
            "QLabel {"
            f"color: {self._rgba(color)};"
            f"{background_style}"
            f"{padding_style}"
            "}"
        )

    def _configure_block_label(
        self,
        label: QtWidgets.QLabel,
        size: int,
        weight: str | None = None,
    ) -> None:
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        label.setFont(self._font(size, weight))
        label.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        label.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)

    def _apply_text_colors(self) -> None:
        self.timer.setStyleSheet(self._label_style(self._colors.text_primary))
        self.now.setStyleSheet(
            self._label_style(
                self._colors.text_primary,
                background=self._colors.block_background,
                background_alpha=140,
                padding=6,
            )
        )
        self.next.setStyleSheet(
            self._label_style(
                self._colors.text_next,
                background=self._colors.block_background,
                background_alpha=120,
                padding=6,
            )
        )
        self.macro.setStyleSheet(
            self._label_style(
                self._colors.text_primary,
                background=self._colors.block_background,
                background_alpha=120,
                padding=6,
            )
        )
        if self._warning_level == "danger":
            warning_color = self._colors.text_danger
            warning_bg = self._colors.warning_block_danger
            warning_bg_alpha = 140
        elif self._warning_level == "warn":
            warning_color = self._colors.text_warning
            warning_bg = self._colors.warning_block_warn
            warning_bg_alpha = 120
        elif self._warning_level == "info":
            warning_color = self._colors.text_info
            warning_bg = self._colors.block_background
            warning_bg_alpha = 90
        else:
            warning_color = self._colors.text_primary
            warning_bg = None
            warning_bg_alpha = None
        self.warning.setStyleSheet(
            self._label_style(
                warning_color,
                background=warning_bg,
                background_alpha=warning_bg_alpha,
                padding=6,
            )
        )

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)

        rect = self.rect()

        base = QtGui.QColor(self._colors.background_base)
        max_alpha = int(255 * self._style.alpha)  # стартовая прозрачность

        gradient = QtGui.QLinearGradient(
            rect.left(),
            0,
            rect.right(),
            0,
        )

        # слева — читаемо
        gradient.setColorAt(
            0.0,
            QtGui.QColor(base.red(), base.green(), base.blue(), max_alpha),
        )

        # середина — уже почти нет
        gradient.setColorAt(
            0.7,
            QtGui.QColor(base.red(), base.green(), base.blue(), int(max_alpha * 0.15)),
        )

        # справа — НОЛЬ
        gradient.setColorAt(
            1.0,
            QtGui.QColor(base.red(), base.green(), base.blue(), 0),
        )

        painter.fillRect(rect, gradient)

        overlay_strength = self._warning_overlay_strength
        if overlay_strength > 0:
            if self._warning_level == "danger":
                overlay_color = self._colors.warning_overlay_danger
            elif self._warning_level == "warn":
                overlay_color = self._colors.warning_overlay_warn
            elif self._warning_level == "info":
                overlay_color = self._colors.block_background
            else:
                overlay_color = None
        if overlay_strength > 0 and overlay_color is not None:
            overlay_alpha = min(255, int(max_alpha * overlay_strength))
            overlay_gradient = QtGui.QLinearGradient(
                rect.left(),
                0,
                rect.right(),
                0,
            )
            overlay_gradient.setColorAt(
                0.0,
                QtGui.QColor(
                    overlay_color.red(),
                    overlay_color.green(),
                    overlay_color.blue(),
                    overlay_alpha,
                ),
            )
            overlay_gradient.setColorAt(
                0.7,
                QtGui.QColor(
                    overlay_color.red(),
                    overlay_color.green(),
                    overlay_color.blue(),
                    int(overlay_alpha * 0.15),
                ),
            )
            overlay_gradient.setColorAt(
                1.0,
                QtGui.QColor(
                    overlay_color.red(),
                    overlay_color.green(),
                    overlay_color.blue(),
                    0,
                ),
            )
            painter.fillRect(rect, overlay_gradient)
        painter.end()

    def _target_overlay_strength(self) -> float:
        if self._warning_level == "danger":
            return 0.65
        if self._warning_level == "warn":
            return 0.45
        if self._warning_level == "info":
            return 0.2
        return 0.0

    def _animate_warning_overlay(self) -> None:
        target = self._target_overlay_strength()
        if self._warning_anim is None:
            self._warning_anim = QtCore.QPropertyAnimation(self, b"warningOverlayStrength")
            self._warning_anim.setDuration(450)
            self._warning_anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self._warning_anim.stop()
        self._warning_anim.setStartValue(self._warning_overlay_strength)
        self._warning_anim.setEndValue(target)
        self._warning_anim.start()

    @QtCore.Property(float)
    def warningOverlayStrength(self) -> float:
        return self._warning_overlay_strength

    @warningOverlayStrength.setter
    def warningOverlayStrength(self, value: float) -> None:
        self._warning_overlay_strength = max(0.0, min(1.0, float(value)))
        self.update()

    def _set_clickthrough(self, enabled: bool) -> None:
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, enabled)
        self.setWindowFlag(QtCore.Qt.WindowTransparentForInput, enabled)
        self.show()

    def set_drag_enabled(self, enabled: bool) -> None:
        """Включает или выключает перетаскивание окна."""
        self._drag_enabled = bool(enabled)

    def toggle_lock(self) -> None:
        """Переключает режим блокировки."""
        self.set_lock(not self._locked)

    def set_lock(self, enabled: bool) -> None:
        """Управляет блокировкой и кликом сквозь окно."""
        enabled = bool(enabled)
        self._locked = enabled
        self.set_drag_enabled(not enabled)
        self._set_clickthrough(enabled)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """Обрабатывает начало перетаскивания."""
        if not self._drag_enabled or event.button() != QtCore.Qt.LeftButton:
            super().mousePressEvent(event)
            return
        self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        event.accept()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        """Обрабатывает перемещение при перетаскивании."""
        if not self._drag_enabled or not (event.buttons() & QtCore.Qt.LeftButton):
            super().mouseMoveEvent(event)
            return
        self.move(event.globalPosition().toPoint() - self._drag_offset)
        event.accept()

    def set_warning(self, text: str | None, level: str | None = None) -> None:
        """Обновляет визуальный уровень предупреждения."""
        self.warning.setText(text or "")
        if level is None and isinstance(text, bool):
            self._warning_level = "warn" if text else ""
        else:
            self._warning_level = str(level or "")
        self._apply_text_colors()
        self._animate_warning_overlay()
        self.update()

    def set_timer(self, text: str) -> None:
        """Обновляет текст таймера."""
        self.timer.setText(text)

    def set_now(self, text: str) -> None:
        """Обновляет блок NOW."""
        self.now.setText(text)

    def set_next(self, text: str) -> None:
        """Обновляет блок NEXT."""
        self.next.setText(text)

    def set_macro(self, text: str) -> None:
        """Обновляет блок MACRO."""
        self.macro.setText(text)

    def every(self, ms: int, fn: Callable[[], None]) -> None:
        """Планирует повторный вызов функции через заданный интервал."""
        QtCore.QTimer.singleShot(ms, fn)

    def set_on_close(self, callback: Callable[[], None]) -> None:
        """Устанавливает обработчик закрытия окна."""
        self._on_close = callback

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """Обрабатывает закрытие окна."""
        if self._closing:
            event.accept()
            return
        if self._on_close:
            self._on_close()
        event.ignore()

    def run(self) -> None:
        """Запускает цикл обработки событий UI."""
        self.show()
        self._app.exec()

    def close(self) -> None:
        """Закрывает окно и завершает приложение."""
        self._closing = True
        self._app.quit()
        super().close()
