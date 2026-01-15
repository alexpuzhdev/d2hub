from __future__ import annotations

from typing import Callable, Optional

from PySide6 import QtCore, QtGui, QtWidgets

from ..hud_style import HudStyle
from ...application.models import MacroLine
from .styles import default_colors


class MacroProgressBar(QtWidgets.QWidget):
    """Прогресс-бар с градиентной заливкой и скошенным краем."""

    def __init__(
        self,
        height: int,
        text_color: QtGui.QColor,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._progress = 0.0
        self._color = QtGui.QColor()
        self._text = ""
        self._text_color = text_color
        self.setFixedHeight(height)

    def set_data(self, text: str, progress: float, color: QtGui.QColor) -> None:
        self._text = text
        self._progress = max(0.0, min(1.0, progress))
        self._color = color
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        rect = self.rect()
        bar_width = int(rect.width() * self._progress)
        if bar_width > 0:
            slant = min(10, bar_width)
            polygon = QtGui.QPolygonF(
                [
                    QtCore.QPointF(rect.left(), rect.top()),
                    QtCore.QPointF(rect.left() + bar_width - slant, rect.top()),
                    QtCore.QPointF(rect.left() + bar_width, rect.center().y()),
                    QtCore.QPointF(rect.left() + bar_width - slant, rect.bottom()),
                    QtCore.QPointF(rect.left(), rect.bottom()),
                ]
            )
            gradient = QtGui.QLinearGradient(rect.left(), 0, rect.left() + bar_width, 0)
            base = QtGui.QColor(self._color)
            gradient.setColorAt(0.0, QtGui.QColor(base.red(), base.green(), base.blue(), 140))
            gradient.setColorAt(1.0, QtGui.QColor(base.red(), base.green(), base.blue(), 60))
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(gradient))
            painter.drawPolygon(polygon)

        painter.setPen(self._text_color)
        painter.drawText(rect.adjusted(4, 0, -4, 0), QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, self._text)
        painter.end()


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
        self._warning_hold_timer = QtCore.QTimer(self)
        self._warning_hold_timer.setSingleShot(True)
        self._warning_base_strength = 0.0
        self._last_warning_text = ""
        self._last_warning_level = ""
        self._warning_fill_color: QtGui.QColor | None = None
        self._warning_fill_alpha = 0
        self._block_levels = {"now": "", "next": "", "macro": ""}
        self._block_strengths = {"now": 0.0, "next": 0.0, "macro": 0.0}
        self._block_anims: dict[str, QtCore.QVariantAnimation] = {}
        self._auto_height_enabled = True
        self._base_height = style.height
        self._locked = False
        self._drag_enabled = True
        self._drag_offset = QtCore.QPoint()
        self._on_close: Optional[Callable[[], None]] = None
        self._closing = False

        self._configure_window()
        self._build_layout()
        self._apply_text_colors()
        self._warning_hold_timer.timeout.connect(self._fade_warning_overlay)

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
        layout.setContentsMargins(
            self._style.margin_horizontal,
            self._style.margin_vertical,
            self._style.margin_horizontal,
            self._style.margin_vertical,
        )
        layout.setSpacing(self._style.spacing)

        self.timer = QtWidgets.QLabel("0:00")
        self.timer.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.timer.setFont(self._font(self._style.font_size + 12, "bold"))

        self.warning = QtWidgets.QLabel("")
        self._configure_block_label(self.warning, self._style.font_size)
        self.warning.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)

        self.now = QtWidgets.QLabel("ГОТОВО  |  F7 LOCK")
        self._configure_block_label(self.now, self._style.font_size)

        self.next = QtWidgets.QLabel("ДАЛЕЕ: —")
        self._configure_block_label(self.next, self._style.font_size)

        self.macro_title = QtWidgets.QLabel("MACRO:")
        self._configure_block_label(self.macro_title, self._style.font_size)
        self.macro_lines_container = QtWidgets.QWidget()
        self.macro_lines_layout = QtWidgets.QVBoxLayout(self.macro_lines_container)
        self.macro_lines_layout.setContentsMargins(0, 0, 0, 0)
        self.macro_lines_layout.setSpacing(self._style.macro_line_spacing)
        self._macro_line_widgets: list[QtWidgets.QWidget] = []

        layout.addWidget(self.timer)
        layout.addWidget(self.warning)
        layout.addWidget(self.now)
        layout.addWidget(self.next)
        if self._style.macro_show_title:
            layout.addWidget(self.macro_title)
        layout.addWidget(self.macro_lines_container)
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
        label.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        label.setAutoFillBackground(True)
        label.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)

    def _configure_macro_progress(self, bar: MacroProgressBar) -> None:
        bar.setFont(self._font(self._style.font_size, "normal"))

    def _apply_text_colors(self) -> None:
        self.timer.setStyleSheet(self._label_style(self._colors.text_primary))
        self.now.setStyleSheet(
            self._label_style(
                self._colors.text_primary,
                background=self._block_background_color("now"),
                background_alpha=140,
                padding=self._style.block_padding,
            )
        )
        self.next.setStyleSheet(
            self._label_style(
                self._colors.text_next,
                background=self._block_background_color("next"),
                background_alpha=120,
                padding=self._style.block_padding,
            )
        )
        self.macro_title.setStyleSheet(
            self._label_style(
                self._colors.text_primary,
                background=self._block_background_color("macro"),
                background_alpha=120,
                padding=self._style.block_padding,
            )
        )
        if self._warning_level == "danger":
            warning_color = self._colors.text_danger
            warning_bg = self._colors.warning_block_danger
            warning_bg_alpha = 230
        elif self._warning_level == "warn":
            warning_color = self._colors.text_warning
            warning_bg = self._colors.warning_block_warn
            warning_bg_alpha = 210
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
        if warning_bg is not None and warning_bg_alpha is not None:
            self._warning_fill_color = warning_bg
            self._warning_fill_alpha = warning_bg_alpha
        else:
            self._warning_fill_color = None
            self._warning_fill_alpha = 0
        self.warning.setStyleSheet(
            self._label_style(
                warning_color,
                background=warning_bg,
                background_alpha=warning_bg_alpha,
                padding=self._style.block_padding,
            )
        )

    def _resize_to_content(self) -> None:
        if not self._auto_height_enabled:
            return
        if self.layout() is not None:
            self.layout().activate()
            content_height = self.layout().sizeHint().height()
        else:
            content_height = self.sizeHint().height()
        desired_height = max(self._base_height, content_height)
        if desired_height > self.height():
            self.resize(self._style.width, desired_height)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, False)

        rect = self.rect()

        base = QtGui.QColor(self._colors.background_base)
        effective_alpha = max(self._style.alpha, 0.75)
        max_alpha = int(255 * effective_alpha)  # стартовая прозрачность

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

        if self._warning_fill_color and self._warning_fill_alpha > 0:
            warning_rect = self.warning.geometry().adjusted(
                -self._style.block_padding,
                -self._style.block_padding,
                self._style.block_padding,
                self._style.block_padding,
            )
            fill_color = QtGui.QColor(self._warning_fill_color)
            fill_color.setAlpha(self._warning_fill_alpha)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(fill_color))
            painter.drawRoundedRect(warning_rect, 4, 4)

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
        if self._block_levels.get(key) == normalized:
            return
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

    def _base_warning_strength(self) -> float:
        if self._warning_level in {"danger", "warn"}:
            return 0.8 if self._warning_level == "danger" else 0.65
        if self._warning_level == "info":
            return 0.45
        return 0.0

    def _animate_warning_overlay(self) -> None:
        target = self._target_warning_strength()
        if self._warning_anim is None:
            self._warning_anim = QtCore.QPropertyAnimation(self, b"warningBlockStrength")
            self._warning_anim.setDuration(240)
            self._warning_anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self._warning_anim.stop()
        self._warning_anim.setStartValue(self._warning_base_strength)
        self._warning_anim.setEndValue(target)
        self._warning_anim.start()
        self._warning_hold_timer.stop()
        self._warning_hold_timer.start(220)

    def _fade_warning_overlay(self) -> None:
        if not self._warning_anim:
            return
        self._warning_anim.stop()
        self._warning_anim.setStartValue(self._warning_block_strength)
        self._warning_anim.setEndValue(self._warning_base_strength)
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
        warning_text = text or ""
        self.warning.setText(warning_text)
        if level is None and isinstance(text, bool):
            warning_level = "warn" if text else ""
        else:
            warning_level = str(level or "")
        should_animate = (
            warning_text != self._last_warning_text
            or warning_level != self._last_warning_level
        )
        self._warning_level = warning_level
        self._last_warning_text = warning_text
        self._last_warning_level = warning_level
        self._warning_base_strength = self._base_warning_strength()
        if not should_animate:
            self._warning_block_strength = self._warning_base_strength
        self._apply_text_colors()
        if should_animate:
            self._animate_warning_overlay()
        self._resize_to_content()
        self.update()

    def set_timer(self, text: str) -> None:
        """Обновляет текст таймера."""
        self.timer.setText(text)

    def set_now(self, text: str, level: str | None = None) -> None:
        """Обновляет блок NOW."""
        self.now.setText(text)
        self._set_block_level("now", level)
        self._resize_to_content()

    def set_next(self, text: str, level: str | None = None) -> None:
        """Обновляет блок NEXT."""
        self.next.setText(text)
        self._set_block_level("next", level)
        self._resize_to_content()

    def _parse_macro_color(self, value: str | None) -> QtGui.QColor:
        if not value:
            return self._colors.block_background
        color = QtGui.QColor(str(value))
        if not color.isValid():
            return self._colors.block_background
        return color

    def _apply_macro_lines(self, lines: list["MacroLine"]) -> None:
        for widget in self._macro_line_widgets:
            self.macro_lines_layout.removeWidget(widget)
            widget.deleteLater()
        self._macro_line_widgets.clear()

        if not lines:
            fallback = QtWidgets.QLabel("MACRO: —")
            self._configure_block_label(fallback, self._style.font_size)
            fallback.setStyleSheet(
                self._label_style(
                    self._colors.text_primary,
                    background=self._block_background_color("macro"),
                    background_alpha=120,
                    padding=self._style.block_padding,
                )
            )
            self.macro_lines_layout.addWidget(fallback)
            self._macro_line_widgets.append(fallback)
            return

        for line in lines:
            bar = MacroProgressBar(
                self._style.macro_bar_height,
                self._colors.text_primary,
            )
            self._configure_macro_progress(bar)
            color = self._parse_macro_color(line.color)
            bar.set_data(line.text, line.progress or 0.0, color)
            self.macro_lines_layout.addWidget(bar)
            self._macro_line_widgets.append(bar)

    def set_macro(
        self,
        text: str,
        level: str | None = None,
        lines: list["MacroLine"] | None = None,
    ) -> None:
        """Обновляет блок MACRO."""
        if self._style.macro_show_title:
            self.macro_title.setText("MACRO:")
        self._set_block_level("macro", level)
        self._apply_macro_lines(lines or [])
        self._resize_to_content()

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
