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
        self._warning_block_strength = 0.0
        self._warning_anim: Optional[QtCore.QPropertyAnimation] = None
        self._block_levels = {"now": "", "next": "", "macro": ""}
        self._block_strengths = {"now": 0.0, "next": 0.0, "macro": 0.0}
        self._block_anims: dict[str, QtCore.QVariantAnimation] = {}
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
                background=self._block_background_color("now"),
                background_alpha=140,
                padding=6,
            )
        )
        self.next.setStyleSheet(
            self._label_style(
                self._colors.text_next,
                background=self._block_background_color("next"),
                background_alpha=120,
                padding=6,
            )
        )
        self.macro.setStyleSheet(
            self._label_style(
                self._colors.text_primary,
                background=self._block_background_color("macro"),
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
        if warning_bg_alpha is not None:
            warning_bg_alpha = int(warning_bg_alpha * self._warning_block_strength)
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

        # середина — мягкое затухание
        gradient.setColorAt(
            0.6,
            QtGui.QColor(base.red(), base.green(), base.blue(), int(max_alpha * 0.22)),
        )

        # справа — почти незаметно
        gradient.setColorAt(
            0.9,
            QtGui.QColor(base.red(), base.green(), base.blue(), 0),
        )

        painter.fillRect(rect, gradient)

        painter.end()

    def _block_background_color(self, key: str) -> QtGui.QColor:
        base = self._colors.block_background
        level = self._block_levels.get(key, "")
        strength = self._block_strengths.get(key, 0.0)
        if level == "danger":
            target = self._colors.warning_block_danger
        elif level == "warn":
            target = self._colors.warning_block_warn
        elif level == "info":
            target = self._colors.block_background
        else:
            target = self._colors.block_background
        return self._blend_colors(base, target, strength)

    @staticmethod
    def _blend_colors(
        base: QtGui.QColor,
        target: QtGui.QColor,
        strength: float,
    ) -> QtGui.QColor:
        strength = max(0.0, min(1.0, float(strength)))
        red = int(base.red() + (target.red() - base.red()) * strength)
        green = int(base.green() + (target.green() - base.green()) * strength)
        blue = int(base.blue() + (target.blue() - base.blue()) * strength)
        return QtGui.QColor(red, green, blue)

    def _target_block_strength(self, level: str) -> float:
        if level in {"danger", "warn"}:
            return 1.0
        if level == "info":
            return 0.6
        return 0.0

    def _set_block_level(self, key: str, level: str | None) -> None:
        normalized = str(level or "").lower()
        self._block_levels[key] = normalized
        target = self._target_block_strength(normalized)
        anim = self._block_anims.get(key)
        if anim is None:
            anim = QtCore.QVariantAnimation(self)
            anim.setDuration(450)
            anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
            anim.valueChanged.connect(
                lambda value, block=key: self._update_block_strength(block, value)
            )
            self._block_anims[key] = anim
        anim.stop()
        anim.setStartValue(self._block_strengths.get(key, 0.0))
        anim.setEndValue(target)
        anim.start()

    def _update_block_strength(self, key: str, value: object) -> None:
        self._block_strengths[key] = max(0.0, min(1.0, float(value)))
        self._apply_text_colors()
        self.update()

    def _target_warning_strength(self) -> float:
        if self._warning_level == "danger":
            return 1.0
        if self._warning_level == "warn":
            return 1.0
        if self._warning_level == "info":
            return 0.6
        return 0.0

    def _animate_warning_overlay(self) -> None:
        target = self._target_warning_strength()
        if self._warning_anim is None:
            self._warning_anim = QtCore.QPropertyAnimation(self, b"warningBlockStrength")
            self._warning_anim.setDuration(450)
            self._warning_anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self._warning_anim.stop()
        self._warning_anim.setStartValue(self._warning_block_strength)
        self._warning_anim.setEndValue(target)
        self._warning_anim.start()

    @QtCore.Property(float)
    def warningBlockStrength(self) -> float:
        return self._warning_block_strength

    @warningBlockStrength.setter
    def warningBlockStrength(self, value: float) -> None:
        self._warning_block_strength = max(0.0, min(1.0, float(value)))
        self._apply_text_colors()
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

    def set_now(self, text: str, level: str | None = None) -> None:
        """Обновляет блок NOW."""
        self.now.setText(text)
        self._set_block_level("now", level)

    def set_next(self, text: str, level: str | None = None) -> None:
        """Обновляет блок NEXT."""
        self.next.setText(text)
        self._set_block_level("next", level)

    def set_macro(self, text: str, level: str | None = None) -> None:
        """Обновляет блок MACRO."""
        self.macro.setText(text)
        self._set_block_level("macro", level)

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
