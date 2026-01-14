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
    """Возвращает палитру в стиле Dota+."""
    return HudColors(
        background_base=QtGui.QColor("#3d535f"),
        text_primary=QtGui.QColor(233, 236, 240),
        text_next=QtGui.QColor(217, 225, 235),
        text_muted=QtGui.QColor(168, 176, 186),
        text_warning=QtGui.QColor(233, 199, 129),
        text_danger=QtGui.QColor(232, 156, 128),
    )
