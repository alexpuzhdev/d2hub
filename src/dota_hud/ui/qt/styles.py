from __future__ import annotations

from dataclasses import dataclass

from PySide6 import QtGui


@dataclass(frozen=True)
class HudColors:
    background_top: QtGui.QColor
    background_bottom: QtGui.QColor
    panel: QtGui.QColor
    panel_alt: QtGui.QColor
    text_primary: QtGui.QColor
    text_muted: QtGui.QColor
    accent_info: QtGui.QColor
    accent_warn: QtGui.QColor
    accent_danger: QtGui.QColor


def default_colors() -> HudColors:
    return HudColors(
        background_top=QtGui.QColor(26, 28, 32),
        background_bottom=QtGui.QColor(12, 12, 14),
        panel=QtGui.QColor(22, 24, 28),
        panel_alt=QtGui.QColor(30, 32, 36),
        text_primary=QtGui.QColor(235, 238, 242),
        text_muted=QtGui.QColor(170, 176, 186),
        accent_info=QtGui.QColor(102, 170, 255),
        accent_warn=QtGui.QColor(255, 176, 64),
        accent_danger=QtGui.QColor(255, 88, 88),
    )
