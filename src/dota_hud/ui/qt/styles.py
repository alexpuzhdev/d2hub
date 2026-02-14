from __future__ import annotations

from dataclasses import dataclass

from PySide6 import QtGui


@dataclass(frozen=True)
class HudColors:
    """Цветовая палитра HUD."""

    background_base: QtGui.QColor
    block_background: QtGui.QColor
    text_primary: QtGui.QColor
    text_next: QtGui.QColor
    text_muted: QtGui.QColor
    text_info: QtGui.QColor
    text_warning: QtGui.QColor
    text_danger: QtGui.QColor
    warning_overlay_warn: QtGui.QColor
    warning_overlay_danger: QtGui.QColor
    warning_block_warn: QtGui.QColor
    warning_block_danger: QtGui.QColor


def default_colors() -> HudColors:
    """Палитра, визуально приближенная к Dota+ HUD."""
    return HudColors(
        # холодный графит с зелёно-циановым уклоном
        background_base=QtGui.QColor(22, 34, 40),
        block_background=QtGui.QColor(18, 28, 32),

        # основной текст: не чисто белый
        text_primary=QtGui.QColor(232, 236, 240),

        # вторичный текст
        text_next=QtGui.QColor(206, 212, 218),

        # приглушённый текст
        text_muted=QtGui.QColor(176, 182, 188),

        # info: нейтральный светлый
        text_info=QtGui.QColor(210, 214, 218),

        # warning: тёплый жёлтый
        text_warning=QtGui.QColor(255, 191, 88),

        # danger: яркий красный
        text_danger=QtGui.QColor(255, 92, 92),

        # предупреждения: фоновые оверлеи
        warning_overlay_warn=QtGui.QColor(165, 116, 44),
        warning_overlay_danger=QtGui.QColor(170, 54, 54),
        warning_block_warn=QtGui.QColor(118, 82, 32),
        warning_block_danger=QtGui.QColor(112, 40, 40),
    )
