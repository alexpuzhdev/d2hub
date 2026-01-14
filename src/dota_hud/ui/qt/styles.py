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

        # warning: золото
        text_warning=QtGui.QColor(215, 185, 120),

        # danger: приглушённый кирпично-красный
        text_danger=QtGui.QColor(210, 135, 120),
    )

