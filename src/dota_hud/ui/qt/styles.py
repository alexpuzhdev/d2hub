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
        background_base=QtGui.QColor(26, 38, 40),
        block_background=QtGui.QColor(24, 34, 36),

        # основной текст: не чисто белый
        text_primary=QtGui.QColor(226, 231, 236),

        # вторичный текст
        text_next=QtGui.QColor(201, 209, 216),

        # приглушённый текст
        text_muted=QtGui.QColor(166, 174, 182),

        # info: нейтральный светлый
        text_info=QtGui.QColor(208, 208, 208),

        # warning: тёплый жёлтый
        text_warning=QtGui.QColor(255, 184, 77),

        # danger: яркий красный
        text_danger=QtGui.QColor(255, 77, 77),

        # предупреждения: фоновые оверлеи
        warning_overlay_warn=QtGui.QColor(172, 118, 35),
        warning_overlay_danger=QtGui.QColor(175, 48, 48),
        warning_block_warn=QtGui.QColor(125, 86, 28),
        warning_block_danger=QtGui.QColor(120, 35, 35),
    )
