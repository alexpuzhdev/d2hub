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
        self._warning_blink_left = 0
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

        self.now = QtWidgets.QLabel(
            "ГОТОВО  |  F8 СТАРТ  F9 СТОП  F10 СБРОС  F7 БЛОК"
        )
        self._configure_block_label(self.now, self._style.font_size)

        self.next = QtWidgets.QLabel("ДАЛЕЕ: —")
        self._configure_block_label(self.next, self._style.font_size)

        self.after = QtWidgets.QLabel("")
        self._configure_block_label(self.after, self._style.font_size)
        self.after.setVisible(False)

        layout.addWidget(self.timer)
        layout.addWidget(self.warning)
        layout.addWidget(self.now)
        layout.addWidget(self.next)
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
        size: int,
        weight: str | None = None,
    ) -> None:
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        label.setFont(self._font(size, weight))
        label.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

    def _apply_text_colors(self) -> None:
        self.timer.setStyleSheet(self._label_style(self._colors.text_primary))
        self.now.setStyleSheet(self._label_style(self._colors.text_primary))
        self.next.setStyleSheet(self._label_style(self._colors.text_next))
        self.after.setStyleSheet(self._label_style(self._colors.text_primary))
        if self._warning_level == "danger":
            warning_color = self._colors.text_danger
        elif self._warning_level == "warn":
            warning_color = self._colors.text_warning
        elif self._warning_level == "info":
            warning_color = self._colors.text_info
        else:
            warning_color = self._colors.text_primary
        self.warning.setStyleSheet(self._label_style(warning_color))

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)

        rect = self.rect()

        base = QtGui.QColor(self._colors.background_base)
        max_alpha = int(255 * 0.6)  # стартовая прозрачность

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
            QtGui.QColor(base.red(), base.green(), base.blue(), int(max_alpha * 0.3)),
        )

        # справа — НОЛЬ
        gradient.setColorAt(
            1.0,
            QtGui.QColor(base.red(), base.green(), base.blue(), 0),
        )

        painter.fillRect(rect, gradient)
        painter.end()

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

    def set_warning(
        self,
        text: str | None,
        level: str | None = None,
        blink: bool = False,
    ) -> None:
        """Обновляет визуальный уровень предупреждения."""
        self.warning.setText(text or "")
        if level is None and isinstance(text, bool):
            self._warning_level = "warn" if text else ""
        else:
            self._warning_level = str(level or "")
        self._apply_text_colors()
        if blink:
            self._start_warning_blink()
        self.update()

    def _start_warning_blink(self) -> None:
        self._warning_blink_left = 4
        self._blink_warning()

    def _blink_warning(self) -> None:
        if self._warning_blink_left <= 0:
            self.warning.setVisible(True)
            return
        self.warning.setVisible(not self.warning.isVisible())
        self._warning_blink_left -= 1
        QtCore.QTimer.singleShot(150, self._blink_warning)

    def set_timer(self, text: str) -> None:
        """Обновляет текст таймера."""
        self.timer.setText(text)

    def set_now(self, text: str) -> None:
        """Обновляет блок NOW."""
        self.now.setText(text)

    def set_next(self, text: str) -> None:
        """Обновляет блок NEXT."""
        self.next.setText(text)

    def set_after(self, text: str) -> None:
        """Обновляет блок AFTER."""
        self.after.setText(text)

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
