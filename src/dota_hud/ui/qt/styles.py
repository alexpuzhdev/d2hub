from __future__ import annotations

from dataclasses import dataclass

from PySide6 import QtGui


@dataclass(frozen=True)
class HudColors:
    """Цветовая палитра HUD."""

    background_base: QtGui.QColor
    text_primary: QtGui.QColor
    text_next: QtGui.QColor
    text_muted: QtGui.QColor
    text_info: QtGui.QColor
    text_warning: QtGui.QColor
    text_danger: QtGui.QColor


def default_colors() -> HudColors:
    """Палитра, визуально приближенная к Dota+ HUD."""
    return HudColors(
        # холодный графит с зелёно-циановым уклоном
        background_base=QtGui.QColor(26, 38, 40),

        # основной текст: не чисто белый
        text_primary=QtGui.QColor(225, 228, 232),

        # вторичный текст
        text_next=QtGui.QColor(200, 206, 214),

        # приглушённый текст
        text_muted=QtGui.QColor(160, 168, 176),

        # info: нейтральный светлый
        text_info=QtGui.QColor(208, 208, 208),

        # warning: тёплый жёлтый
        text_warning=QtGui.QColor(255, 184, 77),

        # danger: яркий красный
        text_danger=QtGui.QColor(255, 77, 77),
    )
